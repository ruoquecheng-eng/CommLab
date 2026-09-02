import numpy as np


def wiener_phase_noise(
    n_samples: int,
    innovation_std_rad: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate a discrete-time Wiener phase-noise trajectory in radians.

    ``innovation_std_rad`` is the standard deviation of the independent phase
    increment per sample. This is an intentionally normalized baseband model,
    not a calibrated oscillator mask in dBc/Hz.
    """
    if n_samples < 0 or innovation_std_rad < 0:
        raise ValueError("n_samples and innovation_std_rad must be nonnegative")
    rng = rng or np.random.default_rng()
    if n_samples == 0:
        return np.empty(0, dtype=float)
    increments = rng.normal(0.0, innovation_std_rad, n_samples)
    increments[0] = 0.0
    return np.cumsum(increments)


def apply_phase_noise(
    signal: np.ndarray,
    innovation_std_rad: float,
    rng: np.random.Generator | None = None,
    return_phase: bool = False,
):
    x = np.asarray(signal, dtype=np.complex128)
    phase = wiener_phase_noise(x.size, innovation_std_rad, rng).reshape(x.shape)
    y = x * np.exp(1j * phase)
    return (y, phase) if return_phase else y
