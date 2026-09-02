import numpy as np


def simulate_safety_aware_control(slots=2600,n_plants=5,policy='safety_value',mean_snr_db=-1.0,seed=0):
    """Shared wireless feedback for safety-constrained scalar plants.

    Each plant has an explicit safe state bound. The scheduler may use age,
    estimation error, or an expected safety-risk reduction proxy. This is an
    educational linear-control abstraction, not a certified safety controller.
    """
    if policy not in {'max_age','max_error','safety_value'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3101)
    # Deliberately create a conflict between estimation error and safety risk:
    # early-index plants are noisy but have generous safety envelopes, while
    # later plants are more unstable and operate closer to tighter bounds.
    a=np.linspace(1.02,1.11,n_plants); k=np.linspace(.34,.52,n_plants)
    bound=np.linspace(4.8,1.85,n_plants); q=np.linspace(.8,1.8,n_plants)
    process_std=np.linspace(.18,.055,n_plants)
    snr0=np.linspace(mean_snr_db-2,mean_snr_db+2,n_plants)
    x=rng.normal(0,.7,n_plants); xh=x.copy(); age=np.zeros(n_plants,int)
    violations=0; stage=[]; margin_hist=[]; ages=[]; success=0
    for t in range(slots):
        err=np.abs(x-xh); snr=snr0+1.7*np.sin(2*np.pi*t/101+np.arange(n_plants))+rng.normal(0,1.0,n_plants)
        p=1-np.exp(-10**(snr/10)/2.4)
        if policy=='max_age': i=int(np.argmax(age))
        elif policy=='max_error': i=int(np.argmax(err))
        else:
            # Sensor-side trigger metadata exposes normalized safety proximity;
            # the scheduler still does not receive the full state before access.
            u=-k*xh; pred=np.abs(a*x+u)
            proximity=np.clip(pred/bound,0,2.0)
            risk=np.maximum(0.0,proximity-.55)/.45
            score=(.25+.75*p)*(12.0*risk**4) + .20*p*q*err**2 + .01*age
            i=int(np.argmax(score))
        if rng.random()<p[i]: xh[i]=x[i]; age[i]=0; success+=1
        u=-k*xh; stage.append(float(np.mean(q*x*x+.05*u*u)))
        violations += int(np.any(np.abs(x)>bound))
        margin_hist.append(float(np.min(bound-np.abs(x))))
        ages.append(float(np.mean(age)))
        # Occasional disturbances make safety risk nontrivial.
        w=rng.normal(0,process_std,n_plants)
        if rng.random()<.025:
            # Rare shocks are more likely on the tight-bound/high-instability side.
            probs=np.linspace(1,4,n_plants); probs=probs/probs.sum()
            j=int(rng.choice(n_plants,p=probs)); w[j]+=rng.normal(0,.72)
        x=a*x+u+w; xh=a*xh+u; age+=1
        x=np.clip(x,-12,12); xh=np.clip(xh,-12,12)
    s=np.asarray(stage)
    return {'policy':policy,'mean_control_cost':float(s.mean()),'p95_control_cost':float(np.quantile(s,.95)),
            'safety_violation_rate':float(violations/slots),'mean_safety_margin':float(np.mean(margin_hist)),
            'mean_information_age':float(np.mean(ages)),'update_success_rate':float(success/slots)}
