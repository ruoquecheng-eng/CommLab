from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn
from commlab.metrics import bit_error_rate
from commlab.modulation import QAMModem


def run(order: int, snrs=range(0, 19, 2), n_bits: int = 192_000, seed: int = 42):
    modem = QAMModem(order)
    rng = np.random.default_rng(seed)
    n_bits -= n_bits % modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    tx = modem.modulate(bits)

    bers = []
    for snr in snrs:
        rx = add_awgn(tx, snr, rng)
        bits_hat = modem.demodulate(rx)
        bers.append(bit_error_rate(bits, bits_hat))
    return np.asarray(list(snrs)), np.asarray(bers)


if __name__ == "__main__":
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)

    for order, label in [(4, "QPSK"), (16, "16-QAM"), (64, "64-QAM")]:
        snr, ber = run(order)
        plt.semilogy(snr, np.maximum(ber, 1e-6), marker="o", label=label)
        print(label, dict(zip(snr.tolist(), ber.tolist())))

    plt.xlabel("Sample/Symbol SNR (dB)")
    plt.ylabel("BER")
    plt.title("Uncoded QAM over AWGN")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    path = out / "ber_awgn.png"
    plt.savefig(path, dpi=160)
    print(f"Saved {path}")
