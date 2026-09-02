# Experiment Artifact Catalog — v1.4

CSV datasets: **88**  
Figures: **148**

## New v1.4 datasets

- `results/data/cell_free_ap_activation_energy.csv` — 12 rows; columns: active_aps, scheme, mean_user_rate, mean_5pct_rate, energy_efficiency
- `results/data/cell_free_pilot_contamination.csv` — 8 rows; columns: pilots, scheme, contamination_cost, channel_nmse, mean_user_rate, mean_5pct_rate
- `results/data/cellfree_ris_joint.csv` — 4 rows; columns: scheme, mean_sum_rate, mean_min_user_rate, mean_user_rate
- `results/data/cross_layer_olla_harq_queue.csv` — 4 rows; columns: scheme, goodput_kbit_per_slot, nack_rate, p95_delay_slots, mean_delay_slots, dropped_packets, pending_packets, delivery_fraction
- `results/data/isac_joint_beamforming_pareto.csv` — 164 rows; columns: sensing_angle_deg, weight_comm, rate, sensing_gain

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v14_suite.py
python tools/build_results_manifest_v14.py
python tools/verify_release_v14.py
```
