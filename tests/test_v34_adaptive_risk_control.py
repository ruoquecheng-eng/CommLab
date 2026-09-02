import pytest

from commlab.computation import simulate_adaptive_risk_control


def test_adaptive_risk_accounting_and_bounds():
    o = simulate_adaptive_risk_control(n_tasks=2600, policy="adaptive_local", seed=41)
    assert 0 <= o["deadline_miss_rate"] <= 1
    assert 0 <= o["critical_miss_rate"] <= 1
    assert 1 <= o["mean_transmissions_per_task"] <= 2
    assert o["resilience_credits_per_task"] <= 0.85 + 1e-12
    assert o["cvar95_latency_ms"] >= o["p95_latency_ms"]


def test_delayed_feedback_is_enforced_and_changes_closed_loop():
    fast = simulate_adaptive_risk_control(
        n_tasks=4200, policy="adaptive_local", feedback_delay=1, drift_strength=1.3, seed=42
    )
    slow = simulate_adaptive_risk_control(
        n_tasks=4200, policy="adaptive_local", feedback_delay=80, drift_strength=1.3, seed=42
    )
    assert fast["feedback_delay"] == 1
    assert slow["feedback_delay"] == 80
    assert abs(fast["mean_active_risk_debt"] - slow["mean_active_risk_debt"]) > 1e-4


def test_local_feedback_reacts_to_critical_class_shift():
    global_policy = simulate_adaptive_risk_control(
        n_tasks=6500, policy="adaptive_global", drift_strength=1.5, budget_per_task=1.0, seed=43
    )
    local = simulate_adaptive_risk_control(
        n_tasks=6500, policy="adaptive_local", drift_strength=1.5, budget_per_task=1.0, seed=43
    )
    assert local["mean_active_risk_debt"] > 0
    assert local["post_drift_critical_miss_rate"] < global_policy["post_drift_critical_miss_rate"]
    assert local["post_drift_task_weighted_miss_rate"] < global_policy["post_drift_task_weighted_miss_rate"]


def test_oracle_is_analysis_only_but_uses_same_budget_contract():
    o = simulate_adaptive_risk_control(
        n_tasks=3000, policy="oracle", budget_per_task=0.7, drift_strength=1.2, seed=44
    )
    assert o["resilience_credits_per_task"] <= 0.7 + 1e-12
    assert o["mean_true_selected_risk"] >= 0


@pytest.mark.parametrize("bad_policy", ["conformal", "genie", "unknown"])
def test_invalid_policy_rejected(bad_policy):
    with pytest.raises(ValueError):
        simulate_adaptive_risk_control(policy=bad_policy)
