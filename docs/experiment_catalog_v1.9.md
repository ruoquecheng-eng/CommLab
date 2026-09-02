# Experiment Artifact Catalog — v1.9

CSV datasets: **116**  
Figures: **202**

## New v1.9 datasets

- `results/data/aircomp_aggregation.csv` — 6 rows; columns: snr_db, orthogonal_mean_mse, full_mean_mse, truncated_mean_mse, orthogonal_median_mse, full_median_mse, truncated_median_mse, full_p90_mse, active_fraction
- `results/data/aircomp_threshold_tradeoff.csv` — 9 rows; columns: threshold, truncated_mse, active_fraction
- `results/data/embb_urllc_slicing.csv` — 27 rows; columns: arrival_rate, policy, embb_throughput, urllc_deadline_miss, wasted_reserved, mean_urllc_delay
- `results/data/energy_harvesting_aoi.csv` — 32 rows; columns: harvest_scale, policy, mean_aoi, p95_aoi, delivery_rate, energy_outage
- `results/data/irsa_coded_random_access.csv` — 36 rows; columns: offered_load, scheme, throughput, packet_loss_rate, replicas_per_decoded, mean_iterations

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v19_suite.py
python tools/build_results_manifest_v19.py
python tools/verify_release_v19.py
```
