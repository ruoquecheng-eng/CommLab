import numpy as np
from commlab.modulation import QAMModem


def test_qpsk_round_trip():
    rng = np.random.default_rng(1)
    bits = rng.integers(0, 2, 1000, dtype=np.uint8)
    modem = QAMModem(4)
    assert np.array_equal(bits, modem.demodulate(modem.modulate(bits)))


def test_16qam_round_trip():
    rng = np.random.default_rng(2)
    bits = rng.integers(0, 2, 2000, dtype=np.uint8)
    modem = QAMModem(16)
    assert np.array_equal(bits, modem.demodulate(modem.modulate(bits)))


def test_average_symbol_energy_is_near_one():
    rng = np.random.default_rng(3)
    for order in (4, 16):
        modem = QAMModem(order)
        bits = rng.integers(0, 2, 200_000, dtype=np.uint8)
        bits = bits[: len(bits) - len(bits) % modem.bits_per_symbol]
        symbols = modem.modulate(bits)
        assert abs(np.mean(np.abs(symbols) ** 2) - 1.0) < 0.03
