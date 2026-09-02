import numpy as np

from commlab.config import OFDMConfig


def orthogonal_mimo_training_waveforms(
    config: OFDMConfig | None = None,
    n_tx: int = 2,
    pilot_value: complex = 1.0 + 0j,
) -> np.ndarray:
    """Create time-orthogonal full-active-carrier MIMO training symbols.

    Training slot t has transmitter t active on every configured active
    subcarrier while the other transmitters are silent. Returns shape
    (n_tx, n_tx * symbol_len), ready for the time-domain MIMO FIR channel.
    """
    cfg = config or OFDMConfig()
    active_bins = np.array([cfg.bin_index(k) for k in cfg.active_subcarriers], dtype=int)
    waves = np.zeros((n_tx, n_tx * cfg.symbol_len), dtype=np.complex128)
    for t in range(n_tx):
        freq = np.zeros(cfg.n_fft, dtype=np.complex128)
        freq[active_bins] = pilot_value
        time = np.fft.ifft(freq) * np.sqrt(cfg.n_fft)
        block = np.concatenate((time[-cfg.cp_len:], time)) if cfg.cp_len else time
        waves[t, t * cfg.symbol_len:(t + 1) * cfg.symbol_len] = block
    return waves


def estimate_mimo_channel_from_training(
    rx_training: np.ndarray,
    config: OFDMConfig | None = None,
    n_tx: int = 2,
    pilot_value: complex = 1.0 + 0j,
) -> np.ndarray:
    """LS estimate H[k] on all active subcarriers from orthogonal training.

    ``rx_training`` has shape (n_rx, n_tx * symbol_len). Returns
    (n_active, n_rx, n_tx), in active-subcarrier order.
    """
    cfg = config or OFDMConfig()
    rx = np.asarray(rx_training, dtype=np.complex128)
    if rx.ndim != 2 or rx.shape[1] < n_tx * cfg.symbol_len:
        raise ValueError("invalid MIMO training waveform shape")
    active_bins = np.array([cfg.bin_index(k) for k in cfg.active_subcarriers], dtype=int)
    H = np.empty((len(active_bins), rx.shape[0], n_tx), dtype=np.complex128)
    for t in range(n_tx):
        block = rx[:, t * cfg.symbol_len:(t + 1) * cfg.symbol_len]
        no_cp = block[:, cfg.cp_len:] if cfg.cp_len else block
        spec = np.fft.fft(no_cp, axis=1) / np.sqrt(cfg.n_fft)
        H[:, :, t] = (spec[:, active_bins] / pilot_value).T
    return H


def active_to_data_mimo_channel(h_active: np.ndarray, config: OFDMConfig | None = None) -> np.ndarray:
    cfg = config or OFDMConfig()
    active = list(cfg.active_subcarriers)
    index = {k: i for i, k in enumerate(active)}
    return np.stack([h_active[index[k]] for k in cfg.data_subcarriers], axis=0)


def lmmse_shrink_mimo_channel(
    h_ls: np.ndarray,
    noise_var: float,
    pilot_power: float = 1.0,
    channel_variance: float = 1.0,
) -> np.ndarray:
    """Scalar-prior LMMSE shrinkage of LS MIMO channel estimates.

    Assumes independent zero-mean channel coefficients with variance
    ``channel_variance`` and LS observation noise variance
    ``noise_var / pilot_power``. It is intentionally simple and transparent,
    serving as a low-SNR benchmark rather than a full covariance-aware Wiener
    estimator.
    """
    if pilot_power <= 0 or channel_variance <= 0 or noise_var < 0:
        raise ValueError("invalid LMMSE parameters")
    sigma_e2 = float(noise_var) / float(pilot_power)
    gain = float(channel_variance) / (float(channel_variance) + sigma_e2)
    return gain * np.asarray(h_ls, dtype=np.complex128)


def estimate_mimo_channel_lmmse_from_training(
    rx_training: np.ndarray,
    noise_var: float,
    config: OFDMConfig | None = None,
    n_tx: int = 2,
    pilot_value: complex = 1.0 + 0j,
    channel_variance: float = 1.0,
) -> np.ndarray:
    """Orthogonal-training LS followed by scalar-prior LMMSE shrinkage."""
    h_ls = estimate_mimo_channel_from_training(rx_training, config, n_tx, pilot_value)
    pilot_power = abs(pilot_value) ** 2
    return lmmse_shrink_mimo_channel(h_ls, noise_var, pilot_power, channel_variance)


def frequency_orthogonal_mimo_training_waveforms(
    config: OFDMConfig | None = None,
    n_tx: int = 2,
    pilot_value: complex = 1.0 + 0j,
) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    """One-symbol frequency-orthogonal MIMO training waveform.

    Active subcarriers are interleaved across transmitters. Each active carrier
    is driven by exactly one Tx, so every receiver observes an interference-free
    pilot for one channel column. Returns ``(tx_waveforms, pilot_subcarriers)``
    where waveforms have shape (n_tx, symbol_len).
    """
    cfg=config or OFDMConfig()
    if n_tx < 1 or n_tx > len(cfg.active_subcarriers):
        raise ValueError("invalid n_tx")
    active=np.asarray(cfg.active_subcarriers,dtype=int)
    sets=tuple(active[t::n_tx].copy() for t in range(n_tx))
    waves=np.zeros((n_tx,cfg.symbol_len),dtype=np.complex128)
    for t,subs in enumerate(sets):
        freq=np.zeros(cfg.n_fft,dtype=np.complex128)
        bins=np.array([cfg.bin_index(int(k)) for k in subs],dtype=int)
        freq[bins]=pilot_value
        time=np.fft.ifft(freq)*np.sqrt(cfg.n_fft)
        waves[t]=np.concatenate((time[-cfg.cp_len:],time)) if cfg.cp_len else time
    return waves,sets


def estimate_mimo_cir_from_frequency_orthogonal_training(
    rx_training: np.ndarray,
    pilot_subcarriers: tuple[np.ndarray, ...],
    cir_len: int,
    config: OFDMConfig | None = None,
    pilot_value: complex = 1.0 + 0j,
    ridge: float = 0.0,
) -> np.ndarray:
    """Finite-CIR LS estimate from one frequency-orthogonal MIMO pilot symbol.

    Returns H on configured active subcarriers with shape
    ``(n_active, n_rx, n_tx)``. The physical prior is only finite channel
    length; there is no statistical covariance model.
    """
    cfg=config or OFDMConfig(); rx=np.asarray(rx_training,dtype=np.complex128)
    n_tx=len(pilot_subcarriers)
    if rx.ndim != 2 or rx.shape[1] < cfg.symbol_len or cir_len < 1 or cir_len > cfg.cp_len + 1:
        raise ValueError("invalid training shape or cir_len")
    block=rx[:,:cfg.symbol_len]; no_cp=block[:,cfg.cp_len:] if cfg.cp_len else block
    spec=np.fft.fft(no_cp,axis=1)/np.sqrt(cfg.n_fft)
    active_bins=np.array([cfg.bin_index(k) for k in cfg.active_subcarriers],dtype=int)
    H=np.empty((len(active_bins),rx.shape[0],n_tx),dtype=np.complex128)
    ell=np.arange(cir_len,dtype=float)
    for t,subs in enumerate(pilot_subcarriers):
        bins=np.array([cfg.bin_index(int(k)) for k in subs],dtype=int)
        if len(bins) < cir_len:
            raise ValueError("not enough pilots to identify requested CIR length")
        F=np.exp(-1j*2*np.pi*bins[:,None]*ell[None,:]/cfg.n_fft)
        G=F.conj().T@F + float(ridge)*np.eye(cir_len)
        for r in range(rx.shape[0]):
            hp=spec[r,bins]/pilot_value
            h=np.linalg.solve(G,F.conj().T@hp)
            Hfull=np.fft.fft(h,n=cfg.n_fft)
            H[:,r,t]=Hfull[active_bins]
    return H
