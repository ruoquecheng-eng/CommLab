import numpy as np


def apply_doppler_multipath(
    signal: np.ndarray,
    taps: np.ndarray,
    delays: np.ndarray,
    normalized_dopplers: np.ndarray,
    n_fft: int,
) -> np.ndarray:
    """Apply a sparse time-varying multipath channel.

    normalized_dopplers are in units of OFDM subcarrier spacing, so a path with
    nu=1 rotates by 2*pi/Nfft radians per sample.
    """
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    h = np.asarray(taps, dtype=np.complex128).reshape(-1)
    d = np.asarray(delays, dtype=int).reshape(-1)
    nu = np.asarray(normalized_dopplers, dtype=float).reshape(-1)
    if not (len(h) == len(d) == len(nu)):
        raise ValueError("taps, delays and normalized_dopplers must have equal length")
    if np.any(d < 0):
        raise ValueError("delays must be nonnegative")
    n = np.arange(len(x))
    y = np.zeros_like(x)
    for tap, delay, dop in zip(h, d, nu):
        shifted = np.zeros_like(x)
        if delay == 0:
            shifted[:] = x
        elif delay < len(x):
            shifted[delay:] = x[:-delay]
        phase = np.exp(1j * 2.0 * np.pi * dop * n / n_fft)
        y += tap * phase * shifted
    return y
