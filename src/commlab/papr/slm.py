import numpy as np

from commlab.config import OFDMConfig


def slm_modulate_data_blocks(
    data_blocks: np.ndarray,
    config: OFDMConfig | None = None,
    n_candidates: int = 4,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Selective Mapping (SLM) PAPR reduction for OFDM data blocks.

    Each candidate multiplies data carriers by random unit-magnitude QPSK phase
    factors. The lowest-PAPR time-domain candidate is selected per OFDM symbol.

    Returns:
      waveform_blocks: (n_symbols, n_fft), CP-free unitary-IFFT waveforms
      selected_phases: (n_symbols, n_data), side information for recovery
      selected_papr_db: (n_symbols,)
    """
    cfg = config or OFDMConfig()
    data = np.asarray(data_blocks, dtype=np.complex128)
    if data.ndim == 1:
        if len(data) % cfg.n_data:
            raise ValueError("data length must be a multiple of n_data")
        data = data.reshape(-1, cfg.n_data)
    if data.shape[1] != cfg.n_data:
        raise ValueError("data_blocks has incompatible n_data dimension")
    if n_candidates < 1:
        raise ValueError("n_candidates must be >=1")
    rng = rng or np.random.default_rng()

    n_sym = data.shape[0]
    best_wave = np.empty((n_sym, cfg.n_fft), dtype=np.complex128)
    best_phase = np.ones((n_sym, cfg.n_data), dtype=np.complex128)
    best_papr = np.full(n_sym, np.inf)
    phase_alphabet = np.array([1, 1j, -1, -1j], dtype=np.complex128)

    for c in range(n_candidates):
        if c == 0:
            phase = np.ones((n_sym, cfg.n_data), dtype=np.complex128)
        else:
            phase = phase_alphabet[rng.integers(0, 4, size=(n_sym, cfg.n_data))]
        freq = np.zeros((n_sym, cfg.n_fft), dtype=np.complex128)
        freq[:, cfg.data_bins] = data * phase
        freq[:, cfg.pilot_bins] = np.asarray(cfg.pilot_values, dtype=np.complex128)
        wave = np.fft.ifft(freq, axis=1) * np.sqrt(cfg.n_fft)
        power = np.abs(wave) ** 2
        papr = 10.0 * np.log10(np.max(power, axis=1) / np.mean(power, axis=1))
        mask = papr < best_papr
        best_papr[mask] = papr[mask]
        best_wave[mask] = wave[mask]
        best_phase[mask] = phase[mask]
    return best_wave, best_phase, best_papr


def recover_slm_data(received_data_blocks: np.ndarray, selected_phases: np.ndarray) -> np.ndarray:
    y = np.asarray(received_data_blocks, dtype=np.complex128)
    p = np.asarray(selected_phases, dtype=np.complex128)
    if y.shape != p.shape:
        raise ValueError("received_data_blocks and selected_phases must have same shape")
    return y * np.conj(p)
