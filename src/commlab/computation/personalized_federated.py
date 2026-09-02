import numpy as np


def _ridge_fit(X,y,l2=1e-2):
    d=X.shape[1]
    return np.linalg.solve(X.T@X/len(y)+l2*np.eye(d), X.T@y/len(y))


def _mse(w,X,y):
    return float(np.mean((X@w-y)**2))


def simulate_personalized_federated(n_clients=12, train_per_client=24, test_per_client=200,
                                    dim=10, heterogeneity=.8, personalization=.35,
                                    l2=2e-2, seed=0):
    """Bias-variance baseline for global-vs-personalized federated models.

    Each client has a shifted local optimum. A pooled ridge model is the global
    model, while a client-local ridge estimate is blended with it. Small local
    datasets intentionally make full personalization noisy, producing a genuine
    interior personalization optimum for moderate heterogeneity.
    """
    if not 0 <= personalization <= 1 or n_clients < 2 or train_per_client < 4:
        raise ValueError('invalid personalized FL setup')
    rng=np.random.default_rng(seed)
    w0=rng.normal(size=dim); w0/=np.linalg.norm(w0)+1e-12
    dirs=rng.normal(size=(n_clients,dim)); dirs/=np.linalg.norm(dirs,axis=1,keepdims=True)+1e-12
    train=[]; test=[]; true=[]
    for k in range(n_clients):
        wk=w0+heterogeneity*dirs[k]; true.append(wk)
        X=rng.normal(size=(train_per_client,dim)); y=X@wk+.45*rng.normal(size=train_per_client)
        Xt=rng.normal(size=(test_per_client,dim)); yt=Xt@wk+.45*rng.normal(size=test_per_client)
        train.append((X,y)); test.append((Xt,yt))
    X=np.concatenate([a for a,_ in train]); y=np.concatenate([b for _,b in train])
    wg=_ridge_fit(X,y,l2)
    locals_=[_ridge_fit(*train[k],l2=l2) for k in range(n_clients)]
    pers=[(1-personalization)*wg+personalization*locals_[k] for k in range(n_clients)]
    global_losses=np.array([_mse(wg,*test[k]) for k in range(n_clients)])
    local_losses=np.array([_mse(locals_[k],*test[k]) for k in range(n_clients)])
    pers_losses=np.array([_mse(pers[k],*test[k]) for k in range(n_clients)])
    return {
        'personalization':float(personalization),
        'mean_global_test_mse':float(global_losses.mean()),
        'mean_local_test_mse':float(local_losses.mean()),
        'mean_personalized_test_mse':float(pers_losses.mean()),
        'p90_personalized_test_mse':float(np.quantile(pers_losses,.9)),
        'personalization_drift':float(np.mean([np.linalg.norm(w-wg) for w in pers])),
        'heterogeneity':float(heterogeneity),
    }
