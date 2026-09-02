from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn
from commlab.config import OFDMConfig
from commlab.frame import build_frame, extract_payload
from commlab.impairments import apply_cfo, prepend_timing_offset
from commlab.metrics import bit_error_rate, evm_percent
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.synchronization import (
    repeated_half_preamble,
    detect_frame_start,
    estimate_cfo_from_repeated_halves,
    correct_cfo,
    estimate_common_phase_from_pilots,
    correct_common_phase,
)


def run(order=16, snrs=(4, 8, 12, 16, 20, 24), normalized_cfo=0.12, n_symbols=300, seed=77):
    cfg = OFDMConfig()
    modem = QAMModem(order)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(seed)
    n_bits = n_symbols * cfg.n_data * modem.bits_per_symbol
    bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    payload = ofdm.modulate(tx_symbols)
    preamble = repeated_half_preamble(cfg.n_fft, seed=123)
    frame = build_frame(payload, preamble)

    rows = []
    for snr in snrs:
        offset = 53
        delayed = prepend_timing_offset(frame, offset)
        impaired = apply_cfo(delayed, normalized_cfo, cfg.n_fft)
        rx = add_awgn(impaired, snr, rng)

        # A: known timing, no CFO correction.
        payload_a = rx[offset + len(preamble) : offset + len(preamble) + len(payload)]
        data_a, _ = ofdm.demodulate(payload_a)
        bits_a = modem.demodulate(data_a)

        # B: practical timing detection + coarse CFO estimate, no pilot phase tracking.
        start, score = detect_frame_start(rx, preamble)
        eps_hat = estimate_cfo_from_repeated_halves(rx[start : start + cfg.n_fft], cfg.n_fft)
        aligned = rx[start : start + len(frame)]
        corrected = correct_cfo(aligned, eps_hat, cfg.n_fft, start_index=start)
        payload_b = extract_payload(corrected, len(preamble), len(payload))
        data_b, pilots_b = ofdm.demodulate(payload_b)
        bits_b = modem.demodulate(data_b)

        # C: add pilot-based common-phase tracking to remove residual CFO phase drift.
        cpe = estimate_common_phase_from_pilots(pilots_b, cfg)
        data_c = correct_common_phase(data_b, cpe, cfg.n_data)
        bits_c = modem.demodulate(data_c)

        # D: genie timing + genie CFO baseline.
        aligned_d = rx[offset : offset + len(frame)]
        corrected_d = correct_cfo(aligned_d, normalized_cfo, cfg.n_fft, start_index=offset)
        payload_d = extract_payload(corrected_d, len(preamble), len(payload))
        data_d, _ = ofdm.demodulate(payload_d)
        bits_d = modem.demodulate(data_d)

        rows.append((
            snr,
            bit_error_rate(bits, bits_a),
            bit_error_rate(bits, bits_b),
            bit_error_rate(bits, bits_c),
            bit_error_rate(bits, bits_d),
            evm_percent(tx_symbols, data_c),
            start - offset,
            eps_hat - normalized_cfo,
            score,
        ))
    return np.asarray(rows, float)


if __name__ == "__main__":
    out_fig = ROOT / "results" / "figures"
    out_data = ROOT / "results" / "data"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_data.mkdir(parents=True, exist_ok=True)

    rows = run()
    np.savetxt(
        out_data / "full_system_sync.csv",
        rows,
        delimiter=",",
        header="snr_db,ber_no_cfo_correction,ber_coarse_cfo_only,ber_coarse_cfo_plus_pilot_cpe,ber_genie_sync,evm_pct_pilot_cpe,timing_error,cfo_error,corr_score",
        comments="",
    )

    plt.figure()
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 1], 1e-6), marker="o", label="No CFO correction")
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 2], 1e-6), marker="o", label="Coarse CFO only")
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 3], 1e-6), marker="o", label="Coarse CFO + pilot CPE")
    plt.semilogy(rows[:, 0], np.maximum(rows[:, 4], 1e-6), marker="o", label="Genie synchronization")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("BER")
    plt.title("16-QAM OFDM with 0.12-Subcarrier CFO")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_fig / "full_system_sync_ber.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(rows[:, 0], rows[:, 5], marker="o")
    plt.xlabel("Sample-domain SNR (dB)")
    plt.ylabel("RMS EVM (%)")
    plt.title("EVM after Coarse CFO + Pilot Phase Tracking")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_fig / "full_system_sync_evm.png", dpi=160)
    plt.close()

    print("SNR, no CFO, coarse CFO, +pilot CPE, genie, EVM%")
    for row in rows:
        print(tuple(row[:6]))
