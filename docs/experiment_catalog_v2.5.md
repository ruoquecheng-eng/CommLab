# Experiment Artifact Catalog — v2.5

CSV datasets: **150**  
Figures: **259**

## New v2.5 datasets

- `results/data/v25_cluster_personalization.csv` — 15 rows; columns: cluster_separation, assignment_error, global_mse, cluster_mse, local_mse
- `results/data/v25_energy_split.csv` — 15 rows; columns: mean_snr_db, policy, accuracy, on_time_accuracy, mean_energy_mj, mean_latency_ms, offload_fraction
- `results/data/v25_model_multicast.csv` — 6 rows; columns: snr_std_db, common_time, layered_time, unicast_time, layered_mean_utility
- `results/data/v25_private_hardware_aircomp.csv` — 20 rows; columns: privacy_noise, adc_bits, median_mse, p90_mse, pa_clip_fraction
- `results/data/v25_private_hardware_pa.csv` — 7 rows; columns: pa_saturation, median_mse, p90_mse, pa_clip_fraction
- `results/data/v25_resilient_async.csv` — 15 rows; columns: byzantine_fraction, strategy, median_final_loss, mean_accept_fraction

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v25_suite.py
python tools/build_results_manifest_v25.py
python tools/verify_release_v25.py
```
