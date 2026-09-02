import numpy as np


def odd_polynomial_features(signal: np.ndarray, order: int = 5) -> np.ndarray:
    """Complex memoryless odd-order basis x|x|^(0,2,...,order-1)."""
    if order < 1 or order % 2 == 0:
        raise ValueError("order must be a positive odd integer")
    x=np.asarray(signal,dtype=np.complex128).reshape(-1)
    degrees=range(0,order,2)
    return np.column_stack([x*np.abs(x)**d for d in degrees])


def fit_indirect_polynomial_dpd(pa_input: np.ndarray, pa_output: np.ndarray, order: int = 7, ridge: float = 1e-8) -> np.ndarray:
    """Indirect-learning postdistorter fit, reused as a predistorter baseline."""
    x=np.asarray(pa_input,dtype=np.complex128).reshape(-1); y=np.asarray(pa_output,dtype=np.complex128).reshape(-1)
    if len(x)!=len(y): raise ValueError("training lengths must match")
    Phi=odd_polynomial_features(y,order)
    G=Phi.conj().T@Phi + float(ridge)*np.eye(Phi.shape[1])
    return np.linalg.solve(G,Phi.conj().T@x)


def apply_polynomial_dpd(desired_signal: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    c=np.asarray(coefficients,dtype=np.complex128).reshape(-1)
    order=2*len(c)-1
    return odd_polynomial_features(desired_signal,order)@c
