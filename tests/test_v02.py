import numpy as np

from commlab.channels import generate_rayleigh_taps
from commlab.config import OFDMConfig
from commlab.equalization import mmse_equalize, zf_equalize
from commlab.estimation import estimate_data_channel_ls
from commlab.metrics import normalized_mean_square_error
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def test_ls_estimation_is_exact_for_flat_channel_without_noise():
    cfg = OFDMConfig()
    rng = np.random.default_rng(10)
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    n_symbols = 8
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 2, dtype=np.uint8)
    tx = ofdm.modulate(modem.modulate(bits))
    h = 0.7 + 0.35j
    data_rx, pilots_rx = ofdm.demodulate(h * tx)
    h_est = estimate_data_channel_ls(pilots_rx, cfg)
    assert np.allclose(h_est, h, atol=1e-12)
    equalized = zf_equalize(data_rx, h_est.reshape(-1))
    assert np.array_equal(bits, modem.demodulate(equalized))


def test_mmse_reduces_to_zf_when_noise_is_zero():
    rng = np.random.default_rng(11)
    y = rng.standard_normal(100) + 1j * rng.standard_normal(100)
    h = 0.5 + rng.random(100) + 1j * (0.1 + rng.random(100))
    assert np.allclose(mmse_equalize(y, h, 0.0), zf_equalize(y, h))


def test_rayleigh_taps_are_sparse_and_normalized():
    taps = generate_rayleigh_taps([0, 3, 8], [0.0, -4.0, -9.0], np.random.default_rng(12))
    assert len(taps) == 9
    assert np.count_nonzero(taps) == 3
    assert np.isclose(np.sum(np.abs(taps) ** 2), 1.0)


def test_nmse_zero_for_identical_arrays():
    x = np.array([1 + 1j, 2 - 0.5j])
    assert normalized_mean_square_error(x, x.copy()) == 0.0


def test_mean_square_error_is_zero_for_exact_match():
    from commlab.metrics import mean_square_error
    x = np.array([1 + 2j, -0.5 + 0.25j])
    assert mean_square_error(x, x.copy()) == 0.0
