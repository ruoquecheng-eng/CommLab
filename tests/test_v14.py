import numpy as np
from commlab.mimo.cell_free import sample_cell_free_channel
from commlab.mimo.pilot_assignment import (
    large_scale_overlap, pilot_contamination_cost,
    greedy_contamination_aware_assignment, lmmse_pilot_channel_estimate,
    normalized_channel_mse,
)
from commlab.ris.cellfree import effective_cellfree_ris_channel, coordinate_optimize_cellfree_ris, cellfree_ris_rates
from commlab.scheduling.cross_layer import simulate_cross_layer_link
from commlab.sensing.joint_beamforming import joint_isac_beamformer, communication_rate, sensing_gain, ula_steering


def test_greedy_pilot_assignment_reduces_structured_overlap():
    beta=np.array([
        [10,8,1,1], [9,7,1,1],
        [1,1,10,8], [1,1,9,7],
    ],float)
    bad=np.array([0,0,1,1])
    greedy=greedy_contamination_aware_assignment(beta,2)
    assert pilot_contamination_cost(beta,greedy) < pilot_contamination_cost(beta,bad)
    assert large_scale_overlap(beta).shape==(4,4)


def test_lmmse_pilot_estimator_improves_with_orthogonal_pilots():
    rng=np.random.default_rng(2)
    beta=np.ones((3,5))
    H=sample_cell_free_channel(beta,rng)
    orth=np.arange(3)
    reuse=np.zeros(3,int)
    E1=lmmse_pilot_channel_estimate(H,beta,orth,100.0,np.random.default_rng(3))
    E2=lmmse_pilot_channel_estimate(H,beta,reuse,100.0,np.random.default_rng(3))
    assert normalized_channel_mse(H,E1) < normalized_channel_mse(H,E2)


def test_cellfree_ris_zero_amplitude_equals_direct():
    rng=np.random.default_rng(4)
    D=(rng.normal(size=(2,3))+1j*rng.normal(size=(2,3)))/np.sqrt(2)
    G=(rng.normal(size=(5,3))+1j*rng.normal(size=(5,3)))/np.sqrt(2)
    R=(rng.normal(size=(2,5))+1j*rng.normal(size=(2,5)))/np.sqrt(2)
    th=rng.uniform(-np.pi,np.pi,5)
    out=effective_cellfree_ris_channel(D,G,R,th,amplitude=0)
    assert np.allclose(out,D)


def test_cellfree_ris_coordinate_history_monotone():
    rng=np.random.default_rng(5)
    D=.2*(rng.normal(size=(2,4))+1j*rng.normal(size=(2,4)))/np.sqrt(2)
    G=.25*(rng.normal(size=(8,4))+1j*rng.normal(size=(8,4)))/np.sqrt(2)
    R=.25*(rng.normal(size=(2,8))+1j*rng.normal(size=(2,8)))/np.sqrt(2)
    th,h=coordinate_optimize_cellfree_ris(D,G,R,10.0,bits=2,iterations=2,objective='sum_rate')
    assert len(th)==8 and np.all(np.diff(h)>=-1e-12)
    assert np.isfinite(cellfree_ris_rates(D,G,R,th,10.0)).all()


def test_cross_layer_harq_improves_reliability_on_same_trace():
    rng=np.random.default_rng(6)
    S,U=500,2
    true=rng.normal(2.0,2.0,(S,U))
    est=true+rng.normal(1.5,1.0,(S,U))
    arr=(rng.random((S,U))<0.15).astype(int)
    kwargs=dict(true_snr_db=true,estimated_snr_db=est,arrivals=arr,
                thresholds_db=[-3,1,5,9],efficiencies=[.5,1,2,3],
                policy='delay_pf',seed=7)
    a=simulate_cross_layer_link(**kwargs,use_olla=False,use_harq=False,max_attempts=1)
    b=simulate_cross_layer_link(**kwargs,use_olla=True,use_harq=True,max_attempts=4)
    assert b['dropped_packets'] <= a['dropped_packets']
    assert np.isfinite(b['goodput_bits_per_slot'])


def test_joint_isac_endpoints_match_expected_beams():
    rng=np.random.default_rng(8)
    h=(rng.normal(size=8)+1j*rng.normal(size=8))/np.sqrt(2)
    ws=joint_isac_beamformer(h,25,0.0)
    wc=joint_isac_beamformer(h,25,1.0)
    a=ula_steering(8,25)
    assert abs(np.vdot(a,ws)) > .999
    mrt=h.conj()/np.linalg.norm(h)
    assert abs(np.vdot(mrt,wc)) > .999
    assert sensing_gain(ws,25) > sensing_gain(wc,25)
    assert communication_rate(h,wc,10) >= communication_rate(h,ws,10)

from commlab.mimo.ap_activation import strongest_ap_activation, coverage_aware_ap_activation, network_energy_efficiency

def test_coverage_aware_activation_helps_weak_geographic_user():
    beta=np.array([[10,9,.1,.1],[.1,.1,9,10]],float)
    s=strongest_ap_activation(beta,2)
    c=coverage_aware_ap_activation(beta,2)
    cov_s=(beta[:,s].sum(axis=1)).min()
    cov_c=(beta[:,c].sum(axis=1)).min()
    assert cov_c>=cov_s
    assert network_energy_efficiency(10,2)>0
