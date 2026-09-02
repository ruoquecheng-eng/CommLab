import numpy as np


def _jain(x):
    x = np.asarray(x, dtype=float)
    return float((x.sum() ** 2) / (len(x) * np.sum(x * x) + 1e-12))


def simulate_carbon_aware_federated(
    n_clients=24,
    select_per_round=6,
    rounds=160,
    dim=8,
    carbon_weight=0.8,
    fairness_weight=0.45,
    policy="balanced",
    seed=0,
):
    """Toy FL orchestration with time-varying carbon intensity.

    Clients belong to three data groups and three grid regions. The cleanest
    grid is deliberately correlated with one data group so that carbon-only
    scheduling can create statistical selection bias. ``balanced`` trades off
    gradient utility, carbon cost, and participation age.

    Carbon is a transparent proxy (gCO2e-like arbitrary units) based on modeled
    per-round device energy times a time-varying regional intensity; it is not a
    lifecycle carbon accounting tool.
    """
    if policy not in {"random", "utility", "carbon", "balanced"}:
        raise ValueError("unknown policy")
    if not 1 <= select_per_round <= n_clients:
        raise ValueError("bad selection count")
    rng = np.random.default_rng(seed + 2702)

    groups = np.arange(n_clients) % 3
    # Three symmetric but distinct local optima; their average is near zero.
    basis = np.zeros((3, dim))
    basis[0, 0] = 1.25
    basis[1, 1] = 1.25
    basis[2, :2] = -0.9
    local_opt = basis[groups] + 0.12 * rng.normal(size=(n_clients, dim))
    global_opt = local_opt.mean(axis=0)
    optimal_loss = float(0.5 * np.mean(np.sum((global_opt[None, :] - local_opt) ** 2, axis=1)))

    # Region assignment is correlated with data group; region 0 is usually
    # cleaner, making carbon-only selection statistically biased.
    regions = groups.copy()
    base_ci = np.array([170.0, 360.0, 540.0])
    energy_j = rng.uniform(0.55, 1.35, size=n_clients)
    latency_ms = rng.uniform(18, 85, size=n_clients)

    w = np.zeros(dim)
    participation = np.zeros(n_clients, dtype=int)
    age = np.zeros(n_clients, dtype=float)
    loss_hist, carbon_hist, latency_hist = [], [], []
    group_counts = np.zeros(3, dtype=int)
    lr = 0.18

    for t in range(rounds):
        # Diurnal-ish regional carbon variation with phase shifts.
        ci = base_ci * (1 + 0.28 * np.sin(2 * np.pi * t / 48 + np.array([0.0, 1.7, 3.1])))
        ci = np.maximum(ci, 70.0)
        carbon_cost = energy_j * ci[regions] / 1000.0
        grads = w[None, :] - local_opt + 0.035 * rng.normal(size=(n_clients, dim))
        utility = np.linalg.norm(grads, axis=1)

        if policy == "random":
            chosen = rng.choice(n_clients, select_per_round, replace=False)
        elif policy == "utility":
            chosen = np.argpartition(-utility, select_per_round - 1)[:select_per_round]
        elif policy == "carbon":
            chosen = np.argpartition(carbon_cost, select_per_round - 1)[:select_per_round]
        else:
            uz = (utility - utility.mean()) / (utility.std() + 1e-9)
            cz = (carbon_cost - carbon_cost.mean()) / (carbon_cost.std() + 1e-9)
            az = age / (1 + age.mean())
            score = uz - carbon_weight * cz + fairness_weight * az
            chosen = np.argpartition(-score, select_per_round - 1)[:select_per_round]

        grad = grads[chosen].mean(axis=0)
        w -= lr * grad
        participation[chosen] += 1
        for g in groups[chosen]:
            group_counts[g] += 1
        age += 1
        age[chosen] = 0
        carbon_hist.append(float(np.sum(carbon_cost[chosen])))
        latency_hist.append(float(np.max(latency_ms[chosen])))
        loss_hist.append(float(0.5 * np.mean(np.sum((w[None, :] - local_opt) ** 2, axis=1))))

    return {
        "policy": policy,
        "final_loss": float(loss_hist[-1]),
        "optimal_loss": optimal_loss,
        "excess_loss": float(loss_hist[-1] - optimal_loss),
        "mean_last20_loss": float(np.mean(loss_hist[-20:])),
        "total_carbon_proxy": float(np.sum(carbon_hist)),
        "mean_round_carbon_proxy": float(np.mean(carbon_hist)),
        "p95_round_latency_ms": float(np.quantile(latency_hist, 0.95)),
        "participation_jain": _jain(participation),
        "group_selection_fraction": group_counts / max(group_counts.sum(), 1),
        "loss_history": np.asarray(loss_hist),
        "carbon_history": np.asarray(carbon_hist),
        "participation": participation,
    }
