import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad
from .robust_federated import aggregate_gradients


def simulate_resilient_async_federated(strategy='naive_mean', n_clients=15, dim=10, rounds=100,
                                        batch_clients=7, max_delay=8, delay_mean=3.0,
                                        byzantine_fraction=.13, attack_scale=5.0,
                                        learning_rate=.08, heterogeneity=.8, seed=0):
    """Asynchronous FL with stale and Byzantine updates in one transparent baseline.

    Strategies:
    - ``naive_mean``: stale updates are averaged directly.
    - ``median``: coordinate-wise median, no explicit staleness handling.
    - ``stale_robust``: coordinate median reference + cosine conflict rejection +
      exponential staleness weighting before averaging accepted updates.

    This is an educational robust-asynchronous baseline, not a claim of optimal
    Byzantine detection.
    """
    if strategy not in {'naive_mean','median','stale_robust'}:
        raise ValueError('unknown strategy')
    if not (0 <= byzantine_fraction < .5) or batch_clients < 3:
        raise ValueError('invalid setup')
    clients, wtrue = make_federated_linear_problem(
        n_clients=n_clients, dim=dim, heterogeneity=heterogeneity, seed=seed)
    rng=np.random.default_rng(seed+2501)
    w=np.zeros(dim); hist=[w.copy()]; losses=[global_loss(w,clients)]
    nb=int(round(n_clients*byzantine_fraction)); bad=set(range(nb))
    accepted=[]; mean_delay=[]
    tau=max(delay_mean,1.0)
    for _ in range(rounds):
        ids=rng.choice(n_clients,size=min(batch_clients,n_clients),replace=False)
        G=[]; delays=[]
        for k in ids:
            d=min(int(rng.poisson(delay_mean)),max_delay,len(hist)-1)
            ws=hist[-1-d]; g=_loss_grad(ws,*clients[int(k)])[1]
            if int(k) in bad:
                g=-attack_scale*g + .05*rng.normal(size=dim)
            G.append(g); delays.append(d)
        G=np.asarray(G); delays=np.asarray(delays)
        if strategy=='naive_mean':
            g=G.mean(axis=0); acc=np.ones(len(G),bool)
        elif strategy=='median':
            g=np.median(G,axis=0); acc=np.ones(len(G),bool)
        else:
            ref=np.median(G,axis=0); nr=np.linalg.norm(ref)+1e-12
            cos=(G@ref)/((np.linalg.norm(G,axis=1)+1e-12)*nr)
            # Reject strongly conflicting vectors. Stale-but-consistent gradients survive.
            acc=cos>-0.05
            if not np.any(acc):
                acc[np.argmax(cos)]=True
            ww=np.exp(-delays[acc]/tau)
            g=np.average(G[acc],axis=0,weights=ww)
        gn=np.linalg.norm(g)
        if gn>30: g*=30/gn
        w-=learning_rate*g; hist.append(w.copy()); losses.append(global_loss(w,clients))
        accepted.append(float(np.mean(acc))); mean_delay.append(float(np.mean(delays[acc])))
    return {
        'strategy':strategy,'final_loss':float(losses[-1]),
        'parameter_error':float(np.linalg.norm(w-wtrue)),
        'mean_accept_fraction':float(np.mean(accepted)),
        'mean_accepted_delay':float(np.mean(mean_delay)),
        'loss_history':np.asarray(losses),
        'byzantine_clients':nb,
    }
