from commlab.computation import (
    simulate_safety_aware_control, simulate_channel_adaptive_depth,
    simulate_edge_failure_recovery, simulate_risk_aware_model_replication,
    simulate_component_selective_control,
)

def test_safety_control_metrics_valid():
    o=simulate_safety_aware_control(slots=700,seed=1)
    assert 0 <= o['safety_violation_rate'] <= 1
    assert o['p95_control_cost'] >= o['mean_control_cost'] >= 0

def test_adaptive_depth_bounds():
    o=simulate_channel_adaptive_depth(n_tasks=900,policy='adaptive',seed=2)
    assert 2 <= o['mean_feature_bits'] <= 8
    assert 1 <= o['mean_model_depth'] <= 4
    assert 0 <= o['on_time_accuracy'] <= 1

def test_failure_recovery_metrics():
    o=simulate_edge_failure_recovery(n_tasks=900,policy='checkpoint',seed=3)
    assert o['p95_latency_ms'] >= o['mean_latency_ms'] > 0
    assert o['recovery_traffic_mb_per_task'] >= 0

def test_model_replication_budget_and_outage():
    o=simulate_risk_aware_model_replication(n_requests=1000,storage_budget_mb=2200,seed=4)
    assert o['storage_used_mb'] <= 2200+1e-9
    assert 0 <= o['model_outage_rate'] <= 1

def test_component_control_bounds():
    o=simulate_component_selective_control(slots=700,seed=5)
    assert 0 <= o['update_success_rate'] <= 1
    assert 6 <= o['mean_payload_bits_per_slot'] <= 7
