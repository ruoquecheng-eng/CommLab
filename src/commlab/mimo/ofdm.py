import numpy as np

from commlab.config import OFDMConfig
from commlab.ofdm import OFDMTransceiver
from .detectors import zf_detect, mmse_detect


def generate_mimo_multipath_taps(
    n_rx: int,
    n_tx: int,
    delays: tuple[int, ...] = (0, 3, 8),
    powers_db: tuple[float, ...] = (0.0, -4.0, -9.0),
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate normalized independent Rayleigh MIMO FIR links.

    Returns shape (n_rx, n_tx, max_delay+1). Total average received power per
    receive antenna is approximately one when each transmit stream has unit power.
    """
    if len(delays) != len(powers_db):
        raise ValueError("delays and powers_db must have equal length")
    rng = rng or np.random.default_rng()
    L = max(delays) + 1
    taps = np.zeros((n_rx, n_tx, L), dtype=np.complex128)
    p = 10.0 ** (np.asarray(powers_db, dtype=float) / 10.0)
    p = p / np.sum(p)
    for r in range(n_rx):
        for t in range(n_tx):
            coeff = (rng.standard_normal(len(p)) + 1j * rng.standard_normal(len(p))) / np.sqrt(2.0)
            coeff *= np.sqrt(p / n_tx)
            taps[r, t, np.asarray(delays, dtype=int)] = coeff
    return taps


def mimo_frequency_response(taps: np.ndarray, n_fft: int) -> np.ndarray:
    """Return H[k] with shape (n_fft, n_rx, n_tx)."""
    h = np.asarray(taps, dtype=np.complex128)
    if h.ndim != 3:
        raise ValueError("taps must have shape (n_rx, n_tx, n_taps)")
    H = np.fft.fft(h, n=n_fft, axis=-1)
    return np.moveaxis(H, -1, 0)


def apply_mimo_multipath_waveforms(tx_waveforms: np.ndarray, taps: np.ndarray) -> np.ndarray:
    """Apply time-domain MIMO FIR channel.

    tx_waveforms shape (n_tx, n_samples); returns (n_rx, n_samples).
    """
    x = np.asarray(tx_waveforms, dtype=np.complex128)
    h = np.asarray(taps, dtype=np.complex128)
    if x.ndim != 2 or h.ndim != 3 or x.shape[0] != h.shape[1]:
        raise ValueError("incompatible waveform/tap shapes")
    n_rx, n_tx, _ = h.shape
    y = np.zeros((n_rx, x.shape[1]), dtype=np.complex128)
    for r in range(n_rx):
        for t in range(n_tx):
            conv = np.convolve(x[t], h[r, t], mode="full")
            y[r] += conv[: x.shape[1]]
    return y


def detect_mimo_ofdm_data(
    rx_waveforms: np.ndarray,
    taps: np.ndarray,
    config: OFDMConfig | None = None,
    method: str = "mmse",
    noise_var_freq: float = 0.0,
) -> np.ndarray:
    """Perfect-CSI linear detection for MIMO-OFDM data carriers.

    Returns detected data symbols with shape (n_symbols, n_data, n_tx).
    Assumes CP covers the channel memory.
    """
    cfg = config or OFDMConfig()
    rx = np.asarray(rx_waveforms, dtype=np.complex128)
    h = np.asarray(taps, dtype=np.complex128)
    if rx.ndim != 2 or h.ndim != 3 or rx.shape[0] != h.shape[0]:
        raise ValueError("incompatible received waveform/tap shapes")

    ofdm = OFDMTransceiver(cfg)
    rx_data_by_ant = []
    for r in range(rx.shape[0]):
        data, _ = ofdm.demodulate(rx[r])
        rx_data_by_ant.append(data.reshape(-1, cfg.n_data))
    # (n_symbols, n_data, n_rx)
    Y = np.stack(rx_data_by_ant, axis=-1)

    H = mimo_frequency_response(h, cfg.n_fft)[cfg.data_bins]  # (n_data,n_rx,n_tx)
    H_batch = np.broadcast_to(H[None, ...], (Y.shape[0],) + H.shape)

    if method.lower() == "zf":
        return zf_detect(Y, H_batch)
    if method.lower() == "mmse":
        return mmse_detect(Y, H_batch, noise_var=noise_var_freq)
    raise ValueError("method must be 'zf' or 'mmse'")


def detect_mimo_ofdm_data_from_frequency_response(
    rx_waveforms: np.ndarray,
    h_data: np.ndarray,
    config: OFDMConfig | None = None,
    method: str = "mmse",
    noise_var_freq: float = 0.0,
) -> np.ndarray:
    """Linear detection using an externally estimated data-carrier H[k].

    ``h_data`` shape is (n_data, n_rx, n_tx).
    """
    cfg = config or OFDMConfig()
    rx = np.asarray(rx_waveforms, dtype=np.complex128)
    H = np.asarray(h_data, dtype=np.complex128)
    if rx.ndim != 2 or H.ndim != 3 or H.shape[0] != cfg.n_data or H.shape[1] != rx.shape[0]:
        raise ValueError("incompatible received waveform/frequency-response shapes")
    ofdm = OFDMTransceiver(cfg)
    rx_data = []
    for r in range(rx.shape[0]):
        data, _ = ofdm.demodulate(rx[r])
        rx_data.append(data.reshape(-1, cfg.n_data))
    Y = np.stack(rx_data, axis=-1)
    H_batch = np.broadcast_to(H[None, ...], (Y.shape[0],) + H.shape)
    if method.lower() == "zf":
        return zf_detect(Y, H_batch)
    if method.lower() == "mmse":
        return mmse_detect(Y, H_batch, noise_var=noise_var_freq)
    raise ValueError("method must be 'zf' or 'mmse'")
