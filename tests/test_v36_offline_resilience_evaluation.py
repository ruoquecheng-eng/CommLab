import pytest

from commlab.computation import simulate_offline_resilience_evaluation, select_offline_resilience_policy


@pytest.mark.parametrize("estimator",["dm","ips","snips","dr","clipped_dr"])
def test_estimators_return_finite_bounded_metrics(estimator):
    o=simulate_offline_resilience_evaluation(n_tasks=2400,estimator=estimator,seed=2)
    assert 0<=o["estimated_weighted_miss"]<=1
    assert 0<=o["oracle_weighted_miss"]<=1
    assert o["standard_error"]>=0
    assert o["critical_logging_unprotected_rate"]==0


def test_safe_targets_have_overlap_under_safe_exploration():
    o=simulate_offline_resilience_evaluation(n_tasks=2600,target_policy="aggressive",exploration_rate=.08,seed=3)
    assert o["identifiable"]
    assert o["support_violation_mass"]==0
    assert o["critical_target_unprotected_probability"]==0


def test_unsafe_critical_probe_is_flagged_not_silently_identified():
    o=simulate_offline_resilience_evaluation(n_tasks=2600,target_policy="unsafe_critical_probe",seed=4)
    assert not o["identifiable"]
    assert o["support_violation_mass"]>0
    assert o["critical_target_unprotected_probability"]>0


def test_low_exploration_reduces_effective_sample_fraction():
    low=simulate_offline_resilience_evaluation(n_tasks=5000,target_policy="sparse",estimator="ips",exploration_rate=.01,seed=5)
    high=simulate_offline_resilience_evaluation(n_tasks=5000,target_policy="sparse",estimator="ips",exploration_rate=.20,seed=5)
    assert low["max_importance_weight"]>high["max_importance_weight"]
    assert low["effective_sample_fraction"]<high["effective_sample_fraction"]


def test_deterministic_logger_exposes_support_failure():
    o=simulate_offline_resilience_evaluation(n_tasks=3000,logging_policy="deterministic",target_policy="balanced",seed=6)
    assert not o["identifiable"]
    assert o["support_violation_mass"]>0


def test_selectors_return_safe_candidate_and_nonnegative_regret():
    for selector in ("greedy","conservative"):
        o=select_offline_resilience_policy(n_tasks=2600,selector=selector,seed=7)
        assert o["selected_policy"] in {"baseline","sparse","balanced","aggressive"}
        assert o["selection_regret"]>=-1e-12


@pytest.mark.parametrize("kwargs",[
    {"estimator":"bad"},{"n_tasks":100},{"exploration_rate":.7},
    {"recency_fraction":0},{"radio_correlation":1.2},{"clip_weight":1},
])
def test_invalid_setup_rejected(kwargs):
    with pytest.raises(ValueError): simulate_offline_resilience_evaluation(**kwargs)
