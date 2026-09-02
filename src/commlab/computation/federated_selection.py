import numpy as np


def make_clustered_federated_problem(n_clients=12, samples_per_client=80, dim=8,
                                     heterogeneity=0.7, noise_std=0.15,
                                     channel_disparity_db=8.0, seed=0):
    """Two-group non-IID linear-regression problem with correlated channel quality.

    Half of the clients have local optima shifted toward +u and stronger average
    channels; the other half are shifted toward -u and weaker channels. The
    equal-client global objective therefore needs both groups. This deliberately
    exposes selection bias when communication policy always favors strong links.
    """
    if n_clients < 4 or n_clients % 2 or samples_per_client < 8 or dim < 2:
        raise ValueError("need an even number of clients >=4 and a nontrivial problem")
    rng = np.random.default_rng(seed)
    base = rng.normal(size=dim); base /= np.linalg.norm(base) + 1e-12
    u = rng.normal(size=dim); u -= base*np.dot(base,u); u /= np.linalg.norm(u)+1e-12
    clients=[]; groups=[]
    for k in range(n_clients):
        g = 1 if k < n_clients//2 else -1
        w_local = base + g*heterogeneity*u
        X = rng.normal(size=(samples_per_client,dim))
        y = X@w_local + noise_std*rng.normal(size=samples_per_client)
        clients.append((X,y)); groups.append(g)
    # Positive group gets stronger long-term amplitude, negative group weaker.
    amp_ratio = 10**(channel_disparity_db/20)
    path_amp=np.ones(n_clients)
    path_amp[:n_clients//2]=np.sqrt(amp_ratio)
    path_amp[n_clients//2:]=1/np.sqrt(amp_ratio)
    return clients, np.asarray(groups), path_amp, base


def _ridge_grad(w,X,y,l2=1e-3):
    r=X@w-y
    return X.T@r/len(y)+l2*w


def _global_loss(w,clients,l2=1e-3):
    vals=[]
    for X,y in clients:
        r=X@w-y; vals.append(.5*np.mean(r*r)+.5*l2*np.dot(w,w))
    return float(np.mean(vals))


def _closed_form_global_optimum(clients,l2=1e-3):
    X=np.concatenate([c[0] for c in clients],axis=0)
    y=np.concatenate([c[1] for c in clients],axis=0)
    A=X.T@X/len(y)+l2*np.eye(X.shape[1]); b=X.T@y/len(y)
    return np.linalg.solve(A,b)


def simulate_selection_biased_fl(strategy='random', n_clients=12, n_select=4,
                                  rounds=100, learning_rate=0.12,
                                  channel_disparity_db=8.0, heterogeneity=0.7,
                                  age_weight=0.35, snr_db=18.0, seed=0):
    """Federated optimization under communication-driven client selection.

    Strategies:
    - ``random``: uniform random participation.
    - ``channel``: strongest instantaneous links.
    - ``age_channel``: channel score multiplied by a participation-age bonus.
    - ``gradient_channel``: gradient norm times instantaneous channel amplitude.

    Selected gradients are aggregated through one analog AirComp resource per
    round. The model is intentionally transparent; no privacy/security claims.
    """
    if n_select<1 or n_select>n_clients or rounds<1:
        raise ValueError('invalid selection setup')
    clients,groups,path_amp,base=make_clustered_federated_problem(
        n_clients=n_clients,heterogeneity=heterogeneity,
        channel_disparity_db=channel_disparity_db,seed=seed)
    rng=np.random.default_rng(seed+991); w=np.zeros_like(base); ages=np.zeros(n_clients)
    counts=np.zeros(n_clients,int); losses=[_global_loss(w,clients)]; selected_gains=[]
    nv=1/(10**(snr_db/10)); ref_scale=None
    for _ in range(rounds):
        fast=np.abs((rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2))
        h=path_amp*fast
        grads=np.stack([_ridge_grad(w,*clients[k]) for k in range(n_clients)])
        if strategy=='random':
            idx=rng.choice(n_clients,size=n_select,replace=False)
        elif strategy=='channel':
            idx=np.argsort(h)[-n_select:]
        elif strategy=='age_channel':
            score=h*(1+age_weight*ages)
            idx=np.argsort(score)[-n_select:]
        elif strategy=='gradient_channel':
            score=h*np.linalg.norm(grads,axis=1)
            idx=np.argsort(score)[-n_select:]
        else:
            raise ValueError('unknown strategy')
        ages+=1; ages[idx]=0; counts[idx]+=1
        gsel=grads[idx]; hsel=h[idx]
        if ref_scale is None: ref_scale=max(float(np.sqrt(np.mean(grads*grads))),1e-8)
        a=max(float(np.min(hsel)),1e-4)
        n=(rng.normal(size=w.size)+1j*rng.normal(size=w.size))*np.sqrt(nv/2)
        ghat=np.real(a*np.sum(gsel/ref_scale,axis=0)+n)/(a*len(idx))*ref_scale
        gn=np.linalg.norm(ghat)
        if gn>20: ghat*=20/gn
        w-=learning_rate*ghat
        selected_gains.append(a); losses.append(_global_loss(w,clients))
    opt=_closed_form_global_optimum(clients)
    group_losses=[]
    for sign in (1,-1):
        cc=[clients[k] for k in range(n_clients) if groups[k]==sign]
        group_losses.append(_global_loss(w,cc))
    p=counts/max(counts.sum(),1); jain=(p.sum()**2)/(n_clients*np.sum(p*p)+1e-12)
    return {
        'strategy':strategy,'loss_history':np.asarray(losses),
        'final_global_loss':float(losses[-1]),
        'parameter_error_to_global_optimum':float(np.linalg.norm(w-opt)),
        'group_plus_loss':float(group_losses[0]),'group_minus_loss':float(group_losses[1]),
        'group_loss_gap':float(abs(group_losses[0]-group_losses[1])),
        'participation_jain':float(jain),
        'plus_selection_fraction':float(counts[groups==1].sum()/max(counts.sum(),1)),
        'mean_selected_weakest_gain':float(np.mean(selected_gains)),
        'channel_uses':int(rounds),'selection_counts':counts,
    }
