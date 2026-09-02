import numpy as np


def make_federated_linear_problem(n_clients=12, samples_per_client=80, dim=12,
                                  heterogeneity=0.8, noise_std=0.2, seed=0):
    if n_clients < 2 or samples_per_client < 4 or dim < 1:
        raise ValueError('invalid federated problem size')
    rng = np.random.default_rng(seed)
    w_true = rng.normal(size=dim)
    w_true /= np.linalg.norm(w_true) + 1e-12
    clients=[]
    for k in range(n_clients):
        shift = heterogeneity * rng.normal(size=dim) / np.sqrt(dim)
        X = rng.normal(size=(samples_per_client, dim)) + shift
        y = X @ w_true + noise_std*rng.normal(size=samples_per_client)
        clients.append((X,y))
    return clients, w_true


def _loss_grad(w, X, y, l2=1e-3):
    r=X@w-y
    loss=.5*np.mean(r*r)+.5*l2*np.dot(w,w)
    grad=X.T@r/len(y)+l2*w
    return float(loss), grad


def global_loss(w, clients, l2=1e-3):
    return float(np.mean([_loss_grad(w,X,y,l2)[0] for X,y in clients]))


def _aircomp_gradient(grads, h, snr_db, mode, threshold, rng, reference_scale=None):
    """Return an analog aggregate gradient and communication channel uses."""
    K,d=grads.shape
    noise_var=1.0/(10**(snr_db/10))
    eps=1e-12
    if mode=='ideal':
        return grads.mean(axis=0), 0, 1.0
    if mode=='orthogonal':
        # Normalize each gradient by a shared RMS scale, transmit separately,
        # equalize each client, then average. This isolates OTA noise cost.
        scale=max(float(reference_scale if reference_scale is not None else np.sqrt(np.mean(grads*grads))),1e-8)
        n=(rng.normal(size=(K,d))+1j*rng.normal(size=(K,d)))*np.sqrt(noise_var/2)
        y=h[:,None]*(grads/scale)+n
        ghat=np.real(y/(h[:,None]+eps))*scale
        return ghat.mean(axis=0), K, 1.0
    if mode=='full_inversion':
        scale=max(float(reference_scale if reference_scale is not None else np.sqrt(np.mean(grads*grads))),1e-8)
        a=max(float(np.min(np.abs(h))),1e-5)
        n=(rng.normal(size=d)+1j*rng.normal(size=d))*np.sqrt(noise_var/2)
        y=a*np.sum(grads/scale,axis=0)+n
        return np.real(y)/(a*K)*scale, 1, 1.0
    if mode=='truncated':
        active=np.abs(h)>=threshold
        ka=int(active.sum())
        if ka==0:
            return np.zeros(d),1,0.0
        scale=max(float(reference_scale if reference_scale is not None else np.sqrt(np.mean(grads[active]*grads[active]))),1e-8)
        a=float(threshold)
        n=(rng.normal(size=d)+1j*rng.normal(size=d))*np.sqrt(noise_var/2)
        y=a*np.sum(grads[active]/scale,axis=0)+n
        # Active-client mean: channel efficiency improves, but client dropout
        # introduces a genuine optimization bias under heterogeneous data.
        return np.real(y)/(a*ka)*scale,1,ka/K
    raise ValueError('unknown aggregation mode')


def simulate_federated_aircomp(n_clients=12, samples_per_client=80, dim=12,
                               rounds=80, learning_rate=0.12, snr_db=15.0,
                               mode='full_inversion', inversion_threshold=.35,
                               heterogeneity=.8, fixed_channel=None, seed=0):
    """Federated linear regression with noisy analog gradient aggregation.

    This intentionally small convex problem makes communication/optimization
    coupling transparent. It is not a neural-network FL benchmark.
    """
    clients,w_true=make_federated_linear_problem(n_clients,samples_per_client,dim,
                                                  heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+12345)
    w=np.zeros(dim)
    losses=[global_loss(w,clients)]
    uses=0; active=[]; agg_err=[]
    reference_scale=None
    for _ in range(rounds):
        grads=np.stack([_loss_grad(w,X,y)[1] for X,y in clients])
        if reference_scale is None:
            reference_scale=float(np.sqrt(np.mean(grads*grads)))
        exact=grads.mean(axis=0)
        if fixed_channel is None:
            h=(rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)
        else:
            h=np.asarray(fixed_channel,dtype=complex)
            if h.size!=n_clients: raise ValueError('fixed_channel length mismatch')
        ghat,u,af=_aircomp_gradient(grads,h,snr_db,mode,inversion_threshold,rng,reference_scale)
        uses+=u; active.append(af)
        agg_err.append(float(np.mean((ghat-exact)**2)))
        # Guard only against rare extreme deep-fade inversion events; the clip
        # threshold is deliberately loose and reported as a limitation.
        gn=np.linalg.norm(ghat)
        if gn>20:
            ghat=ghat*(20/gn)
        w-=learning_rate*ghat
        losses.append(global_loss(w,clients))
    return {
        'loss_history':np.asarray(losses),
        'final_loss':float(losses[-1]),
        'parameter_error':float(np.linalg.norm(w-w_true)),
        'channel_uses':int(uses),
        'mean_active_fraction':float(np.mean(active)) if active else 1.0,
        'mean_aggregation_mse':float(np.mean(agg_err)) if agg_err else 0.0,
        'mode':mode,'snr_db':float(snr_db),
    }
