# Experiment Artifact Catalog — v3.0

CSV datasets: **179**  
Figures: **309**

## New v3.0 datasets

- `results/data/v30_cooperative_control.csv` — 15 rows; columns: mean_snr_db, policy, mean_system_cost, p95_system_cost, mean_formation_error, mean_information_age
- `results/data/v30_failure_aware_edge.csv` — 15 rows; columns: load, policy, mean_latency_ms, p95_latency_ms, failure_rate, deadline_miss_rate, energy_proxy_per_task
- `results/data/v30_joint_cache_offload.csv` — 12 rows; columns: cache_capacity_mb, policy, mean_latency_ms, p95_latency_ms, cache_hit_rate, backhaul_mb_per_request, offload_jain
- `results/data/v30_risk_sensitive_control.csv` — 12 rows; columns: shock_multiplier, policy, mean_control_cost, p95_control_cost, cvar95_control_cost, mean_information_age
- `results/data/v30_variable_rate_control.csv` — 15 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, payload_bits_per_slot, update_success_rate

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v30_suite.py
python tools/build_results_manifest_v30.py
python tools/verify_release_v30.py
```
