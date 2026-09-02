import numpy as np


def _ridge(X,y,l2=1e-2):
    return np.linalg.solve(X.T@X+l2*np.eye(X.shape[1]),X.T@y)


def simulate_federated_distillation(n_clients=10,dim=24,intrinsic_dim=6,
                                    samples_per_client=80,public_probes=12,
                                    heterogeneity=.45,snr_db=20.0,n_test=10000,seed=0):
    """Toy federated knowledge-distillation communication baseline.

    Clients fit local linear teachers. Model averaging uploads ``dim`` scalars
    per client. Distillation uploads teacher logits on a shared public probe set
    and fits a server student. The data live mostly in a low-dimensional latent
    subspace so a modest probe set can preserve task accuracy.
    """
    if public_probes<2 or intrinsic_dim>dim: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed)
    U,_=np.linalg.qr(rng.normal(size=(dim,intrinsic_dim)))
    a=rng.normal(size=intrinsic_dim); a/=np.linalg.norm(a)+1e-12
    wtrue=U@a
    teachers=[]
    for _ in range(n_clients):
        z=rng.normal(size=(samples_per_client,intrinsic_dim)); X=z@U.T+.08*rng.normal(size=(samples_per_client,dim))
        wk=wtrue+heterogeneity*(U@rng.normal(size=intrinsic_dim))/np.sqrt(intrinsic_dim)
        y=X@wk+.25*rng.normal(size=samples_per_client)
        teachers.append(_ridge(X,y))
    wavg=np.mean(teachers,axis=0)
    zp=rng.normal(size=(public_probes,intrinsic_dim)); Xp=zp@U.T+.02*rng.normal(size=(public_probes,dim))
    logits=np.stack([Xp@w for w in teachers])
    nv=10**(-snr_db/10)
    noisy=logits+np.sqrt(nv)*rng.normal(size=logits.shape)
    target=noisy.mean(axis=0)
    wstu=_ridge(Xp,target,l2=.08)
    zt=rng.normal(size=(n_test,intrinsic_dim)); Xt=zt@U.T+.08*rng.normal(size=(n_test,dim)); yt=np.sign(Xt@wtrue)
    def acc(w): return float(np.mean(np.sign(Xt@w)==yt))
    return {'model_average_accuracy':acc(wavg),'distilled_accuracy':acc(wstu),
            'model_upload_scalars':int(n_clients*dim),'distill_upload_scalars':int(n_clients*public_probes),
            'compression_ratio':float(dim/public_probes),'public_probes':int(public_probes)}
