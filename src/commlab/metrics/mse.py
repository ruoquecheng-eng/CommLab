import numpy as np


def mean_square_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.complex128)
    est = np.asarray(estimate, dtype=np.complex128)
    if ref.shape != est.shape:
        raise ValueError("reference and estimate must have the same shape")
    return float(np.mean(np.abs(ref - est) ** 2))
