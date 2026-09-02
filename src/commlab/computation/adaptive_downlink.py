import numpy as np

from .downlink_differential import _packet_success_probability


def simulate_adaptive_differential_broadcast(
    n_clients=24,
    rounds=160,
    dim=32,
    mean_snr_db=2.0,
    snr_std_db=4.5,
    fixed_keyframe_interval=12,
    age_threshold=8.0,
    min_keyframe_spacing=4,
    max_keyframe_spacing=24,
    delta_fraction=0.18,
    policy="age_adaptive",
    target_downlink_size=0.36,
    blockage_start=55,
    blockage_duration=22,
    blockage_db=7.0,
    seed=0,
):
    """Differential FL downlink with adaptive resynchronization.

    The server broadcasts full keyframes or anchor-relative differential packets.
    ``fixed`` uses a periodic keyframe schedule. ``age_adaptive`` triggers a
    keyframe when the 80th-percentile client model age exceeds ``age_threshold``
    (subject to min/max spacing). ``recovery_aware`` additionally avoids spending
    a full-model packet while predicted keyframe delivery is very poor and sends
    it after the channel recovers.

    This is a transparent control baseline inspired by age-aware mixed-timescale
    downlink coding; it is not a reproduction of a published codec.
    """
    if policy not in {"fixed", "age_adaptive", "recovery_aware", "budgeted_age"}:
        raise ValueError("unknown policy")
    if rounds < 4 or n_clients < 1 or not (0 < delta_fraction < 1):
        raise ValueError("invalid setup")
    if min_keyframe_spacing < 1 or max_keyframe_spacing < min_keyframe_spacing:
        raise ValueError("invalid keyframe spacing")

    rng = np.random.default_rng(seed + 2701)
    base_snr = np.clip(rng.normal(mean_snr_db, snr_std_db, size=n_clients), -12, 24)

    # Smooth global model trajectory.
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
    has_anchor = np.ones(n_clients, dtype=bool)
    anchor_round = 0
    last_keyframe = 0
    total_size = 0.0
    keyframes = 0
    success_count = 0
    ages, mses, sizes, keyframe_flags, pfull_hist = [], [], [], [], []

    for t in range(1, rounds):
        # A common blockage episode plus small common shadowing drift creates a
        # regime in which blindly timed keyframes can be wasted.
        common = 1.2 * np.sin(2 * np.pi * t / 67.0)
        if blockage_start <= t < blockage_start + blockage_duration:
            common -= blockage_db
        snr_t = np.clip(base_snr + common + rng.normal(0, 0.7, size=n_clients), -15, 26)
        p_full = _packet_success_probability(snr_t, 1.0)
        pfull_hist.append(float(np.mean(p_full)))

        since = t - last_keyframe
        q80_age = float(np.quantile(t - last_version, 0.8))
        if policy == "fixed":
            keyframe = (t % fixed_keyframe_interval == 0)
        else:
            due_age = q80_age >= age_threshold and since >= min_keyframe_spacing
            due_max = since >= max_keyframe_spacing
            if policy == "budgeted_age":
                # Allow an age-triggered keyframe only when the projected long-run
                # normalized airtime remains near the requested budget. The hard
                # max-spacing safeguard still prevents indefinite desynchronization.
                projected = (total_size + 1.0) / max(t, 1)
                keyframe = due_max or (due_age and projected <= target_downlink_size)
            elif policy == "recovery_aware":
                # If the channel is in deep common outage, defer an age-triggered
                # full model unless the hard max-spacing safeguard fires.
                channel_ok = float(np.mean(p_full)) >= 0.52
                keyframe = due_max or (due_age and channel_ok)
            else:
                keyframe = due_max or due_age

        if keyframe:
            size = 1.0
            last_keyframe = t
            anchor_round = t
            keyframes += 1
        else:
            anchor_age = t - anchor_round
            size = delta_fraction * (1 + 0.065 * max(anchor_age - 1, 0))
            size = min(size, 0.88)  # never call a near-full packet a delta.

        p = _packet_success_probability(snr_t, size)
        ok = rng.random(n_clients) < p
        total_size += size
        sizes.append(size)
        keyframe_flags.append(bool(keyframe))
        success_count += int(ok.sum())

        if keyframe:
            client_model[ok] = models[t]
            last_version[ok] = t
            has_anchor[ok] = True
            has_anchor[~ok] = False
        else:
            applicable = ok & has_anchor
            if np.any(applicable):
                client_model[applicable] = models[t]
                last_version[applicable] = t

        err = np.mean((client_model - models[t]) ** 2, axis=1)
        mses.append(float(np.mean(err)))
        ages.append(float(np.mean(t - last_version)))

    return {
        "policy": policy,
        "mean_model_mse": float(np.mean(mses)),
        "final_model_mse": float(mses[-1]),
        "mean_version_age": float(np.mean(ages)),
        "p95_version_age": float(np.quantile(ages, 0.95)),
        "normalized_downlink_size_per_round": float(total_size / (rounds - 1)),
        "keyframe_fraction": float(keyframes / (rounds - 1)),
        "keyframes": int(keyframes),
        "packet_success_fraction": float(success_count / ((rounds - 1) * n_clients)),
        "mean_full_packet_success_probability": float(np.mean(pfull_hist)),
        "age_history": np.asarray(ages),
        "mse_history": np.asarray(mses),
        "packet_size_history": np.asarray(sizes),
        "keyframe_history": np.asarray(keyframe_flags, dtype=bool),
    }
