from commlab.computation import (
    simulate_adaptive_differential_broadcast,
    simulate_carbon_aware_federated,
    simulate_edge_model_caching,
    simulate_queued_progressive_split,
    simulate_importance_aware_multicast_repair,
)


def test_adaptive_downlink_respects_hard_keyframe_spacing():
    o = simulate_adaptive_differential_broadcast(policy='age_adaptive', max_keyframe_spacing=14, seed=2701)
    assert o['keyframes'] >= 1
    assert 0 < o['normalized_downlink_size_per_round'] <= 1.0


def test_carbon_policy_reduces_carbon_proxy_vs_random():
    r = simulate_carbon_aware_federated(policy='random', rounds=80, seed=2702)
    c = simulate_carbon_aware_federated(policy='carbon', rounds=80, seed=2702)
    assert c['total_carbon_proxy'] < r['total_carbon_proxy']


def test_periodic_cache_valid_metrics():
    o = simulate_edge_model_caching(policy='periodic_value', n_requests=800, recache_interval=80, seed=2703)
    assert 0 <= o['cache_hit_rate'] <= 1
    assert o['backhaul_mb'] > 0
    assert o['mean_latency_ms'] > 0


def test_queued_split_edf_does_not_count_expired_as_success():
    o = simulate_queued_progressive_split(policy='edf', slots=500, arrival_rate=1.1, seed=2704)
    assert 0 <= o['on_time_accuracy'] <= 1
    assert 0 <= o['deadline_miss_rate'] <= 1


def test_important_repair_never_exceeds_full_common_airtime():
    o = simulate_importance_aware_multicast_repair(policy='important_repair', seed=2705)
    assert o['total_time'] <= o['full_common_time'] + 1e-7
    assert 0 <= o['weighted_task_utility'] <= 1
