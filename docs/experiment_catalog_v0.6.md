# Experiment Artifact Catalog — v0.6

CSV datasets: **37**  
Figures: **66**

The JSON manifest records SHA-256 hashes so generated artifacts can be checked for accidental changes.

## v0.6 datasets

- `results/data/iq_imbalance_compensation.csv` — 6 rows; columns: gain_imbalance_db, phase_imbalance_deg, estimated_irr_db, raw_ber, compensated_ber, raw_evm_pct, compensated_evm_pct
- `results/data/ldpc_min_sum_ofdm.csv` — 6 rows; columns: snr_db, sparse_ldpc_min_sum_ber, conv_soft_viterbi_ber, ldpc_avg_iterations, ldpc_converged_fraction
- `results/data/learned_polynomial_dpd.csv` — 5 rows; columns: backoff_db, pa_only_evm_pct, learned_poly_dpd_evm_pct, known_inverse_evm_pct, pa_only_guard_db, learned_poly_guard_db, known_inverse_guard_db
- `results/data/narrowband_interference.csv` — 5 rows; columns: sir_db, target_detected, n_flagged, raw_soft_viterbi_ber, soft_erasure_viterbi_ber
- `results/data/otfs_high_doppler.csv` — 4 rows; columns: moving_path_doppler_bins, ofdm_one_tap_ber, otfs_full_lmmse_ber, ofdm_offdiagonal_energy_fraction, otfs_top2_energy_concentration
- `results/data/sampling_clock_offset.csv` — 7 rows; columns: true_ppm, estimated_ppm, raw_ber, pilot_affine_phase_ber, estimated_sco_resampling_ber, raw_evm_pct, pilot_affine_phase_evm_pct, resampling_evm_pct

## Validation commands

```bash
pip install -e .[dev]
pytest -q
python experiments/run_v06_suite.py
python tools/build_results_manifest.py
```
