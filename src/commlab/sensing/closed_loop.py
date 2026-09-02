import numpy as np

from commlab.sensing.resource_scheduling import joint_sensing_comm_resource_selection, posterior_angle_std


def simulate_sensing_on_demand(process_std_deg: np.ndarray, initial_std_deg: float,
                               candidate_elements, sensing_fractions,
                               snr_per_element_linear: float,
                               reference_std_deg: float = 2.2,
                               fixed_sensing_fraction: float | None = None) -> dict:
    """Covariance-only predictive ISAC resource-control loop.

    ``process_std_deg[t]`` grows prediction uncertainty before slot t. Adaptive
    mode chooses sensing overhead and aperture from expected net rate. Fixed mode
    uses one sensing fraction but still chooses the best aperture after the
    resulting posterior update. No target measurements are simulated here; this
    isolates uncertainty/resource feedback from estimator bias/outlier effects.
    """
    q = np.asarray(process_std_deg, float).reshape(-1)
    if len(q) == 0 or np.any(q < 0) or initial_std_deg <= 0:
        raise ValueError("invalid uncertainty trace")
    if fixed_sensing_fraction is not None and not (0 <= fixed_sensing_fraction < 1):
        raise ValueError("invalid fixed sensing fraction")
    prior = float(initial_std_deg); rows = []
    for t, proc in enumerate(q):
        prior = float(np.sqrt(prior ** 2 + proc ** 2))
        if fixed_sensing_fraction is None:
            out = joint_sensing_comm_resource_selection(prior, candidate_elements, sensing_fractions,
                                                        snr_per_element_linear, reference_std_deg)
            b = out["best"]
        else:
            f = float(fixed_sensing_fraction)
            post = posterior_angle_std(prior, f, reference_std_deg)
            cand = joint_sensing_comm_resource_selection(post, candidate_elements, [0.0],
                                                         snr_per_element_linear, reference_std_deg)
            bb = cand["best"]
            b = {"sensing_fraction": f, "elements": bb["elements"],
                 "posterior_std_deg": post, "raw_rate": bb["raw_rate"],
                 "net_rate": (1-f) * bb["raw_rate"]}
        rows.append({"slot": t, "prior_std_deg": prior, **b})
        prior = float(b["posterior_std_deg"])
    return {
        "rows": rows,
        "mean_net_rate": float(np.mean([r["net_rate"] for r in rows])),
        "mean_sensing_fraction": float(np.mean([r["sensing_fraction"] for r in rows])),
        "mean_posterior_std_deg": float(np.mean([r["posterior_std_deg"] for r in rows])),
    }


def simulate_predictive_sensing_on_demand(process_std_deg: np.ndarray, initial_std_deg: float,
                                          candidate_elements, sensing_fractions,
                                          snr_per_element_linear: float,
                                          reference_std_deg: float = 2.2,
                                          lookahead_weight: float = 0.9) -> dict:
    """Two-step sensing-on-demand controller using next-slot uncertainty value.

    The controller is deliberately small and interpretable: every candidate
    current action is scored by current net communication rate plus a discounted
    best next-slot rate under the known next process-noise scale. It therefore
    captures some value-of-information without invoking RL or a black-box policy.
    """
    q=np.asarray(process_std_deg,float).reshape(-1)
    if len(q)==0 or np.any(q<0) or initial_std_deg<=0 or lookahead_weight<0:
        raise ValueError('invalid predictive sensing inputs')
    prior=float(initial_std_deg); rows=[]
    for t,proc in enumerate(q):
        prior=float(np.sqrt(prior**2+proc**2))
        base=joint_sensing_comm_resource_selection(prior,candidate_elements,sensing_fractions,
                                                   snr_per_element_linear,reference_std_deg)
        best=None
        for row in base['rows']:
            score=float(row['net_rate'])
            if t+1<len(q):
                next_prior=float(np.sqrt(row['posterior_std_deg']**2+q[t+1]**2))
                nxt=joint_sensing_comm_resource_selection(next_prior,candidate_elements,sensing_fractions,
                                                          snr_per_element_linear,reference_std_deg)['best']
                score+=float(lookahead_weight)*float(nxt['net_rate'])
            cand=dict(row); cand['score']=score
            if best is None or score>best['score']: best=cand
        rows.append({'slot':t,'prior_std_deg':prior,**best})
        prior=float(best['posterior_std_deg'])
    return {'rows':rows,
            'mean_net_rate':float(np.mean([r['net_rate'] for r in rows])),
            'mean_sensing_fraction':float(np.mean([r['sensing_fraction'] for r in rows])),
            'mean_posterior_std_deg':float(np.mean([r['posterior_std_deg'] for r in rows]))}
