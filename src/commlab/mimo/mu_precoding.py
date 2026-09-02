import numpy as np


def normalize_precoder(W: np.ndarray, total_power: float = 1.0) -> np.ndarray:
    W=np.asarray(W,dtype=np.complex128)
    p=float(np.sum(np.abs(W)**2))
    if p<=0 or total_power<=0: raise ValueError("invalid precoder power")
    return W*np.sqrt(float(total_power)/p)


def mrt_precoder(H: np.ndarray, total_power: float = 1.0) -> np.ndarray:
    """Conjugate matched-filter precoder for K-user MISO downlink.

    H has shape (users, tx_antennas), W returns (tx_antennas, users).
    """
    A=np.asarray(H,dtype=np.complex128)
    if A.ndim!=2: raise ValueError("H must be 2-D")
    W=A.conj().T
    # Normalize each beam before the global power normalization so weak users
    # are not silently assigned negligible beam power.
    W=W/np.maximum(np.linalg.norm(W,axis=0,keepdims=True),1e-15)
    return normalize_precoder(W,total_power)


def zf_precoder(H: np.ndarray, total_power: float = 1.0) -> np.ndarray:
    """Zero-forcing downlink precoder H^H (H H^H)^-1."""
    A=np.asarray(H,dtype=np.complex128)
    if A.ndim!=2 or A.shape[1] < A.shape[0]:
        raise ValueError("ZF downlink requires tx antennas >= users")
    W=A.conj().T@np.linalg.pinv(A@A.conj().T)
    return normalize_precoder(W,total_power)


def downlink_sinr(H: np.ndarray, W: np.ndarray, snr_linear: float) -> np.ndarray:
    """Per-user SINR for unit-variance independent streams and total Tx power 1."""
    A=np.asarray(H,dtype=np.complex128); B=np.asarray(W,dtype=np.complex128)
    if A.ndim!=2 or B.shape!=(A.shape[1],A.shape[0]) or snr_linear<=0:
        raise ValueError("invalid downlink dimensions/SNR")
    G=A@B; power=np.abs(G)**2
    desired=np.diag(power); interf=np.sum(power,axis=1)-desired
    noise=1.0/float(snr_linear)
    return desired/(interf+noise)


def sum_rate_from_sinr(sinr: np.ndarray) -> float:
    s=np.asarray(sinr,dtype=float)
    return float(np.sum(np.log2(1.0+np.maximum(s,0))))


def jain_fairness(values: np.ndarray) -> float:
    x=np.asarray(values,dtype=float).reshape(-1)
    den=len(x)*float(np.sum(x*x))
    return 0.0 if den<=0 else float(np.sum(x)**2/den)


def favorable_propagation_metric(H: np.ndarray) -> float:
    """Mean absolute normalized inter-user channel correlation."""
    A=np.asarray(H,dtype=np.complex128)
    if A.ndim!=2: raise ValueError("H must be 2-D")
    N=A/np.maximum(np.linalg.norm(A,axis=1,keepdims=True),1e-15)
    C=np.abs(N@N.conj().T); mask=~np.eye(A.shape[0],dtype=bool)
    return float(np.mean(C[mask])) if np.any(mask) else 0.0
