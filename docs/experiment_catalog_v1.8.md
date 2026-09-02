# Experiment Artifact Catalog — v1.8

CSV datasets: **111**  
Figures: **194**

## New v1.8 datasets

- `results/data/aoi_status_updates.csv` — 18 rows; columns: rate_bit_per_use, retransmission, policy, mean_aoi, p95_aoi, mean_peak_aoi, delivery_rate_per_slot, min_user_deliveries, max_user_deliveries
- `results/data/budget_constrained_isac.csv` — 4 rows; columns: budget, used_sensing_fraction, mean_posterior_std_deg, mean_payload_rate, phase_1_sensing, phase_2_sensing, phase_3_sensing, phase_4_sensing, phase_5_sensing
- `results/data/deadline_harq_scheduling.csv` — 12 rows; columns: arrival_probability, policy, arrivals, goodput, deadline_miss_rate, nack_rate, mean_delay, p95_delay, deadline_drops, maxround_drops
- `results/data/event_triggered_ris.csv` — 6 rows; columns: scheme, mean_sum_rate, edge_rate, ideal_mean_sum_rate, updates, control_bits_per_slot, mean_update_interval
- `results/data/grant_free_noma_random_access.csv` — 40 rows; columns: power_spread_db, activity_probability, mode, offered_load_per_resource, throughput_packets_per_slot, throughput_packets_per_resource, success_probability, mean_decoded_per_slot, collision_resource_fraction, attempts, decoded_packets
- `results/data/joint_csi_fronthaul_control.csv` — 36 rows; columns: correlation, budget_bits_per_slot, policy, mean_csi_nmse, edge_rate, mean_sum_rate, used_bits_per_slot, p95_ap_age

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v18_suite.py
python tools/build_results_manifest_v18.py
python tools/verify_release_v18.py
```
