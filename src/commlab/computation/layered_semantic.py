import numpy as np


def simulate_layered_multitask_semantic(dim=16,n_samples=12000,task_angle_deg=60,
                                        snr_db=10,confidence_threshold=.55,seed=0):
    """Progressive two-layer task-oriented communication baseline.

    A rank-one common semantic layer is sent first.  A second orthogonal layer
    is transmitted only when the base-layer task margins are insufficient.
    This creates a variable-length accuracy-vs-channel-use trade-off without a
    learned neural encoder.
    """
    if dim<2 or n_samples<200 or not 0<=task_angle_deg<=90 or confidence_threshold<0:
        raise ValueError('bad layered-semantic setup')
    rng=np.random.default_rng(seed); th=np.deg2rad(task_angle_deg)
    mu1=np.zeros(dim); mu1[0]=1
    mu2=np.zeros(dim); mu2[0]=np.cos(th); mu2[1]=np.sin(th)
    X=rng.normal(size=(n_samples,dim)); y1=X@mu1>=0; y2=X@mu2>=0
    S=np.outer(mu1,mu1)+np.outer(mu2,mu2)
    vals,V=np.linalg.eigh(S); Q=V[:,np.argsort(vals)[::-1][:2]]
    if np.dot(Q[:,0],mu1)<0: Q[:,0]*=-1
    nv=1/(10**(snr_db/10))
    Z=X@Q; scale=max(float(np.sqrt(np.mean(Z*Z))),1e-8)
    Zr=Z/scale+rng.normal(scale=np.sqrt(nv),size=Z.shape)
    Zr*=scale
    # Base reconstruction and confidence in both task scores.
    xb=Zr[:,0,None]*Q[:,0][None,:]
    s1b=xb@mu1; s2b=xb@mu2
    base_acc=.5*(np.mean((s1b>=0)==y1)+np.mean((s2b>=0)==y2))
    # Full two-layer reconstruction.
    xf=Zr@Q.T; s1f=xf@mu1; s2f=xf@mu2
    full_acc=.5*(np.mean((s1f>=0)==y1)+np.mean((s2f>=0)==y2))
    # Margin is normalized by the task coefficient on the base direction.
    denom=max(scale,1e-8)
    margin=np.minimum(np.abs(s1b),np.abs(s2b))/denom
    enhance=margin<confidence_threshold
    s1=s1b.copy(); s2=s2b.copy(); s1[enhance]=s1f[enhance]; s2[enhance]=s2f[enhance]
    adaptive_acc=.5*(np.mean((s1>=0)==y1)+np.mean((s2>=0)==y2))
    return {
        'task_angle_deg':float(task_angle_deg),'snr_db':float(snr_db),
        'base_accuracy':float(base_acc),'base_uses':1.0,
        'full_accuracy':float(full_acc),'full_uses':2.0,
        'adaptive_accuracy':float(adaptive_acc),
        'adaptive_mean_uses':float(1+np.mean(enhance)),
        'enhancement_fraction':float(np.mean(enhance)),
        'confidence_threshold':float(confidence_threshold),
    }
