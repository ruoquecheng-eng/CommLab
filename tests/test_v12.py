import numpy as np

from commlab.ris import optimal_ris_phases, quantize_phases, ris_effective_channel
from commlab.mimo import (
    semi_orthogonal_user_selection, strongest_norm_user_selection,
    hybrid_omp_precoder, precoded_mimo_rate, sparse_geometric_mimo_channel,
    full_digital_svd_rate,
)
from commlab.sensing import estimate_source_count_mdl, ula_steering_vector, NearestNeighborMultiTargetTracker


def test_ris_optimal_phase_coheres_cascaded_terms():
    rng=np.random.default_rng(1); n=32
    a=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2)
    b=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2)
    th=optimal_ris_phases(a,b)
    h=ris_effective_channel(a,b,th)
    assert np.isclose(abs(h),np.sum(np.abs(a*b)),rtol=1e-11,atol=1e-11)
    q=quantize_phases(th,3)
    assert abs(ris_effective_channel(a,b,q)) <= abs(h)+1e-10


def test_sus_selects_less_correlated_users_than_strongest_norm_on_constructed_case():
    H=np.array([
        [3,0,0,0],
        [2.9,.05,0,0],
        [0,2.5,0,0],
        [0,0,2.4,0],
        [0,0,0,2.3],
    ],dtype=complex)
    sus=semi_orthogonal_user_selection(H,4,alpha=.3)
    strong=strongest_norm_user_selection(H,4)
    def maxcorr(idx):
        A=H[idx]/np.linalg.norm(H[idx],axis=1,keepdims=True); C=np.abs(A@A.conj().T); return np.max(C-np.eye(len(idx)))
    assert maxcorr(sus)<maxcorr(strong)


def test_mdl_recovers_two_sources_at_high_snr():
    rng=np.random.default_rng(2); m=10; n=600
    A=np.column_stack([ula_steering_vector(-18,m),ula_steering_vector(24,m)])
    S=(rng.normal(size=(2,n))+1j*rng.normal(size=(2,n)))/np.sqrt(2)
    X=A@S+0.08*(rng.normal(size=(m,n))+1j*rng.normal(size=(m,n)))/np.sqrt(2)
    k,_=estimate_source_count_mdl(X,max_sources=5)
    assert k==2


def test_multitarget_tracker_survives_missed_detection():
    tr=NearestNeighborMultiTargetTracker(dt=1.0,max_misses=2,range_std=1.0,velocity_std=.5,accel_std=.5)
    out=tr.step([(10,2),(50,-1)])
    ids=sorted(x[0] for x in out); assert len(ids)==2
    tr.step([(12.2,2.1)])  # second target missed once
    out=tr.step([(14.0,2.0),(48.0,-1.0)])
    assert len(out)==2
    states={x[0]:(x[1],x[2]) for x in out}
    assert all(i in states for i in ids)
    assert abs(states[ids[0]][0]-14)<3 or abs(states[ids[1]][0]-14)<3


def test_hybrid_omp_rate_is_positive_and_bounded_by_full_digital():
    H,_,_=sparse_geometric_mimo_channel(8,32,4,np.random.default_rng(4))
    F=hybrid_omp_precoder(H,2,4)
    r=precoded_mimo_rate(H,F,10,2); full=full_digital_svd_rate(H,10,2)
    assert r>0 and r<=full+1e-9
