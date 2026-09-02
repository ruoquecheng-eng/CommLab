import numpy as np


def test_memory_polynomial_identity_fit():
    from commlab.rf import fit_memory_polynomial, apply_memory_polynomial
    rng=np.random.default_rng(71)
    x=(rng.normal(size=6000)+1j*rng.normal(size=6000))/np.sqrt(2)
    c=fit_memory_polynomial(x,x,order=5,memory_depth=3,ridge=1e-10)
    y=apply_memory_polynomial(x,c)
    sl=slice(10,None)
    assert np.linalg.norm(y[sl]-x[sl])/np.linalg.norm(x[sl]) < 1e-7


def test_memory_polynomial_known_model_identification():
    from commlab.rf import apply_memory_polynomial, fit_memory_polynomial
    rng=np.random.default_rng(72)
    x=0.4*(rng.normal(size=10000)+1j*rng.normal(size=10000))/np.sqrt(2)
    c=np.array([[1+0j,-.12+.02j,.01+0j],[.08+.03j,-.02+0j,0j]],complex)
    y=apply_memory_polynomial(x,c)
    ch=fit_memory_polynomial(x,y,order=5,memory_depth=2,ridge=1e-10)
    assert np.linalg.norm(ch-c)/np.linalg.norm(c) < 1e-6


def test_ici_matrix_static_is_diagonal():
    from commlab.equalization import time_varying_ofdm_channel_matrix, ici_energy_fraction
    H=time_varying_ofdm_channel_matrix(np.array([1,.3]),np.array([0,3]),np.array([0.,0.]),n_fft=32,cp_len=8)
    assert ici_energy_fraction(H) < 1e-24


def test_ici_full_lmmse_recovers_noiseless_time_varying_symbol():
    from commlab.equalization import time_varying_ofdm_channel_matrix, linear_lmmse_ici_detect
    rng=np.random.default_rng(73); n=24
    H=time_varying_ofdm_channel_matrix(np.array([1,.55*np.exp(.4j)]),np.array([0,2]),np.array([0.,1.2]),n_fft=n,cp_len=6)
    x=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2)
    y=H@x
    xh=linear_lmmse_ici_detect(y,H,noise_var=1e-12)
    assert np.linalg.norm(xh-x)/np.linalg.norm(x) < 2e-5


def test_mimo_lmmse_shrink_reduces_mse_for_noisy_zero_mean_prior():
    from commlab.mimo import lmmse_shrink_mimo_channel
    rng=np.random.default_rng(74)
    h=(rng.normal(size=(200000,))+1j*rng.normal(size=(200000,)))/np.sqrt(2)
    nv=1.0
    n=np.sqrt(nv/2)*(rng.normal(size=len(h))+1j*rng.normal(size=len(h)))
    ls=h+n
    mm=lmmse_shrink_mimo_channel(ls,nv,pilot_power=1.0,channel_variance=1.0)
    assert np.mean(abs(mm-h)**2) < np.mean(abs(ls-h)**2)


def test_otfs_cg_matches_direct_lmmse():
    from commlab.otfs import cg_lmmse_detect, linear_mmse_detect
    rng=np.random.default_rng(75)
    A=(rng.normal(size=(30,30))+1j*rng.normal(size=(30,30)))/np.sqrt(60)
    x=(rng.normal(size=30)+1j*rng.normal(size=30))/np.sqrt(2)
    y=A@x
    nv=.05
    direct=linear_mmse_detect(y,A,nv)
    cg,it,rel=cg_lmmse_detect(y,A,nv,max_iter=100,tol=1e-10)
    assert it > 0 and rel < 1e-9
    assert np.linalg.norm(cg-direct)/np.linalg.norm(direct) < 1e-7


def test_wilson_interval_contains_empirical_rate():
    from commlab.metrics.confidence import wilson_interval
    lo,hi=wilson_interval(50,1000)
    assert lo < .05 < hi and 0 <= lo < hi <= 1


def test_zero_error_wilson_has_nonzero_upper_bound():
    from commlab.metrics.confidence import wilson_interval
    lo,hi=wilson_interval(0,10000)
    assert lo == 0.0 and 0 < hi < 0.001


def test_small_mimo_ml_noiseless_qpsk():
    from commlab.mimo import ml_detect_small
    from commlab.modulation import QAMModem
    rng=np.random.default_rng(76); modem=QAMModem(4)
    labels=np.arange(4,dtype=np.uint8)[:,None]
    bits=((labels >> np.array([1,0])) & 1).astype(np.uint8)
    const=modem.modulate(bits.reshape(-1))
    H=(rng.normal(size=(50,2,2))+1j*rng.normal(size=(50,2,2)))/np.sqrt(2)
    ib=rng.integers(0,4,size=(50,2)); x=const[ib]; y=np.einsum('bij,bj->bi',H,x)
    xh=ml_detect_small(y,H,const)
    assert np.max(np.abs(xh-x)) < 1e-12


def test_frequency_orthogonal_mimo_cir_training_noiseless():
    from commlab.config import OFDMConfig
    from commlab.mimo import frequency_orthogonal_mimo_training_waveforms, estimate_mimo_cir_from_frequency_orthogonal_training, apply_mimo_multipath_waveforms, generate_mimo_multipath_taps, mimo_frequency_response
    cfg=OFDMConfig(); rng=np.random.default_rng(77); taps=generate_mimo_multipath_taps(2,2,rng=rng)
    tx,sets=frequency_orthogonal_mimo_training_waveforms(cfg,2); rx=apply_mimo_multipath_waveforms(tx,taps)
    Hh=estimate_mimo_cir_from_frequency_orthogonal_training(rx,sets,cir_len=taps.shape[-1],config=cfg)
    bins=np.array([cfg.bin_index(k) for k in cfg.active_subcarriers]); H=mimo_frequency_response(taps,cfg.n_fft)[bins]
    assert np.linalg.norm(Hh-H)/np.linalg.norm(H) < 1e-10


def test_frequency_selective_iq_filter_estimation_and_ofdm_inverse():
    from commlab.impairments import apply_frequency_selective_iq_imbalance, estimate_frequency_selective_iq_filters, compensate_frequency_selective_iq_ofdm
    from commlab.config import OFDMConfig
    from commlab.ofdm import OFDMTransceiver
    from commlab.modulation import QAMModem
    rng=np.random.default_rng(78); hd=np.array([1,.05+.02j,-.015j]); hi=np.array([.08+.03j,.025-.01j,.01j])
    train=(rng.normal(size=12000)+1j*rng.normal(size=12000))/np.sqrt(2); yr=apply_frequency_selective_iq_imbalance(train,hd,hi); hdh,hih=estimate_frequency_selective_iq_filters(train,yr,3)
    assert np.linalg.norm(hdh-hd)+np.linalg.norm(hih-hi) < 1e-8
    cfg=OFDMConfig(); m=QAMModem(16); o=OFDMTransceiver(cfg); bits=rng.integers(0,2,80*cfg.n_data*4,dtype=np.uint8); ref=m.modulate(bits); tx=o.modulate(ref); rx=apply_frequency_selective_iq_imbalance(tx,hd,hi); cor=compensate_frequency_selective_iq_ofdm(rx,hdh,hih,cfg.n_fft,cfg.cp_len); z,_=o.demodulate(cor)
    assert np.linalg.norm(z-ref)/np.linalg.norm(ref) < 1e-10
