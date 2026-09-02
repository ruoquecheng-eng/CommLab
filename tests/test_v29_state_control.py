from commlab.computation import (
    simulate_task_aware_model_repair,
    simulate_congested_model_refresh,
    simulate_battery_carbon_fair_fl,
    simulate_twin_guided_model_prefetch,
    simulate_networked_control_scheduling,
)


def test_task_repair_respects_bounded_downlink_load():
    o=simulate_task_aware_model_repair(rounds=70,policy='task_aware',seed=1)
    assert 0 < o['normalized_downlink_size_per_round'] < 1.0
    assert 0 <= o['task_utility_ratio'] <= 1.000001


def test_congested_refresh_exposes_a_real_backhaul_queue():
    o=simulate_congested_model_refresh(n_requests=500,policy='eager',backhaul_service_mb_per_request=.8,seed=2)
    assert o['refresh_requested_mb'] >= o['refresh_delivered_mb']
    assert o['p95_backhaul_queue_mb'] >= 0
    assert 0 <= o['stale_hit_fraction'] <= 1


def test_constrained_fl_obeys_energy_causality_metrics():
    o=simulate_battery_carbon_fair_fl(rounds=80,policy='debt_battery_carbon',harvest_scale=.25,seed=3)
    assert 0 <= o['mean_fraction_clients_energy_infeasible'] <= 1
    assert 0 <= o['participation_jain'] <= 1.000001
    assert o['final_max_virtual_debt'] >= 0


def test_twin_prefetch_has_bounded_hit_and_prefetch_error_rates():
    o=simulate_twin_guided_model_prefetch(slots=400,policy='uncertainty_gated',seed=4)
    assert 0 <= o['cache_hit_rate'] <= 1
    assert 0 <= o['wrong_prefetch_fraction'] <= 1
    assert o['total_backhaul_mb'] >= 0


def test_networked_control_scheduler_returns_finite_closed_loop_cost():
    o=simulate_networked_control_scheduling(slots=500,policy='control_value',seed=5)
    assert o['mean_control_cost'] >= 0
    assert o['max_state_excursion'] < 80.000001
    assert 0 <= o['successful_update_fraction'] <= 1

def test_uncertainty_gating_reduces_wrong_prefetch_under_noisy_twin():
    a=simulate_twin_guided_model_prefetch(slots=700,policy='predictive',twin_noise_std=.8,seed=11)
    b=simulate_twin_guided_model_prefetch(slots=700,policy='uncertainty_gated',twin_noise_std=.8,seed=11)
    assert b['wrong_prefetch_fraction'] < a['wrong_prefetch_fraction']
    assert b['total_backhaul_mb'] < a['total_backhaul_mb']


def test_control_value_can_trade_higher_age_for_lower_closed_loop_cost():
    a=simulate_networked_control_scheduling(slots=1200,policy='max_age',mean_snr_db=-4,seed=7)
    b=simulate_networked_control_scheduling(slots=1200,policy='control_value',mean_snr_db=-4,seed=7)
    assert b['mean_control_cost'] < a['mean_control_cost']
    assert b['mean_information_age'] > a['mean_information_age']
