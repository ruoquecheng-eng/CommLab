import numpy as np


def noise_power_for_snr(signal: np.ndarray, snr_db: float) -> float:
    """Return complex-noise power for the requested sample-domain SNR."""
    x = np.asarray(signal, dtype=np.complex128)
    signal_power = float(np.mean(np.abs(x) ** 2))
    if signal_power == 0.0:
        return 0.0
    return signal_power / (10.0 ** (snr_db / 10.0))


def add_awgn(signal: np.ndarray, snr_db: float, rng: np.random.Generator | None = None) -> np.ndarray:
    """Add circular complex AWGN at a target sample-domain SNR.

    SNR is mean(|x|^2) / mean(|n|^2) over the provided waveform.
    """
    x = np.asarray(signal, dtype=np.complex128)
    rng = rng or np.random.default_rng()
    noise_power = noise_power_for_snr(x, snr_db)
    if noise_power == 0.0:
        return x.copy()
    noise = np.sqrt(noise_power / 2.0) * (
        rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape)
    )
    return x + noise
