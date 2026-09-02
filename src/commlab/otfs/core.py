import numpy as np


def ofdm_grid_modulate(tf_grid: np.ndarray, cp_len: int = 0) -> np.ndarray:
    """OFDM-modulate a time-frequency grid of shape (time_slots, subcarriers)."""
    X = np.asarray(tf_grid, dtype=np.complex128)
    if X.ndim != 2:
        raise ValueError("tf_grid must be 2-D")
    time = np.fft.ifft(X, axis=1, norm="ortho")
    if cp_len:
        if cp_len < 0 or cp_len > X.shape[1]:
            raise ValueError("invalid cp_len")
        time = np.concatenate((time[:, -cp_len:], time), axis=1)
    return time.reshape(-1)


def ofdm_grid_demodulate(waveform: np.ndarray, n_slots: int, n_subcarriers: int, cp_len: int = 0) -> np.ndarray:
    y = np.asarray(waveform, dtype=np.complex128).reshape(-1)
    symbol_len = n_subcarriers + cp_len
    needed = n_slots * symbol_len
    if len(y) < needed:
        raise ValueError("waveform too short")
    blocks = y[:needed].reshape(n_slots, symbol_len)
    blocks = blocks[:, cp_len:]
    return np.fft.fft(blocks, axis=1, norm="ortho")


def otfs_modulate(dd_grid: np.ndarray, cp_len: int = 0) -> np.ndarray:
    """OTFS modulation via unitary ISFFT followed by OFDM modulation.

    Grid convention: axis 0 is Doppler/time-slot index N, axis 1 is delay/
    subcarrier index M.
    """
    Xdd = np.asarray(dd_grid, dtype=np.complex128)
    if Xdd.ndim != 2:
        raise ValueError("dd_grid must be 2-D")
    Xtf = np.fft.ifft(Xdd, axis=0, norm="ortho")
    Xtf = np.fft.fft(Xtf, axis=1, norm="ortho")
    return ofdm_grid_modulate(Xtf, cp_len)


def otfs_demodulate(waveform: np.ndarray, n_doppler: int, n_delay: int, cp_len: int = 0) -> np.ndarray:
    Ytf = ofdm_grid_demodulate(waveform, n_doppler, n_delay, cp_len)
    Ydd = np.fft.fft(Ytf, axis=0, norm="ortho")
    return np.fft.ifft(Ydd, axis=1, norm="ortho")


def apply_delay_doppler_paths(
    waveform: np.ndarray,
    paths: list[tuple[int, float, complex]],
    n_subcarriers: int,
    n_slots: int,
) -> np.ndarray:
    """Apply deterministic integer-delay/fractional-Doppler paths.

    Each path is ``(delay_samples, doppler_bins, coefficient)``. One Doppler bin
    equals 1/(N*M) cycles/sample in this normalized educational model.
    """
    x = np.asarray(waveform, dtype=np.complex128).reshape(-1)
    y = np.zeros_like(x)
    n = np.arange(len(x), dtype=float)
    denom = float(n_subcarriers * n_slots)
    for delay, doppler_bins, coeff in paths:
        d = int(delay)
        if d < 0:
            raise ValueError("delay must be nonnegative")
        shifted = np.zeros_like(x)
        if d == 0:
            shifted[:] = x
        elif d < len(x):
            shifted[d:] = x[:-d]
        phase = np.exp(1j * 2*np.pi*float(doppler_bins)*n/denom)
        y += complex(coeff) * shifted * phase
    return y


def effective_channel_matrix(
    modulator,
    demodulator,
    shape: tuple[int, int],
    channel,
) -> np.ndarray:
    """Numerically build the symbol-domain channel matrix for small grids."""
    n = int(np.prod(shape))
    A = np.empty((n, n), dtype=np.complex128)
    for j in range(n):
        grid = np.zeros(shape, dtype=np.complex128)
        grid.reshape(-1)[j] = 1.0
        y = demodulator(channel(modulator(grid)))
        A[:, j] = np.asarray(y).reshape(-1)
    return A


def linear_mmse_detect(y: np.ndarray, A: np.ndarray, noise_var: float) -> np.ndarray:
    y = np.asarray(y, dtype=np.complex128).reshape(-1)
    H = np.asarray(A, dtype=np.complex128)
    lhs = H.conj().T @ H + float(noise_var) * np.eye(H.shape[1])
    return np.linalg.solve(lhs, H.conj().T @ y)


def sparsify_channel_matrix(A: np.ndarray, keep_per_row: int) -> np.ndarray:
    """Keep the strongest ``keep_per_row`` coefficients in each row."""
    H = np.asarray(A, dtype=np.complex128)
    if H.ndim != 2:
        raise ValueError("A must be 2-D")
    if keep_per_row < 1:
        raise ValueError("keep_per_row must be positive")
    if keep_per_row >= H.shape[1]:
        return H.copy()
    out = np.zeros_like(H)
    idx = np.argpartition(np.abs(H), -keep_per_row, axis=1)[:, -keep_per_row:]
    rows = np.arange(H.shape[0])[:, None]
    out[rows, idx] = H[rows, idx]
    return out


def cg_lmmse_detect(
    y: np.ndarray,
    A: np.ndarray,
    noise_var: float,
    max_iter: int = 50,
    tol: float = 1e-8,
    x0: np.ndarray | None = None,
) -> tuple[np.ndarray, int, float]:
    """Conjugate-gradient solution of the LMMSE normal equations.

    Returns ``(x_hat, iterations, relative_residual)``. This avoids a direct
    dense inverse and is useful as an educational iterative OTFS detector
    baseline when the effective delay-Doppler channel is sparse/structured.
    """
    H = np.asarray(A, dtype=np.complex128)
    rcv = np.asarray(y, dtype=np.complex128).reshape(-1)
    if H.shape[0] != len(rcv):
        raise ValueError("dimension mismatch")
    b = H.conj().T @ rcv
    reg = float(noise_var)

    def matvec(v):
        return H.conj().T @ (H @ v) + reg * v

    x = np.zeros(H.shape[1], dtype=np.complex128) if x0 is None else np.asarray(x0, dtype=np.complex128).reshape(-1).copy()
    res = b - matvec(x)
    p = res.copy()
    rsold = float(np.vdot(res, res).real)
    bnorm = max(float(np.linalg.norm(b)), 1e-30)
    rel = np.sqrt(rsold) / bnorm
    if rel <= tol:
        return x, 0, rel
    for it in range(1, int(max_iter) + 1):
        Ap = matvec(p)
        denom = np.vdot(p, Ap)
        if abs(denom) < 1e-30:
            return x, it - 1, rel
        alpha = rsold / denom
        x += alpha * p
        res -= alpha * Ap
        rsnew = float(np.vdot(res, res).real)
        rel = np.sqrt(rsnew) / bnorm
        if rel <= tol:
            return x, it, rel
        p = res + (rsnew / max(rsold, 1e-30)) * p
        rsold = rsnew
    return x, int(max_iter), rel


def otfs_pilot_dictionary(
    pilot_grid: np.ndarray,
    delay_candidates,
    doppler_candidates,
    cp_len: int = 0,
) -> tuple[np.ndarray,list[tuple[int,float]]]:
    """Build a delay-Doppler path dictionary from one known OTFS pilot grid.

    Each column is the received DD-domain response to a unit-gain candidate
    path. This intentionally uses the same waveform/channel primitives as the
    rest of CommLab, so delay/Doppler phase conventions stay self-consistent.
    """
    P=np.asarray(pilot_grid,dtype=np.complex128)
    if P.ndim!=2: raise ValueError("pilot_grid must be 2-D")
    N,M=P.shape; x=otfs_modulate(P,cp_len)
    cols=[]; params=[]
    for d in delay_candidates:
        for k in doppler_candidates:
            y=apply_delay_doppler_paths(x,[(int(d),float(k),1+0j)],M,N)
            cols.append(otfs_demodulate(y,N,M,cp_len).reshape(-1))
            params.append((int(d),float(k)))
    if not cols: raise ValueError("candidate grid is empty")
    return np.column_stack(cols),params


def omp_estimate_delay_doppler_paths(
    received_dd: np.ndarray,
    pilot_grid: np.ndarray,
    delay_candidates,
    doppler_candidates,
    n_paths: int,
    cp_len: int = 0,
) -> tuple[list[tuple[int,float,complex]],float]:
    """OMP estimate of a sparse integer/grid-aligned OTFS path model.

    The path count is supplied by the caller; this is a transparent sparse
    channel-estimation baseline rather than a standards-compliant estimator.
    Returns ``(estimated_paths, relative_residual)``.
    """
    y=np.asarray(received_dd,dtype=np.complex128).reshape(-1)
    D,params=otfs_pilot_dictionary(pilot_grid,delay_candidates,doppler_candidates,cp_len)
    if D.shape[0]!=len(y) or n_paths<1 or n_paths>D.shape[1]: raise ValueError("invalid OMP dimensions")
    # Normalize only for correlation selection; solve gains on original columns.
    norms=np.maximum(np.linalg.norm(D,axis=0),1e-15); Dn=D/norms
    residual=y.copy(); support=[]; coeff=np.empty(0,dtype=np.complex128)
    for _ in range(int(n_paths)):
        corr=np.abs(Dn.conj().T@residual); corr[support]=-np.inf
        j=int(np.argmax(corr)); support.append(j)
        Ds=D[:,support]; coeff=np.linalg.lstsq(Ds,y,rcond=None)[0]
        residual=y-Ds@coeff
    paths=[(params[j][0],params[j][1],complex(c)) for j,c in zip(support,coeff)]
    rel=float(np.linalg.norm(residual)/max(np.linalg.norm(y),1e-15))
    return paths,rel
