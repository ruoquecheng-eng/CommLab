# Experiment Artifact Catalog — v1.1

CSV datasets: **69**  
Figures: **119**

## New v1.1 datasets

- `results/data/harq_circular_redundancy_versions.csv` — 8 rows; columns: snr_db, scheme, success, avg_tx_bits, avg_rounds, goodput
- `results/data/hybrid_beamforming.csv` — 5 rows; columns: rf_chains, hybrid_mean_rate, full_digital_mean_rate, mean_rate_ratio, hybrid_p10_rate
- `results/data/isac_music_angle.csv` — 2 rows; columns: method, estimated_angle_1, estimated_angle_2, sum_abs_error_deg
- `results/data/isac_range_tracking.csv` — 220 rows; columns: time_s, true_range_m, measurement_m, tracked_range_m, tracked_velocity_mps
- `results/data/isac_range_tracking_summary.csv` — 1 rows; columns: raw_measurement_rmse_m, tracked_rmse_m, miss_fraction
- `results/data/massive_mimo_pilot_contamination.csv` — 5 rows; columns: n_antennas, orthogonal_like_median_sir_db, reused_pilot_median_sir_db, reused_pilot_p10_sir_db
- `results/data/massive_mimo_precoding.csv` — 5 rows; columns: n_tx, mrt_sum_rate, zf_sum_rate, mrt_jain, zf_jain, mean_interuser_corr, channel_hardening_cv
- `results/data/mimo_mmse_sic.csv` — 5 rows; columns: snr_db, zf_ber, mmse_ber, ordered_mmse_sic_ber, kbest4_ber
- `results/data/ofdm_isac_angle.csv` — 3 rows; columns: n_rx, estimated_angle_1_deg, estimated_angle_2_deg, sum_abs_angle_error_deg
- `results/data/otfs_fractional_delay_refinement.csv` — 5 rows; columns: pilot_snr_db, coarse_delay_error, coarse_doppler_error, refined_delay_mae, refined_doppler_mae, relative_residual

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v11_suite.py
python tools/build_results_manifest_v11.py
python tools/verify_release_v11.py
```
