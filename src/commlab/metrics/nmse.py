import numpy as np


def normalized_mean_square_error(reference: np.ndarray, estimate: np.ndarray, eps: float = 1e-15) -> float:
    ref = np.asarray(reference, dtype=np.complex128)
    est = np.asarray(estimate, dtype=np.complex128)
    if ref.shape != est.shape:
        raise ValueError("reference and estimate must have the same shape")
    denominator = float(np.sum(np.abs(ref) ** 2))
    numerator = float(np.sum(np.abs(ref - est) ** 2))
    return numerator / max(denominator, eps)
