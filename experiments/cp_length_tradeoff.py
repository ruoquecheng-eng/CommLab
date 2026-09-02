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


def run(cp_lengths=(0, 2, 4, 8, 12, 16, 24), snr_db=22, n_symbols=1600, seed=91):
    rng = np.random.default_rng(seed)
    modem = QAMModem(16)
    # Delay spread reaches sample 12; CP >= 12 approximately restores circularity.
    taps = np.zeros(13, dtype=np.complex128)
    taps[[0, 3, 7, 12]] = np.array([1.0, 0.55*np.exp(0.4j), 0.32*np.exp(-0.7j), 0.18*np.exp(1.0j)])
    taps /= np.linalg.norm(taps)
    rows = []

    for cp in cp_lengths:
        cfg = OFDMConfig(cp_len=cp)
        ofdm = OFDMTransceiver(cfg)
        n_bits = n_symbols * cfg.n_data * modem.bits_per_symbol
        bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
        symbols = modem.modulate(bits)
        tx = ofdm.modulate(symbols)
        rx = apply_multipath(tx, taps)
        rx = add_awgn(rx, snr_db, rng)
        data, _ = ofdm.demodulate(rx)
        H = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
        H = np.tile(H, n_symbols)
        eq = zf_equalize(data, H)
        ber = bit_error_rate(bits, modem.demodulate(eq))
        efficiency = cfg.n_fft / cfg.symbol_len
        rows.append((cp, ber, efficiency))
    return np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)
    rows = run()
    np.savetxt(out_data / "cp_length_tradeoff.csv", rows, delimiter=",", header="cp_len,ber,time_efficiency", comments="")

    plt.figure()
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 1], 1e-6), marker="o")
    plt.xlabel("Cyclic-prefix length (samples)")
    plt.ylabel("BER")
    plt.title("CP Length vs BER in a 12-Sample-Delay Multipath Channel")
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.savefig(out_fig / "cp_length_ber.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(rows[:, 0], rows[:, 2], marker="o")
    plt.xlabel("Cyclic-prefix length (samples)")
    plt.ylabel("Useful-time efficiency N/(N+CP)")
    plt.title("CP Robustness–Overhead Trade-off")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "cp_length_efficiency.png", dpi=160)
    plt.close()

    print("CP, BER, useful-time efficiency")
    for row in rows:
        print(tuple(row))
