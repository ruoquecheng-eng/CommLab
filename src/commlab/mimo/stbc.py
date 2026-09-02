import numpy as np


def alamouti_encode(symbols: np.ndarray) -> np.ndarray:
    """2x1 Alamouti space-time block code with unit total Tx power per slot.

    Input length must be even. Returns shape (n_blocks, 2_time, 2_tx).
    """
    s = np.asarray(symbols, dtype=np.complex128).reshape(-1)
    if len(s) % 2:
        raise ValueError("Alamouti input symbol count must be even")
    pairs = s.reshape(-1, 2)
    out = np.empty((len(pairs), 2, 2), dtype=np.complex128)
    a = 1.0 / np.sqrt(2.0)
    out[:, 0, 0] = a * pairs[:, 0]
    out[:, 0, 1] = a * pairs[:, 1]
    out[:, 1, 0] = -a * np.conj(pairs[:, 1])
    out[:, 1, 1] = a * np.conj(pairs[:, 0])
    return out


def alamouti_decode(received: np.ndarray, channel: np.ndarray) -> np.ndarray:
    """Decode 2x1 Alamouti blocks with perfect flat-fading CSI.

    received shape (n_blocks,2), channel shape (n_blocks,2).
    """
    y = np.asarray(received, dtype=np.complex128)
    h = np.asarray(channel, dtype=np.complex128)
    if y.ndim != 2 or y.shape[1] != 2 or h.shape != (y.shape[0], 2):
        raise ValueError("invalid Alamouti received/channel shapes")
    h0, h1 = h[:, 0], h[:, 1]
    y0, y1 = y[:, 0], y[:, 1]
    den = (np.abs(h0)**2 + np.abs(h1)**2) / np.sqrt(2.0)
    den = np.maximum(den, 1e-15)
    s0 = (np.conj(h0)*y0 + h1*np.conj(y1)) / den
    s1 = (np.conj(h1)*y0 - h0*np.conj(y1)) / den
    return np.stack((s0, s1), axis=1).reshape(-1)
