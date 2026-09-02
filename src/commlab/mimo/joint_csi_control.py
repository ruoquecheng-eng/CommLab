import numpy as np

from commlab.mimo.cell_free import clustered_mrt_precoder, per_user_rates, sample_cell_free_channel
from commlab.mimo.fronthaul import gauss_markov_channel_step, quantize_complex_csi


def _quantization_nmse_proxy(bits: int) -> float:
    """High-resolution scalar-quantization distortion proxy.

    The constant is intentionally simple; scheduling uses this only to rank
    refresh/bit-depth actions. Actual simulation distortion comes from the real
    scalar quantizer in :mod:`commlab.mimo.fronthaul`.
    """
    if bits < 1:
        raise ValueError("bits must be positive")
    return float(2.0 ** (-2 * int(bits)))


def schedule_joint_csi_actions(beta: np.ndarray, mask: np.ndarray, ages: np.ndarray,
                               correlation: np.ndarray | float, total_budget_bits: int,
                               min_bits: int = 2, max_bits: int = 8) -> list[tuple[int, int]]:
    """Greedy AP-refresh and CSI-bit allocation under one fronthaul budget.

    Candidate utility is the expected stale-channel MSE removed by refreshing an
    AP, minus a transparent quantization-distortion proxy. Cost is the number of
    real/imaginary CSI scalars sent for the AP's active user links.

    One action ``(ap, bits)`` may be selected per AP. This is a deterministic,
    interpretable baseline rather than a globally optimal integer program.
    """
    B = np.asarray(beta, float)
    S = np.asarray(mask, bool)
    a = np.asarray(ages, int).reshape(-1)
    if B.ndim != 2 or S.shape != B.shape or len(a) != B.shape[1] or np.any(a < 0):
        raise ValueError("invalid CSI scheduling inputs")
    M = B.shape[1]
    if np.isscalar(correlation):
        rho = np.full(M, float(correlation))
    else:
        rho = np.asarray(correlation, float).reshape(-1)
    if len(rho) != M or np.any((rho < 0) | (rho > 1)):
        raise ValueError("invalid channel correlation")
    if total_budget_bits < 0 or min_bits < 1 or max_bits < min_bits:
        raise ValueError("invalid bit budget")

    candidates = []
    for m in range(M):
        links = int(S[:, m].sum())
        if links == 0:
            continue
        power = float(np.sum(B[S[:, m], m]))
        stale = power * (1.0 - rho[m] ** (2 * a[m]))
        for b in range(int(min_bits), int(max_bits) + 1):
            cost = 2 * links * b
            residual = power * _quantization_nmse_proxy(b)
            benefit = max(stale - residual, 0.0)
            score = benefit / max(cost, 1)
            candidates.append((score, benefit, -cost, -b, m, b, cost))

    # Highest expected MSE reduction per fronthaul bit first; stable AP index
    # tie-breaking keeps Monte Carlo runs deterministic.
    candidates.sort(reverse=True)
    used = 0
    selected: list[tuple[int, int]] = []
    taken = set()
    for _, benefit, _, _, m, b, cost in candidates:
        if benefit <= 0 or m in taken or used + cost > total_budget_bits:
            continue
        selected.append((int(m), int(b)))
        taken.add(int(m))
        used += int(cost)
    return selected


def simulate_joint_predictive_csi_control(beta: np.ndarray, mask: np.ndarray,
                                          correlation: np.ndarray | float,
                                          snr_linear: float,
                                          total_budget_bits: int,
                                          n_slots: int = 300,
                                          policy: str = "joint",
                                          fixed_bits: int = 5,
                                          min_bits: int = 2,
                                          max_bits: int = 8,
                                          seed: int = 1) -> dict:
    """Cell-Free CSI refresh with prediction, differential feedback and bit budget.

    Policies
    --------
    ``joint``
        Jointly chooses APs and bit depth under the per-slot budget.
    ``uncertainty_fixed``
        Uses fixed bit depth and refreshes APs with largest expected aging MSE.
    ``round_robin``
        Fixed bit depth and deterministic AP rotation.

    At every slot the CPU predicts stale CSI with the known Gauss-Markov mean.
    A refreshed AP sends only the innovation relative to that predictor. Thus the
    experiment couples *when to refresh* and *how accurately to describe the
    innovation* while keeping the quantizer itself fully explicit.
    """
    B = np.asarray(beta, float)
    S = np.asarray(mask, bool)
    if B.ndim != 2 or S.shape != B.shape or np.any(B < 0) or snr_linear <= 0:
        raise ValueError("invalid joint CSI setup")
    if n_slots < 2 or total_budget_bits < 0 or policy not in {"joint", "uncertainty_fixed", "round_robin"}:
        raise ValueError("invalid simulation settings")
    K, M = B.shape
    if np.isscalar(correlation):
        rho = np.full(M, float(correlation))
    else:
        rho = np.asarray(correlation, float).reshape(-1)
    if len(rho) != M or np.any((rho < 0) | (rho > 1)):
        raise ValueError("invalid correlation")

    rng = np.random.default_rng(seed)
    H = sample_cell_free_channel(B, rng)
    Hhat = np.zeros_like(H)
    # Initial acquisition is outside the steady-state budget comparison.
    Hhat[S] = quantize_complex_csi(H[S], max(fixed_bits, min_bits))
    ages = np.zeros(M, int)
    rr = 0

    rates = []
    nmse = []
    bit_hist = []
    action_hist = []
    age_hist = []

    served_links = S.sum(axis=0).astype(int)
    for t in range(int(n_slots)):
        if t > 0:
            # True channel evolves, while the CPU advances its conditional mean.
            for m in range(M):
                H[:, m] = gauss_markov_channel_step(H[:, m], B[:, m], rho[m], rng)
                Hhat[:, m] *= rho[m]
            ages += 1

            if policy == "joint":
                actions = schedule_joint_csi_actions(B, S, ages, rho, total_budget_bits,
                                                     min_bits=min_bits, max_bits=max_bits)
            else:
                costs = 2 * served_links * int(fixed_bits)
                feasible = np.where((served_links > 0) & (costs <= total_budget_bits))[0]
                # A common fixed-bit refresh count gives the two baselines the
                # same per-slot hard budget.
                min_cost = int(np.min(costs[feasible])) if len(feasible) else total_budget_bits + 1
                count = min(M, int(total_budget_bits // max(min_cost, 1))) if min_cost <= total_budget_bits else 0
                if policy == "round_robin":
                    idx = []
                    checked = 0
                    # Never wrap more than once inside a slot: an AP must not
                    # consume the refresh budget twice while another AP starves.
                    while len(idx) < count and checked < M:
                        m = (rr + checked) % M
                        if served_links[m] > 0 and costs[m] <= total_budget_bits:
                            idx.append(m)
                        checked += 1
                    rr = (rr + max(len(idx), 1)) % M
                else:
                    power = np.sum(B * S, axis=0)
                    score = power * (1.0 - rho ** (2 * ages))
                    feasible_set = np.asarray(feasible, int)
                    order = feasible_set[np.lexsort((feasible_set, -score[feasible_set]))]
                    idx = list(order[:count])
                actions = [(int(m), int(fixed_bits)) for m in idx]
                # Enforce the actual heterogeneous-link budget.
                kept = []
                used = 0
                for m, b in actions:
                    c = 2 * served_links[m] * b
                    if used + c <= total_budget_bits:
                        kept.append((m, b)); used += c
                actions = kept

            used_bits = 0
            for m, b in actions:
                served = S[:, m]
                if not np.any(served):
                    continue
                innovation = H[served, m] - Hhat[served, m]
                Hhat[served, m] += quantize_complex_csi(innovation, int(b))
                Hhat[~served, m] = 0
                ages[m] = 0
                used_bits += int(2 * served.sum() * b)
            bit_hist.append(used_bits)
            action_hist.append(actions)
        else:
            bit_hist.append(0)
            action_hist.append([])

        W = clustered_mrt_precoder(Hhat, S)
        rates.append(per_user_rates(H, W, snr_linear))
        err = float(np.sum(np.abs((H - Hhat)[S]) ** 2))
        den = max(float(np.sum(np.abs(H[S]) ** 2)), 1e-15)
        nmse.append(err / den)
        age_hist.append(ages.copy())

    R = np.asarray(rates)
    A = np.asarray(age_hist)
    return {
        "rates": R,
        "mean_user_rate": float(R.mean()),
        "edge_rate": float(np.quantile(R, 0.05)),
        "mean_sum_rate": float(R.sum(axis=1).mean()),
        "mean_csi_nmse": float(np.mean(nmse)),
        "mean_fronthaul_bits_per_slot": float(np.mean(bit_hist[1:])),
        "mean_ap_age": float(A.mean()),
        "p95_ap_age": float(np.quantile(A, 0.95)),
        "bit_history": np.asarray(bit_hist),
        "age_history": A,
        "action_history": action_hist,
    }
