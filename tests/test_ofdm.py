import numpy as np
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def test_ofdm_noiseless_round_trip_zero_ber():
    cfg = OFDMConfig()
    rng = np.random.default_rng(4)
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    n_bits = 12 * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    waveform = ofdm.modulate(tx_symbols)
    rx_symbols, pilots = ofdm.demodulate(waveform)
    bits_hat = modem.demodulate(rx_symbols)
    assert np.array_equal(bits, bits_hat)
    assert pilots.shape == (12, 4)
