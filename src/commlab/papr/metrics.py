import numpy as np


def papr_linear(signal: np.ndarray) -> float:
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    power = np.abs(x) ** 2
    mean = np.mean(power)
    if mean == 0:
        raise ValueError("signal power must be nonzero")
    return float(np.max(power) / mean)


def papr_db(signal: np.ndarray) -> float:
    return float(10.0 * np.log10(papr_linear(signal)))


def clip_magnitude(signal: np.ndarray, ratio_to_rms: float) -> np.ndarray:
    """Hard envelope clipping at ratio_to_rms * RMS magnitude."""
    if ratio_to_rms <= 0:
        raise ValueError("ratio_to_rms must be positive")
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    rms = np.sqrt(np.mean(np.abs(x) ** 2))
    threshold = ratio_to_rms * rms
    mag = np.abs(x)
    scale = np.ones_like(mag)
    mask = mag > threshold
    scale[mask] = threshold / mag[mask]
    return x * scale
