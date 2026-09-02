# Experiment Artifact Catalog — v1.7

CSV datasets: **105**  
Figures: **182**

## New v1.7 datasets

- `results/data/async_cellfree_csi.csv` — 12 rows; columns: updates_per_slot, policy, mean_sum_rate, edge_rate, mean_csi_nmse, mean_ap_age, p95_ap_age
- `results/data/fbl_ir_harq.csv` — 10 rows; columns: snr_db, mode, goodput, nack_rate, drops, mean_delay, p95_delay, mean_rounds
- `results/data/predictive_csi_quantization.csv` — 16 rows; columns: correlation, bits, absolute_nmse, predictive_nmse, nmse_gain_db, innovation_power
- `results/data/queue_aware_isac.csv` — 6 rows; columns: arrival_mean_bits, controller, delivered_bits, mean_sensing, mean_posterior_std_deg, mean_backlog_bits, final_backlog_bits
- `results/data/two_timescale_ris.csv` — 16 rows; columns: update_interval, scheme, mean_sum_rate, edge_rate, control_bits_per_slot

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v17_suite.py
python tools/build_results_manifest_v17.py
python tools/verify_release_v17.py
```
