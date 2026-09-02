import numpy as np


def simulate_cooperative_networked_control(slots=2600,n_agents=6,policy='system_value',mean_snr_db=0.0,seed=0):
    """Coupled multi-agent control over one shared wireless feedback slot.

    Agents form a 1-D chain with diffusive coupling. The system-value scheduler
    accounts for both local estimation error and how an agent's stale state affects
    neighboring formation terms. It is a linear educational baseline, not a vehicle
    dynamics or consensus standard.
    """
    if policy not in {'max_age','local_error','system_value'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3005)
    a=1.055; k=.48; coupling=.12
    x=rng.normal(0,.5,n_agents); xh=x.copy(); age=np.zeros(n_agents,int)
    snr0=np.linspace(mean_snr_db+2.5,mean_snr_db-2.5,n_agents)
    deg=np.ones(n_agents); deg[1:-1]=2
    costs=[]; formation=[]; selected=np.zeros(n_agents,int)
    for t in range(slots):
        err=np.abs(x-xh); snr=snr0+rng.normal(0,1.1,n_agents); p=1-np.exp(-10**(snr/10)/2.3)
        if policy=='max_age': i=int(np.argmax(age))
        elif policy=='local_error': i=int(np.argmax(p*err**2))
        else:
            # Direct one-step value proxy: how much would refreshing candidate i
            # reduce the *global* state/formation estimation error right now?
            base_form=float(np.sum((np.diff(x)-np.diff(xh))**2))
            score=np.zeros(n_agents)
            for j in range(n_agents):
                z=xh.copy(); z[j]=x[j]
                after_form=float(np.sum((np.diff(x)-np.diff(z))**2))
                reduction=max(0.0,base_form-after_form)
                score[j]=p[j]*(err[j]**2+2.8*reduction+.02*age[j])
            i=int(np.argmax(score))
        selected[i]+=1
        if rng.random()<p[i]: xh[i]=x[i]; age[i]=0
        u=-k*xh
        # Physical chain coupling; remote predictor uses its own estimated chain.
        lap=np.zeros(n_agents); laph=np.zeros(n_agents)
        lap[1:-1]=x[:-2]-2*x[1:-1]+x[2:]; lap[0]=x[1]-x[0]; lap[-1]=x[-2]-x[-1]
        laph[1:-1]=xh[:-2]-2*xh[1:-1]+xh[2:]; laph[0]=xh[1]-xh[0]; laph[-1]=xh[-2]-xh[-1]
        form=float(np.mean(np.diff(x)**2)); formation.append(form)
        costs.append(float(np.mean(x*x)+3.0*form+.04*np.mean(u*u)))
        w=rng.normal(0,.08,n_agents); x=a*x+coupling*lap+u+w; xh=a*xh+coupling*laph+u; age+=1
        x=np.clip(x,-80,80); xh=np.clip(xh,-80,80)
    c=np.asarray(costs)
    return {'policy':policy,'mean_system_cost':float(c.mean()),'p95_system_cost':float(np.quantile(c,.95)),
            'mean_formation_error':float(np.mean(formation)),'mean_information_age':float(np.mean(age)),
            'selection_jain':float(selected.sum()**2/(n_agents*np.sum(selected.astype(float)**2)+1e-12))}
