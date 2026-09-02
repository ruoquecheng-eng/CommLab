from commlab.computation import (
    simulate_risk_sensitive_control, simulate_variable_rate_control,
    simulate_failure_aware_edge_orchestration, simulate_joint_cache_offload,
    simulate_cooperative_networked_control,
)


def test_risk_control_returns_tail_metrics():
    o=simulate_risk_sensitive_control(slots=700,policy='risk_value',seed=1)
    assert o['cvar95_control_cost'] >= o['p95_control_cost'] >= 0
    assert o['mean_control_cost'] >= 0


def test_variable_rate_control_has_bounded_payload_and_success():
    o=simulate_variable_rate_control(slots=600,policy='adaptive',seed=2)
    assert 3 <= o['mean_payload_bits_per_slot'] <= 10
    assert 0 <= o['update_success_rate'] <= 1


def test_edge_orchestration_metrics_are_valid():
    o=simulate_failure_aware_edge_orchestration(n_tasks=900,policy='risk_aware',seed=3)
    assert 0 <= o['failure_rate'] <= 1 and 0 <= o['deadline_miss_rate'] <= 1
    assert o['p95_latency_ms'] >= o['mean_latency_ms']


def test_joint_cache_offload_has_bounded_hit_rate():
    o=simulate_joint_cache_offload(n_requests=900,policy='joint',seed=4)
    assert 0 <= o['cache_hit_rate'] <= 1
    assert o['backhaul_mb_per_request'] >= 0


def test_cooperative_control_is_finite():
    o=simulate_cooperative_networked_control(slots=700,policy='system_value',seed=5)
    assert o['mean_system_cost'] >= 0
    assert o['p95_system_cost'] >= o['mean_system_cost']


def test_zero_risk_weight_degenerates_to_mean_value_policy():
    a=simulate_risk_sensitive_control(slots=900,policy='mean_value',mean_snr_db=-2,seed=11)
    b=simulate_risk_sensitive_control(slots=900,policy='risk_value',mean_snr_db=-2,risk_weight=0.0,seed=11)
    assert abs(a['mean_control_cost']-b['mean_control_cost']) < 1e-12
    assert abs(a['cvar95_control_cost']-b['cvar95_control_cost']) < 1e-12
