# Experiment Artifact Catalog — v1.2

CSV datasets: **76**  
Figures: **127**

## New v1.2 datasets

- `results/data/hybrid_omp_precoding.csv` — 5 rows; columns: rf_chains, full_digital, dft_one_shot, omp_hybrid, omp_fraction_of_full
- `results/data/isac_multitarget_kalman_summary.csv` — 1 rows; columns: raw_measurement_range_rmse, tracker_range_rmse, mean_target_coverage, target0_track_fragments, target1_track_fragments, final_confirmed_tracks, frames
- `results/data/isac_multitarget_kalman_tracks.csv` — 480 rows; columns: frame, target, true_range, estimated_range, estimated_velocity, track_id
- `results/data/mu_mimo_user_selection.csv` — 3 rows; columns: scheme, mean_sum_rate, p10_sum_rate, median_gram_condition, mean_user_correlation
- `results/data/music_mdl_close_angle_spectrum.csv` — 1201 rows; columns: angle_deg, bartlett, music
- `results/data/music_mdl_model_order.csv` — 20 rows; columns: snapshots, snr_db, accuracy, mean_estimated_sources
- `results/data/ris_phase_quantization.csv` — 30 rows; columns: elements, scheme, mean_rate, mean_power_gain

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v12_suite.py
python tools/build_results_manifest_v12.py
python tools/verify_release_v12.py
```
