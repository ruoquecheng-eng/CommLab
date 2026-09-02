import numpy as np


def _jain(x):
    x=np.asarray(x,float); return float(x.sum()**2/(len(x)*np.sum(x*x)+1e-12))


def simulate_battery_carbon_fair_fl(
    n_clients=24,
    rounds=240,
    select_per_round=6,
    policy="debt_battery_carbon",
    harvest_scale=0.45,
    carbon_weight=0.8,
    debt_weight=4.0,
    seed=0,
):
    """Long-horizon FL orchestration with participation debt and energy causality.

    Clients differ in local optima, carbon intensity, channel cost, battery size,
    and stochastic renewable/ambient energy harvesting. The best score is useless
    if a device cannot pay the round energy cost; the controller therefore trades
    learning contribution, persistent fairness debt, carbon, and battery margin.
    """
    if policy not in {"random_feasible", "carbon_only", "debt_carbon", "debt_battery_carbon"}:
        raise ValueError("unknown policy")
    if select_per_round < 1 or select_per_round > n_clients or rounds < 20:
        raise ValueError("invalid setup")
    rng=np.random.default_rng(seed+2903)
    dim=5
    group=np.arange(n_clients)%2
    local=rng.normal(0,.18,(n_clients,dim))
    local[group==0,0]-=.75; local[group==1,0]+=.75
    # Low-carbon region is correlated with one data group to make carbon-only
    # selection statistically biased.
    carbon=rng.uniform(.55,.9,n_clients); carbon[group==1]+=rng.uniform(.55,.95,(group==1).sum())
    snr=rng.normal(6,4,n_clients)
    comm_cost=.20 + .42/(1+10**(snr/10))
    compute_cost=rng.uniform(.18,.42,n_clients)
    energy_cost=comm_cost+compute_cost
    capacity=rng.uniform(2.2,4.5,n_clients)
    battery=capacity*rng.uniform(.45,.8,n_clients)
    harvest_base=rng.uniform(.16,.48,n_clients)*harvest_scale
    importance=rng.uniform(.8,1.3,n_clients)
    optimum=np.mean(local,axis=0); optimum_loss=float(.5*np.mean(np.sum((optimum-local)**2,axis=1)))
    w=np.zeros(dim); participation=np.zeros(n_clients,int); debt=np.zeros(n_clients); target=select_per_round/n_clients
    carbon_hist=[]; loss_hist=[]; underfill=0; outage_attempts=0; batt_hist=[]

    for t in range(rounds):
        harvest=rng.exponential(harvest_base)
        battery=np.minimum(capacity,battery+harvest)
        feasible=battery+1e-12>=energy_cost
        grads=w[None]-local
        contribution=np.linalg.norm(grads,axis=1)*importance
        c=(carbon-carbon.mean())/(carbon.std()+1e-9)
        d=debt/(1+debt.mean())
        margin=np.clip((battery-energy_cost)/capacity,-1,1)
        if policy=="random_feasible":
            ids=np.flatnonzero(feasible); rng.shuffle(ids); chosen=ids[:select_per_round]
        else:
            if policy=="carbon_only": score=-carbon_weight*c
            elif policy=="debt_carbon": score=0.45*contribution-carbon_weight*c+debt_weight*d
            else: score=0.45*contribution-carbon_weight*c+debt_weight*d+1.3*margin
            score=np.where(feasible,score,-np.inf)
            order=np.argsort(-score); chosen=order[np.isfinite(score[order])][:select_per_round]
        if len(chosen)<select_per_round: underfill+=1
        outage_attempts += int(np.sum(~feasible))
        if len(chosen):
            w -= .16*grads[chosen].mean(axis=0)
            battery[chosen]-=energy_cost[chosen]
            participation[chosen]+=1
            carbon_hist.append(float(np.sum(carbon[chosen]*energy_cost[chosen])))
        else:
            carbon_hist.append(0.0)
        served=np.zeros(n_clients); served[chosen]=1
        debt=np.maximum(0,debt+target-served)
        loss_hist.append(float(.5*np.mean(np.sum((w[None]-local)**2,axis=1))))
        batt_hist.append(float(np.mean(battery/capacity)))

    rate=participation/rounds
    return {
        "policy":policy,
        "final_loss":float(loss_hist[-1]),
        "optimal_loss":optimum_loss,
        "excess_loss":float(loss_hist[-1]-optimum_loss),
        "total_carbon_proxy":float(np.sum(carbon_hist)),
        "participation_jain":_jain(participation),
        "minimum_participation_rate":float(rate.min()),
        "group0_selection_fraction":float(participation[group==0].sum()/max(participation.sum(),1)),
        "underfilled_round_fraction":float(underfill/rounds),
        "mean_fraction_clients_energy_infeasible":float(outage_attempts/(rounds*n_clients)),
        "mean_battery_fraction":float(np.mean(batt_hist)),
        "final_max_virtual_debt":float(debt.max()),
    }
