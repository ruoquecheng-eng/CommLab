import pytest

from commlab.computation import simulate_observable_resilience


def test_observable_resilience_accounting_bounds():
    o=simulate_observable_resilience(n_tasks=2600,policy="hybrid_feedback",seed=51)
    assert 0 <= o["protected_miss_rate"] <= o["unprotected_counterfactual_miss_rate"] <= 1
    assert o["resilience_credits_per_task"] <= .9 + 1e-12
    assert 1 <= o["mean_transmissions_per_task"] <= 2
    assert o["critical_audit_fraction"] == 0


def test_more_budget_can_mask_more_primary_failures():
    low=simulate_observable_resilience(n_tasks=5000,policy="outcome_only",budget_per_task=.25,seed=52)
    high=simulate_observable_resilience(n_tasks=5000,policy="outcome_only",budget_per_task=1.25,seed=52)
    assert high["masked_failure_rate"] > low["masked_failure_rate"]
    assert high["protected_miss_rate"] < low["protected_miss_rate"]


def test_component_feedback_attributes_radio_and_edge_regimes():
    radio=simulate_observable_resilience(n_tasks=6000,policy="component_telemetry",drift_mode="radio",seed=53)
    edge=simulate_observable_resilience(n_tasks=6000,policy="component_telemetry",drift_mode="edge",seed=53)
    assert radio["duplicate_action_rate"] > edge["duplicate_action_rate"]
    assert edge["replica_action_rate"] > radio["replica_action_rate"]


def test_full_telemetry_suppresses_hybrid_audits():
    o=simulate_observable_resilience(n_tasks=3000,policy="hybrid_feedback",telemetry_probability=1,audit_rate=.2,seed=54)
    assert o["component_observation_rate"] == 1
    assert o["audit_fraction"] == 0


def test_telemetry_loss_reduces_component_observations():
    high=simulate_observable_resilience(n_tasks=3200,policy="component_telemetry",telemetry_probability=.95,seed=55)
    low=simulate_observable_resilience(n_tasks=3200,policy="component_telemetry",telemetry_probability=.25,seed=55)
    assert high["component_observation_rate"] > low["component_observation_rate"]


def test_audits_are_restricted_to_routine_tasks():
    o=simulate_observable_resilience(n_tasks=4000,policy="audit_feedback",audit_rate=.2,seed=56)
    assert o["audit_fraction"] > 0
    assert o["critical_audit_fraction"] == 0


@pytest.mark.parametrize("kwargs",[{"policy":"genie"},{"drift_mode":"cyber"},{"telemetry_probability":1.2}])
def test_invalid_observability_setup(kwargs):
    with pytest.raises(ValueError):
        simulate_observable_resilience(**kwargs)
