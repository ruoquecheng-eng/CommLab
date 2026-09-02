import numpy as np


def test_iq_imbalance_ls_inverse_noiseless():
    from commlab.impairments import apply_iq_imbalance, estimate_iq_coefficients, compensate_iq_imbalance
    rng = np.random.default_rng(61)
    x = rng.normal(size=4000) + 1j*rng.normal(size=4000)
    y = apply_iq_imbalance(x, 2.5, 7.0)
    a,b = estimate_iq_coefficients(x[:1000], y[:1000])
    xh = compensate_iq_imbalance(y, a, b)
    assert np.linalg.norm(xh-x)/np.linalg.norm(x) < 1e-12


def test_iq_identity():
    from commlab.impairments import apply_iq_imbalance
    rng = np.random.default_rng(62)
    x = rng.normal(size=100) + 1j*rng.normal(size=100)
    assert np.max(np.abs(apply_iq_imbalance(x)-x)) < 1e-14


def test_sampling_clock_zero_identity():
    from commlab.impairments import apply_sampling_clock_offset
    rng = np.random.default_rng(63)
    x = rng.normal(size=1000)+1j*rng.normal(size=1000)
    assert np.array_equal(x, apply_sampling_clock_offset(x, 0.0))


def test_sampling_clock_known_compensation_on_bandlimited_tone():
    from commlab.impairments import apply_sampling_clock_offset, compensate_sampling_clock_offset
    n=np.arange(12000); x=np.exp(1j*2*np.pi*0.015*n)
    y=apply_sampling_clock_offset(x, 500.0)
    z=compensate_sampling_clock_offset(y, 500.0)
    # interpolation/boundary loss: compare the well-supported interior
    sl=slice(200,11500)
    evm=np.linalg.norm(z[sl]-x[sl])/np.linalg.norm(x[sl])
    assert evm < 3e-3


def test_tone_interference_power_matches_sir():
    from commlab.impairments import add_complex_tone_interference
    x=np.ones(100000,dtype=complex)
    y=add_complex_tone_interference(x,0.123,10.0)
    i=y-x
    sir=10*np.log10(np.mean(abs(x)**2)/np.mean(abs(i)**2))
    assert abs(sir-10.0)<1e-3


def test_otfs_no_channel_roundtrip():
    from commlab.otfs import otfs_modulate, otfs_demodulate
    rng=np.random.default_rng(64)
    X=rng.normal(size=(6,16))+1j*rng.normal(size=(6,16))
    y=otfs_modulate(X,cp_len=4)
    Z=otfs_demodulate(y,6,16,cp_len=4)
    assert np.max(np.abs(Z-X))<1e-12


def test_ofdm_grid_no_channel_roundtrip():
    from commlab.otfs import ofdm_grid_modulate, ofdm_grid_demodulate
    rng=np.random.default_rng(65)
    X=rng.normal(size=(7,16))+1j*rng.normal(size=(7,16))
    y=ofdm_grid_modulate(X,cp_len=4)
    Z=ofdm_grid_demodulate(y,7,16,cp_len=4)
    assert np.max(np.abs(Z-X))<1e-12


def test_affine_pilot_phase_tracking_recovers_known_ramp():
    from commlab.config import OFDMConfig
    from commlab.synchronization import estimate_affine_phase_from_pilots, correct_affine_phase
    cfg=OFDMConfig(); rng=np.random.default_rng(66)
    n=10; data=rng.normal(size=(n,cfg.n_data))+1j*rng.normal(size=(n,cfg.n_data))
    a=np.linspace(-.3,.4,n); b=np.linspace(.01,.03,n)
    kd=np.asarray(cfg.data_subcarriers)[None,:]; kp=np.asarray(cfg.pilot_subcarriers)[None,:]
    pilots=np.asarray(cfg.pilot_values)[None,:]*np.exp(1j*(a[:,None]+b[:,None]*kp))
    impaired=data*np.exp(1j*(a[:,None]+b[:,None]*kd))
    ah,bh=estimate_affine_phase_from_pilots(pilots,cfg)
    got=correct_affine_phase(impaired.reshape(-1),ah,bh,cfg).reshape(n,cfg.n_data)
    assert np.max(np.abs(got-data))<1e-12


def test_sparse_ldpc_codeword_and_noiseless_decode():
    from commlab.coding import SparseAccumulatorLDPC
    rng=np.random.default_rng(67); code=SparseAccumulatorLDPC(k=48,seed=3)
    u=rng.integers(0,2,code.k,dtype=np.uint8); c=code.encode(u)
    assert not np.any(code.syndrome(c))
    llr=np.where(c==0,20.0,-20.0)
    got,it,ok=code.decode_min_sum(llr,max_iter=20)
    assert ok and np.array_equal(got,u)


def test_polynomial_dpd_identity_fit():
    from commlab.rf import fit_indirect_polynomial_dpd, apply_polynomial_dpd
    rng=np.random.default_rng(68); x=(rng.normal(size=5000)+1j*rng.normal(size=5000))/np.sqrt(2)
    c=fit_indirect_polynomial_dpd(x,x,order=5)
    y=apply_polynomial_dpd(x,c)
    assert np.linalg.norm(y-x)/np.linalg.norm(x)<1e-8
