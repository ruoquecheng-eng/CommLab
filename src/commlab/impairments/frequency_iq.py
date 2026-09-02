import numpy as np


def apply_frequency_selective_iq_imbalance(
    signal: np.ndarray,
    direct_taps: np.ndarray,
    image_taps: np.ndarray,
) -> np.ndarray:
    """Widely-linear FIR IQ impairment y = h_d*x + h_i*conj(x).

    The output is truncated to the input record length. If the channel/filter
    memory is covered by an OFDM cyclic prefix, the corresponding useful-symbol
    relation is circular and can be compensated pairwise in frequency.
    """
    x=np.asarray(signal,dtype=np.complex128).reshape(-1)
    hd=np.asarray(direct_taps,dtype=np.complex128).reshape(-1)
    hi=np.asarray(image_taps,dtype=np.complex128).reshape(-1)
    if len(hd)<1 or len(hi)<1:
        raise ValueError("tap vectors must be nonempty")
    yd=np.convolve(x,hd,mode='full')[:len(x)]
    yi=np.convolve(np.conj(x),hi,mode='full')[:len(x)]
    return yd+yi


def _delayed_matrix(x: np.ndarray, n_taps: int) -> np.ndarray:
    z=np.asarray(x,dtype=np.complex128).reshape(-1); cols=[]
    for m in range(n_taps):
        d=np.zeros_like(z)
        if m==0: d[:]=z
        elif m<len(z): d[m:]=z[:-m]
        cols.append(d)
    return np.column_stack(cols)


def estimate_frequency_selective_iq_filters(
    training_tx: np.ndarray,
    training_rx: np.ndarray,
    n_taps: int,
    ridge: float = 1e-9,
) -> tuple[np.ndarray,np.ndarray]:
    """LS identify direct and conjugate FIR paths from known complex training."""
    x=np.asarray(training_tx,dtype=np.complex128).reshape(-1)
    y=np.asarray(training_rx,dtype=np.complex128).reshape(-1)
    if len(x)!=len(y) or n_taps<1 or len(x)<4*n_taps:
        raise ValueError("invalid training vectors or tap length")
    X=_delayed_matrix(x,n_taps); Xi=_delayed_matrix(np.conj(x),n_taps); A=np.column_stack((X,Xi))
    d=n_taps-1; Af=A[d:]; yf=y[d:]
    G=Af.conj().T@Af+float(ridge)*np.eye(2*n_taps)
    c=np.linalg.solve(G,Af.conj().T@yf)
    return c[:n_taps],c[n_taps:]


def compensate_frequency_selective_iq_ofdm(
    rx_waveform: np.ndarray,
    direct_taps: np.ndarray,
    image_taps: np.ndarray,
    n_fft: int = 64,
    cp_len: int = 16,
) -> np.ndarray:
    """Pairwise mirror-subcarrier inversion for CP-protected OFDM symbols.

    For k != 0,N/2,
      [Y[k], conj(Y[-k])]^T = M_k [X[k], conj(X[-k])]^T.
    The 2x2 matrix uses the estimated direct/image FIR frequency responses.
    DC and Nyquist bins are left unchanged; they are null in CommLab's default
    carrier allocation.
    """
    y=np.asarray(rx_waveform,dtype=np.complex128).reshape(-1)
    sym_len=n_fft+cp_len
    if len(y)%sym_len:
        raise ValueError("waveform must contain an integer number of OFDM symbols")
    hd=np.asarray(direct_taps,dtype=np.complex128).reshape(-1); hi=np.asarray(image_taps,dtype=np.complex128).reshape(-1)
    A=np.fft.fft(hd,n_fft); B=np.fft.fft(hi,n_fft)
    blocks=y.reshape(-1,sym_len); useful=blocks[:,cp_len:] if cp_len else blocks
    Y=np.fft.fft(useful,axis=1)/np.sqrt(n_fft); X=np.zeros_like(Y)
    X[:,0]=Y[:,0]
    if n_fft%2==0: X[:,n_fft//2]=Y[:,n_fft//2]
    upper=n_fft//2
    for k in range(1,upper):
        km=(-k)%n_fft
        M=np.array([[A[k],B[k]],[np.conj(B[km]),np.conj(A[km])]],dtype=np.complex128)
        if abs(np.linalg.det(M))<1e-10:
            raise ValueError("frequency-selective IQ matrix is singular")
        rhs=np.stack((Y[:,k],np.conj(Y[:,km])),axis=-1)
        sol=np.linalg.solve(M,rhs[...,None])[...,0]
        X[:,k]=sol[:,0]; X[:,km]=np.conj(sol[:,1])
    time=np.fft.ifft(X,axis=1)*np.sqrt(n_fft)
    if cp_len:
        out=np.concatenate((time[:,-cp_len:],time),axis=1)
    else: out=time
    return out.reshape(-1)
