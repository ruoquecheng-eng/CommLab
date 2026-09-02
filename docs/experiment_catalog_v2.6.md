# Experiment Artifact Catalog — v2.6

CSV datasets: **155**  
Figures: **269**

## New v2.6 datasets

- `results/data/v26_aircomp_selection.csv` — 16 rows; columns: channel_disparity_db, strategy, final_global_loss, analog_mse_selected, selection_bias_mse, plus_selection_fraction, participation_jain, weakest_gain
- `results/data/v26_downlink_differential.csv` — 18 rows; columns: keyframe_interval, scheme, mean_model_mse, mean_version_age, normalized_size_per_round, packet_success_fraction
- `results/data/v26_eh_aircomp_fl.csv` — 18 rows; columns: harvest_scale, policy, final_global_loss, participation_jain, outage_slot_fraction, plus_selection_fraction, weakest_gain
- `results/data/v26_importance_multicast.csv` — 4 rows; columns: importance_anticorrelation, empirical_importance_snr_corr, snr_half_weighted_utility, importance_weighted_utility, snr_half_time, importance_time, importance_enhanced_fraction
- `results/data/v26_progressive_split.csv` — 20 rows; columns: mean_snr_db, policy, accuracy, on_time_accuracy, mean_channel_uses, mean_latency_ms, deadline_miss_rate, mean_energy_mj

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v26_suite.py
python tools/build_results_manifest_v26.py
python tools/verify_release_v26.py
```
