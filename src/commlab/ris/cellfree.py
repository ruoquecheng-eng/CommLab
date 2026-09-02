import numpy as np
from commlab.mimo.cell_free import clustered_mrt_precoder, per_user_rates


def effective_cellfree_ris_channel(h_direct: np.ndarray, g_ap_ris: np.ndarray,
                                   h_ris_user: np.ndarray, phases: np.ndarray,
                                   amplitude: float = 1.0) -> np.ndarray:
    """K x M distributed-AP channel assisted by one RIS."""
    D = np.asarray(h_direct, np.complex128)
    G = np.asarray(g_ap_ris, np.complex128)  # N x M
    R = np.asarray(h_ris_user, np.complex128)  # K x N
    th = np.asarray(phases, float).reshape(-1)
    if D.ndim != 2 or G.ndim != 2 or R.ndim != 2 or R.shape[0] != D.shape[0] or G.shape[1] != D.shape[1] or G.shape[0] != R.shape[1] or len(th) != G.shape[0]:
        raise ValueError('invalid channel dimensions')
    if not (0 <= amplitude <= 1):
        raise ValueError('invalid amplitude')
    return D + float(amplitude) * (R * np.exp(1j * th)[None, :]) @ G


def cellfree_ris_rates(h_direct: np.ndarray, g_ap_ris: np.ndarray, h_ris_user: np.ndarray,
                       phases: np.ndarray, snr_linear: float, mask: np.ndarray | None = None) -> np.ndarray:
    H = effective_cellfree_ris_channel(h_direct, g_ap_ris, h_ris_user, phases)
    W = clustered_mrt_precoder(H, mask=mask)
    return per_user_rates(H, W, snr_linear)


def coordinate_optimize_cellfree_ris(h_direct: np.ndarray, g_ap_ris: np.ndarray,
                                     h_ris_user: np.ndarray, snr_linear: float,
                                     bits: int = 2, iterations: int = 2,
                                     mask: np.ndarray | None = None,
                                     objective: str = 'sum_rate',
                                     initial_phases: np.ndarray | None = None) -> tuple[np.ndarray, list[float]]:
    """Finite-resolution RIS coordinate ascent for distributed APs.

    ``objective`` is ``sum_rate`` or ``min_rate``.  The latter intentionally
    sacrifices aggregate throughput to favor the weakest user.
    """
    N = np.asarray(g_ap_ris).shape[0]
    if bits < 1 or iterations < 1 or objective not in {'sum_rate', 'min_rate'}:
        raise ValueError('invalid optimization parameters')
    th = np.zeros(N, float) if initial_phases is None else np.asarray(initial_phases, float).reshape(-1).copy()
    if len(th) != N:
        raise ValueError('invalid initial phases')
    levels = 2 * np.pi * np.arange(2 ** int(bits)) / (2 ** int(bits))
    def utility(x):
        r = cellfree_ris_rates(h_direct, g_ap_ris, h_ris_user, x, snr_linear, mask)
        return float(r.sum() if objective == 'sum_rate' else r.min())
    best = utility(th)
    hist = [best]
    for _ in range(int(iterations)):
        for n in range(N):
            old = th[n]; local = best; best_phase = old
            for p in levels:
                th[n] = p
                val = utility(th)
                if val > local + 1e-12:
                    local = val; best_phase = float(p)
            th[n] = best_phase; best = local
        hist.append(best)
    return np.angle(np.exp(1j * th)), hist
