# Experiment Artifact Catalog — v2.7

CSV datasets: **162**  
Figures: **279**

## New v2.7 datasets

- `results/data/v27_adaptive_downlink.csv` — 12 rows; columns: blockage_db, policy, mean_version_age, mean_model_mse, normalized_size_per_round, mean_keyframes, packet_success_fraction
- `results/data/v27_carbon_pareto.csv` — 7 rows; columns: carbon_weight, excess_loss, total_carbon_proxy, participation_jain
- `results/data/v27_carbon_policies.csv` — 4 rows; columns: policy, excess_loss, total_carbon_proxy, participation_jain, p95_round_latency_ms
- `results/data/v27_edge_caching_interval.csv` — 6 rows; columns: recache_interval, mean_latency_ms, cache_hit_rate, backhaul_mb, cache_updates
- `results/data/v27_edge_caching_policies.csv` — 4 rows; columns: policy, mean_latency_ms, p95_latency_ms, cache_hit_rate, backhaul_mb, cache_updates
- `results/data/v27_multicast_repair.csv` — 15 rows; columns: importance_snr_anticorrelation, policy, weighted_task_utility, model_coverage, time_ratio_to_full, repaired_fraction
- `results/data/v27_queued_split.csv` — 30 rows; columns: arrival_rate, policy, on_time_accuracy, on_time_task_utility, deadline_miss_rate, radio_uses_per_request, mean_backlog

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v27_suite.py
python tools/build_results_manifest_v27.py
python tools/verify_release_v27.py
```
