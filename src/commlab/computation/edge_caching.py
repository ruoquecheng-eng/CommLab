import numpy as np


def _greedy_value_cache(popularity, sizes, values, capacity):
    order = np.argsort(-(popularity * values / sizes))
    chosen = []
    used = 0.0
    for i in order:
        if used + sizes[i] <= capacity + 1e-9:
            chosen.append(int(i)); used += float(sizes[i])
    return set(chosen)


def simulate_edge_model_caching(
    n_requests=5000,
    n_models=8,
    cache_capacity_mb=720.0,
    policy="periodic_value",
    recache_interval=160,
    popularity_drift=0.85,
    seed=0,
):
    """Slow-timescale AI-model caching plus fast inference routing.

    A request is served at the edge when its model is cached; otherwise it uses
    a cloud/backhaul path. Cache refreshes consume model-transfer traffic. The
    workload has three popularity phases, exposing the tradeoff between stale
    caches and excessive cache churn.

    Policies: ``static`` (initial popularity only), ``lru`` (reactive),
    ``periodic_popularity`` and ``periodic_value`` (popularity times latency
    saving per MB). This is a transparent caching baseline, not an RL system.
    """
    if policy not in {"static", "lru", "periodic_popularity", "periodic_value", "oracle_phase"}:
        raise ValueError("unknown policy")
    if n_models < 3 or n_requests < 10 or cache_capacity_mb <= 0:
        raise ValueError("invalid setup")
    rng = np.random.default_rng(seed + 2703)

    if n_models == 8:
        # Deliberately decouple model size, popularity and cloud penalty. A pure
        # hit-rate policy may cache a large popular model whose cloud fallback is
        # relatively cheap, whereas value-density can prefer a smaller model with
        # a much larger latency saving per cached MB.
        sizes = np.array([90, 145, 225, 105, 265, 155, 205, 100.], dtype=float)
        edge_ms = np.array([8, 13, 24, 10, 29, 16, 21, 9.], dtype=float)
        extra = np.array([155, 82, 52, 138, 42, 98, 62, 145.], dtype=float)
        sizes *= rng.uniform(.96, 1.04, n_models)
        edge_ms *= rng.uniform(.97, 1.03, n_models)
        cloud_ms = edge_ms + extra * rng.uniform(.96, 1.04, n_models)
    else:
        sizes = np.linspace(90, 240, n_models) * rng.uniform(0.88, 1.12, n_models)
        edge_ms = np.linspace(8, 28, n_models) * rng.uniform(0.9, 1.1, n_models)
        cloud_ms = edge_ms + rng.uniform(65, 125, n_models)
    saving = cloud_ms - edge_ms

    # Phase 1 favors low IDs, phase 2 high IDs, phase 3 middle IDs.
    x = np.arange(n_models)
    centers = [1.2, n_models - 2.0, (n_models - 1) / 2]
    pops = []
    for c in centers:
        p = np.exp(-0.5 * ((x - c) / 1.35) ** 2) + 0.07
        p /= p.sum(); pops.append(p)
    pops = np.asarray(pops)
    # Mix with uniform to tune drift severity.
    pops = popularity_drift * pops + (1 - popularity_drift) / n_models
    pops /= pops.sum(axis=1, keepdims=True)

    init_pop = pops[0]
    if policy == "periodic_value":
        cache = _greedy_value_cache(init_pop, sizes, saving, cache_capacity_mb)
    else:
        cache = _greedy_value_cache(init_pop, sizes, np.ones(n_models), cache_capacity_mb)
    initial_cache = set(cache)
    backhaul_mb = float(np.sum(sizes[list(cache)]))
    cache_updates = 1
    recent = np.ones(n_models) * 1e-3
    last_used = np.full(n_models, -10**9, dtype=int)
    latency, hits = [], []
    phase_hits = np.zeros(3); phase_count = np.zeros(3)

    phase_len = int(np.ceil(n_requests / 3))
    for t in range(n_requests):
        phase = min(t // phase_len, 2)
        p = pops[phase]
        m = int(rng.choice(n_models, p=p))
        hit = m in cache
        hits.append(hit); phase_count[phase] += 1; phase_hits[phase] += int(hit)
        if hit:
            l = edge_ms[m] + rng.lognormal(mean=-1.0, sigma=0.25)
            last_used[m] = t
        else:
            # Cloud/backhaul request path. We count a small request/response
            # payload separately from model-cache fills.
            l = cloud_ms[m] + rng.lognormal(mean=1.5, sigma=0.25)
            backhaul_mb += 2.0
            if policy == "lru" and sizes[m] <= cache_capacity_mb:
                # Evict least-recently used models until the missed model fits.
                while sum(sizes[list(cache)]) + sizes[m] > cache_capacity_mb and cache:
                    victim = min(cache, key=lambda j: last_used[j])
                    cache.remove(victim)
                if m not in cache:
                    cache.add(m); backhaul_mb += float(sizes[m]); cache_updates += 1
                last_used[m] = t
        latency.append(float(l))
        recent *= 0.985; recent[m] += 1.0

        if policy in {"periodic_popularity", "periodic_value", "oracle_phase"} and (t + 1) % recache_interval == 0:
            if policy == "oracle_phase":
                estimate = pops[phase]
            else:
                estimate = recent / recent.sum()
            values = saving if policy == "periodic_value" else np.ones(n_models)
            new_cache = _greedy_value_cache(estimate, sizes, values, cache_capacity_mb)
            added = new_cache - cache
            if added:
                backhaul_mb += float(np.sum(sizes[list(added)]))
            if new_cache != cache:
                cache_updates += 1
            cache = new_cache

    latency = np.asarray(latency)
    return {
        "policy": policy,
        "mean_latency_ms": float(np.mean(latency)),
        "p95_latency_ms": float(np.quantile(latency, 0.95)),
        "cache_hit_rate": float(np.mean(hits)),
        "phase_hit_rates": phase_hits / np.maximum(phase_count, 1),
        "backhaul_mb": float(backhaul_mb),
        "cache_updates": int(cache_updates),
        "initial_cache_models": tuple(sorted(initial_cache)),
        "final_cache_models": tuple(sorted(cache)),
        "model_sizes_mb": sizes,
    }
