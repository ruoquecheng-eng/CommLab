import numpy as np
from commlab.computation import (
    simulate_federated_aircomp, effective_ris_aircomp_channel,
    optimize_ris_aircomp, aircomp_noise_mse_from_channel,
    simulate_task_oriented_classification,
)
from commlab.random_access import simulate_capture_irsa


def test_federated_ideal_converges_and_aircomp_uses_fewer_channel_uses():
    ideal=simulate_federated_aircomp(rounds=35,mode='ideal',seed=21)
    ota=simulate_federated_aircomp(rounds=35,mode='truncated',snr_db=20,seed=21)
    orth=simulate_federated_aircomp(rounds=35,mode='orthogonal',snr_db=20,seed=21)
    assert ideal['loss_history'][-1] < ideal['loss_history'][0]
    assert ota['loss_history'][-1] < ota['loss_history'][0]
    assert ota['channel_uses']==35
    assert orth['channel_uses']==35*12


def test_ris_aircomp_maxmin_improves_weakest_gain_and_mse():
    rng=np.random.default_rng(22); K,N=8,12
    hd=(rng.normal(size=K)+1j*rng.normal(size=K))/np.sqrt(2)*.2
    F=(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2*N)
    g=(rng.normal(size=N)+1j*rng.normal(size=N))/np.sqrt(2*N)
    p,h=optimize_ris_aircomp(hd,F,g,bits=2,sweeps=2,objective='maxmin')
    h0=effective_ris_aircomp_channel(hd,F,g,np.ones(N,dtype=complex))
    h1=effective_ris_aircomp_channel(hd,F,g,p)
    assert np.min(np.abs(h1)) >= np.min(np.abs(h0))-1e-12
    a=aircomp_noise_mse_from_channel(h0,20,n_trials=100,seed=22)
    b=aircomp_noise_mse_from_channel(h1,20,n_trials=100,seed=22)
    assert b['median_mse'] <= a['median_mse']
    assert h.size==2


def test_task_oriented_saves_channel_uses_with_task_utility():
    o=simulate_task_oriented_classification(dim=16,n_samples=5000,separation=2.0,snr_db=10,seed=23)
    assert o['task_channel_uses']==1 and o['raw_channel_uses']==16
    assert o['task_accuracy']>0.8
    assert o['task_reconstruction_mse'] > o['raw_reconstruction_mse']


def test_capture_irsa_power_spread_can_help():
    a=simulate_capture_irsa(.7,80,80,power_spread_db=0,sinr_threshold_db=3,seed=24)
    b=simulate_capture_irsa(.7,80,80,power_spread_db=8,sinr_threshold_db=3,seed=24)
    assert b['throughput'] >= a['throughput']
    assert 0<=b['packet_loss_rate']<=1

from commlab.computation import simulate_cellfree_aircomp

def test_cellfree_aircomp_improves_weakest_gain():
    o=simulate_cellfree_aircomp(n_aps=6,n_devices=8,vector_dim=8,snr_db=18,n_trials=50,seed=25,n_random=80)
    assert o['cellfree_mean_weakest_gain'] >= o['single_ap_mean_weakest_gain']
    assert o['cellfree_median_mse'] <= o['single_ap_median_mse']
