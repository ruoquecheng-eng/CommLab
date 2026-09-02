import numpy as np


def simulate_semantic_harq(n_samples=18000, policy='task_harq', mean_snr_db=2.0,
                           max_rounds=2, confidence_threshold=1.0, seed=0):
    """Reliability-oriented semantic HARQ for a scalar task statistic.

    Samples have a latent task score ``s`` and label sign(s). Each transmission
    sends the same task statistic through an independent block-fading channel;
    retransmissions are MRC-combined. ``channel_harq`` retransmits when the first
    round SNR is poor, while ``task_harq`` retransmits when the *sample-level*
    normalized decision margin is small. This is an educational task-reliability
    abstraction, not a standards HARQ implementation or learned semantic codec.
    """
    if policy not in {'no_harq','channel_harq','task_harq'}:
        raise ValueError('unknown policy')
    if n_samples < 100 or max_rounds < 1:
        raise ValueError('bad semantic HARQ setup')
    rng=np.random.default_rng(seed+3201)
    # Latent task difficulty: many points sit close to the decision boundary.
    s=rng.normal(0,1,n_samples)
    y=s>=0
    # Per-sample block fading, normalized to the requested mean SNR.
    gbar=10**(mean_snr_db/10)
    gamma1=gbar*rng.exponential(1.0,n_samples)
    noise1=rng.normal(size=n_samples)/np.sqrt(np.maximum(gamma1,1e-12))
    obs=s+noise1
    gamma_tot=gamma1.copy(); rounds=np.ones(n_samples,int)
    # Decision confidence uses the normalized margin at the receiver.
    norm_margin=np.abs(obs)*np.sqrt(gamma_tot)
    if policy=='channel_harq':
        request=gamma1 < gbar*.75
    elif policy=='task_harq':
        request=norm_margin < confidence_threshold
    else:
        request=np.zeros(n_samples,bool)
    for r in range(2,max_rounds+1):
        idx=np.flatnonzero(request & (rounds<r))
        if idx.size==0: break
        gamma_new=gbar*rng.exponential(1.0,idx.size)
        noise_new=rng.normal(size=idx.size)/np.sqrt(np.maximum(gamma_new,1e-12))
        obs_new=s[idx]+noise_new
        # MRC of equalized scalar observations.
        obs[idx]=(gamma_tot[idx]*obs[idx]+gamma_new*obs_new)/(gamma_tot[idx]+gamma_new)
        gamma_tot[idx]+=gamma_new; rounds[idx]=r
        if policy=='task_harq':
            nm=np.abs(obs[idx])*np.sqrt(gamma_tot[idx])
            request[idx]=nm<confidence_threshold
        else:
            request[idx]=False
    pred=obs>=0
    acc=float(np.mean(pred==y))
    # Reliability metric on intrinsically hard samples near the class boundary.
    q=np.quantile(np.abs(s),.25); hard=np.abs(s)<=q
    hard_acc=float(np.mean(pred[hard]==y[hard]))
    err=(pred!=y).astype(float)
    # Worst-decile empirical batch error is a simple lower-tail reliability proxy.
    chunks=np.array_split(err,50)
    batch_err=np.array([c.mean() for c in chunks])
    p90_error=float(np.quantile(batch_err,.90))
    return {
        'policy':policy,'mean_snr_db':float(mean_snr_db),'accuracy':acc,
        'hard_sample_accuracy':hard_acc,'p90_batch_error':p90_error,
        'mean_channel_uses':float(rounds.mean()),
        'retransmission_rate':float(np.mean(rounds>1)),
        'mean_combined_snr_db':float(10*np.log10(np.mean(gamma_tot)+1e-12)),
    }
