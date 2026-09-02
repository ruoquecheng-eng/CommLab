from commlab.computation import (simulate_personalized_federated, simulate_straggler_resilience,
    simulate_federated_distillation, simulate_channel_aware_split, simulate_sign_aircomp)


def test_personalization_endpoints_valid():
    a=simulate_personalized_federated(personalization=0,seed=2401)
    b=simulate_personalized_federated(personalization=1,seed=2401)
    assert abs(a['mean_personalized_test_mse']-a['mean_global_test_mse'])<1e-10
    assert abs(b['mean_personalized_test_mse']-b['mean_local_test_mse'])<1e-10


def test_mds_straggler_redundancy_reduces_tail_latency_fixed_seed():
    u=simulate_straggler_resilience(strategy='uncoded',seed=2402,rounds=5000)
    c=simulate_straggler_resilience(strategy='mds',seed=2402,rounds=5000,redundancy=5)
    assert c['p95_latency_ms'] < u['p95_latency_ms']
    assert c['compute_load_ratio']>1


def test_distillation_uses_fewer_scalars_when_probe_count_below_dimension():
    o=simulate_federated_distillation(dim=24,public_probes=10,seed=2403)
    assert o['distill_upload_scalars'] < o['model_upload_scalars']
    assert 0<=o['distilled_accuracy']<=1


def test_channel_aware_split_respects_deadline():
    o=simulate_channel_aware_split(policy='channel_aware',deadline_ms=1.8,seed=2404)
    assert o['deadline_miss_rate']==0
    assert o['mean_channel_uses']>=0


def test_sign_aircomp_more_clients_improves_majority_baseline():
    a=simulate_sign_aircomp(n_clients=5,snr_db=4,client_gradient_noise=.6,trials=500,seed=2405)
    b=simulate_sign_aircomp(n_clients=31,snr_db=4,client_gradient_noise=.6,trials=500,seed=2405)
    assert b['sign_error_rate'] < a['sign_error_rate']
