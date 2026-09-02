import numpy as np


def effective_ris_aircomp_channel(h_direct, device_ris, ris_bs, phases):
    h_direct=np.asarray(h_direct,dtype=complex)
    F=np.asarray(device_ris,dtype=complex)
    g=np.asarray(ris_bs,dtype=complex)
    p=np.asarray(phases,dtype=complex)
    if F.shape!=(h_direct.size,g.size) or p.size!=g.size:
        raise ValueError('dimension mismatch')
    return h_direct + (F*(g*p)[None,:]).sum(axis=1)


def optimize_ris_aircomp(h_direct, device_ris, ris_bs, bits=2, sweeps=2,
                         objective='maxmin'):
    """Finite-bit coordinate ascent for a SISO AirComp RIS.

    ``maxmin`` maximizes the weakest effective device-channel magnitude because
    full-inversion AirComp is bottlenecked by the weakest participating user.
    ``sumgain`` maximizes total channel power as a contrasting non-AirComp-aware
    objective.
    """
    if bits<1 or sweeps<1: raise ValueError('invalid RIS setup')
    N=np.asarray(ris_bs).size
    phases=np.ones(N,dtype=complex)
    code=np.exp(1j*2*np.pi*np.arange(2**bits)/(2**bits))
    hist=[]
    def score(p):
        h=effective_ris_aircomp_channel(h_direct,device_ris,ris_bs,p)
        if objective=='maxmin': return float(np.min(np.abs(h)))
        if objective=='sumgain': return float(np.sum(np.abs(h)**2))
        raise ValueError('unknown objective')
    for _ in range(sweeps):
        for n in range(N):
            best=phases[n]; bs=-np.inf
            for c in code:
                q=phases.copy(); q[n]=c
                s=score(q)
                if s>bs: bs=s; best=c
            phases[n]=best
        hist.append(score(phases))
    return phases,np.asarray(hist)


def aircomp_noise_mse_from_channel(h_eff, snr_db=15.0, vector_dim=32,
                                   n_trials=400, seed=0):
    """Full-inversion AirComp MSE for a fixed effective device channel."""
    h=np.asarray(h_eff,dtype=complex)
    if h.size<2: raise ValueError('need multiple devices')
    rng=np.random.default_rng(seed); K=h.size
    nv=1/(10**(snr_db/10)); a=max(float(np.min(np.abs(h))),1e-6)
    ms=[]
    for _ in range(n_trials):
        x=rng.normal(size=(K,vector_dim)); target=x.mean(axis=0)
        n=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(nv/2)
        est=np.real(a*np.sum(x,axis=0)+n)/(a*K)
        ms.append(np.mean((est-target)**2))
    return {'mean_mse':float(np.mean(ms)),'median_mse':float(np.median(ms)),
            'weakest_gain':a}
