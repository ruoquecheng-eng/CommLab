import numpy as np
from commlab.config import OFDMConfig


def estimate_common_phase_from_pilots(
    received_pilots: np.ndarray,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    """Estimate one common phase error (CPE) per OFDM symbol from pilots.

    This is useful after coarse CFO correction: a small residual CFO produces
    a symbol-to-symbol phase drift that can be tracked by known pilots.
    """
    cfg = config or OFDMConfig()
    p = np.asarray(received_pilots, dtype=np.complex128)
    n_pilots = len(cfg.pilot_values)
    if p.ndim == 1:
        if len(p) % n_pilots:
            raise ValueError("pilot count is not a multiple of pilot carriers")
        p = p.reshape(-1, n_pilots)
    expected = np.asarray(cfg.pilot_values, dtype=np.complex128)[None, :]
    phasor = np.sum(p * np.conj(expected), axis=1)
    return np.angle(phasor)


def correct_common_phase(
    data_symbols: np.ndarray,
    phase_rad: np.ndarray,
    n_data_per_symbol: int,
) -> np.ndarray:
    data = np.asarray(data_symbols, dtype=np.complex128).reshape(-1)
    phase = np.asarray(phase_rad, dtype=float).reshape(-1)
    if len(data) != len(phase) * n_data_per_symbol:
        raise ValueError("data length is incompatible with phase estimates")
    frames = data.reshape(len(phase), n_data_per_symbol)
    corrected = frames * np.exp(-1j * phase[:, None])
    return corrected.reshape(-1)


def estimate_affine_phase_from_pilots(
    received_pilots: np.ndarray,
    config: OFDMConfig | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate per-symbol affine phase versus signed subcarrier index.

    Fits ``phase(k) ~= intercept + slope*k`` to the known pilot ratios. A
    frequency-linear phase is the dominant signature of a fractional timing
    offset, while the intercept captures common phase error.
    """
    cfg = config or OFDMConfig()
    p = np.asarray(received_pilots, dtype=np.complex128)
    n_p = len(cfg.pilot_values)
    if p.ndim == 1:
        if len(p) % n_p:
            raise ValueError("pilot count is not a multiple of pilot carriers")
        p = p.reshape(-1, n_p)
    expected = np.asarray(cfg.pilot_values, dtype=np.complex128)[None, :]
    ratio = p / expected
    k = np.asarray(cfg.pilot_subcarriers, dtype=float)
    order = np.argsort(k); ks = k[order]
    A = np.column_stack((np.ones_like(ks), ks))
    intercept = np.empty(len(p), dtype=float); slope = np.empty(len(p), dtype=float)
    for i,row in enumerate(ratio):
        phase = np.unwrap(np.angle(row[order]))
        coef, *_ = np.linalg.lstsq(A, phase, rcond=None)
        intercept[i], slope[i] = coef
    return intercept, slope


def correct_affine_phase(
    data_symbols: np.ndarray,
    intercept_rad: np.ndarray,
    slope_rad_per_subcarrier: np.ndarray,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    cfg = config or OFDMConfig()
    data = np.asarray(data_symbols, dtype=np.complex128).reshape(-1)
    a = np.asarray(intercept_rad, dtype=float).reshape(-1)
    b = np.asarray(slope_rad_per_subcarrier, dtype=float).reshape(-1)
    if len(a) != len(b) or len(data) != len(a)*cfg.n_data:
        raise ValueError("incompatible affine phase dimensions")
    grid = data.reshape(len(a), cfg.n_data)
    k = np.asarray(cfg.data_subcarriers, dtype=float)[None, :]
    phase = a[:,None] + b[:,None]*k
    return (grid*np.exp(-1j*phase)).reshape(-1)
