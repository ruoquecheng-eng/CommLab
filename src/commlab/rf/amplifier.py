import numpy as np


def rapp_amplifier(signal: np.ndarray, saturation_amplitude: float = 1.0, smoothness: float = 2.0) -> np.ndarray:
    """Memoryless Rapp AM/AM power-amplifier model with no AM/PM distortion."""
    x = np.asarray(signal, dtype=np.complex128)
    if saturation_amplitude <= 0 or smoothness <= 0:
        raise ValueError("saturation_amplitude and smoothness must be positive")
    mag = np.abs(x)
    denom = (1.0 + (mag / saturation_amplitude) ** (2.0 * smoothness)) ** (1.0 / (2.0 * smoothness))
    return x / denom


def scale_for_input_backoff(signal: np.ndarray, ibo_db: float, saturation_amplitude: float = 1.0) -> np.ndarray:
    """Scale waveform so A_sat^2 / mean(|x|^2) equals requested input backoff."""
    x = np.asarray(signal, dtype=np.complex128)
    power = float(np.mean(np.abs(x) ** 2))
    if power == 0.0:
        return x.copy()
    target_power = saturation_amplitude**2 / (10.0 ** (ibo_db / 10.0))
    return x * np.sqrt(target_power / power)


def occupied_guard_power_ratio_db(
    time_symbols: np.ndarray,
    occupied_bins: np.ndarray,
    n_fft: int,
) -> float:
    """Guard-bin leakage relative to occupied-bin power after nonlinear processing.

    Input must contain an integer number of CP-free OFDM symbols.
    """
    x = np.asarray(time_symbols, dtype=np.complex128).reshape(-1)
    if len(x) % n_fft:
        raise ValueError("time_symbols must be an integer number of n_fft blocks")
    blocks = x.reshape(-1, n_fft)
    spec = np.fft.fft(blocks, axis=1) / np.sqrt(n_fft)
    occupied = np.zeros(n_fft, dtype=bool)
    occupied[np.asarray(occupied_bins, dtype=int)] = True
    p_occ = float(np.mean(np.abs(spec[:, occupied]) ** 2))
    p_guard = float(np.mean(np.abs(spec[:, ~occupied]) ** 2))
    if p_guard == 0.0:
        return -np.inf
    return 10.0 * np.log10(p_guard / max(p_occ, 1e-30))


def rapp_inverse_predistort(
    desired_signal: np.ndarray,
    saturation_amplitude: float = 1.0,
    smoothness: float = 2.0,
    max_output_fraction: float = 0.98,
) -> np.ndarray:
    """Model-based inverse predistorter for the memoryless Rapp AM/AM law.

    The requested desired output magnitude is limited below A_sat because the
    Rapp characteristic approaches A_sat asymptotically and cannot produce an
    output at or above saturation. This is an idealized *known-model* baseline,
    not a learned or hardware-calibrated DPD.
    """
    x = np.asarray(desired_signal, dtype=np.complex128)
    A = float(saturation_amplitude)
    p = float(smoothness)
    if A <= 0 or p <= 0 or not (0 < max_output_fraction < 1):
        raise ValueError("invalid Rapp inverse parameters")
    r = np.abs(x)
    target = np.minimum(r, max_output_fraction * A)
    frac = (target / A) ** (2.0 * p)
    drive_mag = target / np.maximum(1.0 - frac, 1e-15) ** (1.0 / (2.0 * p))
    phase = np.exp(1j * np.angle(x))
    return drive_mag * phase
