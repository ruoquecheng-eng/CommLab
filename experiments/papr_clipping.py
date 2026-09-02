from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.config import OFDMConfig
from commlab.metrics import bit_error_rate, evm_percent
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.papr import papr_db, clip_magnitude


def run(order=16, n_symbols=4000, seed=2027):
    cfg = OFDMConfig()
    modem = QAMModem(order)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * modem.bits_per_symbol, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    waveform = ofdm.modulate(tx_symbols)
    frames = waveform.reshape(-1, cfg.symbol_len)[:, cfg.cp_len :]
    paprs = np.array([papr_db(s) for s in frames])

    thresholds = np.array([0.9, 1.1, 1.3, 1.6, 2.0, 3.0])
    rows = []
    for cr in thresholds:
        clipped = clip_magnitude(waveform, cr)
        clipped_frames = clipped.reshape(-1, cfg.symbol_len)[:, cfg.cp_len :]
        clipped_papr = np.mean([papr_db(s) for s in clipped_frames])
        rx_symbols, _ = ofdm.demodulate(clipped)
        rows.append((
            cr,
            clipped_papr,
            evm_percent(tx_symbols, rx_symbols),
            bit_error_rate(bits, modem.demodulate(rx_symbols)),
        ))
    return paprs, np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)

    paprs, rows = run()
    np.savetxt(out_data / "papr_clipping.csv", rows, delimiter=",", header="clip_ratio,mean_papr_db,evm_pct,ber", comments="")

    thresholds = np.linspace(3, 13, 101)
    ccdf = np.array([np.mean(paprs > t) for t in thresholds])
    plt.figure()
    plt.semilogy(thresholds, np.maximum(ccdf, 1e-5))
    plt.xlabel("PAPR threshold (dB)")
    plt.ylabel("Pr(PAPR > threshold)")
    plt.title("OFDM PAPR CCDF (16-QAM)")
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.savefig(out_fig / "papr_ccdf.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(rows[:, 1], rows[:, 2], marker="o")
    for row in rows:
        plt.annotate(f"CR={row[0]:.1f}", (row[1], row[2]))
    plt.xlabel("Mean post-clipping PAPR (dB)")
    plt.ylabel("Clipping EVM (%)")
    plt.title("PAPR–Distortion Trade-off")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "papr_clipping_tradeoff.png", dpi=160)
    plt.close()

    print("Unclipped PAPR mean / 99th percentile:", float(np.mean(paprs)), float(np.quantile(paprs, 0.99)))
    print("clip ratio, mean PAPR, EVM%, BER")
    for row in rows:
        print(tuple(row))
