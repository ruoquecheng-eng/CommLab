import numpy as np


def random_pilot_assignment(n_users: int, n_pilots: int, rng: np.random.Generator) -> np.ndarray:
    if n_users < 1 or n_pilots < 1:
        raise ValueError('positive user/pilot counts required')
    return rng.integers(0, int(n_pilots), size=int(n_users), dtype=int)


def large_scale_overlap(beta: np.ndarray) -> np.ndarray:
    """Cosine overlap of users' large-scale fading fingerprints across APs."""
    B = np.asarray(beta, float)
    if B.ndim != 2 or np.any(B < 0):
        raise ValueError('beta must be nonnegative 2-D')
    n = np.linalg.norm(B, axis=1, keepdims=True)
    X = B / np.maximum(n, 1e-15)
    C = X @ X.T
    np.fill_diagonal(C, 0.0)
    return np.clip(C, 0.0, 1.0)


def pilot_contamination_cost(beta: np.ndarray, assignment: np.ndarray) -> float:
    """Sum of large-scale-fading overlaps among users reusing a pilot."""
    C = large_scale_overlap(beta)
    p = np.asarray(assignment, int).reshape(-1)
    if len(p) != C.shape[0] or np.any(p < 0):
        raise ValueError('invalid pilot assignment')
    same = p[:, None] == p[None, :]
    return float(np.triu(C * same, 1).sum())


def greedy_contamination_aware_assignment(beta: np.ndarray, n_pilots: int) -> np.ndarray:
    """Greedy pilot assignment minimizing accumulated co-pilot overlap.

    Strong users are processed first.  For each user, the pilot yielding the
    smallest sum of large-scale overlap with already assigned co-pilot users is
    selected.  This is a transparent heuristic, not a global optimum.
    """
    B = np.asarray(beta, float)
    if B.ndim != 2 or np.any(B < 0) or n_pilots < 1:
        raise ValueError('invalid beta/pilot count')
    K = B.shape[0]
    P = int(n_pilots)
    C = large_scale_overlap(B)
    order = np.argsort(-B.sum(axis=1))
    out = np.full(K, -1, int)
    load = np.zeros(P, int)
    for rank, k in enumerate(order):
        if rank < min(P, K):
            pilot = rank
        else:
            costs = np.empty(P, float)
            for q in range(P):
                users = np.where(out == q)[0]
                # Tiny load regularizer avoids pathological unbalanced reuse.
                costs[q] = C[k, users].sum() + 1e-6 * load[q]
            pilot = int(np.argmin(costs))
        out[k] = pilot
        load[pilot] += 1
    return out


def lmmse_pilot_channel_estimate(
    true_h: np.ndarray,
    beta: np.ndarray,
    assignment: np.ndarray,
    pilot_snr_linear: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Per-AP LMMSE channel estimate under pilot reuse.

    Model for pilot p at AP m:
        y_pm = sqrt(rho_p) * sum_{j:p_j=p} h_jm + n_pm
    with h_jm ~ CN(0,beta_jm), n~CN(0,1).
    """
    H = np.asarray(true_h, np.complex128)
    B = np.asarray(beta, float)
    p = np.asarray(assignment, int).reshape(-1)
    if H.shape != B.shape or H.ndim != 2 or len(p) != H.shape[0] or pilot_snr_linear <= 0:
        raise ValueError('invalid dimensions/SNR')
    if np.any(p < 0):
        raise ValueError('invalid pilot indices')
    K, M = H.shape
    rho = float(pilot_snr_linear)
    P = int(p.max()) + 1
    noise = (rng.normal(size=(P, M)) + 1j * rng.normal(size=(P, M))) / np.sqrt(2)
    Y = noise.copy()
    for q in range(P):
        users = np.where(p == q)[0]
        if len(users):
            Y[q] += np.sqrt(rho) * H[users].sum(axis=0)
    Hhat = np.zeros_like(H)
    for k in range(K):
        q = p[k]
        users = np.where(p == q)[0]
        denom = 1.0 + rho * B[users].sum(axis=0)
        coeff = np.sqrt(rho) * B[k] / np.maximum(denom, 1e-15)
        Hhat[k] = coeff * Y[q]
    return Hhat


def normalized_channel_mse(true_h: np.ndarray, estimate: np.ndarray) -> float:
    H = np.asarray(true_h, np.complex128)
    E = np.asarray(estimate, np.complex128)
    if H.shape != E.shape:
        raise ValueError('shape mismatch')
    return float(np.sum(np.abs(H - E) ** 2) / max(np.sum(np.abs(H) ** 2), 1e-15))
