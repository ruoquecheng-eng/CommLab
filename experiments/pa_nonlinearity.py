from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import rapp_amplifier, scale_for_input_backoff, occupied_guard_power_ratio_db
from commlab.metrics import bit_error_rate, evm_percent
from commlab.papr import papr_db

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def best_gain(reference, observed):
    return np.vdot(reference, observed) / np.vdot(reference, reference)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(601)
    cfg = OFDMConfig()
    modem = QAMModem(16)
    ofdm = OFDMTransceiver(cfg)
    n_symbols = 1500
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * modem.bits_per_symbol, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    wave = ofdm.modulate(tx_symbols)
    ibos = np.arange(0, 11, 1)
    rows = []

    for ibo in ibos:
        driven = scale_for_input_backoff(wave, float(ibo), saturation_amplitude=1.0)
        y = rapp_amplifier(driven, saturation_amplitude=1.0, smoothness=2.0)
        rx_symbols, _ = ofdm.demodulate(y)
        # Remove deterministic small-signal gain so EVM measures nonlinear distortion.
        g = best_gain(tx_symbols, rx_symbols)
        corrected = rx_symbols / g
        ber = bit_error_rate(bits, modem.demodulate(corrected))
        evm = evm_percent(tx_symbols, corrected)
        blocks = y.reshape(-1, cfg.symbol_len)[:, cfg.cp_len:].reshape(-1)
        occ = np.concatenate((cfg.data_bins, cfg.pilot_bins))
        leakage = occupied_guard_power_ratio_db(blocks, occ, cfg.n_fft)
        rows.append((ibo, ber, evm, papr_db(y), leakage))
        print(f"IBO={ibo:2d} dB | BER={ber:.4g} EVM={evm:6.2f}% PAPR={papr_db(y):.2f} dB guard={leakage:.1f} dB")

    with open(DATA / "pa_nonlinearity.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ibo_db", "ber", "evm_percent", "output_papr_db", "guard_to_occupied_db"])
        w.writerows(rows)

    a = np.asarray(rows)
    plt.figure(figsize=(7.2, 4.8))
    plt.plot(a[:,0], a[:,2], "o-")
    plt.xlabel("Input back-off (dB)")
    plt.ylabel("EVM (%)")
    plt.title("Rapp PA Nonlinearity: Back-off vs In-Band Distortion")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "pa_ibo_evm.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    plt.plot(a[:,0], a[:,4], "s-")
    plt.xlabel("Input back-off (dB)")
    plt.ylabel("Guard / occupied power (dB)")
    plt.title("Rapp PA Nonlinearity: Spectral Regrowth into OFDM Guard Bins")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "pa_spectral_regrowth.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    plt.semilogy(a[:,0], np.maximum(a[:,1], 1/len(bits)), "^-", label="BER")
    plt.xlabel("Input back-off (dB)")
    plt.ylabel("BER")
    plt.title("16-QAM OFDM under Memoryless Power-Amplifier Compression")
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "pa_ibo_ber.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
