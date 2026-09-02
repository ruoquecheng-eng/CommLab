import numpy as np

from commlab.sensing.resource_scheduling import posterior_angle_std
from commlab.sensing.beam_tracking import expected_ula_rate_under_angle_uncertainty


def simulate_budget_constrained_sensing(process_std_deg: np.ndarray, initial_std_deg: float,
                                        candidate_elements, sensing_fractions,
                                        snr_per_element_linear: float,
                                        average_sensing_budget: float,
                                        information_weight: float = 0.6,
                                        dual_step: float = 0.8,
                                        reference_std_deg: float = 2.5) -> dict:
    """Online ISAC sensing control with a long-term average resource budget.

    A virtual dual price penalizes sensing whenever cumulative use exceeds the
    target budget. The controller therefore spends sensing resources during
    high-uncertainty/maneuver periods and saves them during calm periods while
    enforcing the budget only in a long-term average sense.

    This is a transparent primal-dual heuristic, not an optimal constrained MDP.
    """
    q = np.asarray(process_std_deg, float).reshape(-1)
    if len(q) < 1 or initial_std_deg <= 0 or np.any(q < 0):
        raise ValueError("invalid sensing trace")
    if not (0 <= average_sensing_budget < 1) or dual_step < 0 or information_weight < 0:
        raise ValueError("invalid budget parameters")
    elems = [int(x) for x in candidate_elements]
    fracs = [float(x) for x in sensing_fractions]
    if not elems or not fracs or any(x <= 0 for x in elems) or any((x < 0 or x >= 1) for x in fracs):
        raise ValueError("invalid action set")

    prior = float(initial_std_deg)
    price = 0.0
    used_sensing = 0.0
    rows = []
    for t, proc in enumerate(q):
        prior = float(np.sqrt(prior ** 2 + proc ** 2))
        best = None
        # Cumulative token budget makes the long-term resource constraint hard:
        # by the end of slot t, sensing use cannot exceed (t+1)*budget.
        allowed = (t + 1) * float(average_sensing_budget)
        for f in fracs:
            if used_sensing + f > allowed + 1e-12:
                continue
            post = posterior_angle_std(prior, f, reference_std_deg)
            info = float(np.log(max(prior / post, 1.0)))
            for n in elems:
                raw = expected_ula_rate_under_angle_uncertainty(post, n, snr_per_element_linear)
                payload = (1.0 - f) * raw
                utility = payload + information_weight * info - price * f
                cand = (utility, f, n, post, payload, info, raw)
                if best is None or cand[0] > best[0]:
                    best = cand
        if best is None:
            raise RuntimeError('action set must contain a budget-feasible sensing action, typically f=0')
        _, f, n, post, payload, info, raw = best
        used_sensing += f
        price = max(0.0, price + dual_step * (f - average_sensing_budget))
        prior = post
        rows.append({"slot": t, "sensing_fraction": f, "elements": n,
                     "posterior_std_deg": post, "payload_rate": payload,
                     "raw_rate": raw, "information_gain": info, "dual_price": price})

    sf = np.asarray([r["sensing_fraction"] for r in rows], float)
    ps = np.asarray([r["posterior_std_deg"] for r in rows], float)
    pr = np.asarray([r["payload_rate"] for r in rows], float)
    return {
        "rows": rows,
        "mean_sensing_fraction": float(sf.mean()),
        "mean_posterior_std_deg": float(ps.mean()),
        "mean_payload_rate": float(pr.mean()),
        "final_dual_price": float(price),
        "sensing_fraction": sf,
        "posterior_std_deg": ps,
        "payload_rate": pr,
    }
