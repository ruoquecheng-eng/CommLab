import numpy as np
from commlab.computation import (
    topk_compress,allocate_coordinate_budget,simulate_budgeted_compressed_fl,simulate_aircomp_hardware,
    simulate_layered_multitask_semantic,simulate_importance_aware_random_access_fl,
    simulate_two_timescale_ris_aircomp_fl,
)


def test_topk_error_feedback_conserves_dropped_mass():
    x=np.array([1.,-3.,.2,2.])
    q,r=topk_compress(x,2,error_feedback=True)
    assert np.count_nonzero(q)==2
    assert np.allclose(q+r,x)


def test_budgeted_fl_outputs_valid_budget_metrics():
    o=simulate_budgeted_compressed_fl(n_clients=8,n_select=4,coordinate_budget=24,dim=16,rounds=12,seed=2201)
    assert o['topk_per_client']==6
    assert o['coordinates_per_round']<=24
    assert np.isfinite(o['final_loss'])


def test_aircomp_hardware_higher_adc_resolution_is_not_worse_on_fixed_seed():
    a=simulate_aircomp_hardware(n_devices=8,vector_dim=24,adc_bits=3,pa_saturation=3.0,n_trials=80,seed=2202)
    b=simulate_aircomp_hardware(n_devices=8,vector_dim=24,adc_bits=8,pa_saturation=3.0,n_trials=80,seed=2202)
    assert b['median_mse'] <= a['median_mse']


def test_layered_semantic_usage_between_one_and_two():
    o=simulate_layered_multitask_semantic(dim=10,n_samples=3000,task_angle_deg=65,snr_db=12,confidence_threshold=.5,seed=2203)
    assert 1 <= o['adaptive_mean_uses'] <= 2
    assert o['full_accuracy'] >= o['base_accuracy']-0.02


def test_importance_random_access_reports_gradient_mass():
    o=simulate_importance_aware_random_access_fl(n_clients=10,frame_slots=14,rounds=15,mode='importance',seed=2204)
    assert 0<=o['mean_decoded_gradient_mass']<=1
    assert o['mean_repetition_degree']>=2


def test_two_timescale_ris_control_overhead_decreases_with_interval():
    a=simulate_two_timescale_ris_aircomp_fl(n_clients=5,n_ris=6,rounds=12,update_interval=1,seed=2205)
    b=simulate_two_timescale_ris_aircomp_fl(n_clients=5,n_ris=6,rounds=12,update_interval=4,seed=2205)
    assert b['control_bits_per_round'] < a['control_bits_per_round']
    assert np.isfinite(a['final_loss']) and np.isfinite(b['final_loss'])


def test_residual_coordinate_allocator_respects_budget_and_caps():
    k=allocate_coordinate_budget([1.,4.,2.],budget=11,dim=6)
    assert int(k.sum())==11 and np.all(k>=1) and np.all(k<=6)
    assert k[1]>=k[0]
