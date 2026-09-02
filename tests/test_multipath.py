import numpy as np
from commlab.channels import apply_multipath, channel_frequency_response
from commlab.config import OFDMConfig
from commlab.equalization import zf_equalize
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def test_cp_plus_perfect_zf_recovers_bits_in_noiseless_multipath():
    cfg = OFDMConfig()
    rng = np.random.default_rng(5)
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    n_symbols = 20
    n_bits = n_symbols * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    qam = modem.modulate(bits)
    tx = ofdm.modulate(qam)

    taps = np.zeros(7, dtype=np.complex128)
    taps[0] = 1.0
    taps[2] = 0.4 + 0.1j
    taps[6] = 0.2 - 0.1j
    rx = apply_multipath(tx, taps)

    data, _ = ofdm.demodulate(rx)
    h = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    data_eq = zf_equalize(data, np.tile(h, n_symbols))
    bits_hat = modem.demodulate(data_eq)
    assert np.array_equal(bits, bits_hat)
