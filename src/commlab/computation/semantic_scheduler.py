import numpy as np


def simulate_semantic_resource_scheduling(n_users=16,slots=300,resources_per_slot=8,
                                          strategy='channel',snr_mean_db=6,
                                          urgency_weight=.7,seed=0):
    """Queueing baseline where semantic packets have heterogeneous task value.

    A packet has importance, age/urgency, and resource cost. Successful task
    utility equals importance if delivered before expiry. This is a transparent
    scheduler baseline, not a learned semantic codec.
    """
    if strategy not in {'channel','importance','value_per_resource','urgency_aware'}: raise ValueError('unknown strategy')
    rng=np.random.default_rng(seed+2304); queues=[[] for _ in range(n_users)]
    utility=0.; delivered=expired=uses=0; ages=[]
    for t in range(slots):
        for k in range(n_users):
            if rng.random()<.22:
                imp=float(rng.lognormal(mean=0,sigma=.7)); cost=int(rng.integers(1,4)); ttl=int(rng.integers(3,12))
                queues[k].append([imp,cost,ttl,t])
        # expire
        for q in queues:
            keep=[]
            for p in q:
                if t-p[3]>=p[2]: expired+=1
                else: keep.append(p)
            q[:]=keep
        snr_db=snr_mean_db + 5*rng.normal(size=n_users); success=1/(1+np.exp(-(snr_db-2)/2))
        candidates=[]
        for k,q in enumerate(queues):
            if not q: continue
            imp,cost,ttl,arr=q[0]; age=t-arr; slack=max(ttl-age,1)
            if strategy=='channel': score=success[k]
            elif strategy=='importance': score=imp
            elif strategy=='value_per_resource': score=imp*success[k]/cost
            else: score=imp*success[k]*(1+urgency_weight/slack)/cost
            candidates.append((score,k))
        budget=resources_per_slot
        for _,k in sorted(candidates,reverse=True):
            if not queues[k]: continue
            imp,cost,ttl,arr=queues[k][0]
            if cost>budget: continue
            budget-=cost; uses+=cost; p=success[k]
            if rng.random()<p:
                queues[k].pop(0); delivered+=1; utility+=imp; ages.append(t-arr+1)
    backlog=sum(len(q) for q in queues)
    return {'strategy':strategy,'task_utility':float(utility/slots),'delivered':delivered,'expired':expired,
            'resource_utilization':float(uses/(slots*resources_per_slot)),
            'mean_delivery_age':float(np.mean(ages) if ages else np.nan),'final_backlog':backlog}
