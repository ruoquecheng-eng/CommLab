import numpy as np

from .downlink_differential import _packet_success_probability


def simulate_task_aware_model_repair(
    n_clients=24,
    rounds=180,
    dim=24,
    mean_snr_db=7.0,
    snr_std_db=5.0,
    policy="task_aware",
    repair_budget_per_round=0.11,
    global_keyframe_interval=36,
    delta_fraction=0.16,
    burst_strength=2.4,
    seed=0,
):
    """ACK-aware differential downlink repair driven by *current task demand*.

    A client whose chained model state is broken can be repaired using a
    client-specific snapshot. Policies differ only in how the same saved repair
    budget is allocated: by version age, static importance, or current
    task-demand-weighted utility loss. This couples model synchronization to the
    application workload rather than treating every stale client as equally
    urgent.
    """
    if policy not in {"age_only", "static_importance", "task_aware"}:
        raise ValueError("unknown policy")
    if n_clients < 2 or rounds < 20 or repair_budget_per_round <= 0:
        raise ValueError("invalid setup")
    rng = np.random.default_rng(seed + 2901)

    base_snr = np.clip(rng.normal(mean_snr_db, snr_std_db, n_clients), -12, 24)
    z = (base_snr - base_snr.mean()) / (base_snr.std() + 1e-9)
    # High-value clients are deliberately not identical to strong-channel users.
    static_importance = np.exp(0.55 * (-0.45 * z + rng.normal(0, 0.8, n_clients)))
    static_importance /= static_importance.mean()
    phase = rng.uniform(0, 2 * np.pi, n_clients)

    model = np.zeros(dim)
    velocity = np.zeros(dim)
    models = [model.copy()]
    for _ in range(1, rounds):
        velocity = 0.82 * velocity + 0.055 * rng.normal(size=dim)
        model = model + velocity
        models.append(model.copy())
    models = np.asarray(models)

    client_model = np.zeros((n_clients, dim))
    last_version = np.zeros(n_clients, dtype=int)
    chain_ok = np.ones(n_clients, dtype=bool)
    credit = 0.0
    total_size = 0.0
    repair_tx = repair_ok = keyframes = 0
    task_utility = ideal_task_utility = 0.0
    active_task_age = []
    weighted_age_hist = []
    demand_hist = []

    for t in range(1, rounds):
        common_fade = 1.0 * np.sin(2 * np.pi * t / 71)
        if 76 <= t < 92:
            common_fade -= 4.5
        snr_t = np.clip(base_snr + common_fade + rng.normal(0, 0.8, n_clients), -14, 27)

        # Differential update is broadcast every round.
        p_delta = _packet_success_probability(snr_t, delta_fraction)
        got = rng.random(n_clients) < p_delta
        applicable = got & chain_ok & (last_version == t - 1)
        client_model[applicable] += models[t] - models[t - 1]
        last_version[applicable] = t
        chain_ok[~applicable] = False
        total_size += delta_fraction

        # Time-varying inference/task demand. Bursts move across clients, so a
        # static importance score can spend repair budget at the wrong time.
        seasonal = 0.55 + 0.45 * np.maximum(0, np.sin(2 * np.pi * t / 47 + phase))
        burst_center = int((t // 24) % n_clients)
        dist = np.minimum((np.arange(n_clients) - burst_center) % n_clients,
                          (burst_center - np.arange(n_clients)) % n_clients)
        burst = 1.0 + burst_strength * np.exp(-(dist / 2.4) ** 2)
        lam = 0.10 * seasonal * burst * np.sqrt(static_importance)
        tasks = rng.poisson(lam)
        demand_hist.append(float(tasks.sum()))

        if t % global_keyframe_interval == 0:
            p = _packet_success_probability(snr_t, 1.0)
            ok = rng.random(n_clients) < p
            client_model[ok] = models[t]
            last_version[ok] = t
            chain_ok[ok] = True
            total_size += 1.0
            keyframes += 1

        credit += repair_budget_per_round
        for _ in range(n_clients):
            broken = ~chain_ok
            if not np.any(broken):
                break
            age = t - last_version
            size = np.minimum(0.70, 0.18 + 0.025 * age)
            p = _packet_success_probability(snr_t, size)
            base = age * p / np.maximum(size, 1e-9)
            if policy == "age_only":
                score = base
            elif policy == "static_importance":
                score = base * static_importance
            else:
                # Expected immediate task loss without repair. +0.12 prevents a
                # permanently idle client from being starved forever.
                score = base * static_importance * (tasks + 0.12)
            score = np.where(broken, score, -np.inf)
            i = int(np.argmax(score))
            if not np.isfinite(score[i]) or credit + 1e-12 < size[i]:
                break
            credit -= float(size[i])
            total_size += float(size[i])
            repair_tx += 1
            if rng.random() < p[i]:
                repair_ok += 1
                client_model[i] = models[t]
                last_version[i] = t
                chain_ok[i] = True

        age = t - last_version
        # Fresh-model task utility decays with model version age. The ideal uses
        # the same realized tasks but zero age, so ratios are meaningful.
        per_task_value = static_importance * np.exp(-age / 7.0)
        task_utility += float(np.sum(tasks * per_task_value))
        ideal_task_utility += float(np.sum(tasks * static_importance))
        if tasks.sum() > 0:
            active_task_age.append(float(np.sum(tasks * static_importance * age) /
                                         np.sum(tasks * static_importance)))
        weighted_age_hist.append(float(np.sum(static_importance * age) / np.sum(static_importance)))

    return {
        "policy": policy,
        "task_utility_ratio": float(task_utility / max(ideal_task_utility, 1e-12)),
        "mean_active_task_model_age": float(np.mean(active_task_age) if active_task_age else 0.0),
        "mean_static_weighted_model_age": float(np.mean(weighted_age_hist)),
        "normalized_downlink_size_per_round": float(total_size / (rounds - 1)),
        "repair_transmissions": int(repair_tx),
        "repair_success_fraction": float(repair_ok / max(repair_tx, 1)),
        "keyframes": int(keyframes),
        "mean_tasks_per_round": float(np.mean(demand_hist)),
    }
