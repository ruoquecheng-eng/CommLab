import numpy as np


def repeated_half_preamble(n_fft: int = 64, seed: int = 2026) -> np.ndarray:
    """Create a unit-power Schmidl-Cox-style repeated-half preamble.

    This is an educational training sequence, not a standards-compliant WLAN
    preamble. The two identical halves make carrier-frequency offset observable
    from their phase difference.
    """
    if n_fft % 2:
        raise ValueError("n_fft must be even")
    rng = np.random.default_rng(seed)
    half_len = n_fft // 2
    bits_i = rng.integers(0, 2, half_len)
    bits_q = rng.integers(0, 2, half_len)
    half = ((1 - 2 * bits_i) + 1j * (1 - 2 * bits_q)) / np.sqrt(2.0)
    preamble = np.concatenate((half, half)).astype(np.complex128)
    preamble /= np.sqrt(np.mean(np.abs(preamble) ** 2))
    return preamble
