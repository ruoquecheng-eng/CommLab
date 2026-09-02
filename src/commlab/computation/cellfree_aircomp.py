import numpy as np


def choose_cellfree_aircomp_combiner(H, n_random=200, seed=0):
    """Candidate-search max-min combiner for a distributed AirComp uplink.

    H has shape (n_aps, n_devices). The unit-norm CPU combiner is chosen to
    maximize min_k |v^H h_k| over a transparent candidate set. This is a
    baseline search, not a globally optimal multicast/AirComp beamformer.
    """
    H=np.asarray(H,dtype=complex)
    if H.ndim!=2 or min(H.shape)<1: raise ValueError('H must be 2-D')
    M,K=H.shape; rng=np.random.default_rng(seed); cand=[]
    # Each individual AP, equal combining, matched directions to each device,
    # and random unit vectors. These provide interpretable search anchors.
    for m in range(M):
        v=np.zeros(M,dtype=complex); v[m]=1; cand.append(v)
    cand.append(np.ones(M,dtype=complex)/np.sqrt(M))
    for k in range(K):
        h=H[:,k]; n=np.linalg.norm(h)
        if n>1e-12: cand.append(h/n)
    for _ in range(n_random):
        v=(rng.normal(size=M)+1j*rng.normal(size=M)); v/=np.linalg.norm(v)+1e-12; cand.append(v)
    vals=[]
    for v in cand:
        vals.append(float(np.min(np.abs(np.conj(v)@H))))
    i=int(np.argmax(vals))
    return cand[i], vals[i]


def simulate_cellfree_aircomp(n_aps=8, n_devices=12, vector_dim=24, snr_db=15,
                               n_trials=300, seed=0, n_random=200):
    """Compare best-single-AP and cooperative Cell-Free AirComp.

    For each fading realization, devices invert the scalar effective channel
    after receive combining. The common receive amplitude is constrained by the
    weakest device and unit device power. Cooperation improves that bottleneck
    but assumes perfect centralized CSI and phase synchronization.
    """
    if n_aps<1 or n_devices<2 or n_trials<1: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed); nv=1/(10**(snr_db/10)); sm=[]; cm=[]; gains=[]
    for t in range(n_trials):
        H=(rng.normal(size=(n_aps,n_devices))+1j*rng.normal(size=(n_aps,n_devices)))/np.sqrt(2)
        # Best single AP for the weakest-device AirComp objective.
        mins=np.min(np.abs(H),axis=1); m=int(np.argmax(mins)); a1=max(float(mins[m]),1e-6)
        v,g=choose_cellfree_aircomp_combiner(H,n_random=n_random,seed=seed+1000+t); ac=max(g,1e-6)
        x=rng.normal(size=(n_devices,vector_dim)); target=x.mean(axis=0)
        n1=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(nv/2)
        nc=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(nv/2)
        e1=np.real(a1*np.sum(x,axis=0)+n1)/(a1*n_devices)
        # Unit-norm v keeps post-combining noise variance equal to nv.
        ec=np.real(ac*np.sum(x,axis=0)+nc)/(ac*n_devices)
        sm.append(np.mean((e1-target)**2)); cm.append(np.mean((ec-target)**2)); gains.append((a1,ac))
    gains=np.asarray(gains)
    return {'single_ap_median_mse':float(np.median(sm)),
            'cellfree_median_mse':float(np.median(cm)),
            'single_ap_mean_weakest_gain':float(np.mean(gains[:,0])),
            'cellfree_mean_weakest_gain':float(np.mean(gains[:,1])),
            'channel_uses_per_vector':1,'n_aps':int(n_aps)}
