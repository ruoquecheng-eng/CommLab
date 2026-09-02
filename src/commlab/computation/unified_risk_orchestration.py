import numpy as np


def _paired_success(rng, p1, p2, correlation):
    """Generate two Bernoulli link outcomes without post-outcome policy information."""
    shared = rng.random() < correlation
    if shared:
        u = rng.random()
        return bool(u < p1), bool(u < p2)
    return bool(rng.random() < p1), bool(rng.random() < p2)


def _dual_outage_estimate(p1, p2, correlation):
    """Outage of the common-randomness mixture used by :func:`_paired_success`."""
    common = 1.0 - max(p1, p2)
    independent = (1.0 - p1) * (1.0 - p2)
    return float(correlation * common + (1.0 - correlation) * independent)


def simulate_unified_risk_orchestration(
    n_tasks=9000,
    policy="risk_budget",
    budget_per_task=0.85,
    forecast_noise=0.25,
    mean_snr_db=-1.0,
    radio_correlation=0.25,
    edge_risk_scale=1.0,
    seed=0,
):
    """Jointly budget migration, edge replication, and radio duplication.

    The simulator deliberately exposes a *normalized resilience-credit* budget.
    One credit is not claimed to equal a physical joule, byte, or CPU-second;
    actual radio transmissions, replica executions, and migration traffic are
    reported separately.  Policies see noisy one-step edge-risk forecasts and
    pre-transmission link-quality estimates only.  Realized failures and packet
    outcomes are never used as decision-time genie information.

    Parameters
    ----------
    policy:
        ``reactive`` uses no proactive resilience credits and changes edge only
        after an observed execution failure. ``radio_first`` and ``edge_first``
        are transparent fixed-priority baselines. ``risk_budget`` greedily buys
        the largest estimated criticality-weighted risk reduction per credit.
        ``risk_budget_unweighted`` removes task criticality from the same greedy
        rule. ``uncertainty_gated`` uses the criticality-aware rule but
        discounts edge actions when the forecast separation is not large
        relative to forecast uncertainty.
    budget_per_task:
        Credits replenished each task. A small token bucket permits short bursts
        while enforcing the long-run resource budget.

    This is a synthetic cross-layer baseline, not a standards model, production
    edge orchestrator, or calibrated availability trace.
    """
    allowed = {"reactive", "radio_first", "edge_first", "risk_budget", "risk_budget_unweighted", "uncertainty_gated"}
    if policy not in allowed:
        raise ValueError("unknown policy")
    if n_tasks < 200 or budget_per_task < 0 or forecast_noise < 0:
        raise ValueError("invalid setup")
    if not (0 <= radio_correlation <= 1) or edge_risk_scale <= 0:
        raise ValueError("invalid reliability parameters")

    rng = np.random.default_rng(seed + 3301)
    n_nodes = 4
    domains = np.array([0, 0, 1, 1], dtype=int)
    node_bias = np.array([-1.30, -1.05, -0.90, -1.15])

    # Exogenous degradation traces. Policies sharing a seed see the same trace.
    z = np.zeros((n_tasks, n_nodes), dtype=float)
    z[0] = node_bias + rng.normal(0, .08, n_nodes)
    common = 0.0
    for t in range(1, n_tasks):
        common = .95 * common + rng.normal(0, .08)
        shock = rng.normal(0, .13, n_nodes)
        if rng.random() < .010:
            shock[int(rng.integers(n_nodes))] += rng.uniform(.75, 1.35)
        z[t] = .968 * z[t - 1] + .032 * node_bias + .18 * common + shock
        z[t] = np.clip(z[t], -2.5, 1.9)

    node_risk = edge_risk_scale * (.003 + .085 / (1 + np.exp(-2.15 * (z + .10))))
    node_risk = np.clip(node_risk, 0.001, .32)
    # Correlated domain failures are separate from node-specific degradation.
    # The constant common state above is intentionally not used task by task;
    # per-task domain stress below supplies a shared environmental component.
    domain_stress = np.zeros(n_tasks)
    for t in range(1, n_tasks):
        domain_stress[t] = .97 * domain_stress[t - 1] + rng.normal(0, .11)
    domain_prob = np.clip(.006 + .026 * edge_risk_scale / (1 + np.exp(-1.7 * domain_stress)), .002, .16)

    sigma = .025 * forecast_noise
    forecast = np.clip(node_risk + rng.normal(0, sigma, (n_tasks, n_nodes)), 0.001, .36)

    # Radio traces and *pre-transmission* estimates. The second access path is
    # slightly stronger on average but shares slow fading with the primary.
    slow = rng.normal(0, 2.2, n_tasks)
    q1 = mean_snr_db + slow + rng.normal(0, 1.05, n_tasks)
    q2 = mean_snr_db + .78 * slow + .8 + rng.normal(0, 1.20, n_tasks)
    q1_hat = q1 + rng.normal(0, .55, n_tasks)
    q2_hat = q2 + rng.normal(0, .60, n_tasks)

    # Exogenous task classes: rare high-value jobs have tighter deadlines.
    cls = rng.choice(3, n_tasks, p=[.64, .26, .10])
    criticality = np.array([1.0, 2.2, 5.5])[cls]
    deadlines = np.array([62.0, 51.0, 42.0])[cls]

    # Normalized decision prices; real resource metrics are separately exposed.
    C_DUP, C_REPLICA, C_MIGRATE = 0.72, 1.10, 1.80
    state_mb = 72.0
    bucket = 0.0
    bucket_cap = max(3.0, 10.0 * budget_per_task)
    node = 0

    latencies = []
    deadline_miss = task_weighted_miss = 0.0
    total_weight = float(np.sum(criticality))
    radio_tx = replica_exec = migrations = proactive_migrations = 0
    migration_traffic = credits_spent = 0.0
    edge_fail_events = radio_fail_events = 0
    action_counts = {"duplicate": 0, "replicate": 0, "migrate": 0}

    def spend(cost):
        nonlocal bucket, credits_spent
        if bucket + 1e-12 < cost:
            return False
        bucket -= cost
        credits_spent += cost
        return True

    for t in range(n_tasks):
        bucket = min(bucket_cap, bucket + budget_per_task)
        weight = float(criticality[t])
        decision_weight = 1.0 if policy == "risk_budget_unweighted" else weight

        # Current and alternate edge risk estimates include domain outage.
        d_hat = float(np.clip(domain_prob[t], 0, .25))
        cur_hat = d_hat + (1 - d_hat) * float(forecast[t, node])
        alternates = [j for j in range(n_nodes) if domains[j] != domains[node]]
        alt = min(alternates, key=lambda j: forecast[t, j])
        alt_hat = d_hat + (1 - d_hat) * float(forecast[t, alt])

        g1h, g2h = 10 ** (q1_hat[t] / 10), 10 ** (q2_hat[t] / 10)
        p1h = float(1 - np.exp(-g1h / 2.20))
        p2h = float(1 - np.exp(-g2h / 2.35))
        radio_out = 1 - p1h
        dual_out = _dual_outage_estimate(p1h, p2h, radio_correlation)

        # Expected immediate miss-risk proxies. Edge replica is across domains.
        base_risk = 1 - (1 - cur_hat) * (1 - radio_out)
        dup_risk = 1 - (1 - cur_hat) * (1 - dual_out)
        replica_edge_out = cur_hat * alt_hat
        replica_risk = 1 - (1 - replica_edge_out) * (1 - radio_out)
        migrate_risk = 1 - (1 - alt_hat) * (1 - radio_out)

        do_dup = do_replica = do_migrate = False

        if policy == "radio_first":
            if weight * (base_risk - dup_risk) > .018 and spend(C_DUP):
                do_dup = True
            # Replicate only if radio has not consumed the limited credit and
            # the current edge is materially risky.
            if cur_hat > .055 and weight >= 2.2 and spend(C_REPLICA):
                do_replica = True
            gap = cur_hat - alt_hat
            if cur_hat > .085 and gap > .028 and spend(C_MIGRATE):
                do_migrate = True
        elif policy == "edge_first":
            gap = cur_hat - alt_hat
            if cur_hat > .075 and gap > .022 and spend(C_MIGRATE):
                do_migrate = True
            elif cur_hat > .048 and weight >= 2.2 and spend(C_REPLICA):
                do_replica = True
            if radio_out > .48 and spend(C_DUP):
                do_dup = True
        elif policy in {"risk_budget", "risk_budget_unweighted", "uncertainty_gated"}:
            # One-shot value-per-credit ranking, then optionally buy a second
            # orthogonal protection if it still has positive residual value.
            replica_discount = 1.0
            migrate_discount = 1.0
            migration_gap = cur_hat - alt_hat
            if policy == "uncertainty_gated" and sigma > 0:
                # Calibrated forecast uncertainty is available to the runtime;
                # it is not inferred from realized failures. Replication only
                # needs evidence that the current edge is risky, while migration
                # additionally needs convincing evidence that another edge is
                # *actually safer*. The latter therefore receives a stricter
                # separation test and avoids prediction-driven churn.
                replica_discount = max(0.0, cur_hat - 1.15 * sigma) / max(cur_hat, 1e-12)
                sep = max(0.0, migration_gap - 2.35 * np.sqrt(2.0) * sigma)
                migrate_discount = sep / max(migration_gap, 1e-12) if migration_gap > 0 else 0.0
                replica_discount = float(np.clip(replica_discount, 0.0, 1.0))
                migrate_discount = float(np.clip(migrate_discount, 0.0, 1.0))

            benefits = {
                "duplicate": decision_weight * max(0.0, base_risk - dup_risk) / C_DUP,
                "replicate": decision_weight * max(0.0, base_risk - replica_risk) * replica_discount / C_REPLICA,
                # Migration has multi-task value, but speculative movement is
                # discounted because its one-step prediction may be wrong.
                "migrate": decision_weight * max(0.0, base_risk - migrate_risk) * 5.0 * migrate_discount / C_MIGRATE,
            }
            # Demand a small minimum predicted return to avoid spending every
            # accumulated credit on numerical noise.
            for action, value in sorted(benefits.items(), key=lambda kv: kv[1], reverse=True):
                if value < .012:
                    continue
                if action == "duplicate" and not do_dup and spend(C_DUP):
                    do_dup = True
                elif action == "replicate" and not do_replica and spend(C_REPLICA):
                    do_replica = True
                elif action == "migrate" and not do_migrate and spend(C_MIGRATE):
                    do_migrate = True
                # At most two proactive mechanisms per task. This makes the
                # budget allocation visible instead of trivially buying all.
                if int(do_dup) + int(do_replica) + int(do_migrate) >= 2:
                    break

        # Migration happens before execution and changes future service affinity.
        migration_penalty = 0.0
        if do_migrate:
            node = int(alt)
            migrations += 1
            proactive_migrations += 1
            migration_traffic += state_mb
            action_counts["migrate"] += 1
            migration_penalty = 8.5 + float(rng.exponential(1.5))
            # Recompute cross-domain replica target after movement if both were
            # selected. This avoids accidentally placing both copies together.
            alternates = [j for j in range(n_nodes) if domains[j] != domains[node]]
            alt = min(alternates, key=lambda j: forecast[t, j])

        # Realized edge state. Domain and node failures are exogenous.
        domain_down = rng.random(2) < domain_prob[t]
        node_down = rng.random(n_nodes) < node_risk[t]
        cur_alive = (not bool(domain_down[domains[node]])) and (not bool(node_down[node]))
        alt_alive = (not bool(domain_down[domains[alt]])) and (not bool(node_down[alt]))
        edge_ok = cur_alive or (do_replica and alt_alive)
        replica_exec += int(do_replica)
        if do_replica:
            action_counts["replicate"] += 1
        if not cur_alive:
            edge_fail_events += 1

        # Realized radio state with the same correlation model used in the
        # decision-time analytical estimate.
        g1, g2 = 10 ** (q1[t] / 10), 10 ** (q2[t] / 10)
        p1 = float(1 - np.exp(-g1 / 2.20))
        p2 = float(1 - np.exp(-g2 / 2.35))
        s1, s2 = _paired_success(rng, p1, p2, radio_correlation)
        radio_ok = bool(s1 or (do_dup and s2))
        radio_tx += 1 + int(do_dup)
        if do_dup:
            action_counts["duplicate"] += 1
        if not s1:
            radio_fail_events += 1

        # Transparent latency accounting. Failed tasks receive a synthetic
        # recovery-tail latency; successful duplicated paths race.
        d1 = 5.2 + 7.6 / max(g1, .12) + float(rng.exponential(1.25))
        d2 = 5.8 + 7.8 / max(g2, .12) + float(rng.exponential(1.35))
        radio_delay = min(d1, d2) if do_dup else d1
        compute = 15.5 + 2.7 * max(float(z[t, node]) + 1.0, 0.0) + float(rng.exponential(2.6))
        if do_replica:
            # Parallel execution has a small orchestration cost but can mask a
            # slow/failing primary when the cross-domain replica is healthy.
            alt_compute = 16.5 + 2.4 * max(float(z[t, alt]) + 1.0, 0.0) + float(rng.exponential(2.8))
            if cur_alive and alt_alive:
                compute = min(compute, alt_compute) + 1.4
            elif alt_alive:
                compute = alt_compute + 3.0
        L = radio_delay + compute + migration_penalty
        if not (edge_ok and radio_ok):
            L = float(deadlines[t] + 55.0 + rng.exponential(10.0))

        miss = (not (edge_ok and radio_ok)) or (L > deadlines[t])
        deadline_miss += float(miss)
        task_weighted_miss += weight * float(miss)
        latencies.append(L)

        # All non-reactive policies still have a common reactive recovery path
        # after an observed primary-edge failure; this cost is not charged as a
        # proactive resilience decision. It affects future affinity only.
        if not cur_alive:
            candidates = [j for j in range(n_nodes) if j != node and not node_down[j] and not domain_down[domains[j]]]
            if candidates:
                node = int(min(candidates, key=lambda j: forecast[t, j]))
                migrations += 1
                migration_traffic += state_mb

    a = np.asarray(latencies)
    return {
        "policy": policy,
        "budget_per_task": float(budget_per_task),
        "forecast_noise": float(forecast_noise),
        "mean_snr_db": float(mean_snr_db),
        "radio_correlation": float(radio_correlation),
        "edge_risk_scale": float(edge_risk_scale),
        "mean_latency_ms": float(a.mean()),
        "p95_latency_ms": float(np.quantile(a, .95)),
        "deadline_miss_rate": float(deadline_miss / n_tasks),
        "task_weighted_deadline_miss_rate": float(task_weighted_miss / max(total_weight, 1e-12)),
        "mean_transmissions_per_task": float(radio_tx / n_tasks),
        "replica_execution_rate": float(replica_exec / n_tasks),
        "migration_rate": float(migrations / n_tasks),
        "proactive_migration_rate": float(proactive_migrations / n_tasks),
        "migration_traffic_mb_per_task": float(migration_traffic / n_tasks),
        "resilience_credits_per_task": float(credits_spent / n_tasks),
        "duplicate_action_rate": float(action_counts["duplicate"] / n_tasks),
        "replicate_action_rate": float(action_counts["replicate"] / n_tasks),
        "migrate_action_rate": float(action_counts["migrate"] / n_tasks),
        "primary_edge_failure_rate": float(edge_fail_events / n_tasks),
        "primary_radio_failure_rate": float(radio_fail_events / n_tasks),
    }
