import numpy as np


def prepend_timing_offset(signal: np.ndarray, offset: int, fill: complex = 0j) -> np.ndarray:
    """Prepend samples to model unknown frame arrival time."""
    if offset < 0:
        raise ValueError("offset must be nonnegative")
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    prefix = np.full(offset, fill, dtype=np.complex128)
    return np.concatenate((prefix, x))


def apply_cfo(signal: np.ndarray, normalized_cfo: float, n_fft: int = 64, start_index: int = 0) -> np.ndarray:
    """Apply normalized CFO in units of OFDM subcarrier spacing.

    epsilon=1 means an offset of one subcarrier spacing, i.e. Fs/Nfft.
    """
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    n = np.arange(start_index, start_index + len(x))
    rot = np.exp(1j * 2.0 * np.pi * normalized_cfo * n / n_fft)
    return x * rot


def apply_phase_offset(signal: np.ndarray, phase_rad: float) -> np.ndarray:
    x = np.asarray(signal, dtype=np.complex128)
    return x * np.exp(1j * phase_rad)
