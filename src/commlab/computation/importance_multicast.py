import numpy as np


def simulate_importance_aware_model_multicast(n_clients=24, model_bits=120_000,
                                               base_fraction=.45, mean_snr_db=5.0,
                                               snr_std_db=7.0,
                                               importance_anticorrelation=.7,
                                               airtime_penalty=4e-6, seed=0):
    """Layered downlink where model quality has client-dependent task value.

    A base layer reaches everyone. The enhancement layer can be multicast at a
    selected code rate; lowering that rate includes weaker clients but costs more
    airtime. ``importance_aware`` chooses the decoding threshold that maximizes
    weighted task utility minus airtime penalty. ``snr_half`` is the conventional
    stronger-half layered baseline.
    """
    if not 0<base_fraction<1: raise ValueError('bad base fraction')
    rng=np.random.default_rng(seed+2605); snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_clients),-12,25)
    # Higher importance can deliberately correlate with weaker links, exposing
    # the difference between radio efficiency and task utility.
    z=(snr-snr.mean())/(snr.std()+1e-12)
    imp_raw=-importance_anticorrelation*z+np.sqrt(max(1-importance_anticorrelation**2,0))*rng.normal(size=n_clients)
    importance=np.exp(.45*imp_raw); importance/=importance.mean()
    se=np.log2(1+10**(snr/10)); eps=1e-9; base_bits=model_bits*base_fraction; enh_bits=model_bits-base_bits
    base_time=base_bits/(np.min(se)+eps); base_util=.65

    def eval_threshold(thr):
        selected=snr>=thr
        if not np.any(selected): return None
        t=base_time+enh_bits/(np.min(se[selected])+eps)
        util=np.full(n_clients,base_util); util[selected]=1.0
        weighted=float(np.sum(importance*util)/np.sum(importance))
        objective=weighted-airtime_penalty*t
        return t,weighted,float(util.mean()),float(selected.mean()),objective

    med=float(np.median(snr)); snr_half=eval_threshold(med)
    candidates=np.unique(np.r_[snr, np.max(snr)+1e-6])[:-1]
    vals=[eval_threshold(float(t)) for t in candidates]
    best=max(vals,key=lambda x:x[-1])
    full_time=model_bits/(np.min(se)+eps)
    return {
        'snr_half_time':float(snr_half[0]),'snr_half_weighted_utility':float(snr_half[1]),
        'snr_half_mean_utility':float(snr_half[2]),'snr_half_enhanced_fraction':float(snr_half[3]),
        'importance_time':float(best[0]),'importance_weighted_utility':float(best[1]),
        'importance_mean_utility':float(best[2]),'importance_enhanced_fraction':float(best[3]),
        'full_common_time':float(full_time),'importance_snr_correlation':float(np.corrcoef(importance,snr)[0,1]),
    }
