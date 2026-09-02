import numpy as np


def _ridge(X,y,l2=.03):
    d=X.shape[1]
    return np.linalg.solve(X.T@X/len(y)+l2*np.eye(d),X.T@y/len(y))


def _mse(w,X,y): return float(np.mean((X@w-y)**2))


def simulate_clustered_personalization(n_clients=16,dim=10,train_per_client=28,test_per_client=180,
                                       cluster_separation=.8,local_jitter=.25,
                                       cluster_assignment_error=0.0,seed=0):
    """Global vs two-cluster vs local personalization on structured heterogeneity.

    A fraction of clients may be assigned to the wrong server-side cluster to
    expose the cost of imperfect grouping.
    """
    if not 0<=cluster_assignment_error<=.5: raise ValueError('bad assignment error')
    rng=np.random.default_rng(seed+2502)
    base=rng.normal(size=dim); base/=np.linalg.norm(base)+1e-12
    delta=rng.normal(size=dim); delta-=delta.dot(base)*base; delta/=np.linalg.norm(delta)+1e-12
    labels=np.arange(n_clients)%2
    train=[]; test=[]
    for k in range(n_clients):
        sign=-1 if labels[k]==0 else 1
        wk=base+sign*cluster_separation*delta+local_jitter*rng.normal(size=dim)/np.sqrt(dim)
        X=rng.normal(size=(train_per_client,dim)); y=X@wk+.45*rng.normal(size=train_per_client)
        Xt=rng.normal(size=(test_per_client,dim)); yt=Xt@wk+.45*rng.normal(size=test_per_client)
        train.append((X,y)); test.append((Xt,yt))
    Xall=np.concatenate([x for x,_ in train]); yall=np.concatenate([y for _,y in train]); wg=_ridge(Xall,yall)
    observed=labels.copy(); flip=rng.random(n_clients)<cluster_assignment_error; observed[flip]=1-observed[flip]
    wc=[]
    for c in [0,1]:
        ids=np.where(observed==c)[0]
        X=np.concatenate([train[k][0] for k in ids]); y=np.concatenate([train[k][1] for k in ids]); wc.append(_ridge(X,y))
    wl=[_ridge(*train[k]) for k in range(n_clients)]
    lg=np.array([_mse(wg,*test[k]) for k in range(n_clients)])
    lc=np.array([_mse(wc[observed[k]],*test[k]) for k in range(n_clients)])
    ll=np.array([_mse(wl[k],*test[k]) for k in range(n_clients)])
    return {
        'global_mse':float(lg.mean()),'cluster_mse':float(lc.mean()),'local_mse':float(ll.mean()),
        'p90_cluster_mse':float(np.quantile(lc,.9)),
        'assignment_error':float(cluster_assignment_error),
        'cluster_separation':float(cluster_separation),
    }
