import numpy as np


def simulate_joint_cache_offload(n_requests=5000,n_edges=3,n_models=8,cache_capacity_mb=520.,policy='joint',seed=0):
    """Slow-timescale AI-model caching with fast inference offloading.

    Model popularity drifts by phase. Edge caches are refreshed periodically and
    requests choose an edge using radio delay, queueing, and model-miss cost. The
    joint policy values cached models by local demand * latency saving per MB and
    offloads with a queue/miss-aware score. This is a transparent heuristic baseline.
    """
    if policy not in {'nearest','cache_first','joint'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3004)
    size=rng.uniform(70,190,n_models); cloud_extra=rng.uniform(55,105,n_models)
    base_radio=np.array([[7,18,29],[19,7,18],[30,18,7]],float)[:n_edges,:n_edges]
    queues=np.zeros(n_edges); caches=[set() for _ in range(n_edges)]; last=np.full((n_edges,n_models),-1,int)
    recent=np.ones((n_edges,n_models))*1e-3
    phase_probs=[]
    for ph in range(3):
        p=np.ones(n_models); p[(2*ph)%n_models]=7; p[(2*ph+1)%n_models]=5; p/=p.sum(); phase_probs.append(p)
    lat=[]; backhaul=0.; hits=0; cloud=0; off=np.zeros(n_edges,int)
    def refill(e,t):
        nonlocal backhaul
        if policy=='nearest': return
        if policy=='cache_first': val=recent[e]
        else: val=recent[e]*cloud_extra/size
        order=np.argsort(-val); used=0.; new=set()
        for m in order:
            if used+size[m]<=cache_capacity_mb: new.add(int(m)); used+=size[m]
        added=new-caches[e]; backhaul+=float(np.sum(size[list(added)])) if added else 0.; caches[e]=new
    # Warm start based on neutral value.
    for e in range(n_edges): recent[e]=rng.uniform(.8,1.2,n_models); refill(e,0)
    for t in range(n_requests):
        if t and t%180==0:
            for e in range(n_edges): refill(e,t)
            recent*=.45
        queues=np.maximum(0,queues-rng.uniform(.7,1.2,n_edges))
        user=int(rng.integers(0,n_edges)); ph=min(2,3*t//n_requests); m=int(rng.choice(n_models,p=phase_probs[ph]))
        radio=base_radio[user]+rng.uniform(-1.5,1.5,n_edges)
        miss=np.array([0 if m in caches[e] else cloud_extra[m] for e in range(n_edges)])
        if policy=='nearest': e=int(np.argmin(radio))
        elif policy=='cache_first':
            candidates=[e for e in range(n_edges) if m in caches[e]]; e=min(candidates,key=lambda z:radio[z]+8*queues[z]) if candidates else int(np.argmin(radio+8*queues+miss))
        else: e=int(np.argmin(radio+8*queues+miss+2.0*queues**2))
        off[e]+=1; recent[e,m]+=1
        ishit=m in caches[e]; hits+=int(ishit)
        if not ishit:
            backhaul+=size[m]; cloud+=1
            # install on demand using least locally demanded resident model if it fits
            while sum(size[list(caches[e])]) + size[m] > cache_capacity_mb and caches[e]:
                ev=min(caches[e],key=lambda x:recent[e,x]); caches[e].remove(ev)
            if size[m]<=cache_capacity_mb: caches[e].add(m)
        work=0.7+size[m]/180; qdelay=8*queues[e]; queues[e]+=work
        lat.append(float(radio[e]+qdelay+8*work+(0 if ishit else cloud_extra[m])))
    a=np.asarray(lat)
    return {'policy':policy,'mean_latency_ms':float(a.mean()),'p95_latency_ms':float(np.quantile(a,.95)),
            'cache_hit_rate':float(hits/n_requests),'backhaul_mb_per_request':float(backhaul/n_requests),
            'cloud_miss_fraction':float(cloud/n_requests),'offload_jain':float(off.sum()**2/(n_edges*np.sum(off.astype(float)**2)+1e-12))}
