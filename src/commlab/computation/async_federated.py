import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad


def _client_hessian(X, l2=1e-3):
    return X.T @ X / len(X) + l2*np.eye(X.shape[1])


def simulate_asynchronous_federated(strategy='naive', n_clients=12, dim=10, rounds=120,
                                     max_delay=8, delay_mean=3.0, learning_rate=.08,
                                     heterogeneity=1.0, seed=0):
    """Transparent asynchronous FL on convex ridge regression.

    Each client gradient is evaluated on a delayed server model. ``decay`` uses
    exp(-delay/tau) weighting. ``quadratic_corrected`` transports a stale
    gradient to the current model using the exact local Hessian; this is exact
    only for this quadratic baseline and is not presented as a general NN method.
    """
    if strategy not in {'naive','decay','quadratic_corrected'}: raise ValueError('unknown strategy')
    if max_delay < 0 or delay_mean < 0: raise ValueError('invalid delay')
    clients,wtrue=make_federated_linear_problem(n_clients=n_clients,dim=dim,heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+2301); w=np.zeros(dim); hist=[w.copy()]; losses=[global_loss(w,clients)]
    delays=[]; conflicts=[]
    tau=max(delay_mean,1.0)
    H=[_client_hessian(X) for X,_ in clients]
    for t in range(rounds):
        k=int(rng.integers(n_clients))
        d=min(int(rng.poisson(delay_mean)), max_delay, len(hist)-1)
        ws=hist[-1-d]
        _,gs=_loss_grad(ws,*clients[k]); _,gc=_loss_grad(w,*clients[k])
        conflicts.append(float(np.dot(gs,gc)/(np.linalg.norm(gs)*np.linalg.norm(gc)+1e-12)))
        if strategy=='naive': g=gs
        elif strategy=='decay': g=np.exp(-d/tau)*gs
        else: g=gs + H[k]@(w-ws)
        gn=np.linalg.norm(g)
        if gn>30: g*=30/gn
        w=w-learning_rate*g
        hist.append(w.copy()); losses.append(global_loss(w,clients)); delays.append(d)
    return {'strategy':strategy,'loss_history':np.asarray(losses),'final_loss':float(losses[-1]),
            'parameter_error':float(np.linalg.norm(w-wtrue)),'mean_delay':float(np.mean(delays) if delays else 0),
            'mean_stale_current_cosine':float(np.mean(conflicts) if conflicts else 1.0)}
