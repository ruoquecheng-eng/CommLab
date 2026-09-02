# Experiment Artifact Catalog — v3.2

CSV datasets: **196**  
Figures: **343**  
Verified result artifacts: **539**

## Predictive-resilience main line

- `results/data/v32_chance_constrained_inference.csv` — 10 rows; columns: jitter_scale, policy, admission_rate, rejection_rate, admitted_deadline_miss_rate, overall_late_fraction, raw_utility_per_task, on_time_utility_per_task, mean_admitted_latency_ms, p95_admitted_latency_ms
- `results/data/v32_control_uep.csv` — 16 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, safety_violation_rate, critical_component_miss_rate, repetitions_per_slot
- `results/data/v32_failure_domain_zone_risk.csv` — 18 rows; columns: zone_failure_probability, policy, task_weighted_outage_rate, raw_outage_rate, failure_domains_per_model, replication_factor, mean_latency_ms, p95_latency_ms
- `results/data/v32_multi_connectivity.csv` — 18 rows; columns: link_correlation, policy, packet_outage_rate, packet_delivery_rate, transmissions_per_packet, duplication_rate, mean_success_latency_ms, p95_success_latency_ms
- `results/data/v32_multi_connectivity_frontier.csv` — 21 rows; columns: link_correlation, duplication_threshold, packet_outage_rate, transmissions_per_packet, duplication_rate, p95_success_latency_ms
- `results/data/v32_multiconnectivity_safety_control.csv` — 18 rows; columns: link_correlation, policy, mean_control_cost, p95_control_cost, safety_violation_rate, update_success_rate, transmissions_per_slot, duplication_rate
- `results/data/v32_predictive_failure_migration.csv` — 18 rows; columns: forecast_noise, policy, mean_latency_ms, p95_latency_ms, deadline_miss_rate, failure_event_rate, migration_rate, proactive_migration_rate, migration_traffic_mb_per_step

## Preserved earlier v3.2 datasets

- `results/data/v32_failure_domain_replication.csv` — 15 rows; columns: storage_budget_mb, policy, task_weighted_outage_rate, raw_outage_rate, failure_domains_per_model, replication_factor, mean_latency_ms
- `results/data/v32_mixed_control_inference.csv` — 20 rows; columns: arrival_prob, policy, mean_control_cost, p95_control_cost, safety_violation_rate, inference_completion_rate, inference_deadline_miss_rate, inference_utility_per_slot, control_slot_fraction
- `results/data/v32_safety_bit_allocation.csv` — 21 rows; columns: mean_snr_db, policy, mean_control_cost, p95_control_cost, safety_violation_rate, payload_bits_per_slot, component_deliveries_per_slot
- `results/data/v32_semantic_harq.csv` — 18 rows; columns: snr_db, policy, accuracy, hard_sample_accuracy, p90_batch_error, mean_channel_uses, retransmission_rate
- `results/data/v32_service_migration.csv` — 15 rows; columns: mobility, policy, mean_latency_ms, p95_latency_ms, deadline_miss_rate, traffic_mb_per_step, cold_migration_rate, speculative_mispredict_rate

## Reproduction and validation

```bash
python -m pip install -e . --no-build-isolation
python tools/run_v32_suite.py
pytest -q
python -m compileall -q src app experiments tools
python tools/build_manifest_v32.py
python tools/verify_release_v32.py
```
