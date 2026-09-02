from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn
from commlab.impairments import apply_cfo, prepend_timing_offset
from commlab.synchronization import (
    repeated_half_preamble,
    detect_frame_start,
    estimate_cfo_from_repeated_halves,
)


def run(snrs=(-4, 0, 4, 8, 12, 16, 20), trials=300, epsilon=0.18, seed=2026):
    rng = np.random.default_rng(seed)
    preamble = repeated_half_preamble(64, seed=99)
    # A modest random tail makes the detector operate on a packet, not a lone preamble.
    payload = (rng.standard_normal(512) + 1j * rng.standard_normal(512)) / np.sqrt(2)
    frame = np.concatenate((preamble, payload))

    rows = []
    for snr in snrs:
        timing_errors = []
        cfo_errors = []
        detects = 0
        for _ in range(trials):
            offset = int(rng.integers(0, 121))
            tx = prepend_timing_offset(frame, offset)
            tx = apply_cfo(tx, epsilon, n_fft=64)
            rx = add_awgn(tx, snr, rng)
            start, score = detect_frame_start(rx, preamble)
            timing_errors.append(start - offset)
            if abs(start - offset) <= 1:
                detects += 1
            segment = rx[start : start + 64]
            if len(segment) == 64:
                est = estimate_cfo_from_repeated_halves(segment, 64)
                cfo_errors.append(est - epsilon)
        timing_errors = np.asarray(timing_errors, float)
        cfo_errors = np.asarray(cfo_errors, float)
        rows.append((
            snr,
            detects / trials,
            np.mean(np.abs(timing_errors)),
            np.sqrt(np.mean(cfo_errors**2)),
        ))
    return np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)

    rows = run()
    np.savetxt(
        out_data / "synchronization_cfo.csv",
        rows,
        delimiter=",",
        header="snr_db,detection_rate,timing_mae_samples,cfo_rmse_subcarrier",
        comments="",
    )

    plt.figure()
    plt.plot(rows[:, 0], rows[:, 1], marker="o")
    plt.ylim(0, 1.05)
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Detection probability (|timing error| ≤ 1)")
    plt.title("Known-Preamble Frame Detection")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "frame_detection_probability.png", dpi=160)
    plt.close()

    plt.figure()
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 3], 1e-5), marker="o")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("Normalized CFO RMSE")
    plt.title("Repeated-Half CFO Estimation")
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.savefig(out_fig / "cfo_estimation_rmse.png", dpi=160)
    plt.close()

    print("SNR, detection, timing MAE, CFO RMSE")
    for row in rows:
        print(tuple(row))
