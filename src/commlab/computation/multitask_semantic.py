import numpy as np


def simulate_multitask_task_oriented(dim=16,n_samples=12000,task_angle_deg=60,
                                     snr_db=10,seed=0):
    """Analytical two-task semantic baseline with shared/task-specific projections.

    Labels are deterministic signs of two linear functionals of an isotropic
    Gaussian source. Sending each task statistic is sufficient for that task;
    a one-dimensional shared representation must compromise as task directions
    separate, while a rank-two shared subspace preserves both task statistics.
    """
    if dim<2 or n_samples<100 or not 0<=task_angle_deg<=90: raise ValueError('bad setup')
    rng=np.random.default_rng(seed); th=np.deg2rad(task_angle_deg)
    mu1=np.zeros(dim); mu1[0]=1
    mu2=np.zeros(dim); mu2[0]=np.cos(th); mu2[1]=np.sin(th)
    X=rng.normal(size=(n_samples,dim)); y1=(X@mu1>=0); y2=(X@mu2>=0)
    nv=1/(10**(snr_db/10))
    def txrx(A):
        Z=X@A
        scale=max(float(np.sqrt(np.mean(Z*Z))),1e-8)
        N=rng.normal(scale=np.sqrt(nv),size=Z.shape)
        return (Z/scale+N)*scale
    # Raw feature baseline.
    Xr=txrx(np.eye(dim)); a1=float(np.mean((Xr@mu1>=0)==y1)); a2=float(np.mean((Xr@mu2>=0)==y2))
    # Task-specific sufficient statistics, two uses if both tasks are requested.
    A2=np.stack([mu1,mu2],axis=1); Z2=txrx(A2)
    ts1=float(np.mean((Z2[:,0]>=0)==y1)); ts2=float(np.mean((Z2[:,1]>=0)==y2))
    # Rank-one common semantic feature: principal direction of task outer products.
    S=np.outer(mu1,mu1)+np.outer(mu2,mu2); vals,vecs=np.linalg.eigh(S); v=vecs[:,-1]
    if np.dot(v,mu1)<0: v=-v
    z1=txrx(v[:,None])[:,0]
    sh1=float(np.mean(((np.dot(mu1,v)*z1)>=0)==y1)); sh2=float(np.mean(((np.dot(mu2,v)*z1)>=0)==y2))
    # Rank-two shared subspace spans both tasks exactly before channel noise.
    Q,_=np.linalg.qr(A2); Q=Q[:,:2]; zrank2=txrx(Q)
    Xproj=zrank2@Q.T
    r21=float(np.mean((Xproj@mu1>=0)==y1)); r22=float(np.mean((Xproj@mu2>=0)==y2))
    return {'task_angle_deg':float(task_angle_deg),'snr_db':float(snr_db),
            'raw_task1_accuracy':a1,'raw_task2_accuracy':a2,'raw_mean_accuracy':(a1+a2)/2,'raw_uses':dim,
            'task_specific_task1_accuracy':ts1,'task_specific_task2_accuracy':ts2,'task_specific_mean_accuracy':(ts1+ts2)/2,'task_specific_uses':2,
            'shared_rank1_task1_accuracy':sh1,'shared_rank1_task2_accuracy':sh2,'shared_rank1_mean_accuracy':(sh1+sh2)/2,'shared_rank1_uses':1,
            'shared_rank2_task1_accuracy':r21,'shared_rank2_task2_accuracy':r22,'shared_rank2_mean_accuracy':(r21+r22)/2,'shared_rank2_uses':2}
