import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad


def aggregate_gradients(grads, method='mean', trim_fraction=.2):
    G=np.asarray(grads,float)
    if G.ndim!=2: raise ValueError('grads must be 2D')
    if method=='mean': return G.mean(axis=0)
    if method=='median': return np.median(G,axis=0)
    if method=='trimmed_mean':
        n=G.shape[0]; q=int(np.floor(trim_fraction*n))
        if q*2>=n: raise ValueError('trim_fraction too large')
        S=np.sort(G,axis=0)
        return S[q:n-q].mean(axis=0) if q else S.mean(axis=0)
    raise ValueError('unknown aggregation method')


def simulate_byzantine_federated(method='mean', n_clients=15, byzantine_fraction=.2,
                                  attack_scale=5.0, rounds=80, dim=10,
                                  learning_rate=.1, heterogeneity=.8, seed=0):
    """Synchronous FL with a transparent sign-flip/scaling attack baseline."""
    clients,wtrue=make_federated_linear_problem(n_clients=n_clients,dim=dim,heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+2302); w=np.zeros(dim); losses=[global_loss(w,clients)]
    nb=int(round(n_clients*byzantine_fraction)); bad=np.arange(nb)
    for _ in range(rounds):
        G=np.stack([_loss_grad(w,*c)[1] for c in clients])
        if nb:
            # Fixed malicious identities, randomized small jitter prevents an unrealistically identical attack vector.
            G[bad]=-attack_scale*G[bad] + .05*rng.normal(size=G[bad].shape)
        g=aggregate_gradients(G,method=method)
        gn=np.linalg.norm(g)
        if gn>40: g*=40/gn
        w-=learning_rate*g; losses.append(global_loss(w,clients))
    return {'method':method,'final_loss':float(losses[-1]),'loss_history':np.asarray(losses),
            'parameter_error':float(np.linalg.norm(w-wtrue)),'byzantine_clients':nb}
