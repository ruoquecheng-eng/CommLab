import numpy as np


def normalized_preamble_correlation(rx: np.ndarray, preamble: np.ndarray) -> np.ndarray:
    """Normalized sliding correlation magnitude for known-preamble timing."""
    r = np.asarray(rx, dtype=np.complex128).reshape(-1)
    p = np.asarray(preamble, dtype=np.complex128).reshape(-1)
    if len(r) < len(p):
        raise ValueError("received sequence is shorter than preamble")
    corr = np.correlate(r, p, mode="valid")
    p_energy = np.sum(np.abs(p) ** 2)
    rx_energy = np.convolve(np.abs(r) ** 2, np.ones(len(p)), mode="valid")
    return np.abs(corr) ** 2 / (p_energy * rx_energy + 1e-15)


def detect_frame_start(rx: np.ndarray, preamble: np.ndarray) -> tuple[int, float]:
    metric = normalized_preamble_correlation(rx, preamble)
    idx = int(np.argmax(metric))
    return idx, float(metric[idx])


def schmidl_cox_metric(rx: np.ndarray, n_fft: int = 64) -> np.ndarray:
    """Compute the repeated-half Schmidl-Cox timing metric.

    M(d)=|P(d)|^2/R(d)^2, with energy measured over both halves to avoid
    spurious burst-end peaks, similar to the normalization used in GNU Radio.
    """
    r = np.asarray(rx, dtype=np.complex128).reshape(-1)
    if n_fft % 2:
        raise ValueError("n_fft must be even")
    L = n_fft // 2
    if len(r) < 2 * L:
        raise ValueError("received sequence is too short")
    out = np.empty(len(r) - 2 * L + 1, dtype=float)
    for d in range(len(out)):
        a = r[d : d + L]
        b = r[d + L : d + 2 * L]
        P = np.vdot(a, b)
        R = 0.5 * (np.sum(np.abs(a) ** 2) + np.sum(np.abs(b) ** 2))
        out[d] = (np.abs(P) ** 2) / (R**2 + 1e-15)
    return out


def estimate_cfo_from_repeated_halves(preamble_rx: np.ndarray, n_fft: int = 64) -> float:
    """Estimate normalized CFO from the phase between repeated halves.

    The unambiguous range is approximately |epsilon| < 1 for a half-symbol
    repetition. The return value is in subcarrier-spacing units.
    """
    r = np.asarray(preamble_rx, dtype=np.complex128).reshape(-1)
    if len(r) < n_fft:
        raise ValueError("need at least one full preamble")
    L = n_fft // 2
    first = r[:L]
    second = r[L : 2 * L]
    P = np.vdot(first, second)
    phase = np.angle(P)
    return float(phase * n_fft / (2.0 * np.pi * L))


def correct_cfo(signal: np.ndarray, normalized_cfo: float, n_fft: int = 64, start_index: int = 0) -> np.ndarray:
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    n = np.arange(start_index, start_index + len(x))
    rot = np.exp(-1j * 2.0 * np.pi * normalized_cfo * n / n_fft)
    return x * rot
