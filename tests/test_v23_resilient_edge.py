import numpy as np
from commlab.computation import (
    simulate_asynchronous_federated, aggregate_gradients, simulate_byzantine_federated,
    clip_rows, simulate_private_aircomp_fl, simulate_semantic_resource_scheduling,
    simulate_split_inference,
)

def test_quadratic_stale_correction_is_exact_for_local_gradient():
    a=simulate_asynchronous_federated(strategy='naive',rounds=30,max_delay=0,seed=2301)
    b=simulate_asynchronous_federated(strategy='quadratic_corrected',rounds=30,max_delay=0,seed=2301)
    assert np.allclose(a['loss_history'],b['loss_history'])

def test_robust_aggregators_reject_single_extreme_coordinate_outlier():
    G=np.array([[1.,2.],[1.1,1.9],[.9,2.1],[100.,-100.]])
    assert np.linalg.norm(aggregate_gradients(G,'median')-[1.,2.]) < .2
    assert np.linalg.norm(aggregate_gradients(G,'mean')-[1.,2.]) > 10

def test_clipping_respects_norm_bound():
    G=clip_rows([[3.,4.],[.1,.2]],1.0)
    assert np.all(np.linalg.norm(G,axis=1)<=1.000001)

def test_private_aircomp_noise_increases_aggregation_distortion_fixed_seed():
    a=simulate_private_aircomp_fl(rounds=15,privacy_noise_multiplier=0,seed=2303)
    b=simulate_private_aircomp_fl(rounds=15,privacy_noise_multiplier=.8,seed=2303)
    assert b['mean_aggregation_mse'] > a['mean_aggregation_mse']

def test_semantic_scheduler_outputs_valid_metrics():
    o=simulate_semantic_resource_scheduling(slots=40,seed=2304,strategy='urgency_aware')
    assert o['task_utility']>=0 and 0<=o['resource_utilization']<=1

def test_split_inference_resource_ordering():
    l=simulate_split_inference(mode='local',n_samples=3000,seed=2305)
    e=simulate_split_inference(mode='edge',n_samples=3000,seed=2305)
    a=simulate_split_inference(mode='adaptive',n_samples=3000,seed=2305)
    assert l['mean_channel_uses']==0
    assert 0<=a['mean_channel_uses']<=e['mean_channel_uses']
    assert e['mean_channel_uses']>0

def test_byzantine_simulation_finite():
    o=simulate_byzantine_federated(method='median',rounds=10,seed=2306)
    assert np.isfinite(o['final_loss'])

def test_split_latency_increases_when_all_samples_are_offloaded():
    l=simulate_split_inference(mode='local',n_samples=2000,seed=2310)
    e=simulate_split_inference(mode='edge',n_samples=2000,seed=2310)
    assert e['mean_latency_ms'] > l['mean_latency_ms']
