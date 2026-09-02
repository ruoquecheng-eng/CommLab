from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn, apply_multipath, channel_frequency_response
from commlab.config import OFDMConfig
from commlab.estimation import estimate_data_channel_ls
from commlab.metrics import normalized_mean_square_error
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver

PILOT_LAYOUTS = {
    4: (-21, -7, 7, 21),
    8: (-24, -18, -12, -6, 6, 12, 18, 24),
    12: (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24),
}


def run(snrs=(6, 12, 18, 24, 30), n_symbols=1000, seed=121):
    rng = np.random.default_rng(seed)
    modem = QAMModem(4)
    taps = np.zeros(16, dtype=np.complex128)
    taps[[0, 3, 8, 15]] = np.array([1.0, 0.52*np.exp(0.5j), 0.30*np.exp(-0.8j), 0.17*np.exp(1.1j)])
    taps /= np.linalg.norm(taps)
    rows = []

    for count, positions in PILOT_LAYOUTS.items():
        cfg = OFDMConfig(
            pilot_subcarriers=positions,
            pilot_values=tuple(1 + 0j for _ in positions),
        )
        ofdm = OFDMTransceiver(cfg)
        n_bits = n_symbols * cfg.n_data * modem.bits_per_symbol
        bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
        tx = ofdm.modulate(modem.modulate(bits))
        true_h = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
        true_h = np.tile(true_h, (n_symbols, 1))

        for snr in snrs:
            rx = add_awgn(apply_multipath(tx, taps), snr, rng)
            _, pilots = ofdm.demodulate(rx)
            h_hat = estimate_data_channel_ls(pilots, cfg)
            nmse = normalized_mean_square_error(true_h, h_hat)
            payload_fraction = cfg.n_data / len(cfg.active_subcarriers)
            rows.append((count, snr, nmse, payload_fraction))
    return np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)
    rows = run()
    np.savetxt(out_data / "pilot_density_tradeoff.csv", rows, delimiter=",", header="pilot_count,snr_db,channel_nmse,payload_fraction", comments="")

    plt.figure()
    for count in sorted(PILOT_LAYOUTS):
        r = rows[rows[:, 0] == count]
        plt.semilogy(r[:, 1], r[:, 2], marker="o", label=f"{count} pilots")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Channel-estimation NMSE")
    plt.title("Pilot Density vs LS Interpolation Error")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_fig / "pilot_density_nmse.png", dpi=160)
    plt.close()

    unique = []
    for count in sorted(PILOT_LAYOUTS):
        r = rows[rows[:, 0] == count][0]
        unique.append((count, r[3]))
    unique = np.asarray(unique)
    plt.figure()
    plt.plot(unique[:, 0], unique[:, 1], marker="o")
    plt.xlabel("Pilot carriers per OFDM symbol")
    plt.ylabel("Payload fraction of active carriers")
    plt.title("Pilot Density–Payload Overhead Trade-off")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "pilot_density_overhead.png", dpi=160)
    plt.close()

    print("pilot count, SNR, NMSE, payload fraction")
    for row in rows:
        print(tuple(row))
