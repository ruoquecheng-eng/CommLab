import numpy as np


def simulate_control_uep(
    slots=3600,
    policy="critical_uep",
    mean_snr_db=-1.0,
    repetition_budget=5,
    seed=0,
):
    """Unequal repetition protection for a three-component control state.

    Each slot has a fixed repetition budget. ``equal`` rotates the two extra
    repetitions across components; ``critical_uep`` always protects the most
    control-sensitive component. The receiver predicts missing components.
    This exposes critical-state protection versus broad-state freshness.
    """
    if policy not in {"equal", "critical_uep"}:
        raise ValueError("unknown policy")
    if slots < 100 or repetition_budget != 5:
        raise ValueError("this baseline uses a fixed five-transmission budget")

    rng = np.random.default_rng(seed + 3213)
    a = np.array([1.015, 1.035, 1.085])
    k = np.array([.27, .31, .46])
    q = np.array([.55, .95, 4.8])
    proc = np.array([.10, .085, .075])
    snr_offset = np.array([1.2, .2, -1.1])
    x = rng.normal(0, .45, 3)
    xh = x.copy()

    costs = []
    delivered = np.zeros(3, int)
    critical_misses = 0
    safe_viol = 0
    bound = np.array([4.0, 3.0, 1.85])

    for t in range(slots):
        if policy == "critical_uep":
            reps = np.array([1, 1, 3])
        else:
            # Fair 2/2/1 rotation. Same total radio use as UEP.
            low = t % 3
            reps = np.full(3, 2, int)
            reps[low] = 1

        snr = mean_snr_db + snr_offset + 1.1 * np.sin(2*np.pi*t/137 + np.arange(3))
        gamma = 10 ** (snr / 10)
        p_single = 1 - np.exp(-gamma / 2.7)
        p_delivery = 1 - (1 - p_single) ** reps
        ok = rng.random(3) < p_delivery
        delivered += ok
        critical_misses += int(not ok[2])
        xh[ok] = x[ok]

        u = -k * xh
        stage = float(np.sum(q * x * x + .04 * u * u))
        costs.append(stage)
        safe_viol += int(np.any(np.abs(x) > bound))

        w = rng.normal(0, proc, 3)
        if rng.random() < .018:
            w[2] += rng.normal(0, .50)
        x = a * x + u + w
        xh = a * xh + u
        x = np.clip(x, -10, 10)
        xh = np.clip(xh, -10, 10)

    c = np.asarray(costs)
    return {
        "policy": policy,
        "mean_control_cost": float(c.mean()),
        "p95_control_cost": float(np.quantile(c, .95)),
        "safety_violation_rate": float(safe_viol / slots),
        "critical_component_miss_rate": float(critical_misses / slots),
        "mean_repetitions_per_slot": float(repetition_budget),
        "component_delivery_rate": (delivered / slots).astype(float),
    }
