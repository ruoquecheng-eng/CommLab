import numpy as np
from commlab.computation import (
    simulate_selection_biased_fl, simulate_random_access_federated,
    optimize_robust_ris_aircomp, effective_ris_aircomp_channel,
    simulate_imperfect_csi_cellfree_aircomp, simulate_multitask_task_oriented,
)


def test_channel_only_selection_can_be_less_fair_than_age_aware():
    a=simulate_selection_biased_fl('channel',rounds=40,n_select=4,channel_disparity_db=10,seed=101)
    b=simulate_selection_biased_fl('age_channel',rounds=40,n_select=4,channel_disparity_db=10,seed=101)
    assert b['participation_jain'] >= a['participation_jain']
    assert 0 <= a['plus_selection_fraction'] <= 1


def test_irsa_access_decodes_more_than_aloha_at_moderate_load():
    a=simulate_random_access_federated('aloha',n_clients=12,frame_slots=16,rounds=25,seed=102)
    b=simulate_random_access_federated('irsa',n_clients=12,frame_slots=16,rounds=25,seed=102)
    assert b['mean_decoded_fraction'] >= a['mean_decoded_fraction']
    assert b['final_loss'] < b['loss_history'][0]


def test_robust_ris_returns_valid_finite_bit_phases():
    rng=np.random.default_rng(103); K,N=6,8
    hd=(rng.normal(size=K)+1j*rng.normal(size=K))/np.sqrt(2)*.2
    F=(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2*N)
    g=(rng.normal(size=N)+1j*rng.normal(size=N))/np.sqrt(2*N)
    p,h=optimize_robust_ris_aircomp(hd,F,g,error_std=.1,bits=2,sweeps=1,n_uncertainty=6,seed=103)
    assert p.shape==(N,) and np.allclose(np.abs(p),1)
    assert h.size==1 and np.isfinite(h).all()
    he=effective_ris_aircomp_channel(hd,F,g,p)
    assert he.shape==(K,)


def test_robust_cellfree_metrics_are_finite():
    o=simulate_imperfect_csi_cellfree_aircomp(n_aps=5,n_devices=6,n_trials=20,csi_error_std=.2,seed=104)
    for k,v in o.items():
        if k!='csi_error_std': assert np.isfinite(v)
    assert o['naive_median_mse']>=0 and o['robust_median_mse']>=0


def test_multitask_rank_two_preserves_tasks_better_when_orthogonal():
    o=simulate_multitask_task_oriented(dim=12,n_samples=5000,task_angle_deg=90,snr_db=15,seed=105)
    assert o['shared_rank2_mean_accuracy'] > o['shared_rank1_mean_accuracy']
    assert o['shared_rank1_uses']==1 and o['shared_rank2_uses']==2 and o['raw_uses']==12

from commlab.computation import simulate_lcb_cellfree_aircomp

def test_lcb_cellfree_aircomp_outputs_tail_metrics():
    o=simulate_lcb_cellfree_aircomp(n_aps=5,n_devices=6,n_trials=20,max_csi_error=.4,z=.5,seed=106)
    assert o['naive_p90_mse']>=0 and o['lcb_p90_mse']>=0
    assert 0<=o['lcb_win_fraction']<=1
