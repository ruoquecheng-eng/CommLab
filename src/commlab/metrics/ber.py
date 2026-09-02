import numpy as np


def bit_error_rate(reference: np.ndarray, estimate: np.ndarray) -> float:
    a = np.asarray(reference, dtype=np.uint8).reshape(-1)
    b = np.asarray(estimate, dtype=np.uint8).reshape(-1)
    if len(a) != len(b):
        raise ValueError("BER inputs must have equal length")
    if len(a) == 0:
        return 0.0
    return float(np.mean(a != b))
