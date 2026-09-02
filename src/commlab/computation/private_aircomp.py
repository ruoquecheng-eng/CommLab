import numpy as np
from .federated_aircomp import make_federated_linear_problem, global_loss, _loss_grad


def clip_rows(G, clip_norm):
    G=np.asarray(G,float); n=np.linalg.norm(G,axis=1,keepdims=True)
    return G*np.minimum(1.0,clip_norm/(n+1e-12))


def simulate_private_aircomp_fl(n_clients=12,dim=10,rounds=70,snr_db=15,
                                clip_norm=1.0,privacy_noise_multiplier=0.0,
                                learning_rate=.1,heterogeneity=.8,seed=0):
    """AirComp-FL with client-side clipping and Gaussian privacy-noise baseline.

    ``privacy_noise_multiplier`` is sigma/C for clipped gradients. This is a
    DP-style perturbation experiment; no epsilon/delta guarantee is claimed
    because sampling/accounting are intentionally outside this educational model.
    """
    clients,wtrue=make_federated_linear_problem(n_clients=n_clients,dim=dim,heterogeneity=heterogeneity,seed=seed)
    rng=np.random.default_rng(seed+2303); w=np.zeros(dim); losses=[global_loss(w,clients)]; ms=[]
    nv=10**(-snr_db/10)
    for _ in range(rounds):
        G=np.stack([_loss_grad(w,*c)[1] for c in clients]); Gc=clip_rows(G,clip_norm)
        exact=Gc.mean(axis=0)
        Gp=Gc + privacy_noise_multiplier*clip_norm*rng.normal(size=Gc.shape)
        h=(rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)
        a=max(float(np.min(np.abs(h))),.05)
        n=(rng.normal(size=dim)+1j*rng.normal(size=dim))*np.sqrt(nv/2)
        ghat=np.real(a*np.sum(Gp,axis=0)+n)/(a*n_clients)
        ms.append(float(np.mean((ghat-exact)**2)))
        gn=np.linalg.norm(ghat)
        if gn>20: ghat*=20/gn
        w-=learning_rate*ghat; losses.append(global_loss(w,clients))
    return {'privacy_noise_multiplier':float(privacy_noise_multiplier),'final_loss':float(losses[-1]),
            'parameter_error':float(np.linalg.norm(w-wtrue)),'mean_aggregation_mse':float(np.mean(ms)),
            'loss_history':np.asarray(losses)}
