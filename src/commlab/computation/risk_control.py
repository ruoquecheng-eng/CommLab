import numpy as np


def _cvar(x, alpha=.95):
    x=np.asarray(x,float)
    q=np.quantile(x,alpha)
    tail=x[x>=q]
    return float(np.mean(tail)) if tail.size else float(q)


def simulate_risk_sensitive_control(slots=2600,n_plants=5,policy='risk_value',mean_snr_db=-1.0,risk_weight=1.0,shock_multiplier=1.0,seed=0):
    """Risk-sensitive wireless scheduling for independent unstable control loops.

    Rare plant-specific shocks create a meaningful tail-risk objective. ``mean_value``
    prioritizes the expected one-step estimation benefit, whereas ``risk_value`` also
    protects loops with high shock exposure and accumulated estimation mismatch.
    The CVaR metric is empirical and educational; this is not an optimal stochastic
    control solver.
    """
    if policy not in {'max_age','mean_value','risk_value'}: raise ValueError('unknown policy')
    if slots<200 or n_plants<2: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed+3001)
    a=np.linspace(1.025,1.12,n_plants); k=np.linspace(.40,.54,n_plants)
    q=np.linspace(.7,1.7,n_plants); r=.05
    shock_p=np.linspace(.006,.035,n_plants); shock_std=shock_multiplier*np.linspace(.8,2.5,n_plants)
    snr0=np.linspace(mean_snr_db+2.5,mean_snr_db-2.5,n_plants)
    x=rng.normal(0,.5,n_plants); xhat=x.copy(); age=np.zeros(n_plants,int)
    costs=[]; ages=[]; shocks=0; select=np.zeros(n_plants,int)
    for t in range(slots):
        err=np.abs(x-xhat)
        snr=snr0+1.6*np.sin(2*np.pi*t/97+np.arange(n_plants))+rng.normal(0,.9,n_plants)
        p=1-np.exp(-10**(snr/10)/2.5)
        if policy=='max_age': i=int(np.argmax(age))
        else:
            mean_value=p*q*(a**2)*(err**2+.08*x*x)
            if policy=='mean_value': score=mean_value
            else:
                # Proxy for tail exposure if this loop remains stale: rare shocks are
                # amplified by open-loop instability and accumulated age.
                # Incremental tail exposure if a rare disturbance arrives while
                # the controller is operating on a stale estimate. The cross term
                # keeps this small in calm regimes but raises priority once either
                # plant risk or current mismatch is large.
                tail_exposure=shock_p*q*(a**2)*(2*err*shock_std+shock_std**2)*(1+.045*age)
                score=mean_value+risk_weight*p*tail_exposure
            i=int(np.argmax(score))
        select[i]+=1
        if rng.random()<p[i]: xhat[i]=x[i]; age[i]=0
        u=-k*xhat
        stage=q*x*x+r*u*u
        costs.append(float(np.mean(stage))); ages.append(float(np.mean(age)))
        shock_mask=rng.random(n_plants)<shock_p
        w=rng.normal(0,.075,n_plants)+shock_mask*rng.normal(0,shock_std,n_plants)
        shocks+=int(shock_mask.sum())
        x=a*x+u+w; xhat=a*xhat+u; age+=1
        x=np.clip(x,-120,120); xhat=np.clip(xhat,-120,120)
    c=np.asarray(costs)
    return {
        'policy':policy,'mean_control_cost':float(c.mean()),'p95_control_cost':float(np.quantile(c,.95)),
        'cvar95_control_cost':_cvar(c,.95),'mean_information_age':float(np.mean(ages)),
        'max_stage_cost':float(c.max()),'shock_events':int(shocks),
        'selection_jain':float(select.sum()**2/(n_plants*np.sum(select.astype(float)**2)+1e-12)),
    }
