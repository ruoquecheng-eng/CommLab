from commlab.computation import (
    simulate_predictive_failure_migration,
    simulate_chance_constrained_inference,
    simulate_control_uep,
    simulate_multi_connectivity_reliability,
    simulate_multiconnectivity_safety_control,
    simulate_failure_domain_replication,
)


def test_predictive_migration_metrics_and_churn_crossover():
    low = simulate_predictive_failure_migration(steps=2200, policy='predictive_risk', forecast_noise=.1, seed=7)
    high = simulate_predictive_failure_migration(steps=2200, policy='predictive_risk', forecast_noise=1.0, seed=7)
    assert low['mean_latency_ms'] > 0
    assert low['p95_latency_ms'] >= low['mean_latency_ms']
    assert high['migration_rate'] > low['migration_rate']
    assert high['migration_traffic_mb_per_step'] > low['migration_traffic_mb_per_step']


def test_chance_admission_reduces_deadline_tail():
    mean = simulate_chance_constrained_inference(n_tasks=5000, policy='mean_latency', jitter_scale=.8, deadline_ms=50, seed=8)
    chance = simulate_chance_constrained_inference(n_tasks=5000, policy='chance', jitter_scale=.8, deadline_ms=50, seed=8)
    assert chance['admission_rate'] < mean['admission_rate']
    assert chance['deadline_miss_rate'] < mean['deadline_miss_rate']
    assert 0 <= chance['on_time_utility_per_task'] <= chance['raw_utility_per_task'] + 1e-12


def test_control_uep_fixed_radio_budget():
    eq = simulate_control_uep(slots=1600, policy='equal', mean_snr_db=-3, seed=9)
    uep = simulate_control_uep(slots=1600, policy='critical_uep', mean_snr_db=-3, seed=9)
    assert eq['mean_repetitions_per_slot'] == uep['mean_repetitions_per_slot'] == 5.0
    assert uep['critical_component_miss_rate'] < eq['critical_component_miss_rate']
    assert len(uep['component_delivery_rate']) == 3


def test_multi_connectivity_overhead_and_correlation():
    single = simulate_multi_connectivity_reliability(n_packets=8000, policy='single', correlation=.1, seed=10)
    full_low = simulate_multi_connectivity_reliability(n_packets=8000, policy='full_duplicate', correlation=.1, seed=10)
    full_high = simulate_multi_connectivity_reliability(n_packets=8000, policy='full_duplicate', correlation=.9, seed=10)
    adaptive = simulate_multi_connectivity_reliability(n_packets=8000, policy='adaptive', correlation=.1, seed=10)
    assert full_low['packet_outage_rate'] < single['packet_outage_rate']
    assert full_high['packet_outage_rate'] > full_low['packet_outage_rate']
    assert 1.0 < adaptive['mean_transmissions_per_packet'] < 2.0


def test_failure_domain_alias_and_diversity():
    critical = simulate_failure_domain_replication(n_requests=3000, policy='criticality', storage_budget_mb=2800, zone_failure_prob=.1, seed=11)
    diverse = simulate_failure_domain_replication(n_requests=3000, policy='diversity_risk', storage_budget_mb=2800, zone_failure_prob=.1, seed=11)
    assert diverse['mean_failure_domains_per_model'] > critical['mean_failure_domains_per_model']
    assert diverse['storage_used_mb'] <= 2800 + 1e-9


def test_multiconnectivity_control_radio_accounting():
    adaptive = simulate_multiconnectivity_safety_control(slots=1500, policy='adaptive_duplicate', correlation=.4, seed=12)
    full = simulate_multiconnectivity_safety_control(slots=1500, policy='full_duplicate', correlation=.4, seed=12)
    assert 1.0 <= adaptive['mean_transmissions_per_slot'] < 2.0
    assert full['mean_transmissions_per_slot'] == 2.0
    assert 0 <= adaptive['safety_violation_rate'] <= 1


def test_adaptive_duplication_threshold_controls_resource_budget():
    aggressive = simulate_multi_connectivity_reliability(n_packets=9000, policy='adaptive', correlation=.3, seed=13, duplication_threshold=.05)
    conservative = simulate_multi_connectivity_reliability(n_packets=9000, policy='adaptive', correlation=.3, seed=13, duplication_threshold=.35)
    assert aggressive['mean_transmissions_per_packet'] > conservative['mean_transmissions_per_packet']
    assert aggressive['packet_outage_rate'] <= conservative['packet_outage_rate'] + 1e-12
