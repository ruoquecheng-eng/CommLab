# Experiment Artifact Catalog — v2.9

CSV datasets: **174**  
Figures: **299**

## New v2.9 datasets

- `results/data/v29_battery_carbon_fair_fl.csv` — 24 rows; columns: harvest_scale, policy, excess_loss, carbon_proxy, jain_fairness, min_participation, underfilled_round_fraction, energy_infeasible_fraction
- `results/data/v29_congested_model_refresh.csv` — 15 rows; columns: backhaul_service_mb_per_request, policy, task_utility, served_version_age, latency_ms, p95_queue_mb, refresh_requested_mb, refresh_delivered_mb
- `results/data/v29_networked_control.csv` — 20 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, estimation_rmse, mean_information_age, max_state_excursion, update_success_fraction, selection_jain
- `results/data/v29_task_aware_repair.csv` — 18 rows; columns: burst_strength, policy, task_utility_ratio, active_task_model_age, static_weighted_age, downlink_size_per_round
- `results/data/v29_twin_guided_prefetch.csv` — 18 rows; columns: twin_noise_std, policy, latency_ms, cache_hit_rate, backhaul_mb, wrong_prefetch_fraction, prefetch_attempts

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v29_suite.py
python tools/build_results_manifest_v29.py
python tools/verify_release_v29.py
```
