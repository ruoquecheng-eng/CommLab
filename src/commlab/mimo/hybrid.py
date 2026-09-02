import numpy as np


def ula_response(n_ant: int, angle_deg: float, spacing_wavelength: float = 0.5) -> np.ndarray:
    if n_ant<1 or spacing_wavelength<=0: raise ValueError('invalid ULA')
    n=np.arange(n_ant); th=np.deg2rad(float(angle_deg))
    return np.exp(1j*2*np.pi*spacing_wavelength*n*np.sin(th))/np.sqrt(n_ant)


def sparse_geometric_mimo_channel(n_rx: int, n_tx: int, n_paths: int,
                                  rng: np.random.Generator | None = None):
    """Narrowband sparse geometric mmWave-like channel with random AoA/AoD."""
    if min(n_rx,n_tx,n_paths)<1: raise ValueError('invalid channel dimensions')
    rg=np.random.default_rng() if rng is None else rng
    aoa=rg.uniform(-70,70,n_paths); aod=rg.uniform(-70,70,n_paths)
    alpha=(rg.normal(size=n_paths)+1j*rg.normal(size=n_paths))/np.sqrt(2*n_paths)
    H=np.zeros((n_rx,n_tx),complex)
    for g,ar,at in zip(alpha,aoa,aod): H += g*np.outer(ula_response(n_rx,ar),ula_response(n_tx,at).conj())
    H*=np.sqrt(n_rx*n_tx)
    return H,aoa,aod


def dft_codebook(n_ant: int) -> np.ndarray:
    n=np.arange(n_ant)[:,None]; k=np.arange(n_ant)[None,:]
    return np.exp(1j*2*np.pi*n*k/n_ant)/np.sqrt(n_ant)


def full_digital_svd_rate(H: np.ndarray, snr_linear: float, n_streams: int) -> float:
    A=np.asarray(H,complex); s=np.linalg.svd(A,compute_uv=False)[:int(n_streams)]
    if snr_linear<=0 or n_streams<1 or n_streams>min(A.shape): raise ValueError('invalid parameters')
    return float(np.sum(np.log2(1+(snr_linear/n_streams)*s*s)))


def hybrid_dft_svd_rate(H: np.ndarray, snr_linear: float, n_streams: int, n_rf: int) -> float:
    """DFT-beam analog selection followed by low-dimensional digital SVD."""
    A=np.asarray(H,complex); nr,nt=A.shape; ns=int(n_streams); q=int(n_rf)
    if snr_linear<=0 or not (1<=ns<=q<=min(nr,nt)): raise ValueError('need streams <= RF chains <= min antennas')
    Ft=dft_codebook(nt); scores=np.sum(np.abs(A@Ft)**2,axis=0); ti=np.argsort(scores)[-q:]; Frf=Ft[:,ti]
    Wr=dft_codebook(nr); scores_r=np.sum(np.abs(Wr.conj().T@A@Frf)**2,axis=1); ri=np.argsort(scores_r)[-q:]; Wrf=Wr[:,ri]
    He=Wrf.conj().T@A@Frf; s=np.linalg.svd(He,compute_uv=False)[:ns]
    return float(np.sum(np.log2(1+(snr_linear/ns)*s*s)))


def hybrid_omp_precoder(H: np.ndarray, n_streams: int, n_rf: int,
                         codebook: np.ndarray | None = None) -> np.ndarray:
    """OMP hybrid transmit precoder approximating the dominant right-singular subspace.

    Returns the normalized composite precoder F_RF F_BB. The analog dictionary
    defaults to the unitary DFT codebook, so this remains a phase-only,
    codebook-constrained educational baseline rather than a hardware model.
    """
    A=np.asarray(H,dtype=np.complex128); nr,nt=A.shape; ns=int(n_streams); q=int(n_rf)
    if not (1<=ns<=q<=nt): raise ValueError("need streams <= RF chains <= tx antennas")
    D=dft_codebook(nt) if codebook is None else np.asarray(codebook,dtype=np.complex128)
    if D.ndim!=2 or D.shape[0]!=nt: raise ValueError("invalid analog dictionary")
    _,_,Vh=np.linalg.svd(A,full_matrices=False); Fopt=Vh.conj().T[:,:ns]
    residual=Fopt.copy(); chosen=[]
    for _ in range(q):
        score=np.sum(np.abs(D.conj().T@residual)**2,axis=1)
        for j in chosen: score[j]=-np.inf
        idx=int(np.argmax(score)); chosen.append(idx)
        Frf=D[:,chosen]
        Fbb=np.linalg.pinv(Frf)@Fopt
        residual=Fopt-Frf@Fbb
    F=Frf@Fbb
    return F*np.sqrt(ns/max(float(np.sum(np.abs(F)**2)),1e-15))


def precoded_mimo_rate(H: np.ndarray, F: np.ndarray, snr_linear: float, n_streams: int | None = None) -> float:
    """Mutual-information rate with a fixed transmit precoder and optimal receive processing."""
    A=np.asarray(H,dtype=np.complex128); P=np.asarray(F,dtype=np.complex128)
    if A.ndim!=2 or P.ndim!=2 or A.shape[1]!=P.shape[0] or snr_linear<=0: raise ValueError("invalid dimensions/SNR")
    ns=P.shape[1] if n_streams is None else int(n_streams)
    if ns<1: raise ValueError("invalid stream count")
    G=A@P; M=np.eye(A.shape[0],dtype=np.complex128)+(float(snr_linear)/ns)*(G@G.conj().T)
    sign,ld=np.linalg.slogdet(M)
    if sign.real<=0: raise ValueError("non-positive rate matrix")
    return float(ld/np.log(2))
