from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import (
    add_awgn,
    apply_multipath,
    channel_frequency_response,
    generate_rayleigh_taps,
    noise_power_for_snr,
)
from commlab.config import OFDMConfig
from commlab.equalization import mmse_equalize, zf_equalize
from commlab.estimation import estimate_data_channel_ls
from commlab.metrics import bit_error_rate
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def run(
    snrs=range(0, 25, 3),
    n_ofdm_symbols: int = 160,
    n_channels: int = 20,
    seed: int = 31,
):
    cfg = OFDMConfig()
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)
    snrs = np.asarray(list(snrs), dtype=float)

    ber_perfect_zf = np.zeros_like(snrs)
    ber_ls_zf = np.zeros_like(snrs)
    ber_ls_mmse = np.zeros_like(snrs)

    n_bits = n_ofdm_symbols * cfg.n_data * modem.bits_per_symbol

    for _ in range(n_channels):
        bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
        tx = ofdm.modulate(modem.modulate(bits))
        taps = generate_rayleigh_taps([0, 1, 3], [0.0, -6.0, -12.0], rng)
        faded = apply_multipath(tx, taps)
        h_data = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
        h_perfect = np.tile(h_data, n_ofdm_symbols)

        for i, snr in enumerate(snrs):
            noise_var = noise_power_for_snr(faded, float(snr))
            rx = add_awgn(faded, float(snr), rng)
            data_rx, pilots_rx = ofdm.demodulate(rx)

            perfect = zf_equalize(data_rx, h_perfect)
            ber_perfect_zf[i] += bit_error_rate(bits, modem.demodulate(perfect))

            h_est = estimate_data_channel_ls(pilots_rx, cfg).reshape(-1)
            ls_zf = zf_equalize(data_rx, h_est)
            ber_ls_zf[i] += bit_error_rate(bits, modem.demodulate(ls_zf))

            ls_mmse = mmse_equalize(data_rx, h_est, noise_var=noise_var)
            ber_ls_mmse[i] += bit_error_rate(bits, modem.demodulate(ls_mmse))

    return snrs, ber_perfect_zf / n_channels, ber_ls_zf / n_channels, ber_ls_mmse / n_channels


if __name__ == "__main__":
    fig_dir = ROOT / "results" / "figures"
    data_dir = ROOT / "results" / "data"
    fig_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    snr, perfect, ls_zf, ls_mmse = run()
    np.savetxt(
        data_dir / "rayleigh_equalizers.csv",
        np.column_stack((snr, perfect, ls_zf, ls_mmse)),
        delimiter=",",
        header="snr_db,perfect_csi_zf,ls_zf,ls_mmse",
        comments="",
    )

    plt.figure()
    plt.semilogy(snr, np.maximum(perfect, 1e-6), marker="o", label="Perfect CSI + ZF")
    plt.semilogy(snr, np.maximum(ls_zf, 1e-6), marker="s", label="Pilot LS + ZF")
    plt.semilogy(snr, np.maximum(ls_mmse, 1e-6), marker="^", label="Pilot LS + MMSE")
    plt.xlabel("Waveform SNR (dB)")
    plt.ylabel("BER")
    plt.title("QPSK OFDM over Rayleigh Multipath")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    path = fig_dir / "rayleigh_equalizer_comparison.png"
    plt.savefig(path, dpi=160)
    plt.close()

    print("SNR:", snr)
    print("Perfect CSI + ZF:", perfect)
    print("Pilot LS + ZF:", ls_zf)
    print("Pilot LS + MMSE:", ls_mmse)
    print(f"Saved {path}")
