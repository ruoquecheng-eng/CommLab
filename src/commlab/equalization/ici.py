import numpy as np

from commlab.channels.doppler import apply_doppler_multipath


def circular_index_distance(i: np.ndarray, j: np.ndarray, n: int) -> np.ndarray:
    d = np.abs(np.asarray(i) - np.asarray(j))
    return np.minimum(d, n - d)


def time_varying_ofdm_channel_matrix(
    taps: np.ndarray,
    delays: np.ndarray,
    normalized_dopplers: np.ndarray,
    n_fft: int = 64,
    cp_len: int = 16,
    bins: np.ndarray | None = None,
) -> np.ndarray:
    """Numerically build the OFDM frequency-domain channel matrix.

    H[r,c] maps transmitted subcarrier ``bins[c]`` to received subcarrier
    ``bins[r]`` for one CP-protected OFDM symbol under the supplied deterministic
    time-varying multipath channel. Off-diagonal energy quantifies ICI.
    """
    selected = np.arange(n_fft, dtype=int) if bins is None else np.asarray(bins, dtype=int)
    H = np.empty((len(selected), len(selected)), dtype=np.complex128)
    for col, k in enumerate(selected):
        X = np.zeros(n_fft, dtype=np.complex128)
        X[k] = 1.0
        x = np.fft.ifft(X) * np.sqrt(n_fft)
        block = np.concatenate((x[-cp_len:], x)) if cp_len else x
        y = apply_doppler_multipath(block, taps, delays, normalized_dopplers, n_fft)
        useful = y[cp_len:cp_len + n_fft]
        Y = np.fft.fft(useful) / np.sqrt(n_fft)
        H[:, col] = Y[selected]
    return H


def band_limit_channel_matrix(H: np.ndarray, bandwidth: int, circular: bool = False) -> np.ndarray:
    """Keep diagonal +/- ``bandwidth`` couplings in a square channel matrix."""
    A = np.asarray(H, dtype=np.complex128)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("H must be square")
    if bandwidth < 0:
        raise ValueError("bandwidth must be nonnegative")
    n = A.shape[0]
    rows = np.arange(n)[:, None]
    cols = np.arange(n)[None, :]
    dist = circular_index_distance(rows, cols, n) if circular else np.abs(rows - cols)
    return np.where(dist <= bandwidth, A, 0.0)


def linear_lmmse_ici_detect(
    y: np.ndarray,
    H: np.ndarray,
    noise_var: float,
    bandwidth: int | None = None,
    circular_band: bool = False,
) -> np.ndarray:
    """Linear LMMSE detector using a full or band-limited ICI matrix."""
    r = np.asarray(y, dtype=np.complex128).reshape(-1)
    A = np.asarray(H, dtype=np.complex128)
    if A.shape[0] != len(r):
        raise ValueError("observation/channel dimensions do not match")
    if bandwidth is not None:
        A = band_limit_channel_matrix(A, int(bandwidth), circular=circular_band)
    lhs = A.conj().T @ A + float(noise_var) * np.eye(A.shape[1])
    return np.linalg.solve(lhs, A.conj().T @ r)


def ici_energy_fraction(H: np.ndarray) -> float:
    A = np.asarray(H, dtype=np.complex128)
    total = float(np.sum(np.abs(A) ** 2))
    diag = float(np.sum(np.abs(np.diag(A)) ** 2))
    return 0.0 if total == 0 else (total - diag) / total



def cg_lmmse_ici_detect(
    y: np.ndarray,
    H: np.ndarray,
    noise_var: float,
    bandwidth: int | None = None,
    circular_band: bool = False,
    max_iter: int = 80,
    tol: float = 1e-8,
    x0: np.ndarray | None = None,
) -> tuple[np.ndarray, int, float]:
    """Conjugate-gradient LMMSE ICI detector without explicit inversion.

    Solves ``(A^H A + sigma2 I)x=A^H y`` where A is the full or band-limited
    ICI matrix. Returns ``(x_hat, iterations, relative_residual)``.
    """
    r=np.asarray(y,dtype=np.complex128).reshape(-1)
    A=np.asarray(H,dtype=np.complex128)
    if A.shape[0] != len(r):
        raise ValueError("observation/channel dimensions do not match")
    if bandwidth is not None:
        A=band_limit_channel_matrix(A,int(bandwidth),circular=circular_band)
    reg=float(noise_var)
    b=A.conj().T@r
    def mv(v): return A.conj().T@(A@v)+reg*v
    x=np.zeros(A.shape[1],dtype=np.complex128) if x0 is None else np.asarray(x0,dtype=np.complex128).reshape(-1).copy()
    rr=b-mv(x); p=rr.copy(); rs=float(np.vdot(rr,rr).real); bnorm=max(float(np.linalg.norm(b)),1e-30)
    rel=np.sqrt(rs)/bnorm
    if rel <= tol: return x,0,rel
    for it in range(1,int(max_iter)+1):
        Ap=mv(p); den=np.vdot(p,Ap)
        if abs(den)<1e-30: return x,it-1,rel
        alpha=rs/den; x+=alpha*p; rr-=alpha*Ap
        rsn=float(np.vdot(rr,rr).real); rel=np.sqrt(rsn)/bnorm
        if rel <= tol: return x,it,rel
        p=rr+(rsn/max(rs,1e-30))*p; rs=rsn
    return x,int(max_iter),rel


def estimate_banded_ici_matrix(
    x_train: np.ndarray,
    y_train: np.ndarray,
    bandwidth: int,
    ridge: float = 0.0,
    circular_band: bool = False,
) -> np.ndarray:
    """Estimate a banded OFDM ICI matrix from random full-band training.

    Training rows obey ``y_p = H x_p + n_p``. For every output carrier, only
    the diagonal +/- ``bandwidth`` input carriers are fitted. This turns the
    otherwise N-parameter row estimate into a small structured LS problem.
    """
    X=np.asarray(x_train,dtype=np.complex128); Y=np.asarray(y_train,dtype=np.complex128)
    if X.ndim!=2 or Y.shape!=X.shape: raise ValueError("training arrays must have equal 2-D shapes")
    if bandwidth<0 or ridge<0: raise ValueError("invalid bandwidth/ridge")
    p,n=X.shape; H=np.zeros((n,n),dtype=np.complex128)
    cols=np.arange(n)
    for i in range(n):
        dist=circular_index_distance(cols,i,n) if circular_band else np.abs(cols-i)
        support=np.flatnonzero(dist<=int(bandwidth))
        A=X[:,support]
        if ridge>0:
            lhs=A.conj().T@A+float(ridge)*np.eye(len(support)); rhs=A.conj().T@Y[:,i]
            coef=np.linalg.solve(lhs,rhs)
        else:
            coef=np.linalg.lstsq(A,Y[:,i],rcond=None)[0]
        H[i,support]=coef
    return H
