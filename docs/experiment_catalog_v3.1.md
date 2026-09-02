# Experiment Artifact Catalog — v3.1

CSV datasets: **184**  
Figures: **319**

## New v3.1 datasets

- `results/data/v31_adaptive_depth.csv` — 21 rows; columns: mean_snr_db, policy, on_time_accuracy, deadline_miss_rate, mean_feature_bits, mean_model_depth, mean_latency_ms
- `results/data/v31_component_control.csv` — 21 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, mean_payload_bits_per_slot, update_success_rate
- `results/data/v31_failure_recovery.csv` — 18 rows; columns: failure_probability, policy, mean_latency_ms, p95_latency_ms, deadline_miss_rate, recovery_traffic_mb_per_task, compute_load_ratio
- `results/data/v31_model_replication.csv` — 12 rows; columns: storage_budget_mb, policy, model_outage_rate, task_weighted_outage_rate, task_weighted_utility, storage_used_mb, mean_replication_factor
- `results/data/v31_safety_control.csv` — 15 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, safety_violation_rate, mean_information_age

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v31_suite.py
python tools/build_results_manifest_v31.py
python tools/verify_release_v31.py
```
