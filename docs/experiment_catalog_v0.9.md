# Experiment Artifact Catalog — v0.9

CSV datasets: **51**  
Figures: **95**

## New v0.9 datasets

- `results/data/coded_mimo_soft_output.csv` — 18 rows; columns: snr_db, receiver, ber, ci95_low, ci95_high, frame_error_rate, bit_errors, bits
- `results/data/finite_blocklength_awgn.csv` — 130 rows; columns: snr_db, curve, blocklength, rate_bits_per_complex_use, target_error_probability
- `results/data/harq_chase_combining.csv` — 12 rows; columns: snr_db, scheme, success_probability, packet_error_rate, average_transmissions, payload_goodput_bits_per_qpsk_symbol, mean_success_latency_attempts, successful_packets, transmissions
- `results/data/ici_matrix_estimation.csv` — 24 rows; columns: training_symbols, receiver, ber, ci95_low, ci95_high, band_matrix_nmse, ici_energy_fraction
- `results/data/otfs_sparse_path_estimation.csv` — 6 rows; columns: pilot_snr_db, exact_support_probability, pilot_relative_residual, gain_nmse_when_support_correct, estimated_path_lmmse_ber, ci95_low, ci95_high, genie_lmmse_ber
- `results/data/queue_aware_ofdma.csv` — 4 rows; columns: scheduler, throughput_bits_per_slot, jain_fairness, mean_delay_slots, p95_delay_slots, completed_packets, pending_packets, final_backlog_bits, user0_bits, user1_bits, user2_bits, user3_bits

## Validation

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python experiments/run_v09_suite.py
python tools/build_results_manifest_v09.py
python tools/verify_release_v09.py
```
