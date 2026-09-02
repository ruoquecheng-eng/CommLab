import numpy as np


def simulate_progressive_split_inference(n_samples=12000, dim=20, local_dim=4,
                                         chunk_size=4, mean_snr_db=5.0,
                                         snr_std_db=5.0, deadline_ms=2.2,
                                         policy='adaptive', confidence_threshold=.82,
                                         seed=0):
    """Progressive feature transmission with early termination.

    The device first computes a local decision. Residual features are ordered by
    task importance and can be uploaded in chunks. ``adaptive`` requests the
    next chunk only if confidence is insufficient *and* the next transmission
    remains deadline-feasible; it also stops when expected confidence gain per
    transmit energy is too small.
    """
    if policy not in {'local','full','confidence','adaptive'}: raise ValueError('unknown policy')
    if not 0<local_dim<dim or chunk_size<1: raise ValueError('invalid dimensions')
    rng=np.random.default_rng(seed+2602)
    # Deterministic-ish decaying task direction creates progressively useful features.
    mu=np.linspace(1.5,.35,dim); mu*=rng.choice([-1.,1.],size=dim); mu/=np.linalg.norm(mu); mu*=1.55
    order=np.argsort(-np.abs(mu))
    local_idx=order[:local_dim]; residual=list(order[local_dim:])
    chunks=[np.asarray(residual[i:i+chunk_size],int) for i in range(0,len(residual),chunk_size)]
    y=rng.choice([-1.,1.],size=n_samples); X=y[:,None]*mu+rng.normal(size=(n_samples,dim))
    snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_samples),-10,26); glin=10**(snr/10)
    per_use_ms=.085/np.log2(1+glin); tx_power_mw=75.; local_ms=.85; edge_chunk_ms=.08

    observed=np.zeros_like(X); observed[:,local_idx]=X[:,local_idx]
    z=observed@mu; uses=np.zeros(n_samples); latency=np.full(n_samples,local_ms); energy=np.full(n_samples,.10)
    alive=np.ones(n_samples,dtype=bool)

    if policy=='local': alive[:]=False
    for ch in chunks:
        if not np.any(alive): break
        conf=1/(1+np.exp(-2*np.abs(z)))
        tx_time=len(ch)*per_use_ms
        next_latency=latency+tx_time+edge_chunk_ms
        if policy=='full': take=alive
        elif policy=='confidence': take=alive & (conf<confidence_threshold)
        else:
            # Approximate task value of another chunk using its projection energy
            # and current uncertainty. This uses only known model importance, not
            # the unseen feature realization.
            importance=float(np.sum(mu[ch]**2))
            expected_gain=(1-conf)*importance*(1-np.exp(-glin/2.8))
            tx_energy=tx_power_mw*tx_time/1000
            take=alive & (conf<confidence_threshold) & (next_latency<=deadline_ms) & (expected_gain/(tx_energy+1e-5)>1.0)
        if not np.any(take):
            if policy!='full': break
        noise=10**(-snr[take,None]/20)*rng.normal(size=(int(take.sum()),len(ch)))
        observed[np.ix_(take,ch)]=X[np.ix_(take,ch)]+noise
        z[take]=observed[take]@mu
        uses[take]+=len(ch); latency[take]=next_latency[take]
        energy[take]+=tx_power_mw*tx_time[take]/1000
        if policy!='full':
            # Samples that declined the current chunk terminate permanently.
            alive &= take

    pred=np.where(z>=0,1.,-1.); correct=pred==y; misses=latency>deadline_ms
    return {
        'policy':policy,'accuracy':float(correct.mean()),
        'on_time_accuracy':float(np.mean(correct & (~misses))),
        'mean_channel_uses':float(uses.mean()),'mean_latency_ms':float(latency.mean()),
        'deadline_miss_rate':float(misses.mean()),'mean_energy_mj':float(energy.mean()),
        'full_residual_uses':int(dim-local_dim),
        'early_exit_fraction':float(np.mean(uses < (dim-local_dim))),
    }
