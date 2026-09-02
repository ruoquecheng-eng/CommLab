import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad


def _decode_access(n_users,n_slots,rng,mode='irsa',degree_probs=None):
    if n_users==0: return np.empty(0,dtype=int)
    if mode=='orthogonal': return np.arange(n_users,dtype=int)
    if n_slots<1: raise ValueError('n_slots must be positive')
    if mode=='aloha':
        chosen=rng.integers(0,n_slots,size=n_users)
        counts=np.bincount(chosen,minlength=n_slots)
        return np.where(counts[chosen]==1)[0]
    if mode!='irsa': raise ValueError('unknown access mode')
    if degree_probs is None: degree_probs={2:.50,3:.28,8:.22}
    deg=np.array(sorted(degree_probs),int); prob=np.array([degree_probs[d] for d in deg],float); prob/=prob.sum()
    deg=np.minimum(deg,n_slots)
    user_slots=[]; slots=[set() for _ in range(n_slots)]
    for u in range(n_users):
        d=int(rng.choice(deg,p=prob)); ss=rng.choice(n_slots,size=d,replace=False)
        user_slots.append(ss)
        for s in ss: slots[int(s)].add(u)
    unresolved=np.ones(n_users,dtype=bool); decoded=[]
    while True:
        newly=set()
        for members in slots:
            live=[u for u in members if unresolved[u]]
            if len(live)==1: newly.add(live[0])
        if not newly: break
        for u in newly:
            if not unresolved[u]: continue
            unresolved[u]=False; decoded.append(u)
            for s in user_slots[u]: slots[int(s)].discard(u)
    return np.asarray(sorted(decoded),dtype=int)


def simulate_random_access_federated(mode='irsa', n_clients=12, frame_slots=12,
                                     rounds=80, participation_prob=1.0,
                                     heterogeneity=0.8, learning_rate=0.12,
                                     seed=0):
    """Federated linear regression with random-access update delivery.

    Orthogonal access consumes one resource per active client; ALOHA/IRSA use a
    shared frame of ``frame_slots`` resources. Only decoded clients contribute
    to that round's gradient, exposing learning-vs-access-efficiency trade-offs.
    """
    if not 0<participation_prob<=1 or rounds<1: raise ValueError('bad setup')
    clients,w_true=make_federated_linear_problem(n_clients=n_clients,heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+404); w=np.zeros_like(w_true); losses=[global_loss(w,clients)]
    uses=0; fracs=[]; empty=0
    for _ in range(rounds):
        active=np.where(rng.random(n_clients)<participation_prob)[0]
        if mode=='orthogonal':
            decoded_local=np.arange(len(active)); uses+=len(active)
        else:
            decoded_local=_decode_access(len(active),frame_slots,rng,mode=mode); uses+=frame_slots
        decoded=active[decoded_local] if len(decoded_local) else np.empty(0,dtype=int)
        fracs.append(len(decoded)/max(len(active),1))
        if len(decoded)==0:
            empty+=1; losses.append(global_loss(w,clients)); continue
        grads=np.stack([_loss_grad(w,*clients[k])[1] for k in decoded])
        w-=learning_rate*grads.mean(axis=0)
        losses.append(global_loss(w,clients))
    return {
        'mode':mode,'loss_history':np.asarray(losses),'final_loss':float(losses[-1]),
        'parameter_error':float(np.linalg.norm(w-w_true)),
        'channel_uses':int(uses),'mean_decoded_fraction':float(np.mean(fracs)),
        'empty_round_fraction':float(empty/rounds),
        'loss_reduction_per_1000_uses':float((losses[0]-losses[-1])*1000/max(uses,1)),
    }
