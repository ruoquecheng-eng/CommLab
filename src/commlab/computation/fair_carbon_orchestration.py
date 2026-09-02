import numpy as np


def _jain(x):
    x = np.asarray(x, dtype=float)
    return float(x.sum() ** 2 / (len(x) * np.sum(x * x) + 1e-12))


def simulate_fair_carbon_orchestration(
    n_clients=24,
    select_per_round=6,
    rounds=220,
    dim=8,
    carbon_weight=0.8,
    debt_weight=0.7,
    target_participation=None,
    policy="virtual_debt",
    seed=0,
):
    """Long-horizon carbon-aware FL with virtual participation deficits.

    ``virtual_debt`` maintains a deficit queue for each client. Not selecting a
    client increases its debt relative to a target long-run participation rate;
    serving it pays debt down. This turns fairness into a persistent system
    state rather than a one-round age bonus.
    """
    if policy not in {"random", "carbon", "age_balanced", "virtual_debt"}:
        raise ValueError("unknown policy")
    if not 1 <= select_per_round <= n_clients:
        raise ValueError("bad selection count")
    rng = np.random.default_rng(seed + 2803)
    if target_participation is None:
        target_participation = 0.92 * select_per_round / n_clients

    groups = np.arange(n_clients) % 3
    local = np.zeros((n_clients, dim))
    centers = np.zeros((3, dim)); centers[0,0]=1.2; centers[1,1]=1.2; centers[2,:2]=-0.85
    local = centers[groups] + 0.13 * rng.normal(size=(n_clients, dim))
    global_opt = local.mean(axis=0)
    optimum = float(0.5 * np.mean(np.sum((global_opt[None]-local)**2, axis=1)))
    regions = groups.copy()
    base_ci = np.array([150., 350., 570.])
    energy = rng.uniform(.55, 1.35, n_clients)

    w = np.zeros(dim)
    participation = np.zeros(n_clients, dtype=int)
    age = np.zeros(n_clients)
    debt = np.zeros(n_clients)
    group_counts = np.zeros(3, dtype=int)
    loss_hist=[]; carbon_hist=[]; max_debt_hist=[]

    for t in range(rounds):
        ci = base_ci * (1 + .28*np.sin(2*np.pi*t/52 + np.array([0.,1.8,3.0])))
        ci = np.maximum(ci, 65.)
        carbon = energy * ci[regions] / 1000
        grads = w[None] - local + .035*rng.normal(size=(n_clients,dim))
        utility = np.linalg.norm(grads, axis=1)
        uz = (utility-utility.mean())/(utility.std()+1e-9)
        cz = (carbon-carbon.mean())/(carbon.std()+1e-9)

        if policy == "random":
            chosen = rng.choice(n_clients, select_per_round, replace=False)
        elif policy == "carbon":
            chosen = np.argpartition(carbon, select_per_round-1)[:select_per_round]
        elif policy == "age_balanced":
            score = uz - carbon_weight*cz + .55*age/(1+age.mean())
            chosen = np.argpartition(-score, select_per_round-1)[:select_per_round]
        else:
            dz = debt / (1 + debt.mean())
            score = uz - carbon_weight*cz + debt_weight*dz
            chosen = np.argpartition(-score, select_per_round-1)[:select_per_round]

        w -= .18 * grads[chosen].mean(axis=0)
        participation[chosen] += 1
        for g in groups[chosen]: group_counts[g] += 1
        age += 1; age[chosen] = 0
        served = np.zeros(n_clients); served[chosen] = 1
        debt = np.maximum(0.0, debt + target_participation - served)
        carbon_hist.append(float(carbon[chosen].sum()))
        max_debt_hist.append(float(debt.max()))
        loss_hist.append(float(.5*np.mean(np.sum((w[None]-local)**2,axis=1))))

    achieved = participation / rounds
    return {
        "policy": policy,
        "final_loss": float(loss_hist[-1]),
        "optimal_loss": optimum,
        "excess_loss": float(loss_hist[-1]-optimum),
        "total_carbon_proxy": float(np.sum(carbon_hist)),
        "participation_jain": _jain(participation),
        "minimum_participation_rate": float(achieved.min()),
        "maximum_participation_rate": float(achieved.max()),
        "target_participation_rate": float(target_participation),
        "participation_shortfall_fraction": float(np.mean(achieved + 1e-12 < target_participation)),
        "final_max_virtual_debt": float(debt.max()),
        "mean_max_virtual_debt": float(np.mean(max_debt_hist)),
        "group_selection_fraction": group_counts / max(group_counts.sum(),1),
        "loss_history": np.asarray(loss_hist),
        "carbon_history": np.asarray(carbon_hist),
        "debt_history": np.asarray(max_debt_hist),
    }
