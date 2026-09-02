import numpy as np


def _choose_initial_cache(popularity, value, sizes, capacity):
    score = popularity * value / sizes
    order = np.argsort(-score)
    out = set(); used = 0.0
    for i in order:
        if used + sizes[i] <= capacity + 1e-9:
            out.add(int(i)); used += float(sizes[i])
    return out


def simulate_congested_model_refresh(
    n_requests=4200,
    n_models=8,
    cache_capacity_mb=650.0,
    policy="congestion_aware",
    refresh_interval=40,
    backhaul_service_mb_per_request=2.8,
    seed=0,
):
    """Versioned edge-model cache with an explicit refresh backhaul queue.

    Refreshing every stale model can overload the backhaul. A refresh job carries
    a target version and only updates the cache after the requested bytes have
    actually been served. ``congestion_aware`` prices refresh value by model age,
    task demand, transfer size, and current queue pressure.
    """
    if policy not in {"eager", "periodic_value", "congestion_aware"}:
        raise ValueError("unknown policy")
    if n_requests < 100 or refresh_interval < 5 or backhaul_service_mb_per_request <= 0:
        raise ValueError("invalid setup")
    rng = np.random.default_rng(seed + 2902)

    sizes = rng.uniform(80, 230, n_models)
    edge_ms = rng.uniform(7, 20, n_models)
    cloud_ms = edge_ms + rng.uniform(70, 145, n_models)
    value = rng.uniform(0.7, 1.5, n_models)
    update_prob = rng.uniform(0.004, 0.035, n_models)
    sensitivity = rng.uniform(0.05, 0.16, n_models)

    x = np.arange(n_models)
    centers = [1.0, n_models - 2.0, (n_models - 1) / 2]
    pops = []
    for c in centers:
        p = np.exp(-0.5 * ((x - c) / 1.45) ** 2) + 0.04
        pops.append(p / p.sum())
    pops = np.asarray(pops)

    cache = _choose_initial_cache(pops[0], value, sizes, cache_capacity_mb)
    current_version = np.zeros(n_models, dtype=int)
    cache_version = np.full(n_models, -1, dtype=int)
    for i in cache: cache_version[i] = 0

    recent = np.ones(n_models) * 1e-3
    queue = []  # jobs: [model, target_version, remaining_mb]
    queued_models = set()
    requested_mb = 0.0; delivered_mb = 0.0; completed_refresh = 0
    lat_hist=[]; utility_hist=[]; age_hist=[]; q_hist=[]; stale_hits=hits=0

    phase_len = int(np.ceil(n_requests / 3))
    for t in range(n_requests):
        current_version += (rng.random(n_models) < update_prob).astype(int)
        phase = min(t // phase_len, 2)
        p = pops[phase]
        m = int(rng.choice(n_models, p=p))
        recent *= 0.985; recent[m] += 1.0

        if m in cache:
            hits += 1
            age = int(current_version[m] - cache_version[m])
            stale_hits += int(age > 0)
            lat = edge_ms[m]
            util = value[m] * np.exp(-sensitivity[m] * age)
        else:
            age = 0
            lat = cloud_ms[m]
            util = value[m]
        lat_hist.append(float(lat)); utility_hist.append(float(util)); age_hist.append(float(age))

        if t > 0 and t % refresh_interval == 0:
            stale = [i for i in cache if current_version[i] > cache_version[i] and i not in queued_models]
            if stale:
                pop_est = recent / recent.sum()
                q_pressure = sum(j[2] for j in queue) / max(backhaul_service_mb_per_request * refresh_interval, 1e-9)
                candidates=[]
                for i in stale:
                    age_i = current_version[i] - cache_version[i]
                    gain = pop_est[i] * value[i] * (1 - np.exp(-sensitivity[i] * age_i))
                    if policy == "eager":
                        score = age_i + 1e-6
                    elif policy == "periodic_value":
                        score = gain / sizes[i]
                    else:
                        score = gain / (sizes[i] * (1 + 0.8 * q_pressure))
                    candidates.append((score, i))
                candidates.sort(reverse=True)
                if policy == "eager":
                    chosen = [i for _,i in candidates]
                elif policy == "periodic_value":
                    chosen = [i for _,i in candidates[:max(1, len(candidates)//2)]]
                else:
                    # Admission threshold rises with congestion; unused refresh
                    # opportunities are allowed instead of forcing the queue full.
                    threshold = 1.1e-5 * (1 + q_pressure)
                    chosen = [i for s,i in candidates if s > threshold][:2]
                for i in chosen:
                    queue.append([i, int(current_version[i]), float(sizes[i])])
                    queued_models.add(i); requested_mb += float(sizes[i])

        # Backhaul queue service per inference request.
        service = backhaul_service_mb_per_request
        while queue and service > 1e-12:
            job = queue[0]
            xfer = min(service, job[2]); job[2] -= xfer; service -= xfer; delivered_mb += xfer
            if job[2] <= 1e-12:
                i, target, _ = queue.pop(0)
                cache_version[i] = max(cache_version[i], target)
                queued_models.discard(i); completed_refresh += 1
            else:
                break
        q_hist.append(float(sum(j[2] for j in queue)))

    return {
        "policy": policy,
        "cache_hit_rate": float(hits / n_requests),
        "stale_hit_fraction": float(stale_hits / max(hits,1)),
        "mean_served_version_age": float(np.mean(age_hist)),
        "mean_task_utility": float(np.mean(utility_hist)),
        "mean_latency_ms": float(np.mean(lat_hist)),
        "refresh_requested_mb": float(requested_mb),
        "refresh_delivered_mb": float(delivered_mb),
        "completed_refresh_jobs": int(completed_refresh),
        "mean_backhaul_queue_mb": float(np.mean(q_hist)),
        "p95_backhaul_queue_mb": float(np.quantile(q_hist, .95)),
        "final_backhaul_queue_mb": float(q_hist[-1] if q_hist else 0.0),
    }
