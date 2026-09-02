import numpy as np
from .federated_selection import make_clustered_federated_problem, _ridge_grad, _global_loss


def simulate_energy_harvesting_aircomp_fl(policy='channel', n_clients=12, n_select=4,
                                           rounds=120, harvest_scale=.35,
                                           battery_capacity=4, channel_disparity_db=8.0,
                                           heterogeneity=.8, snr_db=18.0,
                                           learning_rate=.10, seed=0):
    """OTA-FL with finite batteries and stochastic energy harvesting.

    Every scheduled analog update costs one energy unit. ``age_energy`` gives a
    participation-age bonus in addition to channel and battery state, reducing
    starvation under heterogeneous channels/harvests. This is a transparent
    scheduling baseline, not an energy-harvesting protocol implementation.
    """
    if policy not in {'channel','energy_channel','age_energy'}: raise ValueError('unknown policy')
    clients,groups,path_amp,base=make_clustered_federated_problem(n_clients=n_clients,heterogeneity=heterogeneity,
        channel_disparity_db=channel_disparity_db,seed=seed)
    rng=np.random.default_rng(seed+2604); w=np.zeros_like(base); battery=np.full(n_clients,battery_capacity/2.0)
    # Per-device harvest heterogeneity, intentionally independent of data group.
    harvest_p=np.clip(harvest_scale*rng.uniform(.55,1.45,size=n_clients),.01,.95)
    ages=np.zeros(n_clients); counts=np.zeros(n_clients,int); losses=[_global_loss(w,clients)]
    outage_slots=0; weakest=[]; nv=1/(10**(snr_db/10)); ref=None
    for _ in range(rounds):
        battery=np.minimum(battery_capacity,battery+(rng.random(n_clients)<harvest_p))
        feasible=np.flatnonzero(battery>=1)
        if feasible.size==0:
            outage_slots+=1; ages+=1; losses.append(_global_loss(w,clients)); continue
        fast=np.abs((rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)); h=path_amp*fast
        G=np.stack([_ridge_grad(w,*c) for c in clients])
        f=feasible; m=min(n_select,len(f))
        if policy=='channel': score=h[f]
        elif policy=='energy_channel': score=h[f]*(.5+battery[f])
        else: score=h[f]*(.5+battery[f])*(1+.28*ages[f])
        idx=f[np.argsort(score)[-m:]]
        battery[idx]-=1; counts[idx]+=1; ages+=1; ages[idx]=0
        if ref is None: ref=max(float(np.sqrt(np.mean(G*G))),1e-8)
        a=max(float(np.min(h[idx])),1e-4); n=(rng.normal(size=w.size)+1j*rng.normal(size=w.size))*np.sqrt(nv/2)
        ghat=np.real(a*np.sum(G[idx]/ref,axis=0)+n)/(a*len(idx))*ref
        gn=np.linalg.norm(ghat)
        if gn>20: ghat*=20/gn
        w-=learning_rate*ghat; weakest.append(a); losses.append(_global_loss(w,clients))
    p=counts/max(counts.sum(),1); jain=(p.sum()**2)/(n_clients*np.sum(p*p)+1e-12)
    return {'policy':policy,'final_global_loss':float(losses[-1]),'participation_jain':float(jain),
            'plus_selection_fraction':float(counts[groups==1].sum()/max(counts.sum(),1)),
            'mean_battery':float(np.mean(battery)),'energy_outage_slot_fraction':float(outage_slots/rounds),
            'mean_selected_weakest_gain':float(np.mean(weakest)) if weakest else 0.0,
            'mean_participations_per_client':float(np.mean(counts)),'loss_history':np.asarray(losses)}
