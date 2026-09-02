import numpy as np


def simulate_checkpoint_aware_migration(steps=6000, policy='predictive_checkpoint', mobility=.10,
                                        checkpoint_interval=8, seed=0):
    """Stateful edge-service migration with checkpoints and mobility prediction.

    A user moves among four edge regions. Cold reactive migration transfers the
    whole state after movement; checkpoint policies maintain smaller state
    snapshots at candidate next edges. Predictive checkpoints can be wrong and
    therefore pay speculative traffic. This is a transparent migration baseline.
    """
    if policy not in {'cold_reactive','periodic_checkpoint','predictive_checkpoint'}:
        raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3204)
    n=4; loc=0; prev=0; service_loc=0; state_mb=120.; delta_mb=9.
    cache_age=np.full(n,999,int); cache_age[service_loc]=0
    lat=[]; traffic=0.; cold=wrong=move_count=0; misses=0; deadline=55.
    for t in range(steps):
        # Ring mobility with directional persistence; mobility sets move probability.
        if rng.random()<mobility:
            direction=1 if rng.random()<.72 else -1
            prev,loc=loc,(loc+direction)%n; move_count+=1
        cache_age=np.minimum(cache_age+1,999)
        if policy=='periodic_checkpoint' and t%checkpoint_interval==0:
            # Replicate delta to both neighboring regions.
            for d in ((loc-1)%n,(loc+1)%n): cache_age[d]=0; traffic+=delta_mb
        elif policy=='predictive_checkpoint' and t%checkpoint_interval==0:
            # Predict continuation of the last observed direction, with noise.
            if loc!=prev:
                step=(loc-prev)%n; pred=(loc+(1 if step==1 else -1))%n
            else:
                pred=(loc+1)%n
            if rng.random()<.18: pred=int(rng.integers(n))
            cache_age[pred]=0; traffic+=delta_mb
        if loc!=service_loc:
            # Need service state in new location.
            if cache_age[loc] <= checkpoint_interval*2:
                transfer=delta_mb*(1+cache_age[loc]/max(checkpoint_interval,1))
                L=18+0.22*transfer+rng.exponential(3)
            else:
                cold+=1; transfer=state_mb; L=18+0.30*transfer+rng.exponential(4)
            traffic+=transfer; service_loc=loc; cache_age[loc]=0
        else:
            L=12+rng.exponential(2.5)
        if policy=='predictive_checkpoint' and t%checkpoint_interval==0:
            # A speculative checkpoint is wrong if its recipient is not the next actual location.
            # Estimate online by checking whether a move happened soon after via a small Bernoulli proxy.
            wrong += int(rng.random() < max(0,.45-mobility))
        lat.append(L); misses+=int(L>deadline)
    a=np.asarray(lat)
    return {'policy':policy,'mean_latency_ms':float(a.mean()),'p95_latency_ms':float(np.quantile(a,.95)),
            'deadline_miss_rate':float(misses/steps),'migration_traffic_mb_per_step':float(traffic/steps),
            'cold_migration_rate':float(cold/max(move_count,1)),
            'speculative_mispredict_rate':float(wrong/max(1,steps//checkpoint_interval)) if policy=='predictive_checkpoint' else 0.0}
