import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad


def _decode_degrees(degrees,n_slots,rng):
    n=len(degrees); user_slots=[]; slots=[set() for _ in range(n_slots)]
    for u,d in enumerate(degrees):
        d=int(np.clip(d,1,n_slots)); ss=rng.choice(n_slots,size=d,replace=False); user_slots.append(ss)
        for s in ss: slots[int(s)].add(u)
    unresolved=np.ones(n,dtype=bool); decoded=[]
    while True:
        new=set()
        for members in slots:
            live=[u for u in members if unresolved[u]]
            if len(live)==1:new.add(live[0])
        if not new: break
        for u in new:
            if not unresolved[u]: continue
            unresolved[u]=False; decoded.append(u)
            for s in user_slots[u]: slots[int(s)].discard(u)
    return np.asarray(sorted(decoded),int)


def simulate_importance_aware_random_access_fl(n_clients=16,frame_slots=20,rounds=80,
                                               participation_prob=.85,heterogeneity=.9,
                                               learning_rate=.1,mode='uniform',seed=0):
    """IRSA-style FL where repetition degree can depend on update importance.

    ``uniform`` uses degree 3 for every active client.  ``importance`` maps
    gradient norm ranks to degrees 2/3/5, protecting large updates at the cost
    of extra replicas and collision pressure.  This is a transparent MAC/FL
    co-design heuristic, not an optimized IRSA degree distribution.
    """
    if mode not in ('uniform','importance') or frame_slots<2: raise ValueError('bad access mode')
    clients,w_true=make_federated_linear_problem(n_clients=n_clients,dim=20,
                                                  heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+9911); w=np.zeros_like(w_true); losses=[global_loss(w,clients)]
    dec_frac=[]; mass_frac=[]; replicas=[]; empty=0
    for _ in range(rounds):
        active=np.where(rng.random(n_clients)<participation_prob)[0]
        if len(active)==0:
            empty+=1; losses.append(global_loss(w,clients)); continue
        grads=np.stack([_loss_grad(w,*clients[k])[1] for k in active])
        imp=np.linalg.norm(grads,axis=1)+1e-12
        if mode=='uniform':
            deg=np.full(len(active),3,int)
        else:
            ranks=np.argsort(np.argsort(imp))/max(len(active)-1,1)
            deg=np.where(ranks>=2/3,4,np.where(ranks>=1/3,3,2)).astype(int)
        decoded_local=_decode_degrees(deg,frame_slots,rng)
        replicas.append(float(np.mean(deg)))
        dec_frac.append(len(decoded_local)/len(active))
        mass_frac.append(float(imp[decoded_local].sum()/imp.sum()) if len(decoded_local) else 0.0)
        if len(decoded_local)==0:
            empty+=1; losses.append(global_loss(w,clients)); continue
        w-=learning_rate*np.mean(grads[decoded_local],axis=0)
        losses.append(global_loss(w,clients))
    return {
        'mode':mode,'final_loss':float(losses[-1]),'loss_history':np.asarray(losses),
        'parameter_error':float(np.linalg.norm(w-w_true)),
        'mean_decoded_fraction':float(np.mean(dec_frac)) if dec_frac else 0.0,
        'mean_decoded_gradient_mass':float(np.mean(mass_frac)) if mass_frac else 0.0,
        'mean_repetition_degree':float(np.mean(replicas)) if replicas else 0.0,
        'empty_round_fraction':float(empty/rounds),
        'channel_uses':int(rounds*frame_slots),
    }
