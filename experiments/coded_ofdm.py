from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import ConvolutionalCode
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn
from commlab.metrics import bit_error_rate


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def ofdm_awgn_hard_bits(bits, snr_db, rng, cfg, modem, ofdm):
    bits = np.asarray(bits, dtype=np.uint8)
    block = cfg.n_data * modem.bits_per_symbol
    pad = (-len(bits)) % block
    padded = np.pad(bits, (0, pad))
    tx = ofdm.modulate(modem.modulate(padded))
    rx = add_awgn(tx, snr_db, rng)
    syms, _ = ofdm.demodulate(rx)
    hard = modem.demodulate(syms)
    return hard[: len(bits)]


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    rng_data = np.random.default_rng(401)
    cfg = OFDMConfig()
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    code = ConvolutionalCode()

    n_info = 30000
    info = rng_data.integers(0, 2, n_info, dtype=np.uint8)
    coded = code.encode(info, terminate=True)
    snrs = np.arange(0, 13, 2)
    rows = []
    for snr in snrs:
        unc_rx = ofdm_awgn_hard_bits(info, snr, np.random.default_rng(1000 + int(snr)), cfg, modem, ofdm)
        coded_rx = ofdm_awgn_hard_bits(coded, snr, np.random.default_rng(2000 + int(snr)), cfg, modem, ofdm)
        decoded = code.decode_hard(coded_rx, terminated=True, trim_tail=True)
        ber_unc = bit_error_rate(info, unc_rx)
        ber_coded = bit_error_rate(info, decoded)
        rows.append((snr, ber_unc, ber_coded))
        print(f"SNR={snr:2d} dB | uncoded={ber_unc:.5g} coded={ber_coded:.5g}")

    with open(DATA / "coded_ofdm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["snr_db", "uncoded_ber", "conv_viterbi_ber"])
        w.writerows(rows)

    arr = np.asarray(rows, dtype=float)
    plt.figure(figsize=(7.2, 4.8))
    plt.semilogy(arr[:, 0], np.maximum(arr[:, 1], 1/n_info), "o-", label="Uncoded QPSK-OFDM")
    plt.semilogy(arr[:, 0], np.maximum(arr[:, 2], 1/n_info), "s-", label="Rate-1/2 conv. code + hard Viterbi")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Information-bit BER")
    plt.title("Forward Error Correction in QPSK-OFDM")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "coded_ofdm_ber.png", dpi=180)
    plt.close()

    # A second plot makes the rate/reliability trade-off explicit.
    plt.figure(figsize=(7.2, 4.8))
    rates = [2.0, 1.0]  # information bits per QPSK data resource element
    labels = ["Uncoded", "Rate-1/2 coded"]
    plt.bar(labels, rates)
    plt.ylabel("Information bits / data subcarrier")
    plt.title("Coding Reliability Comes with Rate Overhead")
    plt.tight_layout()
    plt.savefig(FIG / "coded_ofdm_rate_tradeoff.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
