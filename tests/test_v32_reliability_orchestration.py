from commlab.computation import (
    simulate_semantic_harq, simulate_mixed_control_inference,
    simulate_failure_domain_replication, simulate_checkpoint_aware_migration,
    simulate_safety_bit_allocation,
)


def test_semantic_harq_bounds_and_cost():
    o=simulate_semantic_harq(n_samples=1200,policy='task_harq',seed=1)
    assert 0 <= o['accuracy'] <= 1
    assert 1 <= o['mean_channel_uses'] <= 2
    assert 0 <= o['retransmission_rate'] <= 1


def test_mixed_service_metrics():
    o=simulate_mixed_control_inference(slots=900,policy='task_value',seed=2)
    assert o['mean_control_cost'] >= 0
    assert 0 <= o['inference_completion_rate'] <= 1
    assert 0 <= o['control_slot_fraction'] <= 1


def test_failure_domain_budget_and_outage():
    o=simulate_failure_domain_replication(n_requests=1500,storage_budget_mb=2500,seed=3)
    assert o['storage_used_mb'] <= 2500+1e-9
    assert 0 <= o['task_weighted_outage_rate'] <= 1
    assert o['mean_failure_domains_per_model'] >= 1


def test_service_migration_metrics():
    o=simulate_checkpoint_aware_migration(steps=1200,policy='predictive_checkpoint',seed=4)
    assert o['mean_latency_ms'] > 0
    assert o['p95_latency_ms'] >= o['mean_latency_ms']
    assert o['migration_traffic_mb_per_step'] >= 0


def test_safety_bit_budget_respected():
    o=simulate_safety_bit_allocation(slots=900,policy='risk_bitalloc',bit_budget=10,seed=5)
    assert o['mean_payload_bits_per_slot'] <= 10+1e-9
    assert 0 <= o['safety_violation_rate'] <= 1
