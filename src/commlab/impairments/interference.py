import numpy as np


def add_complex_tone_interference(
    signal: np.ndarray,
    normalized_frequency: float,
    sir_db: float,
    phase_rad: float = 0.0,
) -> np.ndarray:
    """Add a complex sinusoidal interferer at cycles/sample.

    SIR is desired-signal average power divided by tone power.
    """
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    p_sig = float(np.mean(np.abs(x) ** 2))
    p_int = p_sig / (10.0 ** (float(sir_db) / 10.0)) if p_sig > 0 else 0.0
    n = np.arange(len(x), dtype=float)
    tone = np.sqrt(p_int) * np.exp(1j * (2*np.pi*float(normalized_frequency)*n + phase_rad))
    return x + tone


def detect_narrowband_outliers(received_grid: np.ndarray, z_threshold: float = 4.0) -> np.ndarray:
    """Robustly flag frequency bins with persistent excess power.

    ``received_grid`` shape is (n_symbols, n_carriers). Detection operates on
    median carrier power and a MAD-normalized score.
    """
    y = np.asarray(received_grid, dtype=np.complex128)
    if y.ndim != 2:
        raise ValueError("received_grid must be 2-D")
    p = np.median(np.abs(y) ** 2, axis=0)
    med = np.median(p)
    mad = np.median(np.abs(p - med)) + 1e-15
    score = 0.67448975 * (p - med) / mad
    return np.flatnonzero(score > float(z_threshold))
