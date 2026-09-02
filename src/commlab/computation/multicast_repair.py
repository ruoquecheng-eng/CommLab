import numpy as np


def simulate_importance_aware_multicast_repair(
    n_clients=30,
    model_bits=120_000,
    mean_snr_db=3.0,
    snr_std_db=7.0,
    importance_anticorrelation=0.75,
    policy="important_repair",
    aggressive_quantile=0.35,
    seed=0,
):
    """Aggressive multicast plus selective unicast repair.

    A full common broadcast is reliable but bottlenecked by the weakest user.
    An aggressive multicast targets a higher SNR quantile; users below that
    threshold miss the enhancement. Optional repair unicasts can recover missed
    clients. ``important_repair`` repairs missed users in descending task-value
    per unicast-airtime until the total time reaches the conservative full-common
    baseline. ``all_repair`` repairs everyone and can exceed that baseline.
    """
    if policy not in {"no_repair", "important_repair", "all_repair"}:
        raise ValueError("unknown policy")
    rng = np.random.default_rng(seed + 2705)
    snr = np.clip(rng.normal(mean_snr_db, snr_std_db, size=n_clients), -12, 25)
    z = (snr - snr.mean()) / (snr.std() + 1e-9)
    raw = -importance_anticorrelation * z + np.sqrt(max(1 - importance_anticorrelation ** 2, 0)) * rng.normal(size=n_clients)
    importance = np.exp(.55 * raw); importance /= importance.mean()
    se = np.log2(1 + 10 ** (snr / 10)); eps = 1e-9

    full_common_time = model_bits / (np.min(se) + eps)
    threshold = float(np.quantile(snr, aggressive_quantile))
    target = snr >= threshold
    aggressive_rate = np.min(se[target])
    multicast_time = model_bits / (aggressive_rate + eps)
    received = target.copy()
    repair_time = 0.0

    missed = np.where(~received)[0]
    if policy == "all_repair":
        order = missed
    elif policy == "important_repair":
        repair_cost = model_bits / (se[missed] + eps)
        score = importance[missed] / repair_cost
        order = missed[np.argsort(-score)]
    else:
        order = np.array([], dtype=int)

    for i in order:
        c = model_bits / (se[i] + eps)
        if policy == "important_repair" and multicast_time + repair_time + c > full_common_time:
            continue
        repair_time += float(c); received[i] = True

    utility = float(np.sum(importance * received) / np.sum(importance))
    return {
        "policy": policy,
        "weighted_task_utility": utility,
        "mean_model_coverage": float(np.mean(received)),
        "total_time": float(multicast_time + repair_time),
        "multicast_time": float(multicast_time),
        "repair_time": float(repair_time),
        "full_common_time": float(full_common_time),
        "time_ratio_to_full": float((multicast_time + repair_time) / full_common_time),
        "repaired_fraction": float(np.mean(received & (~target))),
        "importance_snr_correlation": float(np.corrcoef(importance, snr)[0, 1]),
    }
