from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn, apply_multipath, channel_frequency_response
from commlab.config import OFDMConfig
from commlab.equalization import zf_equalize
from commlab.metrics import bit_error_rate
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def run(snrs=range(0, 25, 3), n_ofdm_symbols: int = 300, seed: int = 7):
    cfg = OFDMConfig()
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)

    n_bits = n_ofdm_symbols * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    qam = modem.modulate(bits)
    tx = ofdm.modulate(qam)

    # A frequency-selective channel whose delay spread fits inside the CP.
    taps = np.zeros(9, dtype=np.complex128)
    taps[0] = 1.0
    taps[3] = 0.55 * np.exp(1j * 0.35)
    taps[8] = 0.25 * np.exp(-1j * 0.7)
    taps /= np.sqrt(np.sum(np.abs(taps) ** 2))

    faded = apply_multipath(tx, taps)
    h = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]

    ber_no_eq = []
    ber_zf = []
    for snr in snrs:
        rx = add_awgn(faded, snr, rng)
        data_rx, _ = ofdm.demodulate(rx)

        bits_no_eq = modem.demodulate(data_rx)
        ber_no_eq.append(bit_error_rate(bits, bits_no_eq))

        h_all = np.tile(h, n_ofdm_symbols)
        data_eq = zf_equalize(data_rx, h_all)
        bits_eq = modem.demodulate(data_eq)
        ber_zf.append(bit_error_rate(bits, bits_eq))

    return np.asarray(list(snrs)), np.asarray(ber_no_eq), np.asarray(ber_zf)


if __name__ == "__main__":
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    snr, no_eq, zf = run()

    plt.semilogy(snr, np.maximum(no_eq, 1e-6), marker="o", label="Multipath, no EQ")
    plt.semilogy(snr, np.maximum(zf, 1e-6), marker="s", label="Multipath + perfect-CSI ZF")
    plt.xlabel("Waveform SNR (dB)")
    plt.ylabel("BER")
    plt.title("OFDM over Frequency-Selective Multipath")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    path = out / "ofdm_multipath_zf.png"
    plt.savefig(path, dpi=160)
    print("SNR:", snr)
    print("No EQ:", no_eq)
    print("ZF:", zf)
    print(f"Saved {path}")
