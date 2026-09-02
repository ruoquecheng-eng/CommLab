import numpy as np
from .federated_aircomp import make_federated_linear_problem,global_loss,_loss_grad
from .ris_aircomp import effective_ris_aircomp_channel,optimize_ris_aircomp


def simulate_two_timescale_ris_aircomp_fl(n_clients=8,n_ris=10,rounds=70,
                                           update_interval=4,rho=.98,bits=2,
                                           snr_db=12,learning_rate=.1,seed=0):
    """FL over AirComp with slowly updated finite-bit RIS phases.

    Device-RIS/direct channels evolve through Gauss-Markov fading.  The RIS is
    optimized for the weakest effective device only every ``update_interval``
    learning rounds, while clients still perform current-channel inversion each
    round.  Reports learning loss together with RIS control overhead.
    """
    if n_clients<2 or n_ris<2 or rounds<1 or update_interval<1 or not 0<=rho<=1:
        raise ValueError('bad two-timescale RIS-FL setup')
    clients,w_true=make_federated_linear_problem(n_clients=n_clients,dim=16,
                                                  heterogeneity=.8,seed=seed)
    rng=np.random.default_rng(seed+441); w=np.zeros_like(w_true); losses=[global_loss(w,clients)]
    hd=(rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)*.18
    F=(rng.normal(size=(n_clients,n_ris))+1j*rng.normal(size=(n_clients,n_ris)))/np.sqrt(2*n_ris)
    g=(rng.normal(size=n_ris)+1j*rng.normal(size=n_ris))/np.sqrt(2*n_ris)
    phases=np.ones(n_ris,complex); nv=1/(10**(snr_db/10)); weak=[]; updates=0; ref=None
    for t in range(rounds):
        if t>0:
            hd=rho*hd+np.sqrt(max(1-rho*rho,0))*((rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)*.18)
            F=rho*F+np.sqrt(max(1-rho*rho,0))*((rng.normal(size=(n_clients,n_ris))+1j*rng.normal(size=(n_clients,n_ris)))/np.sqrt(2*n_ris))
            g=rho*g+np.sqrt(max(1-rho*rho,0))*((rng.normal(size=n_ris)+1j*rng.normal(size=n_ris))/np.sqrt(2*n_ris))
        if t%update_interval==0:
            phases,_=optimize_ris_aircomp(hd,F,g,bits=bits,sweeps=1,objective='maxmin'); updates+=1
        h=effective_ris_aircomp_channel(hd,F,g,phases); a=max(float(np.min(np.abs(h))),1e-4); weak.append(a)
        grads=np.stack([_loss_grad(w,*c)[1] for c in clients]); exact_scale=np.sqrt(np.mean(grads*grads))
        if ref is None: ref=max(float(exact_scale),1e-8)
        n=(rng.normal(size=w.size)+1j*rng.normal(size=w.size))*np.sqrt(nv/2)
        ghat=np.real(a*np.sum(grads/ref,axis=0)+n)/(a*n_clients)*ref
        gn=np.linalg.norm(ghat)
        if gn>20: ghat*=20/gn
        w-=learning_rate*ghat; losses.append(global_loss(w,clients))
    control_bits=updates*n_ris*bits
    return {
        'update_interval':int(update_interval),'final_loss':float(losses[-1]),
        'loss_history':np.asarray(losses),'parameter_error':float(np.linalg.norm(w-w_true)),
        'mean_weakest_gain':float(np.mean(weak)),'p10_weakest_gain':float(np.percentile(weak,10)),
        'ris_updates':int(updates),'ris_control_bits':int(control_bits),
        'control_bits_per_round':float(control_bits/rounds),
    }
