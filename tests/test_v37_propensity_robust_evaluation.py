import pytest

from commlab.computation import simulate_propensity_robust_evaluation, select_propensity_robust_policy


@pytest.mark.parametrize("mode",["recorded_true","recorded_nominal","stale_recorded","estimated_full","estimated_crossfit","misspecified"])
def test_propensity_modes_are_finite_and_safe(mode):
    o=simulate_propensity_robust_evaluation(n_tasks=2200,propensity_mode=mode,seed=2)
    assert 0<=o["estimated_weighted_miss"]<=1
    assert 0<=o["oracle_weighted_miss"]<=1
    assert o["critical_logging_unprotected_rate"]==0
    assert o["effective_sample_fraction"]>0


def test_true_propensity_has_zero_propensity_error_and_unit_gamma():
    o=simulate_propensity_robust_evaluation(n_tasks=2400,propensity_mode="recorded_true",hidden_confounding=1.2,seed=3)
    assert o["propensity_mae"]==0
    assert o["required_sensitivity_gamma"]==pytest.approx(1.0)


def test_hidden_confounding_requires_wider_odds_envelope():
    clear=simulate_propensity_robust_evaluation(n_tasks=3000,propensity_mode="recorded_nominal",hidden_confounding=0,seed=4)
    hidden=simulate_propensity_robust_evaluation(n_tasks=3000,propensity_mode="recorded_nominal",hidden_confounding=1.4,seed=4)
    assert clear["required_sensitivity_gamma"]==pytest.approx(1.0)
    assert hidden["required_sensitivity_gamma"]>clear["required_sensitivity_gamma"]
    assert hidden["propensity_mae"]>clear["propensity_mae"]


def test_sensitivity_interval_widens_and_contains_point_at_gamma_one():
    one=simulate_propensity_robust_evaluation(n_tasks=2600,sensitivity_gamma=1,seed=5)
    wide=simulate_propensity_robust_evaluation(n_tasks=2600,sensitivity_gamma=3,seed=5)
    assert one["sensitivity_low"]==pytest.approx(one["estimated_weighted_miss"])
    assert one["sensitivity_high"]==pytest.approx(one["estimated_weighted_miss"])
    assert wide["sensitivity_width"]>one["sensitivity_width"]
    assert wide["sensitivity_low"]<=wide["estimated_weighted_miss"]<=wide["sensitivity_high"]


@pytest.mark.parametrize("selector",["point","sensitivity_guard"])
def test_selector_returns_safe_candidate(selector):
    o=select_propensity_robust_policy(n_tasks=1800,selector=selector,seed=6)
    assert o["selected_policy"] in {"baseline","sparse","balanced","aggressive"}
    assert o["selection_regret"]>=-1e-12


@pytest.mark.parametrize("kwargs",[
    {"n_tasks":100},{"propensity_mode":"bad"},{"estimator":"bad"},
    {"exploration_floor":0},{"folds":1},{"hidden_confounding":-1},
    {"sensitivity_gamma":.9},{"clip_weight":1},
])
def test_invalid_setup_rejected(kwargs):
    with pytest.raises(ValueError): simulate_propensity_robust_evaluation(**kwargs)
