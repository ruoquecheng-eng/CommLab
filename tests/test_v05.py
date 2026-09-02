import numpy as np

from commlab.coding import ConvolutionalCode
from commlab.modulation import QAMModem


def test_qam_llr_sign_matches_hard_decisions():
    rng = np.random.default_rng(51)
    for order in (4, 16, 64):
        modem = QAMModem(order)
        n = 6000 - (6000 % modem.bits_per_symbol)
        bits = rng.integers(0, 2, n, dtype=np.uint8)
        syms = modem.modulate(bits)
        llr = modem.llr_maxlog(syms, 1e-4)
        hard_from_llr = (llr < 0).astype(np.uint8)
        assert np.array_equal(bits, hard_from_llr)


def test_soft_viterbi_noiseless_roundtrip():
    rng = np.random.default_rng(52)
    code = ConvolutionalCode()
    bits = rng.integers(0, 2, 1000, dtype=np.uint8)
    coded = code.encode(bits)
    llr = np.where(coded == 0, 20.0, -20.0)
    got = code.decode_soft(llr)
    assert np.array_equal(bits, got)


def test_phase_noise_zero_is_identity():
    from commlab.impairments import apply_phase_noise
    rng = np.random.default_rng(53)
    x = rng.normal(size=1000) + 1j * rng.normal(size=1000)
    assert np.array_equal(x, apply_phase_noise(x, 0.0, rng))


def test_rapp_inverse_cascade_is_nearly_linear_below_saturation():
    from commlab.rf import rapp_amplifier, rapp_inverse_predistort
    rng = np.random.default_rng(54)
    x = 0.65 * (rng.normal(size=2000) + 1j*rng.normal(size=2000)) / np.sqrt(2)
    # keep target well inside the inverse's valid output region
    x = np.where(np.abs(x) > 0.8, 0.8 * x / np.maximum(np.abs(x), 1e-15), x)
    drive = rapp_inverse_predistort(x, smoothness=2.5)
    y = rapp_amplifier(drive, smoothness=2.5)
    assert np.linalg.norm(y-x) / np.linalg.norm(x) < 1e-10


def test_mimo_training_estimator_is_exact_noiseless():
    from commlab.config import OFDMConfig
    from commlab.mimo import (
        orthogonal_mimo_training_waveforms, generate_mimo_multipath_taps,
        apply_mimo_multipath_waveforms, estimate_mimo_channel_from_training,
        mimo_frequency_response,
    )
    cfg = OFDMConfig(cp_len=16)
    rng = np.random.default_rng(55)
    tx = orthogonal_mimo_training_waveforms(cfg, 2)
    taps = generate_mimo_multipath_taps(2, 2, rng=rng)
    rx = apply_mimo_multipath_waveforms(tx, taps)
    est = estimate_mimo_channel_from_training(rx, cfg, 2)
    active_bins = np.array([cfg.bin_index(k) for k in cfg.active_subcarriers])
    truth = mimo_frequency_response(taps, cfg.n_fft)[active_bins]
    assert np.max(np.abs(est-truth)) < 1e-10


def test_alamouti_noiseless_roundtrip():
    from commlab.mimo import alamouti_encode, alamouti_decode
    rng=np.random.default_rng(56); modem=QAMModem(4)
    bits=rng.integers(0,2,4000,dtype=np.uint8); s=modem.modulate(bits)
    x=alamouti_encode(s); h=(rng.normal(size=(len(x),2))+1j*rng.normal(size=(len(x),2)))/np.sqrt(2)
    y=np.sum(x*h[:,None,:],axis=2)
    got=alamouti_decode(y,h)
    assert np.max(np.abs(got-s)) < 1e-10
