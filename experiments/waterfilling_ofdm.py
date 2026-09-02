from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.channels import channel_frequency_response
from commlab.resource_allocation import waterfill_power_allocation, parallel_channel_capacity_bits

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    cfg = OFDMConfig()
    # Deterministic frequency-selective channel with several deep/notched regions.
    taps = np.zeros(16, dtype=np.complex128)
    taps[[0, 2, 5, 9, 15]] = [1.0, 0.62*np.exp(0.3j), 0.42*np.exp(-0.9j), 0.27*np.exp(1.4j), 0.14*np.exp(-0.2j)]
    taps /= np.linalg.norm(taps)
    H = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    gains = np.abs(H)**2
    n = len(gains)
    total_power = float(n)  # equal allocation would be 1 per data subcarrier
    snrs = np.arange(-5, 31, 5)
    rows = []

    allocations = {}
    for snr_db in snrs:
        noise = 10.0 ** (-snr_db/10.0)
        p_eq = np.full(n, total_power/n)
        p_wf = waterfill_power_allocation(gains, total_power, noise)
        c_eq = parallel_channel_capacity_bits(gains, p_eq, noise)
        c_wf = parallel_channel_capacity_bits(gains, p_wf, noise)
        rows.append((snr_db, c_eq/n, c_wf/n, np.count_nonzero(p_wf > 1e-8)))
        allocations[snr_db] = p_wf
        print(f"SNR={snr_db:3d} dB | equal={c_eq/n:.3f} b/s/Hz/carrier waterfill={c_wf/n:.3f} active={np.count_nonzero(p_wf>1e-8)}")

    with open(DATA / "waterfilling_ofdm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["snr_db", "equal_power_capacity_per_carrier", "waterfill_capacity_per_carrier", "active_carriers"])
        w.writerows(rows)

    a = np.asarray(rows)
    plt.figure(figsize=(7.2, 4.8))
    plt.plot(a[:,0], a[:,1], "o-", label="Equal power")
    plt.plot(a[:,0], a[:,2], "s-", label="Water-filling")
    plt.xlabel("Nominal SNR (dB)")
    plt.ylabel("Average spectral efficiency (bit/s/Hz per data carrier)")
    plt.title("OFDM Parallel-Channel Resource Allocation")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "waterfilling_capacity.png", dpi=180)
    plt.close()

    # Show how low-SNR water-filling avoids deep fades.
    snr_show = 0
    p = allocations[snr_show]
    signed = np.asarray(cfg.data_subcarriers)
    order = np.argsort(signed)
    fig, ax1 = plt.subplots(figsize=(8.2, 4.8))
    ax1.plot(signed[order], 10*np.log10(gains[order] + 1e-12), "o-", label="Channel gain")
    ax1.set_xlabel("Subcarrier index")
    ax1.set_ylabel("Channel power gain (dB)")
    ax2 = ax1.twinx()
    ax2.step(signed[order], p[order], where="mid", label="Water-filled power")
    ax2.set_ylabel("Allocated power")
    ax1.set_title("Water-Filling Avoids Deep-Fade OFDM Subcarriers at 0 dB")
    fig.tight_layout()
    fig.savefig(FIG / "waterfilling_allocation.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
