import numpy as np
from .federated_selection import make_clustered_federated_problem, _ridge_grad, _global_loss, _closed_form_global_optimum


def _select_diverse(grads, h, n_select):
    """Greedy channel-aware gradient-diversity selection."""
    norms=np.linalg.norm(grads,axis=1)+1e-12
    first=int(np.argmax(h*norms)); chosen=[first]
    while len(chosen)<n_select:
        cand=[i for i in range(len(h)) if i not in chosen]
        scores=[]
        for i in cand:
            sims=[abs(np.dot(grads[i],grads[j]))/(norms[i]*norms[j]) for j in chosen]
            novelty=1-max(sims)
            scores.append((h[i]**.6)*(0.15+novelty))
        chosen.append(cand[int(np.argmax(scores))])
    return np.asarray(chosen,int)


def simulate_aircomp_selection_federated(strategy='channel', n_clients=12, n_select=4,
                                           rounds=100, channel_disparity_db=10.0,
                                           heterogeneity=.8, snr_db=16.0,
                                           learning_rate=.11, seed=0):
    """OTA-FL user selection: aggregation quality versus learning diversity.

    ``channel`` minimizes analog difficulty by selecting strong instantaneous
    links. ``diversity`` trades some weakest-link gain for gradient-direction
    diversity. ``all`` schedules all devices and pays the weakest-link AirComp
    penalty. The underlying two-group problem deliberately correlates data group
    and long-term channel strength.
    """
    if strategy not in {'channel','diversity','all','random'}: raise ValueError('unknown strategy')
    clients,groups,path_amp,base=make_clustered_federated_problem(
        n_clients=n_clients,heterogeneity=heterogeneity,channel_disparity_db=channel_disparity_db,seed=seed)
    rng=np.random.default_rng(seed+2601); w=np.zeros_like(base); counts=np.zeros(n_clients,int)
    losses=[_global_loss(w,clients)]; agg_mse=[]; analog_mse=[]; selection_bias=[]; weakest=[]; nv=1/(10**(snr_db/10)); ref=None
    for _ in range(rounds):
        fast=np.abs((rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)); h=path_amp*fast
        G=np.stack([_ridge_grad(w,*c) for c in clients]); exact_all=G.mean(axis=0)
        if strategy=='all': idx=np.arange(n_clients)
        elif strategy=='channel': idx=np.argsort(h)[-n_select:]
        elif strategy=='random': idx=rng.choice(n_clients,size=n_select,replace=False)
        else: idx=_select_diverse(G,h,n_select)
        counts[idx]+=1; gsel=G[idx]; hsel=h[idx]
        if ref is None: ref=max(float(np.sqrt(np.mean(G*G))),1e-8)
        a=max(float(np.min(hsel)),1e-4); n=(rng.normal(size=w.size)+1j*rng.normal(size=w.size))*np.sqrt(nv/2)
        ghat=np.real(a*np.sum(gsel/ref,axis=0)+n)/(a*len(idx))*ref
        exact_sel=gsel.mean(axis=0)
        analog_mse.append(float(np.mean((ghat-exact_sel)**2)))
        selection_bias.append(float(np.mean((exact_sel-exact_all)**2)))
        agg_mse.append(float(np.mean((ghat-exact_all)**2))); weakest.append(a)
        gn=np.linalg.norm(ghat)
        if gn>20: ghat*=20/gn
        w-=learning_rate*ghat; losses.append(_global_loss(w,clients))
    opt=_closed_form_global_optimum(clients); p=counts/max(counts.sum(),1); jain=(p.sum()**2)/(n_clients*np.sum(p*p)+1e-12)
    return {
        'strategy':strategy,'final_global_loss':float(losses[-1]),
        'parameter_error_to_global_optimum':float(np.linalg.norm(w-opt)),
        'mean_aggregation_mse_to_all_clients':float(np.mean(agg_mse)),
        'mean_analog_mse_to_selected_mean':float(np.mean(analog_mse)),
        'mean_selection_bias_mse':float(np.mean(selection_bias)),
        'mean_selected_weakest_gain':float(np.mean(weakest)),
        'plus_selection_fraction':float(counts[groups==1].sum()/max(counts.sum(),1)),
        'participation_jain':float(jain),'loss_history':np.asarray(losses),
    }
