from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.papr import slm_modulate_data_blocks

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def ccdf(samples, thresholds):
    return np.array([np.mean(samples > x) for x in thresholds])


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    cfg = OFDMConfig()
    modem = QAMModem(16)
    rng = np.random.default_rng(801)
    n_symbols = 5000
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 4, dtype=np.uint8)
    data = modem.modulate(bits).reshape(n_symbols, cfg.n_data)

    results = {}
    for U in (1, 4, 8):
        _, _, papr = slm_modulate_data_blocks(data, cfg, n_candidates=U, rng=np.random.default_rng(810+U))
        results[U] = papr
        print(f"SLM U={U}: mean={np.mean(papr):.3f} dB, P99={np.percentile(papr,99):.3f} dB, max={np.max(papr):.3f} dB")

    with open(DATA / "papr_slm_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_candidates", "mean_papr_db", "p99_papr_db", "max_papr_db", "side_info_bits_per_symbol"])
        for U, papr in results.items():
            side = 0 if U == 1 else int(np.ceil(np.log2(U)))
            w.writerow([U, np.mean(papr), np.percentile(papr,99), np.max(papr), side])

    thresholds = np.linspace(4.0, 12.0, 81)
    plt.figure(figsize=(7.2, 4.8))
    for U, marker in [(1,"-"),(4,"--"),(8,"-.")]:
        c = ccdf(results[U], thresholds)
        plt.semilogy(thresholds, np.maximum(c, 1/n_symbols), marker, label=f"SLM candidates U={U}")
    plt.xlabel("PAPR threshold (dB)")
    plt.ylabel("CCDF: Pr(PAPR > threshold)")
    plt.title("Distortionless Selective Mapping for OFDM PAPR Reduction")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "papr_slm_ccdf.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    us = np.array([1,4,8])
    p99 = np.array([np.percentile(results[u],99) for u in us])
    plt.plot(us, p99, "o-")
    plt.xlabel("Number of SLM candidates")
    plt.ylabel("99th-percentile PAPR (dB)")
    plt.title("PAPR Reduction vs SLM Search Complexity")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "papr_slm_complexity.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
