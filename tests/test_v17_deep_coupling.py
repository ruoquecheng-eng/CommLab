import numpy as np

from commlab.mimo.async_csi import csi_prediction_mse_score, select_csi_refresh_aps, simulate_async_cellfree_csi
from commlab.mimo.cell_free import user_centric_mask
from commlab.scheduling.ir_harq_fbl import block_fading_ir_error_probability, simulate_fbl_ir_harq_queue
from commlab.ris.two_timescale import apply_ris_phase_noise, simulate_two_timescale_cellfree_ris
from commlab.sensing.queue_control import simulate_queue_aware_isac_control


def test_csi_prediction_score_increases_with_age():
    beta=np.ones((2,3)); rho=np.full(3,.95)
    a=csi_prediction_mse_score(beta,np.array([0,1,5]),rho)
    assert a[0] == 0 and a[2] > a[1] > a[0]


def test_uncertainty_refresh_selects_old_high_power_ap():
    beta=np.array([[10.,1.,1.],[5.,1.,1.]])
    idx=select_csi_refresh_aps(beta,np.array([5,5,5]),np.full(3,.95),1,'uncertainty')
    assert int(idx[0])==0


def test_async_csi_fixed_budget_and_finite_metrics():
    rng=np.random.default_rng(1); beta=np.exp(rng.normal(size=(4,8))); mask=user_centric_mask(beta,4)
    out=simulate_async_cellfree_csi(beta,mask,np.linspace(.94,.995,8),5.0,updates_per_slot=2,n_slots=40,seed=2)
    assert np.isfinite(out['edge_rate']) and out['mean_csi_nmse']>=0
    assert all(len(x)==2 for x in out['update_history'][1:])


def test_ir_error_probability_improves_with_more_redundancy():
    p1=block_fading_ir_error_probability([2.0],[80],80.0)
    p2=block_fading_ir_error_probability([2.0,2.0],[80,80],80.0)
    assert p2 < p1


def test_ir_harq_queue_returns_valid_goodput():
    rng=np.random.default_rng(3); S,U=150,2
    true=rng.normal(1.5,1.0,(S,U)); est=true+1.0; arr=(rng.random((S,U))<.18).astype(int)
    out=simulate_fbl_ir_harq_queue(true,est,arr,[-4,0,4,8],[.5,1,2,3],round_blocklength=60,mode='ir',seed=4)
    assert out['goodput_bits_per_channel_use']>=0 and out['nack_rate']<=1


def test_zero_phase_noise_is_exact():
    th=np.linspace(-1,1,8); got=apply_ris_phase_noise(th,0,np.random.default_rng(5))
    assert np.allclose(np.exp(1j*got),np.exp(1j*th))


def test_two_timescale_ris_reports_lower_control_overhead():
    rng=np.random.default_rng(6); seq=[]
    K,M,N=2,3,4
    for _ in range(6):
        D=.2*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
        G=.2*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
        R=.2*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
        seq.append((D,G,R))
    out=simulate_two_timescale_cellfree_ris(seq,8,bits=1,ris_update_interval=3,history_window=3,seed=7)
    assert out['ris_control_bits_per_slot_two_timescale'] < out['ris_control_bits_per_slot_fast']
    assert np.isfinite(out['two_timescale']['mean_sum_rate'])


def test_queue_aware_isac_is_finite_and_resource_bounded():
    S,U=50,2; proc=np.r_[np.full(25,.1),np.full(25,.8)]
    arrivals=np.zeros((S,U)); arrivals[:,0]=60; arrivals[:,1]=40
    rates=np.full((S,U),120.)
    out=simulate_queue_aware_isac_control(proc,arrivals,rates,.5,[8,16,32],[0,.02,.05,.1],.12)
    assert out['final_backlog_bits']>=0 and 0<=out['mean_sensing_fraction']<1
    assert np.isfinite(out['mean_posterior_std_deg'])


def test_predictive_csi_matches_absolute_at_zero_correlation_order_of_magnitude():
    from commlab.mimo.predictive_csi import predictive_csi_quantization_trace
    b=np.ones((3,5)); o=predictive_csi_quantization_trace(b,0.0,4,n_slots=60,seed=9)
    ratio=o['mean_predictive_nmse']/max(o['mean_absolute_nmse'],1e-15)
    assert .2 < ratio < 5.0


def test_predictive_csi_improves_high_correlation_distortion():
    from commlab.mimo.predictive_csi import predictive_csi_quantization_trace
    b=np.ones((4,8)); o=predictive_csi_quantization_trace(b,.995,3,n_slots=100,seed=10)
    assert o['mean_predictive_nmse'] < o['mean_absolute_nmse']
