from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn
from commlab.config import OFDMConfig
from commlab.metrics import bit_error_rate
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def evaluate(snrs=range(0, 27, 3), orders=(4, 16, 64), n_symbols=800, target_ber=1e-2, seed=88):
    cfg = OFDMConfig()
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)
    ber = np.zeros((len(orders), len(tuple(snrs))))
    snrs = tuple(snrs)

    for i, order in enumerate(orders):
        modem = QAMModem(order)
        bits = rng.integers(0, 2, n_symbols * cfg.n_data * modem.bits_per_symbol, dtype=np.uint8)
        symbols = modem.modulate(bits)
        wave = ofdm.modulate(symbols)
        for j, snr in enumerate(snrs):
            rx = add_awgn(wave, snr, rng)
            data, _ = ofdm.demodulate(rx)
            ber[i, j] = bit_error_rate(bits, modem.demodulate(data))

    selected = np.empty(len(snrs), dtype=int)
    goodput = np.empty(len(snrs), dtype=float)
    for j, snr in enumerate(snrs):
        feasible = [i for i in range(len(orders)) if ber[i, j] <= target_ber]
        idx = feasible[-1] if feasible else 0
        selected[j] = orders[idx]
        bits_per_symbol = int(np.log2(orders[idx]))
        # Effective uncoded delivered information bits per time-domain sample.
        goodput[j] = bits_per_symbol * cfg.n_data / cfg.symbol_len * (1.0 - ber[idx, j])
    return np.asarray(snrs), np.asarray(orders), ber, selected, goodput


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)

    snrs, orders, ber, selected, goodput = evaluate()
    table = np.column_stack((snrs, ber.T, selected, goodput))
    np.savetxt(
        out_data / "adaptive_modulation.csv",
        table,
        delimiter=",",
        header="snr_db,ber_qpsk,ber_16qam,ber_64qam,selected_order,effective_goodput_bits_per_sample",
        comments="",
    )

    plt.figure()
    for i, order in enumerate(orders):
        plt.semilogy(snrs, np.maximum(ber[i], 1e-6), marker="o", label=f"{order}-QAM")
    plt.axhline(1e-2, linestyle="--", label="BER target 1e-2")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("BER")
    plt.title("OFDM Modulation-Order Selection")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_fig / "adaptive_modulation_ber.png", dpi=160)
    plt.close()

    plt.figure()
    plt.step(snrs, selected, where="mid")
    plt.yticks([4, 16, 64], ["QPSK", "16-QAM", "64-QAM"])
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Selected modulation")
    plt.title("Simple Link Adaptation under BER ≤ 1e-2")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "adaptive_modulation_selection.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(snrs, goodput, marker="o")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Effective uncoded goodput (bits/sample)")
    plt.title("Adaptive-Modulation Goodput")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "adaptive_modulation_goodput.png", dpi=160)
    plt.close()

    print("SNR / selected order / effective goodput")
    for s, m, g in zip(snrs, selected, goodput):
        print(int(s), int(m), float(g))
