import numpy as np


def zf_equalize(symbols: np.ndarray, channel: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    y = np.asarray(symbols, dtype=np.complex128)
    h = np.asarray(channel, dtype=np.complex128)
    safe_h = np.where(np.abs(h) < eps, eps + 0j, h)
    return y / safe_h
