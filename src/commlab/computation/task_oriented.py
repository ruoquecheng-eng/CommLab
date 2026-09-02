import numpy as np


def simulate_task_oriented_classification(dim=16, n_samples=10000, separation=1.8,
                                           snr_db=5.0, seed=0):
    """Toy task-oriented communication baseline for binary classification.

    Two equally likely Gaussian classes have means +/-mu and identity covariance.
    The scalar projection mu^T x is a sufficient statistic for the Bayes task,
    so transmitting that statistic can preserve classification utility using one
    channel use, while destroying source reconstruction fidelity. This is an
    analytical toy baseline, not a learned semantic codec.
    """
    if dim<2 or n_samples<100 or separation<=0: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed)
    mu=np.zeros(dim); mu[0]=separation
    y=rng.integers(0,2,size=n_samples); s=2*y-1
    X=s[:,None]*mu[None,:]+rng.normal(size=(n_samples,dim))
    nv=1/(10**(snr_db/10))
    # Raw feature transport: normalize average per-coordinate power then transmit
    # every feature independently. Receiver uses the same sufficient projection.
    scale=np.sqrt(np.mean(X*X))
    nr=rng.normal(scale=np.sqrt(nv),size=X.shape)
    Xr=X/scale+nr; Xr*=scale
    pred_raw=(Xr@mu>=0).astype(int)
    acc_raw=float(np.mean(pred_raw==y))
    recon_raw=float(np.mean((Xr-X)**2))
    # Task-oriented scalar transmission.
    z=X@mu
    zscale=max(float(np.sqrt(np.mean(z*z))),1e-8)
    zrx=(z/zscale+rng.normal(scale=np.sqrt(nv),size=n_samples))*zscale
    pred_task=(zrx>=0).astype(int)
    acc_task=float(np.mean(pred_task==y))
    # Best rank-one source reconstruction from the scalar statistic. This is
    # intentionally poor for nuisance dimensions, showing task/source divergence.
    Xhat=np.outer(zrx/(np.dot(mu,mu)+1e-12),mu)
    recon_task=float(np.mean((Xhat-X)**2))
    return {'raw_accuracy':acc_raw,'task_accuracy':acc_task,
            'raw_reconstruction_mse':recon_raw,
            'task_reconstruction_mse':recon_task,
            'raw_channel_uses':int(dim),'task_channel_uses':1,
            'compression_ratio':float(dim),'snr_db':float(snr_db)}
