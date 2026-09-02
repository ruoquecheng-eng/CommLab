from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class OFDMConfig:
    """Baseline 64-point OFDM configuration inspired by common WLAN layouts.

    This is not a standards-compliant IEEE 802.11 implementation. The layout
    simply uses 52 active subcarriers: 48 data + 4 pilots.
    """

    n_fft: int = 64
    cp_len: int = 16
    pilot_subcarriers: tuple[int, ...] = (-21, -7, 7, 21)
    pilot_values: tuple[complex, ...] = (1 + 0j, 1 + 0j, 1 + 0j, -1 + 0j)
    active_subcarriers: tuple[int, ...] = field(
        default_factory=lambda: tuple(list(range(-26, 0)) + list(range(1, 27)))
    )

    @property
    def data_subcarriers(self) -> tuple[int, ...]:
        pilots = set(self.pilot_subcarriers)
        return tuple(k for k in self.active_subcarriers if k not in pilots)

    @property
    def n_data(self) -> int:
        return len(self.data_subcarriers)

    @property
    def symbol_len(self) -> int:
        return self.n_fft + self.cp_len

    def bin_index(self, subcarrier: int) -> int:
        return subcarrier % self.n_fft

    @property
    def data_bins(self) -> np.ndarray:
        return np.array([self.bin_index(k) for k in self.data_subcarriers], dtype=int)

    @property
    def pilot_bins(self) -> np.ndarray:
        return np.array([self.bin_index(k) for k in self.pilot_subcarriers], dtype=int)
