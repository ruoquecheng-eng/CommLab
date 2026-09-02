import numpy as np


def _pair(rng, p1, p2, rho):
    shared = rng.random() < rho
    if shared:
        u = rng.random(); return u < p1, u < p2
    return rng.random() < p1, rng.random() < p2


def simulate_multiconnectivity_safety_control(
    slots=3200,
    policy="adaptive_duplicate",
    correlation=0.25,
    mean_snr_db=-2.0,
    seed=0,
):
    """Couple dual-link packet duplication to safety-aware networked control.

    A max-error scheduler selects one of five plants. Full duplication always
    uses two links; adaptive duplication uses two only for high normalized
    safety risk or weak predicted primary delivery. Reports safety violations
    together with radio transmissions per slot.
    """
    if policy not in {"single", "full_duplicate", "adaptive_duplicate"}:
        raise ValueError("unknown policy")
    if not (0 <= correlation <= 1):
        raise ValueError("invalid correlation")

    rng = np.random.default_rng(seed + 3215)
    n = 5
    a = np.linspace(1.02, 1.105, n)
    k = np.linspace(.34, .50, n)
    q = np.linspace(.8, 2.0, n)
    bound = np.linspace(4.6, 1.9, n)
    proc = np.linspace(.16, .06, n)
    snr0 = np.linspace(mean_snr_db - 1.5, mean_snr_db + 1.2, n)
    x = rng.normal(0, .6, n); xh = x.copy(); age = np.zeros(n, int)

    violations = successes = dup_count = 0
    costs = []; tx_total = 0
    for t in range(slots):
        err = np.abs(x - xh)
        proximity = np.abs(a*x - k*xh) / bound
        score = err * q + 2.2 * np.maximum(proximity - .55, 0) ** 2 + .015 * age
        i = int(np.argmax(score))

        snr1 = snr0[i] + 1.5*np.sin(2*np.pi*t/109 + i) + rng.normal(0, .8)
        snr2 = snr0[i] + .8 + 1.2*np.sin(2*np.pi*t/127 + .7*i) + rng.normal(0, .9)
        p1 = 1 - np.exp(-10**(snr1/10)/2.45)
        p2 = 1 - np.exp(-10**(snr2/10)/2.55)
        if policy == "single":
            dup = False
        elif policy == "full_duplicate":
            dup = True
        else:
            dup = (proximity[i] > .80) or (p1 < .24)
        s1, s2 = _pair(rng, p1, p2, correlation)
        ok = bool(s1 or (dup and s2))
        tx_total += 1 + int(dup); dup_count += int(dup)
        if ok:
            xh[i] = x[i]; age[i] = 0; successes += 1

        u = -k*xh
        costs.append(float(np.mean(q*x*x + .05*u*u)))
        violations += int(np.any(np.abs(x) > bound))
        w = rng.normal(0, proc, n)
        if rng.random() < .024:
            probs = np.linspace(1, 4, n); probs /= probs.sum()
            j = int(rng.choice(n, p=probs)); w[j] += rng.normal(0, .68)
        x = a*x + u + w; xh = a*xh + u; age += 1
        x = np.clip(x, -12, 12); xh = np.clip(xh, -12, 12)

    c = np.asarray(costs)
    return {
        "policy": policy,
        "mean_control_cost": float(c.mean()),
        "p95_control_cost": float(np.quantile(c, .95)),
        "safety_violation_rate": float(violations / slots),
        "update_success_rate": float(successes / slots),
        "mean_transmissions_per_slot": float(tx_total / slots),
        "duplication_rate": float(dup_count / slots),
    }
