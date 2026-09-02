from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn
from commlab.modulation import QAMModem


if __name__ == "__main__":
    rng = np.random.default_rng(123)
    modem = QAMModem(16)
    bits = rng.integers(0, 2, 20_000, dtype=np.uint8)
    tx = modem.modulate(bits)
    rx = add_awgn(tx, 12, rng)

    plt.scatter(rx.real[:2500], rx.imag[:2500], s=8, alpha=0.45)
    plt.xlabel("In-phase")
    plt.ylabel("Quadrature")
    plt.title("16-QAM Constellation at 12 dB SNR")
    plt.grid(True)
    plt.axis("equal")
    plt.tight_layout()
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "constellation_16qam.png"
    plt.savefig(path, dpi=160)
    print(f"Saved {path}")
