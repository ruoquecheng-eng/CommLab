import numpy as np
from commlab.mimo.fronthaul import quantize_complex_csi,csi_quantization_nmse,fronthaul_csi_bits
from commlab.ris.robust import perturb_complex_channel,sample_average_optimize_cellfree_ris
from commlab.ris.cellfree import cellfree_ris_rates
from commlab.information_theory.finite_blocklength import normal_approximation_error_probability
from commlab.scheduling.short_packet import simulate_short_packet_cross_layer
from commlab.sensing.resource_scheduling import posterior_angle_std,joint_sensing_comm_resource_selection


def test_csi_quantization_improves_with_bits():
    rng=np.random.default_rng(1)
    h=(rng.normal(size=(8,12))+1j*rng.normal(size=(8,12)))/np.sqrt(2)
    q2=quantize_complex_csi(h,2); q6=quantize_complex_csi(h,6)
    assert csi_quantization_nmse(h,q6)<csi_quantization_nmse(h,q2)
    mask=np.ones_like(h,bool)
    assert fronthaul_csi_bits(mask,6)==3*fronthaul_csi_bits(mask,2)


def test_robust_ris_history_monotone():
    rng=np.random.default_rng(2); K,M,N=2,3,6
    D=.2*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
    G=.25*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
    R=.25*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    samples=[]
    for _ in range(4):
        samples.append((perturb_complex_channel(D,.05,rng),perturb_complex_channel(G,.05,rng),perturb_complex_channel(R,.05,rng)))
    th,h=sample_average_optimize_cellfree_ris(samples,10,bits=2,iterations=2)
    assert len(th)==N and np.all(np.diff(h)>=-1e-12)
    assert np.isfinite(cellfree_ris_rates(D,G,R,th,10)).all()


def test_fbl_error_probability_decreases_with_snr():
    p1=float(normal_approximation_error_probability(1.0,200,1.0))
    p2=float(normal_approximation_error_probability(10.0,200,1.0))
    assert 0<=p2<p1<=1


def test_fbl_aware_short_packet_link_is_valid():
    rng=np.random.default_rng(3); S,U=300,2
    true=rng.normal(5,2,(S,U)); est=true+1.5+rng.normal(0,.8,(S,U)); arr=(rng.random((S,U))<.12).astype(int)
    a=simulate_short_packet_cross_layer(true,est,arr,[-3,1,5,9],[.5,1,2,3],fbl_aware=False,seed=4)
    b=simulate_short_packet_cross_layer(true,est,arr,[-3,1,5,9],[.5,1,2,3],fbl_aware=True,seed=4)
    assert np.isfinite(a['goodput_bits_per_slot']) and np.isfinite(b['goodput_bits_per_slot'])
    assert 0<=b['nack_rate']<=1


def test_sensing_fraction_reduces_posterior_uncertainty():
    a=posterior_angle_std(5,.01); b=posterior_angle_std(5,.2)
    assert b<a<5


def test_joint_sensing_resource_returns_grid_optimum():
    out=joint_sensing_comm_resource_selection(4,[8,16,32],[0,.02,.05,.1,.2],.25)
    assert out['best']['elements'] in {8,16,32}
    assert 0<=out['best']['sensing_fraction']<1
    assert len(out['rows'])==15

from commlab.scheduling.short_packet import simulate_short_packet_goodput_trace

def test_short_packet_goodput_trace_has_rate_reliability_tradeoff():
    rng=np.random.default_rng(9); t=rng.normal(4,2,500); e=t+2.0
    a=simulate_short_packet_goodput_trace(t,e,[-3,1,5,9],[.5,1,2,3],120,fbl_aware=False,seed=10)
    b=simulate_short_packet_goodput_trace(t,e,[-3,1,5,9],[.5,1,2,3],120,fbl_aware=True,seed=10)
    assert b['mean_mcs_index']<=a['mean_mcs_index']
    assert 0<=a['goodput_bits_per_use']<=3 and 0<=b['goodput_bits_per_use']<=3
from commlab.mimo.fronthaul import gauss_markov_channel_step

def test_gauss_markov_channel_endpoints():
    rng=np.random.default_rng(12); h=np.ones((2,3),complex); b=np.ones((2,3))
    assert np.allclose(gauss_markov_channel_step(h,b,1.0,rng),h)
    y=gauss_markov_channel_step(h,b,0.0,np.random.default_rng(12))
    assert y.shape==h.shape and np.isfinite(y).all()
