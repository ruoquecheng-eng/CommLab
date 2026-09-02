import numpy as np

from commlab.random_access.irsa import simulate_irsa
from commlab.computation.aircomp import simulate_aircomp_mean_aggregation
from commlab.scheduling.network_slicing import simulate_embb_urllc_slicing
from commlab.scheduling.energy_aoi import simulate_energy_harvesting_aoi


def test_irsa_zero_load_and_sic_gain():
    z=simulate_irsa(50,0.0,20,seed=1)
    assert z['decoded_packets']==0 and z['packet_loss_rate']==1.0
    a=simulate_irsa(80,.75,250,{3:1.0},iterative_sic=False,seed=2)
    b=simulate_irsa(80,.75,250,{3:1.0},iterative_sic=True,seed=2)
    assert b['throughput_packets_per_slot'] >= a['throughput_packets_per_slot']
    assert b['packet_loss_rate'] <= a['packet_loss_rate']


def test_aircomp_channel_use_and_mse_finite():
    o=simulate_aircomp_mean_aggregation(12,8,20,80,.35,seed=3)
    assert o['orthogonal_channel_uses_per_vector']==12
    assert o['aircomp_channel_uses_per_vector']==1
    assert 0<o['mean_active_fraction']<=1
    for k in ['orthogonal_mse','full_inversion_mse','truncated_inversion_mse']:
        assert np.isfinite(o[k]) and o[k]>=0


def test_preemptive_slicing_avoids_reservation_waste():
    r=simulate_embb_urllc_slicing(1200,24,.15,3,2,policy='reserved',fixed_reserved_prbs=8,seed=4)
    p=simulate_embb_urllc_slicing(1200,24,.15,3,2,policy='preemptive',seed=4)
    assert r['wasted_reserved_fraction']>0
    assert p['embb_throughput_bits_per_minislot'] > r['embb_throughput_bits_per_minislot']
    assert 0<=p['urllc_deadline_miss_rate']<=1


def test_energy_harvesting_aoi_energy_constraint_matters():
    rng=np.random.default_rng(5); T=rng.normal(4,2,(1000,4))
    low=simulate_energy_harvesting_aoi(T,np.full(4,.08),battery_capacity=2,seed=5)
    high=simulate_energy_harvesting_aoi(T,np.full(4,.7),battery_capacity=2,seed=5)
    assert low['energy_outage_fraction'] > high['energy_outage_fraction']
    assert low['mean_aoi'] > high['mean_aoi']
