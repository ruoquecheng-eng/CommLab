import numpy as np


def generate_rayleigh_taps(
    delays: np.ndarray | list[int] | tuple[int, ...],
    powers_db: np.ndarray | list[float] | tuple[float, ...],
    rng: np.random.Generator | None = None,
    normalize: bool = True,
) -> np.ndarray:
    """Generate a sparse complex Rayleigh multipath impulse response.

    Each specified path coefficient is CN(0, power_linear). Delays are integer
    sample offsets. By default the realized impulse response is normalized to
    unit total energy so experiments are easier to compare across random seeds.
    """
    delays = np.asarray(delays, dtype=int)
    powers_db = np.asarray(powers_db, dtype=float)
    if delays.ndim != 1 or powers_db.ndim != 1 or len(delays) != len(powers_db):
        raise ValueError("delays and powers_db must be one-dimensional arrays of equal length")
    if len(delays) == 0 or np.any(delays < 0):
        raise ValueError("delays must contain non-negative sample offsets")

    rng = rng or np.random.default_rng()
    powers = 10.0 ** (powers_db / 10.0)
    coeffs = np.sqrt(powers / 2.0) * (
        rng.standard_normal(len(delays)) + 1j * rng.standard_normal(len(delays))
    )
    taps = np.zeros(int(delays.max()) + 1, dtype=np.complex128)
    taps[delays] = coeffs
    energy = float(np.sum(np.abs(taps) ** 2))
    if normalize and energy > 0.0:
        taps /= np.sqrt(energy)
    return taps
