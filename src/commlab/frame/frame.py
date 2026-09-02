import numpy as np


def build_frame(payload: np.ndarray, preamble: np.ndarray) -> np.ndarray:
    p = np.asarray(preamble, dtype=np.complex128).reshape(-1)
    x = np.asarray(payload, dtype=np.complex128).reshape(-1)
    return np.concatenate((p, x))


def extract_payload(frame_aligned: np.ndarray, preamble_len: int, payload_len: int | None = None) -> np.ndarray:
    x = np.asarray(frame_aligned, dtype=np.complex128).reshape(-1)
    if len(x) < preamble_len:
        raise ValueError("frame shorter than preamble")
    y = x[preamble_len:]
    if payload_len is not None:
        if len(y) < payload_len:
            raise ValueError("frame does not contain complete payload")
        y = y[:payload_len]
    return y
