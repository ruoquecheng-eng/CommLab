import numpy as np


def _greedy_cache(score, sizes, capacity):
    order = np.argsort(-(score / np.maximum(sizes, 1e-9)))
    out, used = set(), 0.0
    for i in order:
        if used + sizes[i] <= capacity + 1e-9:
            out.add(int(i)); used += float(sizes[i])
    return out


def simulate_version_aware_edge_caching(
    n_requests=5000,
    n_models=8,
    cache_capacity_mb=700.0,
    policy="version_value",
    refresh_interval=100,
    refresh_budget_mb=260.0,
    seed=0,
):
    """Edge-model caching with model-version freshness and refresh traffic.

    Model versions evolve independently. A cached hit can therefore be stale.
    Task utility decays with version age, while cloud fallback is fresh but slow.
    Policies trade popularity, cloud-latency saving, staleness and model-transfer
    cost. ``version_value`` refreshes/caches by expected task-value gain per MB.
    """
    if policy not in {"popularity", "latency_value", "version_value", "lru"}:
        raise ValueError("unknown policy")
    if n_models < 3 or n_requests < 20 or refresh_interval < 5 or refresh_budget_mb <= 0:
        raise ValueError("invalid setup")
    rng = np.random.default_rng(seed + 2802)

    sizes = np.linspace(85, 235, n_models) * rng.uniform(0.9, 1.1, n_models)
    edge_ms = np.linspace(7, 24, n_models) * rng.uniform(0.92, 1.08, n_models)
    cloud_ms = edge_ms + rng.uniform(65, 145, n_models)
    # Some models evolve rapidly, others slowly.
    update_prob = np.linspace(0.006, 0.045, n_models)[rng.permutation(n_models)]
    sensitivity = rng.uniform(0.055, 0.18, n_models)  # utility decay per missed version
    task_value = rng.uniform(0.7, 1.5, n_models)

    x = np.arange(n_models)
    centers = [1.0, n_models - 2.0, (n_models - 1) / 2]
    pops = []
    for c in centers:
        p = np.exp(-0.5 * ((x - c) / 1.4) ** 2) + 0.06
        p /= p.sum(); pops.append(p)
    pops = np.asarray(pops)

    current_version = np.zeros(n_models, dtype=int)
    cache_version = np.full(n_models, -1, dtype=int)
    recent = np.ones(n_models) * 1e-3
    last_used = np.full(n_models, -10**9, dtype=int)

    init_score = pops[0] * task_value
    cache = _greedy_cache(init_score, sizes, cache_capacity_mb)
    for i in cache:
        cache_version[i] = current_version[i]
    backhaul_mb = float(np.sum(sizes[list(cache)]))
    refresh_mb = backhaul_mb
    request_backhaul_mb = 0.0
    latency, utility, ages, hit = [], [], [], []
    refresh_events = 1

    phase_len = int(np.ceil(n_requests / 3))
    for t in range(n_requests):
        # Independent model evolution; version counters are the hidden state that
        # a conventional hit-rate cache ignores.
        current_version += (rng.random(n_models) < update_prob).astype(int)
        phase = min(t // phase_len, 2)
        p = pops[phase]
        m = int(rng.choice(n_models, p=p))
        recent *= 0.988; recent[m] += 1
        is_hit = m in cache
        hit.append(is_hit)

        if is_hit:
            age = int(current_version[m] - cache_version[m])
            q = float(np.exp(-sensitivity[m] * age))
            latency.append(float(edge_ms[m] + rng.lognormal(-1.1, .22)))
            utility.append(float(task_value[m] * q))
            ages.append(age)
            last_used[m] = t
        else:
            # Cloud always uses the current version.
            latency.append(float(cloud_ms[m] + rng.lognormal(1.3, .22)))
            utility.append(float(task_value[m]))
            ages.append(0)
            request_backhaul_mb += 1.5
            if policy == "lru" and sizes[m] <= cache_capacity_mb:
                while sum(sizes[list(cache)]) + sizes[m] > cache_capacity_mb and cache:
                    victim = min(cache, key=lambda j: last_used[j])
                    cache.remove(victim); cache_version[victim] = -1
                if m not in cache:
                    cache.add(m); cache_version[m] = current_version[m]
                    backhaul_mb += float(sizes[m]); refresh_mb += float(sizes[m]); refresh_events += 1
                last_used[m] = t

        if policy != "lru" and (t + 1) % refresh_interval == 0:
            pop_est = recent / recent.sum()
            age = np.maximum(current_version - np.maximum(cache_version, 0), 0)
            latency_saving = cloud_ms - edge_ms
            if policy == "popularity":
                score = pop_est
            elif policy == "latency_value":
                score = pop_est * latency_saving * task_value
            else:
                # Expected value of holding a *fresh* edge copy rather than a
                # stale cached copy or a cloud miss. This rewards popular models
                # whose versions drift quickly and whose task utility is sensitive.
                stale_loss = 1 - np.exp(-sensitivity * age)
                score = pop_est * task_value * (0.35 * latency_saving / latency_saving.mean() + 1.7 * stale_loss + 0.25)
            desired_cache = _greedy_cache(score, sizes, cache_capacity_mb)
            if policy == "version_value":
                # A hard per-refresh transfer budget prevents version-awareness
                # from winning simply by downloading every model update. Candidate
                # actions (new model fills or differential refreshes) are ranked by
                # expected task-utility gain per MB.
                budget = float(refresh_budget_mb)
                working = set(cache)
                actions = []
                for i in desired_cache:
                    if i not in cache:
                        cost = float(sizes[i])
                        benefit = float(pop_est[i] * task_value[i] * (1 + (cloud_ms[i]-edge_ms[i])/100))
                        actions.append((benefit/max(cost,1e-9), 'add', int(i), cost))
                    else:
                        gap = int(current_version[i] - max(cache_version[i], 0))
                        if gap > 0:
                            frac = min(1.0, 0.12 + 0.075 * gap)
                            cost = float(sizes[i] * frac)
                            stale_loss = 1 - np.exp(-sensitivity[i] * gap)
                            benefit = float(pop_est[i] * task_value[i] * stale_loss)
                            actions.append((benefit/max(cost,1e-9), 'refresh', int(i), cost))
                for _, kind, i, cost in sorted(actions, reverse=True):
                    if cost > budget + 1e-9:
                        continue
                    if kind == 'add':
                        # Free capacity using the least valuable cached item.
                        while sum(sizes[list(working)]) + sizes[i] > cache_capacity_mb and working:
                            victim = min(working, key=lambda j: score[j]/max(sizes[j],1e-9))
                            working.remove(victim); cache_version[victim] = -1
                        if sum(sizes[list(working)]) + sizes[i] <= cache_capacity_mb + 1e-9:
                            working.add(i); cache_version[i] = current_version[i]
                            budget -= cost; backhaul_mb += cost; refresh_mb += cost; refresh_events += 1
                    else:
                        if i in working:
                            cache_version[i] = current_version[i]
                            budget -= cost; backhaul_mb += cost; refresh_mb += cost; refresh_events += 1
                cache = working
            else:
                new_cache = desired_cache
                for i in new_cache:
                    if i not in cache:
                        backhaul_mb += float(sizes[i]); refresh_mb += float(sizes[i]); refresh_events += 1
                        cache_version[i] = current_version[i]
                for i in cache - new_cache:
                    cache_version[i] = -1
                cache = new_cache

    latency = np.asarray(latency); utility = np.asarray(utility); ages = np.asarray(ages)
    return {
        "policy": policy,
        "cache_hit_rate": float(np.mean(hit)),
        "mean_latency_ms": float(np.mean(latency)),
        "p95_latency_ms": float(np.quantile(latency, .95)),
        "mean_task_utility": float(np.mean(utility)),
        "mean_served_version_age": float(np.mean(ages)),
        "p95_served_version_age": float(np.quantile(ages, .95)),
        "backhaul_mb": float(backhaul_mb + request_backhaul_mb),
        "model_refresh_mb": float(refresh_mb),
        "request_backhaul_mb": float(request_backhaul_mb),
        "refresh_events": int(refresh_events),
    }
