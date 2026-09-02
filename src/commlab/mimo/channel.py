import numpy as np


def rayleigh_mimo_channel(
    n_samples: int,
    n_rx: int = 2,
    n_tx: int = 2,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """IID CN(0,1) flat-fading MIMO channel matrices."""
    rng = rng or np.random.default_rng()
    return (
        rng.standard_normal((n_samples, n_rx, n_tx))
        + 1j * rng.standard_normal((n_samples, n_rx, n_tx))
    ) / np.sqrt(2.0)


def apply_mimo_channel(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    X = np.asarray(x, dtype=np.complex128)
    H = np.asarray(h, dtype=np.complex128)
    if H.shape[:-2] != X.shape[:-1] or H.shape[-1] != X.shape[-1]:
        raise ValueError("incompatible H and x shapes")
    return np.einsum("...ij,...j->...i", H, X)


def exponential_correlation_matrix(n_ant: int, rho: float) -> np.ndarray:
    """Hermitian exponential antenna correlation matrix R[i,j]=rho^|i-j|."""
    if n_ant < 1 or abs(rho) >= 1:
        raise ValueError("n_ant must be positive and |rho| < 1")
    idx=np.arange(n_ant)
    return (complex(rho) ** np.abs(idx[:,None]-idx[None,:])).astype(np.complex128)


def correlated_rayleigh_mimo_channel(
    n_samples: int,
    n_rx: int = 2,
    n_tx: int = 2,
    rho_rx: float = 0.0,
    rho_tx: float = 0.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Kronecker-correlated Rayleigh MIMO channel samples.

    H = R_rx^(1/2) W R_tx^(1/2), with W i.i.d. CN(0,1).
    """
    if n_samples < 1:
        raise ValueError("n_samples must be positive")
    g=rng or np.random.default_rng()
    Rr=exponential_correlation_matrix(n_rx,rho_rx)
    Rt=exponential_correlation_matrix(n_tx,rho_tx)
    er,Ur=np.linalg.eigh(Rr); et,Ut=np.linalg.eigh(Rt)
    Sr=Ur@np.diag(np.sqrt(np.maximum(er,0)))@Ur.conj().T
    St=Ut@np.diag(np.sqrt(np.maximum(et,0)))@Ut.conj().T
    W=(g.normal(size=(n_samples,n_rx,n_tx))+1j*g.normal(size=(n_samples,n_rx,n_tx)))/np.sqrt(2)
    return np.einsum('ab,nbc,cd->nad',Sr,W,St)


def mimo_capacity_bits_per_hz(H: np.ndarray, snr_linear: float, n_tx: int | None = None) -> np.ndarray:
    """Instantaneous equal-power MIMO capacity log2 det(I + snr/Nt H H^H)."""
    A=np.asarray(H,dtype=np.complex128)
    nt=A.shape[-1] if n_tx is None else int(n_tx)
    if snr_linear < 0 or nt < 1:
        raise ValueError("invalid SNR or n_tx")
    Hr=np.swapaxes(A.conj(),-1,-2)
    gram=A@Hr
    eye=np.eye(A.shape[-2],dtype=np.complex128)
    mats=eye+(float(snr_linear)/nt)*gram
    sign,logdet=np.linalg.slogdet(mats)
    if np.any(np.real(sign)<=0):
        raise RuntimeError("capacity matrix was not positive definite")
    return np.real(logdet)/np.log(2.0)
