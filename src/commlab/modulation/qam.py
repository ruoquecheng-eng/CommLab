import numpy as np


class QAMModem:
    """Gray-coded square QAM modem supporting QPSK, 16-QAM and 64-QAM.

    Constellations are normalized to unit average symbol energy.
    Each I/Q axis uses the binary-reflected Gray sequence from the most
    negative to the most positive amplitude level.
    """

    def __init__(self, order: int = 4):
        if order not in (4, 16, 64):
            raise ValueError("supported QAM orders are 4, 16 and 64")
        self.order = order
        self.bits_per_symbol = int(np.log2(order))
        self.bits_per_axis = self.bits_per_symbol // 2
        self.level_count = int(np.sqrt(order))
        self.levels = np.arange(-(self.level_count - 1), self.level_count, 2, dtype=float)
        self.normalization = np.sqrt(2.0 * (self.level_count**2 - 1) / 3.0)

        # Map Gray-labelled input integer -> monotonic amplitude index.
        self._gray_to_index = np.empty(self.level_count, dtype=int)
        self._index_to_gray = np.empty(self.level_count, dtype=int)
        for binary_index in range(self.level_count):
            gray = binary_index ^ (binary_index >> 1)
            self._gray_to_index[gray] = binary_index
            self._index_to_gray[binary_index] = gray

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
        if len(bits) % self.bits_per_symbol:
            raise ValueError("bit count must be a multiple of bits_per_symbol")
        groups = bits.reshape(-1, self.bits_per_symbol)
        i_bits = groups[:, : self.bits_per_axis]
        q_bits = groups[:, self.bits_per_axis :]
        i = self._bits_to_axis(i_bits)
        q = self._bits_to_axis(q_bits)
        return (i + 1j * q) / self.normalization

    def demodulate(self, symbols: np.ndarray) -> np.ndarray:
        z = np.asarray(symbols, dtype=np.complex128).reshape(-1)
        i_bits = self._axis_to_bits(z.real * self.normalization)
        q_bits = self._axis_to_bits(z.imag * self.normalization)
        return np.concatenate((i_bits, q_bits), axis=1).reshape(-1)


    def llr_maxlog(self, symbols: np.ndarray, noise_var: float) -> np.ndarray:
        """Return max-log bit LLRs, log P(bit=0)/P(bit=1), for AWGN symbols.

        ``noise_var`` is E[|n|^2] for circular complex noise. The same routine
        works after equalization when the caller supplies an effective noise
        variance.
        """
        if noise_var <= 0:
            # A very small variance turns exact constellation points into
            # effectively infinite-confidence decisions without inf arithmetic.
            noise_var = 1e-15
        z = np.asarray(symbols, dtype=np.complex128).reshape(-1)
        labels = np.arange(self.order, dtype=int)
        bits = ((labels[:, None] >> np.arange(self.bits_per_symbol - 1, -1, -1)) & 1).astype(np.uint8)
        # Build symbols using this modem's actual bit labelling, avoiding any
        # assumptions about how Gray labels map onto I/Q axes.
        const = self.modulate(bits.reshape(-1)).reshape(-1)
        d2 = np.abs(z[:, None] - const[None, :]) ** 2
        out = np.empty((len(z), self.bits_per_symbol), dtype=float)
        for b in range(self.bits_per_symbol):
            d0 = np.min(d2[:, bits[:, b] == 0], axis=1)
            d1 = np.min(d2[:, bits[:, b] == 1], axis=1)
            out[:, b] = (d1 - d0) / noise_var
        return out.reshape(-1)

    def _bits_to_axis(self, bits: np.ndarray) -> np.ndarray:
        weights = 1 << np.arange(self.bits_per_axis - 1, -1, -1)
        gray_labels = bits.astype(int) @ weights
        indices = self._gray_to_index[gray_labels]
        return self.levels[indices]

    def _axis_to_bits(self, values: np.ndarray) -> np.ndarray:
        nearest = np.argmin(np.abs(values[:, None] - self.levels[None, :]), axis=1)
        gray_labels = self._index_to_gray[nearest]
        shifts = np.arange(self.bits_per_axis - 1, -1, -1)
        return ((gray_labels[:, None] >> shifts[None, :]) & 1).astype(np.uint8)
