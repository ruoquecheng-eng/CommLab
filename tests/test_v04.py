import numpy as np

from commlab.coding import ConvolutionalCode
from commlab.rf import rapp_amplifier, scale_for_input_backoff
from commlab.channels import apply_doppler_multipath, apply_multipath
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.mimo import (
    generate_mimo_multipath_taps,
    apply_mimo_multipath_waveforms,
    detect_mimo_ofdm_data,
)


def test_convolutional_code_noiseless_roundtrip():
    rng = np.random.default_rng(21)
    code = ConvolutionalCode()
    bits = rng.integers(0, 2, 1000, dtype=np.uint8)
    encoded = code.encode(bits, terminate=True)
    decoded = code.decode_hard(encoded, terminated=True, trim_tail=True)
    assert np.array_equal(bits, decoded)


def test_convolutional_viterbi_corrects_sparse_errors():
    rng = np.random.default_rng(22)
    code = ConvolutionalCode()
    bits = rng.integers(0, 2, 300, dtype=np.uint8)
    encoded = code.encode(bits)
    corrupted = encoded.copy()
    # Isolated errors, spaced widely enough for this short-memory code to recover.
    corrupted[[40, 140, 260, 420]] ^= 1
    decoded = code.decode_hard(corrupted)
    assert np.array_equal(bits, decoded)


def test_rapp_is_linear_at_large_backoff():
    rng = np.random.default_rng(23)
    x = rng.normal(size=1000) + 1j * rng.normal(size=1000)
    scaled = scale_for_input_backoff(x, 30.0)
    y = rapp_amplifier(scaled, smoothness=3.0)
    rel = np.linalg.norm(y - scaled) / np.linalg.norm(scaled)
    assert rel < 1e-5


def test_doppler_zero_matches_sparse_multipath():
    rng = np.random.default_rng(24)
    x = rng.normal(size=500) + 1j * rng.normal(size=500)
    delays = np.array([0, 3, 7])
    coeff = np.array([1.0, 0.4 + 0.2j, -0.1j])
    taps = np.zeros(delays.max() + 1, dtype=np.complex128)
    taps[delays] = coeff
    y0 = apply_multipath(x, taps)
    y1 = apply_doppler_multipath(x, coeff, delays, np.zeros(3), n_fft=64)
    assert np.max(np.abs(y0 - y1)) < 1e-12


def test_mimo_ofdm_noiseless_perfect_csi_roundtrip():
    rng = np.random.default_rng(25)
    cfg = OFDMConfig(cp_len=16)
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    n_symbols = 8
    bits_by_tx = []
    waves = []
    for _ in range(2):
        bits = rng.integers(0, 2, n_symbols * cfg.n_data * 2, dtype=np.uint8)
        bits_by_tx.append(bits)
        waves.append(ofdm.modulate(modem.modulate(bits)))
    tx = np.stack(waves)
    taps = generate_mimo_multipath_taps(2, 2, rng=rng)
    rx = apply_mimo_multipath_waveforms(tx, taps)
    detected = detect_mimo_ofdm_data(rx, taps, cfg, method="zf")
    for t in range(2):
        got = modem.demodulate(detected[..., t].reshape(-1))
        assert np.array_equal(bits_by_tx[t], got)


def test_slm_is_recoverable_with_side_information():
    from commlab.papr import slm_modulate_data_blocks, recover_slm_data
    rng = np.random.default_rng(26)
    cfg = OFDMConfig()
    modem = QAMModem(16)
    bits = rng.integers(0, 2, 10 * cfg.n_data * 4, dtype=np.uint8)
    data = modem.modulate(bits).reshape(-1, cfg.n_data)
    wave, phase, _ = slm_modulate_data_blocks(data, cfg, n_candidates=4, rng=rng)
    freq = np.fft.fft(wave, axis=1) / np.sqrt(cfg.n_fft)
    observed = freq[:, cfg.data_bins]
    recovered = recover_slm_data(observed, phase)
    assert np.max(np.abs(recovered - data)) < 1e-10


def test_time_domain_ls_channel_estimator_exact_noiseless():
    from commlab.estimation import estimate_channel_time_domain_ls
    from commlab.channels import apply_multipath, channel_frequency_response
    pilots = (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24)
    cfg = OFDMConfig(pilot_subcarriers=pilots, pilot_values=tuple(1+0j for _ in pilots))
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(27)
    bits = rng.integers(0, 2, 12 * cfg.n_data * 2, dtype=np.uint8)
    taps = np.zeros(9, dtype=np.complex128)
    taps[[0,3,8]] = [0.8, 0.3+0.2j, -0.15j]
    tx = ofdm.modulate(modem.modulate(bits))
    rx = apply_multipath(tx, taps)
    _, received_pilots = ofdm.demodulate(rx)
    hhat = estimate_channel_time_domain_ls(received_pilots, 9, cfg)
    true_h = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    assert np.max(np.abs(hhat - true_h[None,:])) < 1e-10


def test_waterfilling_conserves_power_and_beats_equal_allocation():
    from commlab.resource_allocation import waterfill_power_allocation, parallel_channel_capacity_bits
    gains = np.array([0.05, 0.2, 1.0, 3.0, 0.4])
    total = 5.0
    noise = 1.0
    p = waterfill_power_allocation(gains, total, noise)
    peq = np.full(len(gains), total/len(gains))
    assert abs(np.sum(p) - total) < 1e-9
    assert np.all(p >= 0)
    assert parallel_channel_capacity_bits(gains, p, noise) >= parallel_channel_capacity_bits(gains, peq, noise) - 1e-10
