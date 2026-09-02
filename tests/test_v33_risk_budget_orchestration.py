from commlab.computation import simulate_unified_risk_orchestration


def test_risk_budget_accounting_and_bounds():
    o = simulate_unified_risk_orchestration(
        n_tasks=2600, policy="risk_budget", budget_per_task=.75, seed=21
    )
    assert 0 <= o["deadline_miss_rate"] <= 1
    assert 0 <= o["task_weighted_deadline_miss_rate"] <= 1
    assert 1.0 <= o["mean_transmissions_per_task"] <= 2.0
    assert 0 <= o["replica_execution_rate"] <= 1
    # Token-bucket bursts are allowed, but long-run spend cannot materially
    # exceed replenishment (initial bucket is zero).
    assert o["resilience_credits_per_task"] <= .75 + 1e-9


def test_radio_correlation_reduces_duplication_value():
    low = simulate_unified_risk_orchestration(
        n_tasks=3500, policy="risk_budget", budget_per_task=.75,
        mean_snr_db=-3.0, edge_risk_scale=.55, radio_correlation=.05, seed=22,
    )
    high = simulate_unified_risk_orchestration(
        n_tasks=3500, policy="risk_budget", budget_per_task=.75,
        mean_snr_db=-3.0, edge_risk_scale=.55, radio_correlation=.92, seed=22,
    )
    assert high["duplicate_action_rate"] < low["duplicate_action_rate"]


def test_uncertainty_gate_suppresses_noisy_proactive_migration():
    greedy = simulate_unified_risk_orchestration(
        n_tasks=3600, policy="risk_budget", budget_per_task=.85,
        forecast_noise=1.1, seed=23,
    )
    gated = simulate_unified_risk_orchestration(
        n_tasks=3600, policy="uncertainty_gated", budget_per_task=.85,
        forecast_noise=1.1, seed=23,
    )
    assert gated["proactive_migration_rate"] < greedy["proactive_migration_rate"]
    assert gated["migration_traffic_mb_per_task"] <= greedy["migration_traffic_mb_per_task"] + 1e-12


def test_resource_regime_changes_action_mix():
    radio_limited = simulate_unified_risk_orchestration(
        n_tasks=3500, policy="risk_budget", budget_per_task=.8,
        mean_snr_db=-4.0, edge_risk_scale=.45, seed=24,
    )
    edge_limited = simulate_unified_risk_orchestration(
        n_tasks=3500, policy="risk_budget", budget_per_task=.8,
        mean_snr_db=5.0, edge_risk_scale=2.0, seed=24,
    )
    assert radio_limited["duplicate_action_rate"] > edge_limited["duplicate_action_rate"]
    assert (edge_limited["replicate_action_rate"] + edge_limited["migrate_action_rate"]) > (
        radio_limited["replicate_action_rate"] + radio_limited["migrate_action_rate"]
    )


def test_task_weighted_policy_preserves_critical_utility_signal():
    weighted = simulate_unified_risk_orchestration(
        n_tasks=5000, policy="risk_budget", budget_per_task=.48,
        mean_snr_db=6.0, edge_risk_scale=1.0, seed=25,
    )
    unweighted = simulate_unified_risk_orchestration(
        n_tasks=5000, policy="risk_budget_unweighted", budget_per_task=.48,
        mean_snr_db=6.0, edge_risk_scale=1.0, seed=25,
    )
    assert weighted["task_weighted_deadline_miss_rate"] <= unweighted["task_weighted_deadline_miss_rate"] + .02
    assert weighted["resilience_credits_per_task"] <= .48 + 1e-9
    assert unweighted["resilience_credits_per_task"] <= .48 + 1e-9


def test_high_budget_uncertainty_gate_can_leave_credits_unspent():
    greedy = simulate_unified_risk_orchestration(
        n_tasks=3600, policy="risk_budget", budget_per_task=2.2,
        forecast_noise=.4, mean_snr_db=6.0, seed=26,
    )
    gated = simulate_unified_risk_orchestration(
        n_tasks=3600, policy="uncertainty_gated", budget_per_task=2.2,
        forecast_noise=.4, mean_snr_db=6.0, seed=26,
    )
    assert gated["resilience_credits_per_task"] < greedy["resilience_credits_per_task"]
    assert gated["proactive_migration_rate"] < greedy["proactive_migration_rate"]
