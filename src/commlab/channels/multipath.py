import numpy as np


def apply_multipath(signal: np.ndarray, taps: np.ndarray, keep_length: bool = True) -> np.ndarray:
    x = np.asarray(signal, dtype=np.complex128)
    h = np.asarray(taps, dtype=np.complex128)
    y = np.convolve(x, h, mode="full")
    return y[: len(x)] if keep_length else y


def channel_frequency_response(taps: np.ndarray, n_fft: int) -> np.ndarray:
    h = np.asarray(taps, dtype=np.complex128)
    return np.fft.fft(h, n=n_fft)
