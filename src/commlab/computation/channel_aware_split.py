import numpy as np


def simulate_channel_aware_split(n_samples=12000,dim=16,local_dim=4,
                                 mean_snr_db=8.0,snr_std_db=5.0,
                                 deadline_ms=2.0,policy='channel_aware',seed=0):
    """Early-exit/offload policy with per-sample channel and deadline variation."""
    rng=np.random.default_rng(seed)
    mu=rng.normal(size=dim); mu/=np.linalg.norm(mu); mu*=1.35
    y=rng.choice([-1.,1.],size=n_samples); X=y[:,None]*mu+rng.normal(size=(n_samples,dim))
    zloc=X[:,:local_dim]@mu[:local_dim]; conf=1/(1+np.exp(-2*np.abs(zloc))); pred=np.where(zloc>=0,1.,-1.)
    snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_samples),-8,30)
    uses=dim-local_dim; local_ms=1.0; edge_ms=.55
    # crude adaptive symbol time: better links carry one normalized feature faster
    sym_ms=.11/np.log2(1+10**(snr/10))
    offload_latency=local_ms+uses*sym_ms+edge_ms
    if policy=='static': need=conf<.75
    elif policy=='channel_aware':
        # Offload only when confidence is low, edge has enough reliability, and deadline is feasible.
        edge_reliability=1-np.exp(-10**(snr/10)/2.5)
        gain=(1-conf)*edge_reliability
        need=(gain>.12)&(offload_latency<=deadline_ms)
    elif policy=='oracle_feasible': need=(conf<.9)&(offload_latency<=deadline_ms)
    else: raise ValueError('unknown policy')
    sigma=10**(-snr[need]/20)
    if need.any():
        Xe=X[need].copy(); Xe[:,local_dim:]+=sigma[:,None]*rng.normal(size=(need.sum(),uses))
        pred[need]=np.where(Xe@mu>=0,1.,-1.)
    latency=np.full(n_samples,local_ms); latency[need]=offload_latency[need]
    misses=latency>deadline_ms
    correct=(pred==y)
    ontime_correct=correct & (~misses)
    return {'policy':policy,'accuracy':float(np.mean(correct)),
            'on_time_accuracy':float(np.mean(ontime_correct)),
            'mean_channel_uses':float(uses*np.mean(need)),
            'offload_fraction':float(np.mean(need)),
            'mean_latency_ms':float(latency.mean()),'deadline_miss_rate':float(misses.mean())}
