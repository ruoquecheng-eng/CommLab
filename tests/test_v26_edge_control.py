from commlab.computation import (
    simulate_differential_model_broadcast, simulate_progressive_split_inference,
    simulate_aircomp_selection_federated, simulate_energy_harvesting_aircomp_fl,
    simulate_importance_aware_model_multicast,
)


def test_anchored_delta_recovers_better_than_chained_same_keyframes():
    a=simulate_differential_model_broadcast(scheme='chained_delta',keyframe_interval=12,seed=2601)
    b=simulate_differential_model_broadcast(scheme='anchored_delta',keyframe_interval=12,seed=2601)
    assert b['mean_version_age'] <= a['mean_version_age']


def test_progressive_split_uses_no_more_than_full_residual():
    o=simulate_progressive_split_inference(policy='adaptive',seed=2602)
    assert o['mean_channel_uses'] <= o['full_residual_uses']
    assert o['deadline_miss_rate'] == 0


def test_aircomp_diversity_reduces_selection_bias():
    c=simulate_aircomp_selection_federated(strategy='channel',channel_disparity_db=12,rounds=70,seed=2603)
    d=simulate_aircomp_selection_federated(strategy='diversity',channel_disparity_db=12,rounds=70,seed=2603)
    assert abs(d['plus_selection_fraction']-.5) < abs(c['plus_selection_fraction']-.5)


def test_eh_age_policy_improves_participation_fairness():
    c=simulate_energy_harvesting_aircomp_fl(policy='channel',harvest_scale=.3,rounds=80,seed=2604)
    a=simulate_energy_harvesting_aircomp_fl(policy='age_energy',harvest_scale=.3,rounds=80,seed=2604)
    assert a['participation_jain'] >= c['participation_jain']


def test_importance_multicast_returns_valid_tradeoff():
    o=simulate_importance_aware_model_multicast(seed=2605)
    assert 0 < o['importance_weighted_utility'] <= 1.5
    assert o['importance_time'] > 0
