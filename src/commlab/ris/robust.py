import numpy as np
from commlab.ris.cellfree import cellfree_ris_rates


def perturb_complex_channel(x: np.ndarray, nmse: float, rng: np.random.Generator) -> np.ndarray:
    """Add isotropic complex Gaussian perturbation with requested expected NMSE."""
    a=np.asarray(x,np.complex128)
    if nmse<0: raise ValueError('nmse must be nonnegative')
    if nmse==0: return a.copy()
    p=float(np.mean(np.abs(a)**2))
    n=(rng.normal(size=a.shape)+1j*rng.normal(size=a.shape))/np.sqrt(2)
    return a+np.sqrt(float(nmse)*max(p,1e-15))*n


def sample_average_optimize_cellfree_ris(channel_samples, snr_linear: float, bits: int = 2,
                                          iterations: int = 2, mask: np.ndarray | None = None,
                                          objective: str = 'sum_rate', initial_phases=None):
    """Finite-bit coordinate ascent maximizing average utility over CSI samples."""
    samples=list(channel_samples)
    if not samples or bits<1 or iterations<1 or objective not in {'sum_rate','min_rate'}: raise ValueError('invalid robust RIS setup')
    N=np.asarray(samples[0][1]).shape[0]
    th=np.zeros(N,float) if initial_phases is None else np.asarray(initial_phases,float).reshape(-1).copy()
    if len(th)!=N: raise ValueError('invalid initial phases')
    for D,G,R in samples:
        if np.asarray(G).shape[0]!=N: raise ValueError('inconsistent RIS size')
    levels=2*np.pi*np.arange(2**int(bits))/(2**int(bits))
    def utility(x):
        vals=[]
        for D,G,R in samples:
            r=cellfree_ris_rates(D,G,R,x,snr_linear,mask)
            vals.append(float(r.sum() if objective=='sum_rate' else r.min()))
        return float(np.mean(vals))
    best=utility(th); hist=[best]
    for _ in range(int(iterations)):
        for n in range(N):
            local=best; bp=th[n]
            for p in levels:
                th[n]=p; v=utility(th)
                if v>local+1e-12: local=v; bp=float(p)
            th[n]=bp; best=local
        hist.append(best)
    return np.angle(np.exp(1j*th)),hist
