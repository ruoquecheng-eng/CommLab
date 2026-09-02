import numpy as np
from scipy.ndimage import map_coordinates


def _interp_complex(x: np.ndarray, positions: np.ndarray) -> np.ndarray:
    """Cubic complex interpolation for fractional resampling.

    Cubic interpolation is materially more faithful than linear interpolation
    for broadband OFDM waveforms while keeping this educational model compact.
    """
    coords = np.asarray(positions, dtype=float)[None, :]
    real = map_coordinates(x.real, coords, order=3, mode="constant", cval=0.0, prefilter=True)
    imag = map_coordinates(x.imag, coords, order=3, mode="constant", cval=0.0, prefilter=True)
    return real + 1j * imag


def apply_sampling_clock_offset(signal: np.ndarray, ppm: float) -> np.ndarray:
    """Apply receiver sampling-clock offset using complex linear resampling.

    The receiver's output sample n observes transmitter time n*(1+eps), where
    eps=ppm*1e-6. Positive ppm therefore accumulates an advancing timing error.
    The output length equals the input length; samples beyond the modeled record
    are zero-filled.
    """
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    eps = float(ppm) * 1e-6
    if eps == 0.0:
        return x.copy()
    if 1.0 + eps <= 0:
        raise ValueError("invalid sampling-clock ratio")
    positions = np.arange(len(x), dtype=float) * (1.0 + eps)
    return _interp_complex(x, positions)


def compensate_sampling_clock_offset(signal: np.ndarray, ppm: float) -> np.ndarray:
    """Known-offset inverse resampling baseline."""
    y = np.asarray(signal, dtype=np.complex128).reshape(-1)
    eps = float(ppm) * 1e-6
    if eps == 0.0:
        return y.copy()
    if 1.0 + eps <= 0:
        raise ValueError("invalid sampling-clock ratio")
    positions = np.arange(len(y), dtype=float) / (1.0 + eps)
    return _interp_complex(y, positions)


def training_correlation_peak(rx: np.ndarray, training: np.ndarray, start: int, stop: int) -> int:
    """Find the strongest known-training correlation start inside [start, stop)."""
    y = np.asarray(rx, dtype=np.complex128).reshape(-1)
    p = np.asarray(training, dtype=np.complex128).reshape(-1)
    lo = max(0, int(start)); hi = min(int(stop), len(y) - len(p) + 1)
    if hi <= lo:
        raise ValueError("empty training search interval")
    metric = np.empty(hi - lo, dtype=float)
    denom_p = np.linalg.norm(p) + 1e-30
    for j, d in enumerate(range(lo, hi)):
        seg = y[d:d+len(p)]
        metric[j] = abs(np.vdot(p, seg)) / ((np.linalg.norm(seg) + 1e-30) * denom_p)
    return lo + int(np.argmax(metric))


def estimate_sampling_clock_ppm_from_two_training(
    rx: np.ndarray,
    training: np.ndarray,
    tx_start_1: int,
    tx_start_2: int,
    search_radius: int,
) -> tuple[float, tuple[int, int]]:
    """Estimate SCO from timing drift between two known training bursts.

    For this module's resampling convention, observed separation is approximately
    transmitted_separation/(1+eps).
    """
    if tx_start_2 <= tx_start_1:
        raise ValueError("second training burst must follow the first")
    p1 = training_correlation_peak(rx, training, tx_start_1-search_radius, tx_start_1+search_radius+1)
    p2_expected = tx_start_2
    p2 = training_correlation_peak(rx, training, p2_expected-search_radius, p2_expected+search_radius+1)
    observed = p2 - p1
    if observed <= 0:
        raise ValueError("invalid observed training separation")
    transmitted = tx_start_2 - tx_start_1
    eps_hat = transmitted / observed - 1.0
    return float(eps_hat * 1e6), (p1, p2)
