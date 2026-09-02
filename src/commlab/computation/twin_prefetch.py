import numpy as np


def simulate_twin_guided_model_prefetch(
    slots=1800,
    n_modes=4,
    cache_slots=2,
    policy="uncertainty_gated",
    twin_noise_std=0.45,
    backhaul_load_ms=42.0,
    seed=0,
):
    """Digital-twin-guided edge-model prefetch for a mode-switching process.

    A physical system moves through operating modes, each requiring a different
    edge model. The twin predicts the next mode from a noisy state estimate.
    Blind prediction can churn the cache when uncertainty is high; the gated
    policy prefetches only when confidence and expected latency saving justify the
    model load. This is a transparent state-machine baseline, not an ML predictor.
    """
    if policy not in {"reactive", "predictive", "uncertainty_gated"}:
        raise ValueError("unknown policy")
    if n_modes < 3 or cache_slots < 1 or cache_slots >= n_modes or slots < 100:
        raise ValueError("invalid setup")
    rng=np.random.default_rng(seed+2904)
    # Circular physical modes with dwell times and occasional reversals.
    mode=0; direction=1; dwell=0; dwell_target=int(rng.integers(20,46))
    cache=[0]
    while len(cache)<cache_slots: cache.append((cache[-1]+1)%n_modes)
    last_used={m:-10**9 for m in range(n_modes)}
    model_size=rng.uniform(90,210,n_modes)
    edge_ms=rng.uniform(7,15,n_modes); cloud_ms=edge_ms+rng.uniform(70,125,n_modes)
    prefetch_mb=reactive_mb=wrong_prefetch=attempts=hits=0
    latency=[]; confidence_hist=[]

    for t in range(slots):
        dwell+=1
        if dwell>=dwell_target:
            if rng.random()<.12: direction*=-1
            mode=(mode+direction)%n_modes; dwell=0; dwell_target=int(rng.integers(20,46))
        # Twin observes normalized progress through the current mode.
        progress=dwell/max(dwell_target,1)
        noisy_progress=progress+rng.normal(0,.28*twin_noise_std)
        # The twin must also infer transition direction. At high uncertainty it
        # can prefetch the *wrong model*, not merely prefetch at the wrong time.
        direction_signal=direction+rng.normal(0,1.55*twin_noise_std)
        predicted_direction=1 if direction_signal>=0 else -1
        predicted=(mode+predicted_direction)%n_modes
        actual_next=(mode+direction)%n_modes
        trans_conf=1/(1+np.exp(-8*(noisy_progress-.70)))
        dir_conf=min(1.0,abs(direction_signal)/(1+1.2*twin_noise_std))
        confidence=float(np.clip(trans_conf*dir_conf*np.exp(-.18*twin_noise_std),0,1))
        confidence_hist.append(confidence)

        if policy!="reactive" and predicted not in cache:
            do = policy=="predictive" or (confidence>.48 and backhaul_load_ms < (cloud_ms[predicted]-edge_ms[predicted])*.75)
            if do:
                attempts+=1
                cand=[m for m in cache if m!=mode]
                if not cand: cand=list(cache)
                ev=min(cand,key=lambda m:last_used.get(m,-10**9)); cache.remove(ev); cache.append(predicted)
                prefetch_mb+=model_size[predicted]
                if predicted!=actual_next: wrong_prefetch+=1

        if mode in cache:
            hits+=1; lat=edge_ms[mode]; last_used[mode]=t
        else:
            lat=cloud_ms[mode]+backhaul_load_ms
            # Reactive load installs the actually requested model after miss.
            ev=min(cache,key=lambda m:last_used.get(m,-10**9)); cache.remove(ev); cache.append(mode)
            reactive_mb+=model_size[mode]; last_used[mode]=t
        latency.append(float(lat))

    return {
        "policy":policy,
        "cache_hit_rate":float(hits/slots),
        "mean_inference_latency_ms":float(np.mean(latency)),
        "p95_inference_latency_ms":float(np.quantile(latency,.95)),
        "prefetch_backhaul_mb":float(prefetch_mb),
        "reactive_backhaul_mb":float(reactive_mb),
        "total_backhaul_mb":float(prefetch_mb+reactive_mb),
        "prefetch_attempts":int(attempts),
        "wrong_prefetch_fraction":float(wrong_prefetch/max(attempts,1)),
        "mean_twin_transition_confidence":float(np.mean(confidence_hist)),
    }
