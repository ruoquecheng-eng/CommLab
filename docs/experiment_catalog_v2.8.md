# Experiment Artifact Catalog — v2.8

CSV datasets: **169**  
Figures: **289**

## New v2.8 datasets

- `results/data/v28_digital_twin_sync.csv` — 18 rows; columns: policy, control_parameter, position_rmse, p95_position_error, mean_aoii, normalized_radio_load_per_slot, update_attempt_fraction, update_success_fraction
- `results/data/v28_fair_carbon_pareto.csv` — 6 rows; columns: debt_weight, excess_loss, total_carbon_proxy, participation_jain, minimum_participation_rate
- `results/data/v28_fair_carbon_policies.csv` — 4 rows; columns: policy, excess_loss, total_carbon_proxy, participation_jain, minimum_participation_rate, participation_shortfall_fraction, final_max_virtual_debt
- `results/data/v28_selective_downlink_repair.csv` — 24 rows; columns: mean_snr_db, policy, weighted_version_age, weighted_model_mse, weighted_fresh_coverage, normalized_downlink_size_per_round, repair_transmissions, keyframes
- `results/data/v28_split_admission.csv` — 18 rows; columns: arrival_rate, policy, on_time_task_utility, on_time_accuracy, deadline_miss_rate, radio_uses_per_request, admission_fraction, mean_backlog
- `results/data/v28_versioned_caching_budget.csv` — 6 rows; columns: refresh_budget_mb_per_epoch, cache_hit_rate, mean_latency_ms, mean_task_utility, mean_served_version_age, backhaul_mb
- `results/data/v28_versioned_caching_policies.csv` — 4 rows; columns: policy, cache_hit_rate, mean_latency_ms, mean_task_utility, mean_served_version_age, backhaul_mb, model_refresh_mb

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v28_suite.py
python tools/build_results_manifest_v28.py
python tools/verify_release_v28.py
```
