import numpy as np
from commlab.information_theory.finite_blocklength import normal_approximation_error_probability


def simulate_energy_harvesting_aoi(true_snr_db: np.ndarray,
                                    harvest_probabilities: np.ndarray,
                                    battery_capacity: int=4,
                                    blocklength: int=90, rate: float=1.0,
                                    policy: str="age_reliability",
                                    seed: int=1) -> dict:
    """Generate-at-will AoI scheduling with Bernoulli energy harvesting.

    One transmission costs one energy unit. Energy arrives before scheduling each
    slot and batteries saturate at ``battery_capacity``. Policies are ``max_age``,
    ``max_snr``, ``age_reliability`` and ``energy_aware``. The latter mildly
    favors high-battery users to reduce overflow while retaining freshness and
    reliability terms.
    """
    T=np.asarray(true_snr_db,float); hp=np.asarray(harvest_probabilities,float)
    if T.ndim!=2 or hp.shape!=(T.shape[1],) or np.any((hp<0)|(hp>1)):
        raise ValueError("invalid energy-AoI inputs")
    if battery_capacity<1 or policy not in {"max_age","max_snr","age_reliability","energy_aware"}:
        raise ValueError("invalid energy-AoI setting")
    rng=np.random.default_rng(seed); S,U=T.shape
    bat=np.zeros(U,dtype=int); age=np.ones(U,float); hist=np.zeros((S,U),float)
    successes=np.zeros(U,int); scheduled=np.zeros(U,int); energy_outage=0; overflow=0
    for t in range(S):
        harvest=rng.random(U)<hp
        overflow+=int(np.sum(harvest & (bat>=battery_capacity)))
        bat=np.minimum(battery_capacity,bat+harvest.astype(int))
        eligible=np.where(bat>0)[0]
        age+=1
        if len(eligible)==0:
            energy_outage+=1; hist[t]=age; continue
        snr_lin=10**(T[t,eligible]/10)
        pe=normal_approximation_error_probability(snr_lin,blocklength,rate)
        if policy=="max_age": score=age[eligible]
        elif policy=="max_snr": score=T[t,eligible]
        elif policy=="age_reliability": score=age[eligible]*(1-pe)
        else:
            score=age[eligible]*(1-pe)*(0.5+0.5*bat[eligible]/battery_capacity)
        u=int(eligible[int(np.argmax(score))]); scheduled[u]+=1; bat[u]-=1
        pe_u=float(normal_approximation_error_probability(10**(T[t,u]/10),blocklength,rate))
        if rng.random()>=pe_u:
            age[u]=1.0; successes[u]+=1
        hist[t]=age
    return {
        "mean_aoi":float(hist.mean()),
        "p95_aoi":float(np.quantile(hist,.95)),
        "per_user_mean_aoi":hist.mean(axis=0),
        "delivery_rate_per_slot":float(successes.sum()/max(S,1)),
        "energy_outage_fraction":float(energy_outage/max(S,1)),
        "harvest_overflow_events":int(overflow),
        "successes":successes,"scheduled":scheduled,
        "final_battery":bat,"age_history":hist,
    }
