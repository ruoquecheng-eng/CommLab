import numpy as np
from commlab.config import OFDMConfig


class OFDMTransceiver:
    """OFDM modulation/demodulation with pilots and cyclic prefix."""

    def __init__(self, config: OFDMConfig | None = None):
        self.cfg = config or OFDMConfig()

    def modulate(self, data_symbols: np.ndarray) -> np.ndarray:
        data_symbols = np.asarray(data_symbols, dtype=np.complex128).reshape(-1)
        if len(data_symbols) % self.cfg.n_data:
            raise ValueError(f"symbol count must be a multiple of {self.cfg.n_data}")

        frames = data_symbols.reshape(-1, self.cfg.n_data)
        freq = np.zeros((len(frames), self.cfg.n_fft), dtype=np.complex128)
        freq[:, self.cfg.data_bins] = frames
        freq[:, self.cfg.pilot_bins] = np.asarray(self.cfg.pilot_values, dtype=np.complex128)

        time = np.fft.ifft(freq, axis=1) * np.sqrt(self.cfg.n_fft)
        if self.cfg.cp_len > 0:
            cp = time[:, -self.cfg.cp_len :]
            with_cp = np.concatenate((cp, time), axis=1)
        else:
            with_cp = time
        return with_cp.reshape(-1)

    def demodulate(self, rx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        rx = np.asarray(rx, dtype=np.complex128).reshape(-1)
        if len(rx) % self.cfg.symbol_len:
            raise ValueError("received length is not an integer number of OFDM symbols")

        frames = rx.reshape(-1, self.cfg.symbol_len)
        no_cp = frames[:, self.cfg.cp_len :] if self.cfg.cp_len > 0 else frames
        freq = np.fft.fft(no_cp, axis=1) / np.sqrt(self.cfg.n_fft)
        data = freq[:, self.cfg.data_bins]
        pilots = freq[:, self.cfg.pilot_bins]
        return data.reshape(-1), pilots
