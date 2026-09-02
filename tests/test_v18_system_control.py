import numpy as np

from commlab.mimo.cell_free import user_centric_mask
from commlab.mimo.joint_csi_control import schedule_joint_csi_actions, simulate_joint_predictive_csi_control
from commlab.scheduling.deadline_harq import simulate_deadline_fbl_harq
from commlab.scheduling.aoi import simulate_status_update_aoi
from commlab.ris.event_triggered import simulate_event_triggered_cellfree_ris
from commlab.sensing.budget_control import simulate_budget_constrained_sensing


def test_joint_csi_scheduler_respects_budget_and_age_priority():
    beta=np.array([[5.,1.,2.],[4.,1.,2.]])
    mask=np.ones_like(beta,dtype=bool)
    acts=schedule_joint_csi_actions(beta,mask,np.array([6,1,3]),np.full(3,.97),24,min_bits=2,max_bits=5)
    used=sum(2*mask[:,m].sum()*b for m,b in acts)
    assert used<=24
    assert acts and acts[0][0]==0


def test_joint_predictive_csi_returns_finite_network_metrics():
    rng=np.random.default_rng(1); beta=np.exp(rng.normal(size=(4,8))); mask=user_centric_mask(beta,4)
    out=simulate_joint_predictive_csi_control(beta,mask,.98,8,total_budget_bits=96,n_slots=50,seed=2)
    assert np.isfinite(out['edge_rate']) and out['mean_csi_nmse']>=0
    assert out['mean_fronthaul_bits_per_slot']<=96+1e-9


def test_deadline_harq_counts_expired_packets():
    S,U=40,2
    true=np.full((S,U),-4.0); est=true.copy(); arr=np.ones((S,U),int)
    out=simulate_deadline_fbl_harq(true,est,arr,[-6,-2,2],[.5,1,2],deadline_slots=2,
                                   round_blocklength=40,policy='edf',seed=3)
    assert out['deadline_drops']>0
    assert 0<=out['deadline_miss_rate']<=1


def test_aoi_reliable_channel_stays_low():
    T=np.full((100,3),20.0)
    out=simulate_status_update_aoi(T,T,blocklength=80,rate=.5,policy='max_age',seed=4)
    assert out['mean_aoi']<5
    assert out['delivery_rate_per_slot']>.9


def test_aoi_age_reliability_is_finite_under_fading():
    rng=np.random.default_rng(5); T=rng.normal(2,4,(150,4)); E=T+rng.normal(0,1,T.shape)
    out=simulate_status_update_aoi(T,E,blocklength=80,rate=1.0,policy='age_reliability',retransmission='chase',seed=6)
    assert np.isfinite(out['mean_aoi']) and out['mean_aoi']>=1
    assert out['age_history'].shape==T.shape


def test_event_triggered_ris_respects_control_bounds():
    rng=np.random.default_rng(7); seq=[]; K,M,N=2,3,4
    base=[.2*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2),
          .2*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2),
          .2*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)]
    for t in range(8):
        seq.append(tuple(x*np.exp(1j*.03*t) for x in base))
    out=simulate_event_triggered_cellfree_ris(seq,10,bits=1,rate_drop_threshold=.05,min_interval=2,max_interval=4,seed=8)
    assert out['n_updates']>=2
    assert out['control_bits_per_slot']<=N
    assert np.isfinite(out['mean_sum_rate'])


def test_budget_constrained_sensing_tracks_budget_order():
    proc=np.r_[np.full(40,.08),np.full(40,.8),np.full(40,.08)]
    lo=simulate_budget_constrained_sensing(proc,.5,[8,16,32],[0,.02,.05,.1,.15],.12,.03,dual_step=1.5)
    hi=simulate_budget_constrained_sensing(proc,.5,[8,16,32],[0,.02,.05,.1,.15],.12,.10,dual_step=1.5)
    assert lo['mean_sensing_fraction'] < hi['mean_sensing_fraction']
    assert np.isfinite(lo['mean_payload_rate']) and np.isfinite(hi['mean_payload_rate'])

def test_round_robin_joint_csi_never_refreshes_same_ap_twice_per_slot():
    rng=np.random.default_rng(11); beta=np.exp(rng.normal(size=(3,6))); mask=np.ones_like(beta,dtype=bool)
    out=simulate_joint_predictive_csi_control(beta,mask,.98,8,total_budget_bits=1000,n_slots=8,
                                              policy='round_robin',fixed_bits=4,seed=12)
    for actions in out['action_history'][1:]:
        aps=[m for m,_ in actions]
        assert len(aps)==len(set(aps))

from commlab.random_access.grant_free import sic_decode_powers, simulate_grant_free_random_access

def test_sic_can_decode_power_separated_collision():
    # Strong user first, then weak user after perfect cancellation.
    assert sic_decode_powers(np.array([20.0,2.0]),1.0)==2


def test_grant_free_noma_is_finite_and_can_beat_collision_baseline():
    a=simulate_grant_free_random_access(80,16,400,.08,mean_snr_db=10,power_spread_db=8,mode='oma_collision',seed=20)
    b=simulate_grant_free_random_access(80,16,400,.08,mean_snr_db=10,power_spread_db=8,mode='noma_sic',seed=20)
    assert 0<=a['success_probability']<=1 and 0<=b['success_probability']<=1
    assert b['throughput_packets_per_slot']>=a['throughput_packets_per_slot']

def test_budget_constrained_sensing_never_exceeds_long_term_budget():
    proc=np.r_[np.full(20,.1),np.full(20,.8)]
    out=simulate_budget_constrained_sensing(proc,.5,[8,16],[0,.02,.05,.1],.1,.03,information_weight=4.0,dual_step=1.0)
    assert out['mean_sensing_fraction'] <= .03 + 1e-12
