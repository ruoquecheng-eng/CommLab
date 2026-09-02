import numpy as np


def mmse_equalize(
    symbols: np.ndarray,
    channel: np.ndarray,
    noise_var: float | np.ndarray,
    symbol_energy: float = 1.0,
    eps: float = 1e-12,
) -> np.ndarray:
    """One-tap scalar MMSE equalizer for OFDM subcarriers.

    y = h*x + n, E|x|^2 = symbol_energy, E|n|^2 = noise_var.
    """
    y = np.asarray(symbols, dtype=np.complex128)
    h = np.asarray(channel, dtype=np.complex128)
    nv = np.asarray(noise_var, dtype=float)
    denom = np.abs(h) ** 2 + nv / max(symbol_energy, eps)
    return np.conj(h) * y / np.maximum(denom, eps)
