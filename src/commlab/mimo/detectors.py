import numpy as np


def zf_detect(y: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Batch zero-forcing detector for narrowband MIMO.

    h shape: (..., n_rx, n_tx), y shape: (..., n_rx)
    returns: (..., n_tx)
    """
    H = np.asarray(h, dtype=np.complex128)
    Y = np.asarray(y, dtype=np.complex128)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    pinv = np.linalg.pinv(H)
    return np.einsum("...ij,...j->...i", pinv, Y)


def mmse_detect(
    y: np.ndarray,
    h: np.ndarray,
    noise_var: float,
    symbol_energy: float = 1.0,
) -> np.ndarray:
    """Batch linear MMSE detector for narrowband MIMO."""
    H = np.asarray(h, dtype=np.complex128)
    Y = np.asarray(y, dtype=np.complex128)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    Hh = np.swapaxes(np.conj(H), -1, -2)
    gram = Hh @ H
    n_tx = H.shape[-1]
    reg = (noise_var / symbol_energy) * np.eye(n_tx, dtype=np.complex128)
    rhs = np.einsum("...ij,...j->...i", Hh, Y)
    return np.linalg.solve(gram + reg, rhs[..., None])[..., 0]


def ml_detect_small(y: np.ndarray, h: np.ndarray, constellation: np.ndarray) -> np.ndarray:
    """Exhaustive maximum-likelihood detector for small MIMO systems.

    Intended for educational 2x2/3x3 low-order constellations only. Complexity
    grows exponentially as M**n_tx and is reported as such in the project docs.
    """
    H=np.asarray(h,dtype=np.complex128); Y=np.asarray(y,dtype=np.complex128)
    const=np.asarray(constellation,dtype=np.complex128).reshape(-1)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    n_tx=H.shape[-1]
    grids=np.meshgrid(*([const]*n_tx),indexing='ij')
    candidates=np.stack([g.reshape(-1) for g in grids],axis=1)  # (M^nt, nt)
    flatH=H.reshape(-1,H.shape[-2],n_tx); flatY=Y.reshape(-1,Y.shape[-1])
    out=np.empty((len(flatH),n_tx),dtype=np.complex128)
    for i,(Hi,yi) in enumerate(zip(flatH,flatY)):
        pred=candidates @ Hi.T
        metric=np.sum(np.abs(pred-yi[None,:])**2,axis=1)
        out[i]=candidates[int(np.argmin(metric))]
    return out.reshape(Y.shape[:-1]+(n_tx,))



def k_best_detect(
    y: np.ndarray,
    h: np.ndarray,
    constellation: np.ndarray,
    k_best: int = 8,
    return_expansions: bool = False,
):
    """Breadth-first QR K-best detector for small/medium MIMO systems.

    The ML metric ``||y-Hs||^2`` is transformed with a reduced QR
    decomposition. The tree is expanded from the last transmit layer upward,
    retaining only the K lowest accumulated Euclidean metrics at every depth.
    ``k_best=1`` is a greedy SIC-like search; sufficiently large K recovers
    exhaustive ML. This is an educational complexity/performance baseline.
    """
    H=np.asarray(h,dtype=np.complex128); Y=np.asarray(y,dtype=np.complex128)
    const=np.asarray(constellation,dtype=np.complex128).reshape(-1)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    if k_best < 1 or len(const) < 1:
        raise ValueError("k_best and constellation must be nonempty")
    n_rx,n_tx=H.shape[-2],H.shape[-1]
    if n_rx < n_tx:
        raise ValueError("K-best implementation requires n_rx >= n_tx")
    flatH=H.reshape(-1,n_rx,n_tx); flatY=Y.reshape(-1,n_rx)
    out=np.empty((len(flatH),n_tx),dtype=np.complex128); total_exp=0
    for b,(Hb,yb) in enumerate(zip(flatH,flatY)):
        Q,R=np.linalg.qr(Hb,mode='reduced')
        z=Q.conj().T@yb
        # State is (metric, vector); unassigned symbols are zeros.
        states=[(0.0,np.zeros(n_tx,dtype=np.complex128))]
        for i in range(n_tx-1,-1,-1):
            cand=[]
            for metric,vec in states:
                known=np.dot(R[i,i+1:],vec[i+1:]) if i+1<n_tx else 0.0j
                for sym in const:
                    v=vec.copy(); v[i]=sym
                    resid=z[i]-known-R[i,i]*sym
                    cand.append((metric+float(abs(resid)**2),v))
            total_exp += len(cand)
            cand.sort(key=lambda item:item[0])
            states=cand[:min(int(k_best),len(cand))]
        out[b]=states[0][1]
    result=out.reshape(Y.shape[:-1]+(n_tx,))
    return (result,total_exp) if return_expansions else result


def _candidate_vectors_and_bits(constellation: np.ndarray, bit_labels: np.ndarray, n_tx: int):
    """Enumerate symbol vectors and matching per-stream bit labels."""
    const=np.asarray(constellation,dtype=np.complex128).reshape(-1)
    labels=np.asarray(bit_labels,dtype=np.uint8)
    if labels.ndim!=2 or labels.shape[0]!=len(const):
        raise ValueError("bit_labels must have one row per constellation point")
    grids=np.meshgrid(*([np.arange(len(const))]*int(n_tx)),indexing='ij')
    idx=np.stack([g.reshape(-1) for g in grids],axis=1)
    return const[idx], labels[idx]


def maxlog_ml_llr(
    y: np.ndarray,
    h: np.ndarray,
    constellation: np.ndarray,
    bit_labels: np.ndarray,
    noise_var: float,
) -> np.ndarray:
    """Exact small-MIMO max-log bit LLRs by exhaustive vector enumeration.

    The returned convention is ``log P(bit=0)/P(bit=1)`` and the output shape
    is ``(..., n_tx, bits_per_symbol)``. This is deliberately a reference
    detector: complexity grows as ``M**n_tx``.
    """
    H=np.asarray(h,dtype=np.complex128); Y=np.asarray(y,dtype=np.complex128)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    if noise_var <= 0: raise ValueError("noise_var must be positive")
    n_rx,n_tx=H.shape[-2],H.shape[-1]
    candidates,bits=_candidate_vectors_and_bits(constellation,bit_labels,n_tx)
    bps=bits.shape[-1]
    flatH=H.reshape(-1,n_rx,n_tx); flatY=Y.reshape(-1,n_rx)
    out=np.empty((len(flatH),n_tx,bps),dtype=float)
    for q,(Hi,yi) in enumerate(zip(flatH,flatY)):
        pred=candidates @ Hi.T
        metric=np.sum(np.abs(pred-yi[None,:])**2,axis=1)
        for tx in range(n_tx):
            for b in range(bps):
                d0=np.min(metric[bits[:,tx,b]==0]); d1=np.min(metric[bits[:,tx,b]==1])
                out[q,tx,b]=(d1-d0)/float(noise_var)
    return out.reshape(Y.shape[:-1]+(n_tx,bps))


def k_best_soft_llr(
    y: np.ndarray,
    h: np.ndarray,
    constellation: np.ndarray,
    bit_labels: np.ndarray,
    noise_var: float,
    k_best: int = 16,
    llr_clip: float = 40.0,
    return_expansions: bool = False,
):
    """Approximate max-log soft-output QR K-best MIMO detector.

    Final K candidates form a list approximation to the max-log APP search.
    When the retained list contains no hypothesis for one bit value, the LLR
    saturates at ``+/-llr_clip`` rather than claiming infinite certainty.
    """
    H=np.asarray(h,dtype=np.complex128); Y=np.asarray(y,dtype=np.complex128)
    const=np.asarray(constellation,dtype=np.complex128).reshape(-1)
    labels=np.asarray(bit_labels,dtype=np.uint8)
    if labels.ndim!=2 or labels.shape[0]!=len(const): raise ValueError("invalid bit_labels")
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]: raise ValueError("incompatible H and y shapes")
    if noise_var<=0 or k_best<1: raise ValueError("invalid noise_var/k_best")
    n_rx,n_tx=H.shape[-2],H.shape[-1]; bps=labels.shape[1]
    if n_rx<n_tx: raise ValueError("K-best requires n_rx >= n_tx")
    flatH=H.reshape(-1,n_rx,n_tx); flatY=Y.reshape(-1,n_rx)
    out=np.empty((len(flatH),n_tx,bps),dtype=float); total_exp=0
    for q,(Hb,yb) in enumerate(zip(flatH,flatY)):
        Q,R=np.linalg.qr(Hb,mode='reduced'); z=Q.conj().T@yb
        # state: accumulated metric, symbols, constellation indices
        states=[(0.0,np.zeros(n_tx,dtype=np.complex128),np.full(n_tx,-1,dtype=int))]
        for i in range(n_tx-1,-1,-1):
            cand=[]
            for metric,vec,inds in states:
                known=np.dot(R[i,i+1:],vec[i+1:]) if i+1<n_tx else 0.0j
                for ci,sym in enumerate(const):
                    v=vec.copy(); ids=inds.copy(); v[i]=sym; ids[i]=ci
                    resid=z[i]-known-R[i,i]*sym
                    cand.append((metric+float(abs(resid)**2),v,ids))
            total_exp += len(cand); cand.sort(key=lambda item:item[0]); states=cand[:min(int(k_best),len(cand))]
        metrics=np.array([s[0] for s in states],float)
        ids=np.stack([s[2] for s in states]); listbits=labels[ids]  # (K,tx,bps)
        for tx in range(n_tx):
            for b in range(bps):
                m0=metrics[listbits[:,tx,b]==0]; m1=metrics[listbits[:,tx,b]==1]
                if len(m0)==0: val=-float(llr_clip)
                elif len(m1)==0: val=float(llr_clip)
                else: val=(float(np.min(m1))-float(np.min(m0)))/float(noise_var)
                out[q,tx,b]=float(np.clip(val,-llr_clip,llr_clip))
    result=out.reshape(Y.shape[:-1]+(n_tx,bps))
    return (result,total_exp) if return_expansions else result


def mmse_sic_detect(
    y: np.ndarray,
    h: np.ndarray,
    constellation: np.ndarray,
    noise_var: float,
    symbol_energy: float = 1.0,
    ordered: bool = True,
    return_order: bool = False,
):
    """Ordered MMSE successive-interference-cancellation detector.

    At each stage the residual channel is re-filtered with an MMSE front end.
    When ``ordered`` is true, the stream with the smallest diagonal element of
    the MMSE error covariance is detected first. The sliced symbol is then
    cancelled before the next stage. This provides a transparent bridge between
    linear MMSE and tree-search/ML detectors.
    """
    H=np.asarray(h,dtype=np.complex128); Y=np.asarray(y,dtype=np.complex128)
    const=np.asarray(constellation,dtype=np.complex128).reshape(-1)
    if H.shape[:-2] != Y.shape[:-1] or H.shape[-2] != Y.shape[-1]:
        raise ValueError("incompatible H and y shapes")
    if noise_var < 0 or symbol_energy <= 0 or len(const)<1:
        raise ValueError("invalid MMSE-SIC parameters")
    n_rx,n_tx=H.shape[-2],H.shape[-1]
    flatH=H.reshape(-1,n_rx,n_tx); flatY=Y.reshape(-1,n_rx)
    out=np.empty((len(flatH),n_tx),dtype=np.complex128)
    orders=np.empty((len(flatH),n_tx),dtype=int)
    reg=float(noise_var)/float(symbol_energy)
    for b,(Hb,yb) in enumerate(zip(flatH,flatY)):
        remaining=list(range(n_tx)); Hr=Hb.copy(); r=yb.copy(); xhat=np.zeros(n_tx,complex)
        for stage in range(n_tx):
            G=np.linalg.inv(Hr.conj().T@Hr + reg*np.eye(Hr.shape[1]))
            W=G@Hr.conj().T
            soft=W@r
            if ordered:
                # Posterior error covariance is proportional to G; smaller
                # diagonal means a more reliable stream at this stage.
                local=int(np.argmin(np.real(np.diag(G))))
            else:
                local=0
            stream=remaining[local]
            sym=const[int(np.argmin(np.abs(soft[local]-const)**2))]
            xhat[stream]=sym; orders[b,stage]=stream
            r=r-Hr[:,local]*sym
            Hr=np.delete(Hr,local,axis=1); remaining.pop(local)
        out[b]=xhat
    result=out.reshape(Y.shape[:-1]+(n_tx,)); order_result=orders.reshape(Y.shape[:-1]+(n_tx,))
    return (result,order_result) if return_order else result
