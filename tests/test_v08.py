import numpy as np


def _qpsk_constellation():
    from commlab.modulation import QAMModem
    modem=QAMModem(4)
    labels=np.arange(4,dtype=np.uint8)[:,None]
    bits=((labels >> np.array([1,0])) & 1).astype(np.uint8)
    return modem.modulate(bits.reshape(-1))


def test_kbest_matches_ml_when_k_large_enough():
    from commlab.mimo import k_best_detect, ml_detect_small
    rng=np.random.default_rng(801); const=_qpsk_constellation()
    H=(rng.normal(size=(30,2,2))+1j*rng.normal(size=(30,2,2)))/np.sqrt(2)
    idx=rng.integers(0,4,size=(30,2)); x=const[idx]
    y=np.einsum('bij,bj->bi',H,x)+.05*(rng.normal(size=(30,2))+1j*rng.normal(size=(30,2)))
    a=ml_detect_small(y,H,const); b=k_best_detect(y,H,const,k_best=16)
    assert np.max(np.abs(a-b)) < 1e-12


def test_kbest_noiseless_recovers_qpsk():
    from commlab.mimo import k_best_detect
    rng=np.random.default_rng(802); const=_qpsk_constellation()
    H=(rng.normal(size=(100,2,2))+1j*rng.normal(size=(100,2,2)))/np.sqrt(2)
    idx=rng.integers(0,4,size=(100,2)); x=const[idx]; y=np.einsum('bij,bj->bi',H,x)
    xh=k_best_detect(y,H,const,k_best=4)
    assert np.max(np.abs(xh-x)) < 1e-12


def test_ici_cg_matches_direct_lmmse():
    from commlab.equalization import cg_lmmse_ici_detect, linear_lmmse_ici_detect
    rng=np.random.default_rng(803); n=36
    H=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))/np.sqrt(2*n)
    x=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2); y=H@x
    direct=linear_lmmse_ici_detect(y,H,.07)
    cg,it,rel=cg_lmmse_ici_detect(y,H,.07,max_iter=150,tol=1e-10)
    assert it>0 and rel<1e-9
    assert np.linalg.norm(cg-direct)/np.linalg.norm(direct) < 1e-7


def test_rls_memory_polynomial_tracks_static_model():
    from commlab.rf import apply_memory_polynomial, rls_fit_memory_polynomial
    rng=np.random.default_rng(804)
    x=.3*(rng.normal(size=8000)+1j*rng.normal(size=8000))/np.sqrt(2)
    c=np.array([[1+0j,-.10+.02j,.01+0j],[.07+.01j,-.018+.005j,0j]],complex)
    y=apply_memory_polynomial(x,c)
    ch,err=rls_fit_memory_polynomial(x,y,order=5,memory_depth=2,forgetting_factor=.999,delta=1e3)
    assert np.linalg.norm(ch-c)/np.linalg.norm(c) < 3e-3
    assert np.nanmean(err[-1000:]) < np.nanmean(err[100:1100])


def test_correlated_mimo_channel_correlation_grows():
    from commlab.mimo import correlated_rayleigh_mimo_channel
    rng=np.random.default_rng(805)
    H0=correlated_rayleigh_mimo_channel(40000,2,2,0,0,rng)
    H9=correlated_rayleigh_mimo_channel(40000,2,2,.9,.9,rng)
    c0=abs(np.corrcoef(H0[:,0,0].real,H0[:,0,1].real)[0,1])
    c9=abs(np.corrcoef(H9[:,0,0].real,H9[:,0,1].real)[0,1])
    assert c9 > c0 + .5


def test_mimo_capacity_nonnegative():
    from commlab.mimo import correlated_rayleigh_mimo_channel, mimo_capacity_bits_per_hz
    H=correlated_rayleigh_mimo_channel(100,2,2,.5,.5,np.random.default_rng(806))
    c=mimo_capacity_bits_per_hz(H,10.0)
    assert c.shape==(100,) and np.all(c>=0)


def test_polar_noiseless_sc_roundtrip():
    from commlab.coding import PolarCode
    rng=np.random.default_rng(807); code=PolarCode(128,64)
    for _ in range(5):
        b=rng.integers(0,2,code.k,dtype=np.uint8); x=code.encode(b)
        llr=(1-2*x.astype(float))*80
        assert np.array_equal(code.decode_sc(llr),b)


def test_polar_reliability_order_is_permutation():
    from commlab.coding import bec_reliability_order
    order=bec_reliability_order(128)
    assert np.array_equal(np.sort(order),np.arange(128))


def test_proportional_fair_scheduler_shapes_and_fairness_helper():
    from commlab.scheduling import proportional_fair_schedule, jain_fairness_index
    rng=np.random.default_rng(808); R=1+rng.random((20,3,12)); alloc,ach,T=proportional_fair_schedule(R,beta=.9)
    assert alloc.shape==(20,12) and ach.shape==(20,3) and T.shape==(3,)
    assert abs(jain_fairness_index(np.ones(4))-1.0)<1e-12


def test_stateful_rls_memory_model_converges():
    from commlab.rf import MemoryPolynomialRLS, apply_memory_polynomial
    rng=np.random.default_rng(809); x=.25*(rng.normal(size=5000)+1j*rng.normal(size=5000))/np.sqrt(2)
    c=np.array([[1+0j,-.08+.01j],[.05+.02j,-.01+0j]],complex); y=apply_memory_polynomial(x,c)
    rls=MemoryPolynomialRLS(order=3,memory_depth=2,forgetting_factor=.999,delta=1e3); rls.update(x,y,stride=1)
    assert np.linalg.norm(rls.coefficients-c)/np.linalg.norm(c)<5e-3


def test_mrt_beamforming_matches_channel_norm_gain():
    from commlab.mimo import mrt_beamformer, miso_effective_gain
    rng=np.random.default_rng(817); h=(rng.normal(size=(100,4))+1j*rng.normal(size=(100,4)))/np.sqrt(2)
    g=miso_effective_gain(h,mrt_beamformer(h))
    assert np.max(np.abs(g-np.sum(np.abs(h)**2,axis=1)))<1e-10


def test_generalized_memory_model_exact_identification():
    from commlab.rf import apply_generalized_memory, fit_generalized_memory, default_generalized_memory_pa_coefficients
    rng=np.random.default_rng(819); x=.25*(rng.normal(size=8000)+1j*rng.normal(size=8000))/np.sqrt(2); c=default_generalized_memory_pa_coefficients(); y=apply_generalized_memory(x,c); ch=fit_generalized_memory(x,y,ridge=1e-10)
    assert np.linalg.norm(ch-c)/np.linalg.norm(c)<1e-5
