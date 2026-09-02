# Experiment Artifact Catalog — v1.5

CSV datasets: **94**  
Figures: **160**

## New v1.5 datasets

- `results/data/cell_free_csi_aging.csv` — 12 rows; columns: mobility, correlation, update_interval, fronthaul_bits_per_slot, mean_rate, edge_rate
- `results/data/cell_free_fronthaul_csi.csv` — 15 rows; columns: aps_per_user, bits_per_component, mean_rate, edge_rate, csi_nmse, fronthaul_bits_per_update
- `results/data/cellfree_ris_robust_imperfect_csi.csv` — 15 rows; columns: channel_nmse, method, mean_sum_rate, p10_sum_rate
- `results/data/isac_sensing_resource_scheduling.csv` — 6 rows; columns: prior_std_deg, optimal_sensing_fraction, optimal_elements, posterior_std_deg, net_rate
- `results/data/isac_sensing_resource_surface.csv` — 216 rows; columns: prior_std_deg, sensing_fraction, elements, posterior_std_deg, raw_rate, net_rate
- `results/data/short_packet_fbl_cross_layer.csv` — 15 rows; columns: blocklength, scheme, goodput_bits_per_use, nack_rate, mean_mcs_index, mean_predicted_true_bler, final_olla_offset_db

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v15_suite.py
python tools/build_results_manifest_v15.py
python tools/verify_release_v15.py
```
