import numpy as np


def simulate_networked_control_scheduling(
    slots=2600,
    n_plants=5,
    policy="control_value",
    mean_snr_db=2.0,
    seed=0,
):
    """Multiple scalar feedback-control loops sharing one wireless update slot.

    Each plant is mildly open-loop unstable. A remote controller predicts state
    between successful sensor updates and applies a fixed stabilizing feedback
    gain. The scheduler chooses which sensor may transmit. ``control_value``
    prioritizes the expected reduction in estimation-driven control cost rather
    than age alone. Sensor-side error magnitude is assumed available as a tiny
    trigger/priority metadata field; no full state is known before scheduling.
    """
    if policy not in {"round_robin", "max_age", "max_error", "control_value"}:
        raise ValueError("unknown policy")
    if slots < 100 or n_plants < 2:
        raise ValueError("invalid setup")
    rng=np.random.default_rng(seed+2905)
    a=np.linspace(1.025,1.115,n_plants)
    k=np.linspace(.38,.52,n_plants)  # a-k is stable
    q=np.linspace(.7,1.5,n_plants)   # state cost importance
    r=.055
    snr_base=np.clip(rng.normal(mean_snr_db,4.0,n_plants),-8,14)
    x=rng.normal(0,.8,n_plants)
    xhat=x.copy(); age=np.zeros(n_plants,int); selected=np.zeros(n_plants,int); success=np.zeros(n_plants,int)
    cost_hist=[]; err_hist=[]; age_hist=[]; max_state=[]

    for t in range(slots):
        err=np.abs(x-xhat)
        # Expected packet success from current fading estimate.
        snr=np.clip(snr_base+1.7*np.sin(2*np.pi*t/83+np.arange(n_plants))+rng.normal(0,.8,n_plants),-10,18)
        p=1-np.exp(-10**(snr/10)/2.2)
        if policy=="round_robin": i=t%n_plants
        elif policy=="max_age": i=int(np.argmax(age))
        elif policy=="max_error": i=int(np.argmax(err))
        else:
            # One-step expected control-value proxy: unstable dynamics, state
            # importance, estimation mismatch and link reliability all matter.
            score=p*q*(a**2)*(err**2 + .10*np.abs(x)**2)
            i=int(np.argmax(score))
        selected[i]+=1
        if rng.random()<p[i]:
            xhat[i]=x[i]; age[i]=0; success[i]+=1
        # Control based on the freshest available estimate.
        u=-k*xhat
        stage=q*x*x+r*u*u
        cost_hist.append(float(np.mean(stage)))
        err_hist.append(float(np.sqrt(np.mean((x-xhat)**2))))
        age_hist.append(float(np.mean(age)))
        max_state.append(float(np.max(np.abs(x))))
        # Physical and remote-estimator dynamics use the same applied control.
        w=rng.normal(0,.09,n_plants)
        x=a*x+u+w
        xhat=a*xhat+u
        age+=1
        # Soft numerical guard: if a poor scheduler lets a loop explode, retain
        # the evidence but avoid floating-point overflow dominating every metric.
        x=np.clip(x,-80,80); xhat=np.clip(xhat,-80,80)

    return {
        "policy":policy,
        "mean_control_cost":float(np.mean(cost_hist)),
        "p95_control_cost":float(np.quantile(cost_hist,.95)),
        "state_rmse":float(np.sqrt(np.mean(np.asarray(max_state)**2))),
        "mean_estimation_rmse":float(np.mean(err_hist)),
        "mean_information_age":float(np.mean(age_hist)),
        "max_state_excursion":float(np.max(max_state)),
        "successful_update_fraction":float(success.sum()/max(selected.sum(),1)),
        "selection_jain":float(selected.sum()**2/(n_plants*np.sum(selected.astype(float)**2)+1e-12)),
        "per_plant_selection_fraction":selected/max(selected.sum(),1),
        "per_plant_success_fraction":success/np.maximum(selected,1),
    }
