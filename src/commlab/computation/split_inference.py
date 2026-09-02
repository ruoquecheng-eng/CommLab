import numpy as np


def simulate_split_inference(dim=16,local_dim=4,n_samples=12000,snr_db=8,
                             confidence_threshold=.7,mode='adaptive',
                             local_compute_ms=1.0,edge_compute_ms=0.6,symbol_time_ms=0.08,seed=0):
    """Gaussian classification with local early inference and wireless edge refinement.

    Local inference uses the first ``local_dim`` coordinates. Edge inference
    uses all coordinates; adaptive mode offloads residual coordinates only when
    local posterior confidence is below a threshold. Channel uses count feature
    scalars and do not model a specific codec/protocol.
    """
    if not (1<=local_dim<dim): raise ValueError('invalid local_dim')
    if mode not in {'local','edge','adaptive'}: raise ValueError('unknown mode')
    rng=np.random.default_rng(seed+2305)
    mu=rng.normal(size=dim); mu/=np.linalg.norm(mu); mu*=1.4
    y=rng.choice([-1.,1.],size=n_samples); X=y[:,None]*mu + rng.normal(size=(n_samples,dim))
    sigma=np.sqrt(10**(-snr_db/10))
    zloc=X[:,:local_dim]@mu[:local_dim]
    # calibrated-ish confidence proxy from local margin
    conf=1/(1+np.exp(-2*np.abs(zloc)))
    local_pred=np.where(zloc>=0,1.,-1.)
    if mode=='local': pred=local_pred; uses=np.zeros(n_samples)
    else:
        need=np.ones(n_samples,bool) if mode=='edge' else conf<confidence_threshold
        Xedge=X.copy(); Xedge[need,local_dim:]+=sigma*rng.normal(size=(need.sum(),dim-local_dim))
        zedge=Xedge@mu; edge_pred=np.where(zedge>=0,1.,-1.)
        pred=local_pred.copy(); pred[need]=edge_pred[need]
        uses=need.astype(float)*(dim-local_dim)
    off=uses>0
    latency=np.full(n_samples,float(local_compute_ms))
    latency[off]+=uses[off]*float(symbol_time_ms)+float(edge_compute_ms)
    return {'mode':mode,'accuracy':float(np.mean(pred==y)),'mean_channel_uses':float(np.mean(uses)),
            'offload_fraction':float(np.mean(off)),'local_accuracy':float(np.mean(local_pred==y)),
            'mean_latency_ms':float(np.mean(latency)),'p95_latency_ms':float(np.quantile(latency,.95))}
