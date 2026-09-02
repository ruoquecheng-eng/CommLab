from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn, apply_multipath, channel_frequency_response, generate_rayleigh_taps
from commlab.config import OFDMConfig
from commlab.estimation import estimate_data_channel_ls
from commlab.metrics import normalized_mean_square_error
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver


def run_nmse(snrs=range(0, 31, 3), n_ofdm_symbols: int = 300, seed: int = 21):
    cfg = OFDMConfig()
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)

    n_bits = n_ofdm_symbols * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    tx = ofdm.modulate(modem.modulate(bits))
    taps = generate_rayleigh_taps([0, 1, 3], [0.0, -6.0, -12.0], rng)
    faded = apply_multipath(tx, taps)
    h_true = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    h_true_frames = np.tile(h_true, (n_ofdm_symbols, 1))

    nmse = []
    snapshot = None
    for snr in snrs:
        rx = add_awgn(faded, snr, rng)
        _, pilots_rx = ofdm.demodulate(rx)
        h_est = estimate_data_channel_ls(pilots_rx, cfg)
        nmse.append(normalized_mean_square_error(h_true_frames, h_est))
        if snr == 18:
            snapshot = h_est[0].copy()

    if snapshot is None:
        snapshot = h_est[0].copy()
    return np.asarray(list(snrs)), np.asarray(nmse), h_true, snapshot, taps


if __name__ == "__main__":
    fig_dir = ROOT / "results" / "figures"
    data_dir = ROOT / "results" / "data"
    fig_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    snr, nmse, h_true, h_est, taps = run_nmse()
    np.savetxt(data_dir / "channel_estimation_nmse.csv", np.column_stack((snr, nmse)),
               delimiter=",", header="snr_db,nmse", comments="")

    plt.figure()
    plt.semilogy(snr, np.maximum(nmse, 1e-12), marker="o")
    plt.xlabel("Waveform SNR (dB)")
    plt.ylabel("Channel-estimation NMSE")
    plt.title("Pilot LS + Linear Interpolation")
    plt.grid(True, which="both")
    plt.tight_layout()
    p1 = fig_dir / "channel_estimation_nmse.png"
    plt.savefig(p1, dpi=160)
    plt.close()

    sc = np.asarray(OFDMConfig().data_subcarriers)
    plt.figure()
    plt.plot(sc, np.abs(h_true), label="True |H[k]|")
    plt.plot(sc, np.abs(h_est), marker=".", label="Estimated |H[k]| at 18 dB")
    plt.xlabel("Signed subcarrier index")
    plt.ylabel("Magnitude")
    plt.title("Frequency-Selective Channel: True vs Estimated")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    p2 = fig_dir / "channel_estimation_snapshot.png"
    plt.savefig(p2, dpi=160)
    plt.close()

    print("Rayleigh taps:", taps)
    print("SNR:", snr)
    print("NMSE:", nmse)
    print(f"Saved {p1}")
    print(f"Saved {p2}")
