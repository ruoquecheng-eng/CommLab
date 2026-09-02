import numpy as np


def simulate_predictive_failure_migration(
    steps=6000,
    policy="predictive_risk",
    forecast_noise=0.25,
    deadline_ms=62.0,
    seed=0,
):
    """Stateful edge execution under node degradation and noisy failure forecasts.

    The environment is generated independently of the policy: four nodes have
    slowly varying latent degradation risks, occasional common stress, and
    Bernoulli execution failures. ``predictive_risk`` may migrate before a
    failure based on a noisy one-step risk forecast. As forecast noise rises,
    false alarms create migration churn and can erase the latency benefit.

    This is a transparent synthetic resilience baseline, not a production
    failure predictor or a measured edge trace.
    """
    if policy not in {"sticky", "reactive", "predictive_risk"}:
        raise ValueError("unknown policy")
    if steps < 100 or forecast_noise < 0:
        raise ValueError("invalid setup")

    rng = np.random.default_rng(seed + 3211)
    n_nodes = 4

    # Exogenous latent degradation trace shared by all policy runs with a seed.
    z = np.zeros((steps, n_nodes), float)
    z[0] = np.array([-1.35, -1.15, -0.95, -1.05]) + rng.normal(0, .10, n_nodes)
    common = 0.0
    for t in range(1, steps):
        common = .94 * common + rng.normal(0, .10)
        shock = rng.normal(0, .16, n_nodes)
        if rng.random() < .012:
            j = int(rng.integers(n_nodes))
            shock[j] += rng.uniform(.9, 1.5)
        z[t] = .965 * z[t-1] + .035 * np.array([-1.30, -1.10, -.90, -1.05]) + .20 * common + shock
        z[t] = np.clip(z[t], -2.4, 1.9)

    true_risk = .004 + .105 / (1 + np.exp(-2.2 * (z + .15)))
    # A forecast has calibrated signal plus independent error. The noise term is
    # deliberately exposed because false alarms are the research variable.
    f_noise = rng.normal(size=(steps, n_nodes))
    forecast = np.clip(true_risk + forecast_noise * .025 * f_noise, 0.0, .28)

    u_fail = rng.random((steps, n_nodes))
    failed = u_fail < true_risk
    base_latency = 17.5 + 3.2 * np.maximum(z + 1.0, 0) + rng.exponential(2.8, (steps, n_nodes))

    service_node = 0
    latencies = []
    failures = migrations = proactive = deadline_misses = 0
    traffic_mb = 0.0
    migration_penalty_ms = 9.5
    recovery_penalty_ms = 58.0
    state_mb = 72.0

    for t in range(steps):
        # Predictive migration is only useful if a materially safer node exists.
        if policy == "predictive_risk":
            cur_hat = forecast[t, service_node]
            best = int(np.argmin(forecast[t]))
            gap = cur_hat - forecast[t, best]
            # Noise-sensitive trigger: a fixed risk floor plus relative gap.
            # Larger forecast error therefore creates false positives/churn.
            if best != service_node and cur_hat > .040 and gap > .010:
                service_node = best
                migrations += 1
                proactive += 1
                traffic_mb += state_mb
                mig_pen = migration_penalty_ms
            else:
                mig_pen = 0.0
        else:
            mig_pen = 0.0

        node = service_node
        L = float(base_latency[t, node]) + mig_pen
        if failed[t, node]:
            failures += 1
            # Recovery selects the least risky *currently observed* alternative;
            # no future genie information is used.
            candidates = [j for j in range(n_nodes) if j != node]
            if policy in {"reactive", "predictive_risk"}:
                nxt = min(candidates, key=lambda j: forecast[t, j])
                service_node = int(nxt)
                migrations += 1
                traffic_mb += state_mb
            # Sticky keeps logical affinity but still pays a restart/recovery hit.
            L += recovery_penalty_ms + rng.exponential(10.0)

        latencies.append(L)
        deadline_misses += int(L > deadline_ms)

    a = np.asarray(latencies)
    return {
        "policy": policy,
        "forecast_noise": float(forecast_noise),
        "mean_latency_ms": float(a.mean()),
        "p95_latency_ms": float(np.quantile(a, .95)),
        "deadline_miss_rate": float(deadline_misses / steps),
        "failure_event_rate": float(failures / steps),
        "migration_rate": float(migrations / steps),
        "proactive_migration_rate": float(proactive / steps),
        "migration_traffic_mb_per_step": float(traffic_mb / steps),
    }
