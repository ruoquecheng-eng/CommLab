from __future__ import annotations

from collections import deque

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def _dual_outage(p, q, correlation):
    """Common-shock mixture used for decision and outcome probabilities."""
    return float(correlation * max(p, q) + (1.0 - correlation) * p * q)


def _cvar(values, alpha=0.95):
    a = np.asarray(values, dtype=float)
    threshold = float(np.quantile(a, alpha))
    tail = a[a >= threshold]
    return float(tail.mean()) if tail.size else threshold


def simulate_adaptive_risk_control(
    n_tasks=6000,
    policy="adaptive_local",
    target_miss_rate=0.10,
    budget_per_task=0.85,
    adaptation_rate=0.035,
    feedback_delay=1,
    drift_strength=1.0,
    mean_snr_db=3.0,
    radio_correlation=0.25,
    edge_risk_scale=1.0,
    seed=0,
):
    """Closed-loop resilience orchestration under calibration drift.

    The runtime can buy dual-link duplication, cross-domain execution, and
    proactive migration from one token bucket.  ``point_greedy`` trusts stale
    point-risk estimates; ``static_guard`` adds a fixed deployment margin;
    ``adaptive_global`` updates one risk-debt variable from delayed outcomes;
    and ``adaptive_local`` maintains separate debts for routine, important,
    and critical tasks.  ``oracle`` sees the synthetic probabilities (not the
    realized Bernoulli outcomes) and is an analysis-only clairvoyant-risk
    reference, not an optimization lower bound.

    Adaptive policies update from *past revealed misses only*.  A configured
    feedback delay is enforced with a queue, so current outcomes cannot affect
    current decisions.  The update resembles adaptive-risk-control feedback,
    but this simulator does not claim conformal coverage: its losses are
    action-dependent, temporally dependent, and evaluated on synthetic data.
    """
    allowed = {"point_greedy", "static_guard", "adaptive_global", "adaptive_local", "oracle"}
    if policy not in allowed:
        raise ValueError("unknown policy")
    if n_tasks < 300 or not (0 < target_miss_rate < 0.5):
        raise ValueError("invalid task count or target")
    if budget_per_task < 0 or adaptation_rate < 0 or feedback_delay < 1:
        raise ValueError("invalid online-control setup")
    if drift_strength < 0 or edge_risk_scale <= 0 or not (0 <= radio_correlation <= 1):
        raise ValueError("invalid reliability setup")

    rng = np.random.default_rng(seed + 3401)
    n_nodes = 4
    domains = np.array([0, 0, 1, 1], dtype=int)
    classes = rng.choice(3, n_tasks, p=[0.68, 0.24, 0.08])
    weights = np.array([1.0, 2.5, 6.0])[classes]
    class_targets = target_miss_rate * np.array([1.20, 0.82, 0.48])
    drift_start = int(0.52 * n_tasks)
    drift = drift_strength * _sigmoid((np.arange(n_tasks) - drift_start) / max(18.0, 0.035 * n_tasks))

    # Slowly varying radio conditions plus a deployment shift.  The stale
    # estimator tracks only 30% of the new drift and therefore becomes
    # overconfident after the change point.
    radio_state = np.zeros(n_tasks)
    edge_state = np.zeros((n_tasks, n_nodes))
    for t in range(1, n_tasks):
        radio_state[t] = 0.965 * radio_state[t - 1] + rng.normal(0, 0.14)
        edge_state[t] = 0.972 * edge_state[t - 1] + rng.normal(0, 0.11, n_nodes)
    snr_term = 0.18 / (1.0 + np.exp(0.72 * mean_snr_db))
    true_radio = np.clip(0.025 + snr_term + 0.105 * drift + 0.030 * _sigmoid(radio_state), 0.005, 0.48)
    estimated_radio = np.clip(
        0.025 + snr_term + 0.032 * drift + 0.030 * _sigmoid(radio_state)
        + rng.normal(0, 0.009, n_tasks),
        0.003,
        0.45,
    )

    node_bias = np.array([-0.018, -0.006, 0.008, -0.012])
    node_drift = np.array([1.45, 0.90, 1.10, 0.55])
    true_edge = np.empty((n_tasks, n_nodes))
    estimated_edge = np.empty_like(true_edge)
    critical_shift = (classes == 2).astype(float)
    for j in range(n_nodes):
        common = 0.023 + 0.020 * _sigmoid(edge_state[:, j]) + node_bias[j]
        true_edge[:, j] = np.clip(
            edge_risk_scale * (common + 0.070 * node_drift[j] * drift + 0.080 * drift * critical_shift),
            0.003,
            0.42,
        )
        estimated_edge[:, j] = np.clip(
            edge_risk_scale * (common + 0.022 * node_drift[j] * drift + 0.018 * drift * critical_shift)
            + rng.normal(0, 0.008, n_tasks),
            0.002,
            0.38,
        )

    # Tight-deadline tails are class dependent and also drift.  The predictor
    # is deliberately stale, creating an end-to-end calibration problem rather
    # than only a component failure-estimation problem.
    true_tail = np.clip(np.array([0.018, 0.030, 0.050])[classes] + 0.038 * drift, 0.005, 0.28)
    estimated_tail = np.clip(np.array([0.018, 0.030, 0.050])[classes] + 0.011 * drift, 0.004, 0.20)

    # Paired uniforms and latency innovations make same-seed policy comparisons
    # use the same exogenous sample path without revealing outcomes in advance.
    outcome_uniform = rng.random(n_tasks)
    latency_noise = rng.exponential(3.0, n_tasks)
    recovery_noise = rng.exponential(9.0, n_tasks)

    C_DUP, C_REPLICA, C_MIGRATE = 0.72, 1.10, 1.80
    bucket = 0.0
    bucket_cap = max(3.0, 9.0 * budget_per_task)
    node = 0
    global_debt = 0.018
    local_debt = np.full(3, 0.018)
    feedback = deque()

    misses = np.zeros(n_tasks, dtype=float)
    predicted_selected = np.zeros(n_tasks, dtype=float)
    true_selected = np.zeros(n_tasks, dtype=float)
    latency = np.zeros(n_tasks, dtype=float)
    credits = radio_tx = replicas = migrations = 0.0
    action_counts = np.zeros(3, dtype=int)
    selected_codes = np.zeros(n_tasks, dtype=int)
    debt_trace = np.zeros(n_tasks)

    def combined_risk(radio, edge, tail):
        return float(1.0 - (1.0 - radio) * (1.0 - edge) * (1.0 - tail))

    for t in range(n_tasks):
        # Only outcomes whose feedback delay has elapsed are usable.
        while feedback and feedback[0][0] <= t:
            _, observed_class, observed_miss = feedback.popleft()
            if policy == "adaptive_global":
                global_debt = float(np.clip(
                    global_debt + adaptation_rate * (observed_miss - target_miss_rate), 0.0, 0.30
                ))
            elif policy == "adaptive_local":
                k = int(observed_class)
                local_debt[k] = float(np.clip(
                    local_debt[k] + adaptation_rate * (observed_miss - class_targets[k]), 0.0, 0.34
                ))

        bucket = min(bucket_cap, bucket + budget_per_task)
        k = int(classes[t])
        target = float(class_targets[k] if policy == "adaptive_local" else target_miss_rate)
        if policy == "adaptive_global":
            guard = global_debt
        elif policy == "adaptive_local":
            guard = float(local_debt[k])
        elif policy == "static_guard":
            guard = 0.032
        else:
            guard = 0.0
        debt_trace[t] = guard

        if policy == "oracle":
            r_est = float(true_radio[t])
            e_est_vec = true_edge[t]
            tail_est = float(true_tail[t])
        else:
            r_est = float(estimated_radio[t])
            e_est_vec = estimated_edge[t]
            tail_est = float(estimated_tail[t])

        cur_e = float(e_est_vec[node])
        alternates = [j for j in range(n_nodes) if domains[j] != domains[node]]
        alt = int(min(alternates, key=lambda j: e_est_vec[j]))
        alt_e = float(e_est_vec[alt])
        base = combined_risk(r_est, cur_e, tail_est)
        r_dup = _dual_outage(r_est, min(0.95 * r_est, r_est), radio_correlation)
        e_rep = _dual_outage(cur_e, alt_e, 0.18)
        dup_risk = combined_risk(r_dup, cur_e, tail_est)
        rep_risk = combined_risk(r_est, e_rep, tail_est)
        mig_risk = combined_risk(r_est, alt_e, min(0.30, tail_est + 0.025))

        # The fixed point-estimate baseline has no feedback term and therefore
        # keeps the deployment threshold.  Risk debt lowers that threshold only
        # after revealed misses.  A fairly material base threshold is
        # intentional: otherwise every policy simply empties the bucket on the
        # first available task and online calibration cannot change allocation.
        risk_pressure = max(0.0, guard / max(target, 1e-9))
        threshold = 0.14 / (1.0 + 1.7 * risk_pressure)
        if policy == "adaptive_local":
            # Local control is not merely three copies of the global update:
            # it reserves aggressiveness for the rare class with the tightest
            # risk target instead of letting frequent routine feedback drain
            # the shared bucket before a critical task arrives.
            threshold *= float(np.array([1.85, 1.15, 0.52])[k])
        value_weight = float(weights[t])
        candidates = [
            (value_weight * max(0.0, base - dup_risk) / C_DUP, 0, C_DUP),
            (value_weight * max(0.0, base - rep_risk) / C_REPLICA, 1, C_REPLICA),
            (value_weight * max(0.0, base - mig_risk) * 3.0 / C_MIGRATE, 2, C_MIGRATE),
        ]
        chosen = []
        for score, action, cost in sorted(candidates, reverse=True):
            if score < threshold or bucket + 1e-12 < cost:
                continue
            bucket -= cost
            credits += cost
            chosen.append(action)
            action_counts[action] += 1
            if len(chosen) == 2:
                break

        do_dup, do_replica, do_migrate = (0 in chosen), (1 in chosen), (2 in chosen)
        selected_codes[t] = int(do_dup) + 2 * int(do_replica) + 4 * int(do_migrate)
        radio_tx += 1 + int(do_dup)
        replicas += int(do_replica)

        if do_migrate:
            node = alt
            migrations += 1
            alternates = [j for j in range(n_nodes) if domains[j] != domains[node]]
            alt = int(min(alternates, key=lambda j: e_est_vec[j]))

        # Evaluate the selected actions with the hidden synthetic probabilities.
        r_true = float(true_radio[t])
        cur_true = float(true_edge[t, node])
        alt_true = float(true_edge[t, alt])
        tail_true = float(true_tail[t]) + (0.025 if do_migrate else 0.0)
        if do_dup:
            r_true = _dual_outage(r_true, min(0.95 * r_true, r_true), radio_correlation)
        if do_replica:
            cur_true = _dual_outage(cur_true, alt_true, 0.18)
        actual_risk = combined_risk(r_true, cur_true, min(0.32, tail_true))

        r_pred = r_est
        edge_pred = float(e_est_vec[node])
        tail_pred = tail_est + (0.025 if do_migrate else 0.0)
        if do_dup:
            r_pred = _dual_outage(r_pred, min(0.95 * r_pred, r_pred), radio_correlation)
        if do_replica:
            edge_pred = _dual_outage(edge_pred, float(e_est_vec[alt]), 0.18)
        selected_prediction = combined_risk(r_pred, edge_pred, min(0.30, tail_pred))

        miss = float(outcome_uniform[t] < actual_risk)
        misses[t] = miss
        predicted_selected[t] = selected_prediction
        true_selected[t] = actual_risk
        feedback.append((t + feedback_delay, k, miss))
        base_latency = 18.0 + 2.0 * k + latency_noise[t] + 4.5 * int(do_migrate)
        latency[t] = base_latency if not miss else (42.0 - 3.0 * k) + 38.0 + recovery_noise[t]

    post = np.arange(n_tasks) >= drift_start
    early_post = (np.arange(n_tasks) >= drift_start) & (
        np.arange(n_tasks) < min(n_tasks, drift_start + max(250, n_tasks // 12))
    )
    total_weight = float(np.sum(weights))
    weighted_miss = float(np.sum(weights * misses) / total_weight)
    post_weight = float(np.sum(weights[post]))
    class_miss = []
    post_class_miss = []
    class_calibration_gap = []
    for k in range(3):
        mask = classes == k
        pmask = mask & post
        class_miss.append(float(misses[mask].mean()))
        post_class_miss.append(float(misses[pmask].mean()))
        class_calibration_gap.append(float(misses[mask].mean() - predicted_selected[mask].mean()))

    win = max(80, n_tasks // 20)
    rolling = np.convolve(weights * misses, np.ones(win), mode="valid") / np.convolve(weights, np.ones(win), mode="valid")
    switch_rate = float(np.mean(selected_codes[1:] != selected_codes[:-1]))
    return {
        "policy": policy,
        "target_miss_rate": float(target_miss_rate),
        "budget_per_task": float(budget_per_task),
        "adaptation_rate": float(adaptation_rate),
        "feedback_delay": int(feedback_delay),
        "drift_strength": float(drift_strength),
        "deadline_miss_rate": float(misses.mean()),
        "task_weighted_deadline_miss_rate": weighted_miss,
        "post_drift_task_weighted_miss_rate": float(np.sum(weights[post] * misses[post]) / post_weight),
        "early_post_drift_weighted_miss_rate": float(
            np.sum(weights[early_post] * misses[early_post]) / np.sum(weights[early_post])
        ),
        "routine_miss_rate": class_miss[0],
        "important_miss_rate": class_miss[1],
        "critical_miss_rate": class_miss[2],
        "post_drift_routine_miss_rate": post_class_miss[0],
        "post_drift_important_miss_rate": post_class_miss[1],
        "post_drift_critical_miss_rate": post_class_miss[2],
        "critical_target_excess": float(post_class_miss[2] - class_targets[2]),
        "mean_predicted_miss_risk": float(predicted_selected.mean()),
        "calibration_gap": float(misses.mean() - predicted_selected.mean()),
        "max_class_calibration_gap": float(max(abs(x) for x in class_calibration_gap)),
        "brier_score": float(np.mean((predicted_selected - misses) ** 2)),
        "max_rolling_weighted_miss_rate": float(rolling.max()),
        "mean_latency_ms": float(latency.mean()),
        "p95_latency_ms": float(np.quantile(latency, 0.95)),
        "cvar95_latency_ms": _cvar(latency, 0.95),
        "resilience_credits_per_task": float(credits / n_tasks),
        "mean_transmissions_per_task": float(radio_tx / n_tasks),
        "replica_execution_rate": float(replicas / n_tasks),
        "proactive_migration_rate": float(migrations / n_tasks),
        "duplicate_action_rate": float(action_counts[0] / n_tasks),
        "replicate_action_rate": float(action_counts[1] / n_tasks),
        "migrate_action_rate": float(action_counts[2] / n_tasks),
        "action_switch_rate": switch_rate,
        "mean_active_risk_debt": float(debt_trace.mean()),
        "final_active_risk_debt": float(debt_trace[-1]),
        "mean_true_selected_risk": float(true_selected.mean()),
    }
