import numpy as np


def simulate_failure_domain_replication(n_requests=18000, policy='domain_aware', storage_budget_mb=3200, seed=0, zone_failure_prob=None):
    """AI-model placement with correlated edge failure domains.

    Nodes are grouped into failure domains (e.g. site/rack/power domain). A
    domain-aware policy spreads replicas across domains instead of treating node
    failures as independent. This is a storage/availability abstraction.
    """
    aliases={'criticality':'independent_risk','diversity_risk':'domain_aware'}
    policy=aliases.get(policy,policy)
    if policy not in {'popularity','independent_risk','domain_aware'}:
        raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3203)
    sizes=np.array([100,140,180,230,290,360],float)
    pop=np.array([.28,.23,.18,.14,.10,.07]); pop/=pop.sum()
    critical=np.array([.8,1.0,1.2,2.0,3.8,6.0])
    # 6 nodes, 3 correlated domains. Domain 0 has individually reliable nodes but larger common shock.
    domains=np.array([0,0,1,1,2,2]); node_fail=np.array([.025,.035,.055,.065,.08,.09])
    if zone_failure_prob is None:
        domain_fail=np.array([.10,.035,.02])
    else:
        z=float(zone_failure_prob)
        if not 0 <= z < .5: raise ValueError('invalid zone failure probability')
        domain_fail=np.array([z,z,z])
    if storage_budget_mb < sizes.sum(): raise ValueError('budget too small for one copy/model')
    placements=[[int(np.argmin(node_fail))] for _ in sizes]; used=float(sizes.sum())
    def marginal(m,node):
        nodes=placements[m]
        if node in nodes: return -1e9
        w=pop[m] if policy=='popularity' else pop[m]*critical[m]
        if policy=='domain_aware':
            newdom=int(domains[node] not in domains[nodes]); spread=1+2.5*newdom
        else: spread=1.0
        return w*spread/((node_fail[node]+.02)*sizes[m])
    while True:
        best=None
        for m in range(len(sizes)):
            if used+sizes[m]>storage_budget_mb: continue
            for node in range(len(node_fail)):
                sc=marginal(m,node)
                if best is None or sc>best[0]: best=(sc,m,node)
        if best is None or best[0]<0: break
        _,m,node=best; placements[m].append(node); used+=sizes[m]
    # Vectorized request evaluation keeps the Monte Carlo large enough for the
    # outage tail without making release validation dominated by Python loops.
    req_model=rng.choice(len(sizes),size=n_requests,p=pop)
    dom_down=rng.random((n_requests,3))<domain_fail[None,:]
    node_down=rng.random((n_requests,6))<node_fail[None,:]
    alive_count=np.zeros(n_requests,dtype=int)
    for m,nodes in enumerate(placements):
        idx=np.where(req_model==m)[0]
        if len(idx)==0: continue
        ns=np.asarray(nodes,dtype=int)
        alive=(~dom_down[idx[:,None],domains[ns][None,:]]) & (~node_down[idx[:,None],ns[None,:]])
        alive_count[idx]=alive.sum(axis=1)
    outage_mask=alive_count==0
    weights=critical[req_model]
    lat=18+4/np.maximum(alive_count,1)+rng.exponential(4,n_requests)
    lat[outage_mask]=120.0
    reps=np.array([len(x) for x in placements])
    unique_domains=np.array([len(set(domains[x])) for x in placements])
    return {'policy':policy,'zone_failure_prob':float(domain_fail.mean()),'storage_used_mb':used,'mean_replication_factor':float(reps.mean()),
            'mean_failure_domains_per_model':float(unique_domains.mean()),
            'model_outage_rate':float(outage_mask.mean()),
            'task_weighted_outage_rate':float(weights[outage_mask].sum()/max(weights.sum(),1e-12)),
            'mean_latency_ms':float(np.mean(lat)),'p95_latency_ms':float(np.quantile(lat,.95))}
