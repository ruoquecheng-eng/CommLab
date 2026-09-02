from commlab.computation import (
    simulate_resilient_async_federated, simulate_clustered_personalization,
    simulate_private_hardware_aircomp, simulate_energy_aware_split,
    simulate_layered_model_multicast,
)


def test_resilient_async_beats_naive_under_attack_delay():
    a=simulate_resilient_async_federated(strategy='naive_mean',rounds=60,seed=2501)
    b=simulate_resilient_async_federated(strategy='stale_robust',rounds=60,seed=2501)
    assert b['final_loss'] < a['final_loss']


def test_cluster_personalization_endpoints_structured_heterogeneity():
    o=simulate_clustered_personalization(cluster_separation=1.1,cluster_assignment_error=0,seed=2502)
    assert o['cluster_mse'] < o['global_mse']


def test_private_hardware_more_adc_bits_not_worse_fixed_seed():
    a=simulate_private_hardware_aircomp(adc_bits=3,trials=80,seed=2503)
    b=simulate_private_hardware_aircomp(adc_bits=8,trials=80,seed=2503)
    assert b['median_mse'] <= a['median_mse']


def test_energy_aware_split_respects_deadline():
    o=simulate_energy_aware_split(policy='energy_aware',deadline_ms=2.2,seed=2504)
    assert o['deadline_miss_rate']==0
    assert o['mean_energy_mj']>0


def test_layered_multicast_uses_less_time_than_serial_unicast():
    o=simulate_layered_model_multicast(seed=2505)
    assert o['layered_time'] < o['unicast_time']
    assert 0<o['layered_mean_utility']<=1
