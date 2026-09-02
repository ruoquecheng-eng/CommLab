import numpy as np
from .ris_aircomp import effective_ris_aircomp_channel
from .cellfree_aircomp import choose_cellfree_aircomp_combiner


def optimize_robust_ris_aircomp(hd_hat,F_hat,g_hat,error_std=.15,bits=2,sweeps=2,
                                n_uncertainty=16,quantile=.15,seed=0):
    """Finite-bit RIS coordinate ascent using a lower-tail weakest-link score."""
    if error_std<0 or not 0<=quantile<=1: raise ValueError('bad uncertainty setup')
    rng=np.random.default_rng(seed); hd_hat=np.asarray(hd_hat,complex); F_hat=np.asarray(F_hat,complex); g_hat=np.asarray(g_hat,complex)
    N=g_hat.size; code=np.exp(1j*2*np.pi*np.arange(2**bits)/(2**bits)); phases=np.ones(N,complex)
    scenarios=[]
    for _ in range(n_uncertainty):
        # Treat error_std as a relative RMS uncertainty so heterogeneous
        # channel components (direct/RIS hops) receive comparable normalized
        # perturbations rather than an arbitrary common absolute variance.
        sh=max(float(np.sqrt(np.mean(np.abs(hd_hat)**2))),1e-8)
        sF=max(float(np.sqrt(np.mean(np.abs(F_hat)**2))),1e-8)
        sg=max(float(np.sqrt(np.mean(np.abs(g_hat)**2))),1e-8)
        eh=(rng.normal(size=hd_hat.shape)+1j*rng.normal(size=hd_hat.shape))/np.sqrt(2)*error_std*sh
        eF=(rng.normal(size=F_hat.shape)+1j*rng.normal(size=F_hat.shape))/np.sqrt(2)*error_std*sF
        eg=(rng.normal(size=g_hat.shape)+1j*rng.normal(size=g_hat.shape))/np.sqrt(2)*error_std*sg
        scenarios.append((hd_hat+eh,F_hat+eF,g_hat+eg))
    def score(p):
        vals=[]
        for hd,F,g in scenarios:
            vals.append(np.min(np.abs(effective_ris_aircomp_channel(hd,F,g,p))))
        return float(np.quantile(vals,quantile))
    hist=[]
    for _ in range(sweeps):
        for n in range(N):
            best=phases[n]; bs=-np.inf
            for c in code:
                q=phases.copy(); q[n]=c; s=score(q)
                if s>bs: bs=s; best=c
            phases[n]=best
        hist.append(score(phases))
    return phases,np.asarray(hist)


def choose_robust_cellfree_aircomp_combiner(Hhat,error_std=.15,n_random=120,
                                             n_uncertainty=20,quantile=.15,seed=0):
    """Candidate-search Cell-Free combiner robust to imperfect CSI."""
    Hhat=np.asarray(Hhat,complex); M,K=Hhat.shape; rng=np.random.default_rng(seed)
    sig=np.asarray(error_std,float)
    if sig.ndim==0: sig=np.full(Hhat.shape,float(sig))
    elif sig.shape!=Hhat.shape: raise ValueError('error_std must be scalar or H-shaped')
    # Reuse interpretable candidate family and augment with random directions.
    candidates=[]
    for m in range(M):
        v=np.zeros(M,complex); v[m]=1; candidates.append(v)
    candidates.append(np.ones(M,complex)/np.sqrt(M))
    for k in range(K):
        h=Hhat[:,k]; candidates.append(h/(np.linalg.norm(h)+1e-12))
    for _ in range(n_random):
        v=rng.normal(size=M)+1j*rng.normal(size=M); v/=np.linalg.norm(v)+1e-12; candidates.append(v)
    samples=[]
    for _ in range(n_uncertainty):
        e=(rng.normal(size=Hhat.shape)+1j*rng.normal(size=Hhat.shape))/np.sqrt(2)*sig
        samples.append(Hhat+e)
    scores=[]
    for v in candidates:
        weak=[np.min(np.abs(np.conj(v)@Hs)) for Hs in samples]
        scores.append(float(np.quantile(weak,quantile)))
    i=int(np.argmax(scores)); return candidates[i],scores[i]


def simulate_imperfect_csi_cellfree_aircomp(n_aps=8,n_devices=10,snr_db=15,
                                             csi_error_std=.15,n_trials=180,seed=0):
    """Compare naive and lower-tail-robust Cell-Free AirComp combining."""
    rng=np.random.default_rng(seed); nv=1/(10**(snr_db/10)); naive=[]; robust=[]; ng=[]; rg=[]
    for t in range(n_trials):
        H=(rng.normal(size=(n_aps,n_devices))+1j*rng.normal(size=(n_aps,n_devices)))/np.sqrt(2)
        E=(rng.normal(size=H.shape)+1j*rng.normal(size=H.shape))/np.sqrt(2)*csi_error_std
        Hhat=H+E
        vn,_=choose_cellfree_aircomp_combiner(Hhat,n_random=80,seed=seed+3*t)
        vr,_=choose_robust_cellfree_aircomp_combiner(Hhat,csi_error_std,n_random=60,n_uncertainty=12,seed=seed+5*t)
        an=max(float(np.min(np.abs(np.conj(vn)@H))),1e-6); ar=max(float(np.min(np.abs(np.conj(vr)@H))),1e-6)
        # Expected full-inversion aggregation MSE for real average with complex AWGN.
        # Real-part noise variance is nv/2 and averaging divides by K^2 a^2.
        naive.append(nv/(2*n_devices*n_devices*an*an)); robust.append(nv/(2*n_devices*n_devices*ar*ar)); ng.append(an); rg.append(ar)
    return {'naive_median_mse':float(np.median(naive)),'robust_median_mse':float(np.median(robust)),
            'naive_p90_mse':float(np.quantile(naive,.9)),'robust_p90_mse':float(np.quantile(robust,.9)),
            'naive_mean_weakest_gain':float(np.mean(ng)),'robust_mean_weakest_gain':float(np.mean(rg)),
            'csi_error_std':float(csi_error_std)}


def simulate_heterogeneous_csi_cellfree_aircomp(n_aps=8,n_devices=10,snr_db=15,
                                                   max_csi_error=.35,n_trials=180,seed=0):
    """Imperfect-CSI AirComp with AP-dependent estimation quality.

    APs have heterogeneous CSI uncertainty, modeling unequal pilot quality or
    fronthaul/estimator fidelity. The robust combiner sees the error-variance
    profile, while the naive combiner optimizes only the point estimate.
    """
    rng=np.random.default_rng(seed); nv=1/(10**(snr_db/10)); na=[]; ro=[]; wins=0
    ap_sigma=np.linspace(.03,max_csi_error,n_aps)
    sig=ap_sigma[:,None]*np.ones((1,n_devices))
    for t in range(n_trials):
        H=(rng.normal(size=(n_aps,n_devices))+1j*rng.normal(size=(n_aps,n_devices)))/np.sqrt(2)
        E=(rng.normal(size=H.shape)+1j*rng.normal(size=H.shape))/np.sqrt(2)*sig
        Hhat=H+E
        vn,_=choose_cellfree_aircomp_combiner(Hhat,n_random=100,seed=seed+13*t)
        vr,_=choose_robust_cellfree_aircomp_combiner(Hhat,sig,n_random=100,n_uncertainty=18,quantile=.12,seed=seed+17*t)
        an=max(float(np.min(np.abs(np.conj(vn)@H))),1e-6); ar=max(float(np.min(np.abs(np.conj(vr)@H))),1e-6)
        na.append(nv/(2*n_devices*n_devices*an*an)); ro.append(nv/(2*n_devices*n_devices*ar*ar)); wins+=int(ar>an)
    return {'naive_median_mse':float(np.median(na)),'robust_median_mse':float(np.median(ro)),
            'naive_p90_mse':float(np.quantile(na,.9)),'robust_p90_mse':float(np.quantile(ro,.9)),
            'robust_win_fraction':float(wins/n_trials),'max_csi_error':float(max_csi_error)}


def choose_lcb_cellfree_aircomp_combiner(Hhat,error_std,n_random=120,z=1.0,seed=0):
    """Lower-confidence-bound combiner for heterogeneous CSI uncertainty.

    For candidate v and device k, the projected estimation-error standard
    deviation is sqrt(sum_m |v_m|^2 sigma_mk^2). The score is the weakest
    estimated magnitude minus ``z`` times this uncertainty.
    """
    Hhat=np.asarray(Hhat,complex); M,K=Hhat.shape; sig=np.asarray(error_std,float)
    if sig.ndim==0: sig=np.full(Hhat.shape,float(sig))
    elif sig.shape!=Hhat.shape: raise ValueError('error_std must be scalar or H-shaped')
    rng=np.random.default_rng(seed); cand=[]
    for m in range(M):
        v=np.zeros(M,complex); v[m]=1; cand.append(v)
    cand.append(np.ones(M,complex)/np.sqrt(M))
    for k in range(K):
        h=Hhat[:,k]; cand.append(h/(np.linalg.norm(h)+1e-12))
    for _ in range(n_random):
        v=rng.normal(size=M)+1j*rng.normal(size=M); v/=np.linalg.norm(v)+1e-12; cand.append(v)
    scores=[]
    for v in cand:
        est=np.abs(np.conj(v)@Hhat)
        std=np.sqrt((np.abs(v)[:,None]**2 * sig**2).sum(axis=0))
        scores.append(float(np.min(est-z*std)))
    i=int(np.argmax(scores)); return cand[i],scores[i]


def simulate_lcb_cellfree_aircomp(n_aps=8,n_devices=10,snr_db=15,max_csi_error=.35,
                                  n_trials=180,z=1.0,seed=0):
    rng=np.random.default_rng(seed); nv=1/(10**(snr_db/10)); na=[]; rb=[]; wins=0
    ap_sigma=np.linspace(.03,max_csi_error,n_aps); sig=ap_sigma[:,None]*np.ones((1,n_devices))
    for t in range(n_trials):
        H=(rng.normal(size=(n_aps,n_devices))+1j*rng.normal(size=(n_aps,n_devices)))/np.sqrt(2)
        E=(rng.normal(size=H.shape)+1j*rng.normal(size=H.shape))/np.sqrt(2)*sig; Hhat=H+E
        vn,_=choose_cellfree_aircomp_combiner(Hhat,n_random=120,seed=seed+11*t)
        vr,_=choose_lcb_cellfree_aircomp_combiner(Hhat,sig,n_random=120,z=z,seed=seed+13*t)
        an=max(float(np.min(np.abs(np.conj(vn)@H))),1e-6); ar=max(float(np.min(np.abs(np.conj(vr)@H))),1e-6)
        na.append(nv/(2*n_devices*n_devices*an*an)); rb.append(nv/(2*n_devices*n_devices*ar*ar)); wins+=int(ar>an)
    return {'naive_median_mse':float(np.median(na)),'lcb_median_mse':float(np.median(rb)),
            'naive_p90_mse':float(np.quantile(na,.9)),'lcb_p90_mse':float(np.quantile(rb,.9)),
            'lcb_win_fraction':float(wins/n_trials),'max_csi_error':float(max_csi_error),'z':float(z)}
