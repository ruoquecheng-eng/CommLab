from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.metrics import bit_error_rate
from commlab.mimo import rayleigh_mimo_channel, apply_mimo_channel, zf_detect, mmse_detect
from commlab.modulation import QAMModem


def run(snrs=(0, 3, 6, 9, 12, 15, 18, 21, 24), n_vectors=80_000, seed=313):
    rng = np.random.default_rng(seed)
    modem = QAMModem(4)
    n_tx = 2
    bits = rng.integers(0, 2, n_vectors * n_tx * modem.bits_per_symbol, dtype=np.uint8)
    x = modem.modulate(bits).reshape(n_vectors, n_tx)
    h = rayleigh_mimo_channel(n_vectors, 2, 2, rng)
    clean = apply_mimo_channel(x, h)
    rows = []

    for snr_db in snrs:
        # E[|sum_j h_ij x_j|^2] = n_tx for unit-energy streams / CN(0,1) H.
        noise_var = n_tx / (10 ** (snr_db / 10.0))
        noise = np.sqrt(noise_var / 2) * (
            rng.standard_normal(clean.shape) + 1j * rng.standard_normal(clean.shape)
        )
        y = clean + noise
        x_zf = zf_detect(y, h)
        x_mmse = mmse_detect(y, h, noise_var, symbol_energy=1.0)
        ber_zf = bit_error_rate(bits, modem.demodulate(x_zf.reshape(-1)))
        ber_mmse = bit_error_rate(bits, modem.demodulate(x_mmse.reshape(-1)))
        rows.append((snr_db, ber_zf, ber_mmse))
    return np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)
    rows = run()
    np.savetxt(out_data / "mimo_2x2.csv", rows, delimiter=",", header="snr_db,ber_zf,ber_mmse", comments="")

    plt.figure()
    plt.semilogy(rows[:, 0], rows[:, 1], marker="o", label="2x2 ZF")
    plt.semilogy(rows[:, 0], rows[:, 2], marker="o", label="2x2 MMSE")
    plt.xlabel("Per-receive-antenna SNR (dB)")
    plt.ylabel("BER")
    plt.title("2x2 QPSK Spatial Multiplexing over Flat Rayleigh Fading")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_fig / "mimo_2x2_zf_mmse.png", dpi=160)
    plt.close()

    print("SNR, ZF BER, MMSE BER")
    for row in rows:
        print(tuple(row))
