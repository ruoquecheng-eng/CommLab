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
from commlab.metrics import mean_square_error
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def run(snrs=range(0, 25, 3), n_ofdm_symbols: int = 300, seed: int = 41):
    cfg = OFDMConfig()
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)

    n_bits = n_ofdm_symbols * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    symbols = modem.modulate(bits)
    tx = ofdm.modulate(symbols)
    taps = generate_rayleigh_taps([0, 1, 3], [0.0, -6.0, -12.0], rng)
    faded = apply_multipath(tx, taps)
    h = np.tile(channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins], n_ofdm_symbols)

    mse_zf, mse_mmse = [], []
    for snr in snrs:
        noise_var = noise_power_for_snr(faded, float(snr))
        rx = add_awgn(faded, float(snr), rng)
        data_rx, _ = ofdm.demodulate(rx)
        zf = zf_equalize(data_rx, h)
        mmse = mmse_equalize(data_rx, h, noise_var=noise_var)
        mse_zf.append(mean_square_error(symbols, zf))
        mse_mmse.append(mean_square_error(symbols, mmse))
    return np.asarray(list(snrs)), np.asarray(mse_zf), np.asarray(mse_mmse)


if __name__ == "__main__":
    fig_dir = ROOT / "results" / "figures"
    data_dir = ROOT / "results" / "data"
    fig_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    snr, zf, mmse = run()
    np.savetxt(
        data_dir / "mmse_symbol_mse.csv",
        np.column_stack((snr, zf, mmse)),
        delimiter=",",
        header="snr_db,zf_symbol_mse,mmse_symbol_mse",
        comments="",
    )
    plt.figure()
    plt.semilogy(snr, zf, marker="o", label="Perfect CSI + ZF")
    plt.semilogy(snr, mmse, marker="s", label="Perfect CSI + MMSE")
    plt.xlabel("Waveform SNR (dB)")
    plt.ylabel("Equalized-symbol MSE")
    plt.title("ZF vs MMSE: Symbol Estimation Error")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    path = fig_dir / "mmse_symbol_mse.png"
    plt.savefig(path, dpi=160)
    plt.close()
    print("SNR:", snr)
    print("ZF MSE:", zf)
    print("MMSE MSE:", mmse)
    print(f"Saved {path}")
