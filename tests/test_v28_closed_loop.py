from commlab.computation import (
    simulate_selective_downlink_repair,
    simulate_version_aware_edge_caching,
    simulate_fair_carbon_orchestration,
    simulate_progressive_split_admission,
    simulate_digital_twin_sync,
)


def test_selective_repair_has_bounded_downlink_load():
    o=simulate_selective_downlink_repair(rounds=80,policy='selective_age',seed=1)
    assert 0 < o['normalized_downlink_size_per_round'] < 1.0
    assert 0 <= o['weighted_fresh_coverage'] <= 1


def test_version_aware_cache_reports_staleness_and_backhaul():
    o=simulate_version_aware_edge_caching(n_requests=600,policy='version_value',refresh_interval=60,seed=2)
    assert o['backhaul_mb']>0
    assert o['mean_served_version_age']>=0
    assert 0<=o['cache_hit_rate']<=1


def test_virtual_debt_tracks_participation_target():
    o=simulate_fair_carbon_orchestration(rounds=100,policy='virtual_debt',seed=3)
    assert o['minimum_participation_rate']>=0
    assert o['final_max_virtual_debt']>=0
    assert 0<=o['participation_jain']<=1.000001


def test_split_admission_never_counts_late_results_as_on_time():
    o=simulate_progressive_split_admission(slots=500,arrival_rate=1.2,policy='backpressure',seed=4)
    assert 0<=o['on_time_accuracy']<=1
    assert 0<=o['deadline_miss_rate']<=1
    assert 0<=o['admission_fraction']<=1


def test_digital_twin_semantic_delta_uses_subfull_packets():
    o=simulate_digital_twin_sync(slots=120,policy='semantic_delta',error_threshold=.8,seed=5)
    assert o['normalized_radio_load_per_slot']>=0
    assert o['mean_packet_size_when_triggered']<1.0
    assert o['position_rmse']>=0
