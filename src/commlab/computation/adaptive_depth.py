import numpy as np


def _acc_model(bits,depth,snr_db,difficulty):
    # Smooth toy task-accuracy model: feature precision and compute depth both help.
    feat=1-np.exp(-.42*bits*10**(snr_db/20))
    comp=1-np.exp(-.62*depth)
    base=.52+.45*feat*comp
    return np.clip(base-.16*difficulty*(1-comp),.5,.995)


def simulate_channel_adaptive_depth(n_tasks=12000,policy='adaptive',mean_snr_db=2.0,latency_budget_ms=3.0,seed=0):
    """Joint feature-bit and edge-depth selection under a task latency budget.

    bits in {2,4,8} represent feature precision; depth in {1,2,3,4} represents
    progressively deeper edge inference. Accuracy is an analytic proxy, not a DNN.
    """
    if policy not in {'fixed_light','fixed_deep','adaptive'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3102); snr=rng.normal(mean_snr_db,4.0,n_tasks); diff=rng.beta(2.2,2.2,n_tasks)
    bits_set=np.array([2,4,8]); depth_set=np.array([1,2,3,4])
    acc=[]; lat=[]; bits_used=[]; depth_used=[]; misses=0
    for s,dif in zip(snr,diff):
        if policy=='fixed_light': b,dep=2,2
        elif policy=='fixed_deep': b,dep=8,4
        else:
            best=None
            for b in bits_set:
                rate=.75*np.log2(1+10**(s/10))+1e-3
                comm=.22 + .085*b/rate
                for dep in depth_set:
                    comp=.38+.42*dep
                    L=comm+comp; A=float(_acc_model(b,dep,s,dif))
                    feasible=L<=latency_budget_ms
                    score=(A if feasible else A-2.0*(L-latency_budget_ms)) - .008*b-.01*dep
                    if best is None or score>best[0]: best=(score,b,dep,L,A)
            _,b,dep,_,_=best
        rate=.75*np.log2(1+10**(s/10))+1e-3
        L=.22+.085*b/rate+.38+.42*dep
        A=float(_acc_model(b,dep,s,dif))
        ok=L<=latency_budget_ms; misses+=int(not ok)
        # Late tasks count only local/fallback quality in on-time metric.
        acc.append(A if ok else .5); lat.append(L); bits_used.append(b); depth_used.append(dep)
    return {'policy':policy,'on_time_accuracy':float(np.mean(acc)),'deadline_miss_rate':float(misses/n_tasks),
            'mean_latency_ms':float(np.mean(lat)),'mean_feature_bits':float(np.mean(bits_used)),
            'mean_model_depth':float(np.mean(depth_used))}
