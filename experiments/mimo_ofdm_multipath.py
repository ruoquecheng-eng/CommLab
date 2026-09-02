from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn, noise_power_for_snr
from commlab.mimo import (
    generate_mimo_multipath_taps,
    apply_mimo_multipath_waveforms,
    detect_mimo_ofdm_data,
)
from commlab.metrics import bit_error_rate

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    cfg = OFDMConfig(cp_len=16)
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    n_symbols = 250
    snrs = np.arange(0, 25, 4)
    n_channels = 12
    rows = []

    for snr in snrs:
        zf_err = mmse_err = total = 0
        for c in range(n_channels):
            rng = np.random.default_rng(50000 + int(snr)*100 + c)
            bits_by_tx = []
            waves = []
            for _ in range(2):
                bits = rng.integers(0, 2, n_symbols * cfg.n_data * 2, dtype=np.uint8)
                bits_by_tx.append(bits)
                waves.append(ofdm.modulate(modem.modulate(bits)))
            tx = np.stack(waves)
            taps = generate_mimo_multipath_taps(2, 2, rng=rng)
            clean = apply_mimo_multipath_waveforms(tx, taps)
            rx = np.stack([add_awgn(clean[r], snr, rng) for r in range(2)])
            # Unit-norm FFT preserves per-sample complex noise variance.
            nv = float(np.mean([noise_power_for_snr(clean[r], snr) for r in range(2)]))
            zf = detect_mimo_ofdm_data(rx, taps, cfg, method="zf", noise_var_freq=nv)
            mm = detect_mimo_ofdm_data(rx, taps, cfg, method="mmse", noise_var_freq=nv)
            for t in range(2):
                bz = modem.demodulate(zf[..., t].reshape(-1))
                bm = modem.demodulate(mm[..., t].reshape(-1))
                zf_err += np.count_nonzero(bz != bits_by_tx[t])
                mmse_err += np.count_nonzero(bm != bits_by_tx[t])
                total += len(bits_by_tx[t])
        ber_zf = zf_err / total
        ber_mmse = mmse_err / total
        rows.append((snr, ber_zf, ber_mmse, 2 * 2))
        print(f"SNR={snr:2d} dB | MIMO-OFDM ZF={ber_zf:.5g} MMSE={ber_mmse:.5g}")

    with open(DATA / "mimo_ofdm_multipath.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["snr_db", "zf_ber", "mmse_ber", "raw_bits_per_data_re"])
        w.writerows(rows)

    a = np.asarray(rows)
    floor = 1 / (n_symbols * cfg.n_data * 2 * 2 * n_channels)
    plt.figure(figsize=(7.2, 4.8))
    plt.semilogy(a[:,0], np.maximum(a[:,1], floor), "o-", label="2×2 MIMO-OFDM ZF")
    plt.semilogy(a[:,0], np.maximum(a[:,2], floor), "s-", label="2×2 MIMO-OFDM MMSE")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("BER")
    plt.title("2×2 MIMO-OFDM over Frequency-Selective Rayleigh Multipath")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "mimo_ofdm_multipath_ber.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
