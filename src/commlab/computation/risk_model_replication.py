import numpy as np


def simulate_risk_aware_model_replication(n_requests=12000,policy='risk_aware',storage_budget_mb=1800,seed=0):
    """Replicate edge AI models across failure-prone servers under a storage budget."""
    if policy not in {'popularity','risk_aware','full_redundancy'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3104)
    sizes=np.array([90,120,160,210,260,320,380],float); pop=np.array([.25,.21,.17,.14,.10,.08,.05]); pop/=pop.sum()
    critical=np.array([.8,.9,1.1,1.0,2.8,3.8,7.0]); node_fail=np.array([.045,.10,.22,.38])
    replicas=np.ones(len(sizes),int)
    base_storage=float(sizes.sum())
    if storage_budget_mb < base_storage:
        raise ValueError(f'storage budget must be at least {base_storage:.0f} MB for one copy/model')
    if policy=='full_redundancy': replicas[:]=4
    else:
        used=float(sizes.sum())
        while True:
            candidates=[]
            for m in range(len(sizes)):
                if replicas[m]>=4 or used+sizes[m]>storage_budget_mb: continue
                # marginal outage reduction; risk-aware weights criticality and model popularity.
                fail_product=np.prod(np.sort(node_fail)[:replicas[m]])
                w=pop[m] if policy=='popularity' else pop[m]*critical[m]
                candidates.append((w*fail_product/sizes[m],m))
            if not candidates: break
            _,m=max(candidates); replicas[m]+=1; used+=sizes[m]
    # Assign replicas to most reliable nodes for this simple baseline.
    fail_sorted=np.sort(node_fail); lat=[]; outage=0; utility=[]; outage_weight=0.0; total_weight=0.0
    for _ in range(n_requests):
        m=int(rng.choice(len(sizes),p=pop)); r=replicas[m]
        alive=[rng.random()>fail_sorted[j] for j in range(min(r,4))]
        total_weight += critical[m]
        if not any(alive):
            outage+=1; outage_weight += critical[m]; L=120.; u=0.
        else:
            # More replicas slightly reduce routing distance/queue tail.
            L=18+8/r+rng.exponential(5); u=critical[m]
        lat.append(L); utility.append(u)
    a=np.asarray(lat)
    return {'policy':policy,'mean_latency_ms':float(a.mean()),'p95_latency_ms':float(np.quantile(a,.95)),
            'model_outage_rate':float(outage/n_requests),'task_weighted_outage_rate':float(outage_weight/max(total_weight,1e-12)),'task_weighted_utility':float(np.mean(utility)),
            'storage_used_mb':float(np.dot(replicas,sizes)),'mean_replication_factor':float(np.mean(replicas)),
            'replication_factors':replicas}
