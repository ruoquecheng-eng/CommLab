import numpy as np


def evm_rms(reference: np.ndarray, estimate: np.ndarray) -> float:
    """RMS error-vector magnitude as a linear ratio."""
    x = np.asarray(reference, dtype=np.complex128).reshape(-1)
    y = np.asarray(estimate, dtype=np.complex128).reshape(-1)
    if x.shape != y.shape:
        raise ValueError("reference and estimate must have the same shape")
    denom = np.sum(np.abs(x) ** 2)
    if denom == 0:
        raise ValueError("reference energy must be nonzero")
    return float(np.sqrt(np.sum(np.abs(x - y) ** 2) / denom))


def evm_percent(reference: np.ndarray, estimate: np.ndarray) -> float:
    return 100.0 * evm_rms(reference, estimate)


def evm_db(reference: np.ndarray, estimate: np.ndarray) -> float:
    value = evm_rms(reference, estimate)
    if value == 0:
        return float("-inf")
    return float(20.0 * np.log10(value))
