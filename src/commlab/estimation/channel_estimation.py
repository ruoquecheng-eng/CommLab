import numpy as np
from commlab.config import OFDMConfig


def ls_pilot_channel_estimate(
    received_pilots: np.ndarray,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    """Least-squares channel estimates on pilot subcarriers.

    Returns shape (n_ofdm_symbols, n_pilots).
    """
    cfg = config or OFDMConfig()
    pilots = np.asarray(received_pilots, dtype=np.complex128)
    if pilots.ndim == 1:
        if len(pilots) % len(cfg.pilot_bins):
            raise ValueError("pilot count is not a multiple of number of pilot carriers")
        pilots = pilots.reshape(-1, len(cfg.pilot_bins))
    expected = np.asarray(cfg.pilot_values, dtype=np.complex128)[None, :]
    return pilots / expected


def interpolate_channel_to_data(
    pilot_channel: np.ndarray,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    """Linearly interpolate complex LS pilot estimates onto data carriers.

    Real and imaginary components are interpolated independently versus signed
    subcarrier index. Edge data carriers use nearest-pilot extrapolation.
    Returns shape (n_ofdm_symbols, n_data).
    """
    cfg = config or OFDMConfig()
    hp = np.asarray(pilot_channel, dtype=np.complex128)
    if hp.ndim == 1:
        hp = hp.reshape(1, -1)
    if hp.shape[1] != len(cfg.pilot_subcarriers):
        raise ValueError("pilot_channel has incompatible pilot dimension")

    pilot_sc = np.asarray(cfg.pilot_subcarriers, dtype=float)
    data_sc = np.asarray(cfg.data_subcarriers, dtype=float)
    order = np.argsort(pilot_sc)
    xp = pilot_sc[order]

    out = np.empty((hp.shape[0], len(data_sc)), dtype=np.complex128)
    for i, row in enumerate(hp):
        sorted_row = row[order]
        real = np.interp(data_sc, xp, sorted_row.real)
        imag = np.interp(data_sc, xp, sorted_row.imag)
        out[i] = real + 1j * imag
    return out


def estimate_data_channel_ls(
    received_pilots: np.ndarray,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    """Convenience function: pilot LS estimate + linear interpolation."""
    cfg = config or OFDMConfig()
    hp = ls_pilot_channel_estimate(received_pilots, cfg)
    return interpolate_channel_to_data(hp, cfg)


def estimate_channel_time_domain_ls(
    received_pilots: np.ndarray,
    max_channel_len: int,
    config: OFDMConfig | None = None,
) -> np.ndarray:
    """Model-based LS channel estimation using a finite-length CIR model.

    The pilot-domain LS samples satisfy H[k_p] = sum_l h[l] exp(-j2*pi*k_p*l/N).
    If the assumed channel length is not larger than the number of independent
    pilots, solve for h by least squares and FFT it onto the data subcarriers.

    Returns shape (n_ofdm_symbols, n_data).
    """
    cfg = config or OFDMConfig()
    if max_channel_len < 1 or max_channel_len > len(cfg.pilot_bins):
        raise ValueError("max_channel_len must be between 1 and the number of pilots")
    hp = ls_pilot_channel_estimate(received_pilots, cfg)
    bins = cfg.pilot_bins.astype(float)
    ell = np.arange(max_channel_len, dtype=float)
    A = np.exp(-1j * 2.0 * np.pi * bins[:, None] * ell[None, :] / cfg.n_fft)
    pinv = np.linalg.pinv(A)
    h_hat = hp @ pinv.T
    padded = np.zeros((hp.shape[0], cfg.n_fft), dtype=np.complex128)
    padded[:, :max_channel_len] = h_hat
    H = np.fft.fft(padded, axis=1)
    return H[:, cfg.data_bins]
