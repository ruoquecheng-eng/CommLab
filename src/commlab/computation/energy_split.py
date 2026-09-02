import numpy as np


def simulate_energy_aware_split(n_samples=10000,dim=16,local_dim=4,mean_snr_db=6,snr_std_db=5,
                                deadline_ms=2.2,policy='energy_aware',seed=0):
    """Split inference with communication energy, latency and task accuracy.

    The device may finish locally or transmit residual features to the edge.
    ``energy_aware`` offloads only when expected confidence gain per joule is
    worthwhile and the deadline is feasible.
    """
    if policy not in {'static','deadline_aware','energy_aware'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+2504); mu=rng.normal(size=dim); mu/=np.linalg.norm(mu); mu*=1.35
    y=rng.choice([-1.,1.],size=n_samples); X=y[:,None]*mu+rng.normal(size=(n_samples,dim))
    z=X[:,:local_dim]@mu[:local_dim]; conf=1/(1+np.exp(-2*np.abs(z))); pred=np.where(z>=0,1.,-1.)
    snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_samples),-8,28); glin=10**(snr/10)
    uses=dim-local_dim; local_ms=1.0; edge_ms=.5; sym_ms=.10/np.log2(1+glin)
    tx_power_mw=80.0; tx_energy_mj=tx_power_mw*(uses*sym_ms)/1000
    local_energy_mj=.12
    latency=local_ms+uses*sym_ms+edge_ms
    if policy=='static': need=conf<.75
    elif policy=='deadline_aware': need=(conf<.82)&(latency<=deadline_ms)
    else:
        reliability=1-np.exp(-glin/2.5); gain=(1-conf)*reliability
        score=gain/(tx_energy_mj+1e-4)
        need=(score>1.25)&(latency<=deadline_ms)
    if np.any(need):
        Xe=X[need].copy(); Xe[:,local_dim:]+=10**(-snr[need,None]/20)*rng.normal(size=(need.sum(),uses))
        pred[need]=np.where(Xe@mu>=0,1.,-1.)
    sample_latency=np.full(n_samples,local_ms); sample_latency[need]=latency[need]
    misses=sample_latency>deadline_ms; energy=np.full(n_samples,local_energy_mj); energy[need]+=tx_energy_mj[need]
    corr=pred==y
    return {'policy':policy,'accuracy':float(corr.mean()),'on_time_accuracy':float(np.mean(corr&(~misses))),
            'mean_latency_ms':float(sample_latency.mean()),'deadline_miss_rate':float(misses.mean()),
            'mean_energy_mj':float(energy.mean()),'offload_fraction':float(need.mean()),
            'mean_channel_uses':float(uses*need.mean())}
