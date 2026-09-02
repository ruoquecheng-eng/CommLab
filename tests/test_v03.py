import numpy as np

from commlab.modulation.qam import QAMModem
from commlab.metrics.evm import evm_rms
from commlab.synchronization.preamble import repeated_half_preamble
from commlab.impairments.synchronization import apply_cfo, prepend_timing_offset
from commlab.synchronization.sync import (
    detect_frame_start,
    estimate_cfo_from_repeated_halves,
    correct_cfo,
    schmidl_cox_metric,
)
from commlab.papr.metrics import papr_db, clip_magnitude


def test_64qam_round_trip():
    rng = np.random.default_rng(10)
    modem = QAMModem(64)
    bits = rng.integers(0, 2, 6000, dtype=np.uint8)
    symbols = modem.modulate(bits)
    assert np.array_equal(bits, modem.demodulate(symbols))
    assert abs(np.mean(np.abs(symbols) ** 2) - 1.0) < 0.05


def test_evm_zero_on_exact_match():
    x = np.array([1 + 1j, -1 - 1j], dtype=np.complex128)
    assert evm_rms(x, x) == 0.0


def test_timing_detection_noiseless():
    rng = np.random.default_rng(11)
    preamble = repeated_half_preamble(64, seed=3)
    payload = rng.normal(size=400) + 1j * rng.normal(size=400)
    frame = np.concatenate((preamble, payload))
    rx = prepend_timing_offset(frame, 37)
    start, metric = detect_frame_start(rx, preamble)
    assert start == 37
    assert metric > 0.999


def test_cfo_estimation_and_correction_noiseless():
    preamble = repeated_half_preamble(64, seed=4)
    epsilon = 0.23
    rx = apply_cfo(preamble, epsilon, n_fft=64)
    est = estimate_cfo_from_repeated_halves(rx, 64)
    assert abs(est - epsilon) < 1e-12
    corrected = correct_cfo(rx, est, 64)
    # CFO correction can leave no residual phase because start_index matches injection.
    assert np.max(np.abs(corrected - preamble)) < 1e-10


def test_schmidl_cox_metric_peaks_on_preamble_region():
    preamble = repeated_half_preamble(64, seed=5)
    rx = prepend_timing_offset(preamble, 25)
    metric = schmidl_cox_metric(rx, 64)
    peak = int(np.argmax(metric))
    assert peak == 25
    assert metric[peak] > 0.999


def test_clipping_reduces_or_preserves_papr():
    rng = np.random.default_rng(12)
    x = rng.normal(size=1024) + 1j * rng.normal(size=1024)
    y = clip_magnitude(x, 1.2)
    assert papr_db(y) <= papr_db(x) + 1e-12


def test_ofdm_supports_zero_cp():
    from commlab.config import OFDMConfig
    from commlab.ofdm import OFDMTransceiver
    rng = np.random.default_rng(13)
    cfg = OFDMConfig(cp_len=0)
    modem = QAMModem(4)
    n_bits = cfg.n_data * modem.bits_per_symbol * 5
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    ofdm = OFDMTransceiver(cfg)
    wave = ofdm.modulate(tx_symbols)
    assert len(wave) == 5 * cfg.n_fft
    rx_symbols, _ = ofdm.demodulate(wave)
    assert np.array_equal(bits, modem.demodulate(rx_symbols))


def test_pilot_common_phase_tracking():
    from commlab.config import OFDMConfig
    from commlab.synchronization import estimate_common_phase_from_pilots, correct_common_phase
    cfg = OFDMConfig()
    phase = np.array([0.2, -0.5, 1.0])
    expected = np.asarray(cfg.pilot_values)[None, :]
    pilots = expected * np.exp(1j * phase[:, None])
    est = estimate_common_phase_from_pilots(pilots, cfg)
    assert np.max(np.abs(np.angle(np.exp(1j * (est - phase))))) < 1e-12
    data = np.ones((3, cfg.n_data), dtype=np.complex128) * np.exp(1j * phase[:, None])
    corrected = correct_common_phase(data.reshape(-1), est, cfg.n_data)
    assert np.max(np.abs(corrected - 1.0)) < 1e-12


def test_mimo_detectors_noiseless_and_mmse_limit():
    from commlab.mimo import zf_detect, mmse_detect, apply_mimo_channel
    H = np.array([
        [[1.0 + 0.2j, 0.3 - 0.1j], [0.2 + 0.4j, 1.1 - 0.2j]],
        [[0.8 - 0.1j, -0.2 + 0.3j], [0.1 + 0.2j, 1.2 + 0.1j]],
    ], dtype=np.complex128)
    x = np.array([[1+1j, -1+1j], [-1-1j, 1-1j]], dtype=np.complex128) / np.sqrt(2)
    y = apply_mimo_channel(x, H)
    z = zf_detect(y, H)
    m = mmse_detect(y, H, noise_var=1e-14)
    assert np.max(np.abs(z - x)) < 1e-10
    assert np.max(np.abs(m - z)) < 1e-10
