# Experiment Artifact Catalog — v1.0

CSV datasets: **59**  
Figures: **109**

## New v1.0 datasets

- `results/data/coded_mimo_ldpc.csv` — 8 rows; columns: snr_db, receiver, ber, ci95_low, ci95_high, fer, avg_ldpc_iterations
- `results/data/full_receiver_impairment_stress.csv` — 4 rows; columns: stage, ber, evm_rms, frame_start_true, frame_start_estimated, cfo_true, cfo_estimated
- `results/data/harq_incremental_redundancy.csv` — 10 rows; columns: snr_db, scheme, packet_success_rate, avg_transmitted_coded_bits, avg_rounds, payload_goodput_bit_per_tx_bit
- `results/data/ofdm_isac_cfar.csv` — 12 rows; columns: snr_db, target, detection_probability, mean_false_alarms_per_map
- `results/data/ofdm_isac_range_doppler.csv` — 2 rows; columns: target, true_range_m, estimated_range_m, range_error_m, true_velocity_mps, estimated_velocity_mps, velocity_error_mps, peak_magnitude
- `results/data/ofdm_isac_resolution.csv` — 4 rows; columns: ofdm_symbols, coherent_processing_interval_ms, velocity_bin_mps
- `results/data/olla_link_adaptation.csv` — 2 rows; columns: scheme, steady_bler, steady_goodput_bit_per_use, mean_mcs_index, mean_snr_backoff_db
- `results/data/otfs_offgrid_refinement.csv` — 5 rows; columns: pilot_snr_db, coarse_doppler_mae_bins, refined_doppler_mae_bins, coarse_relative_residual, refined_relative_residual

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v10_suite.py
python tools/build_results_manifest_v10.py
python tools/verify_release_v10.py
```
