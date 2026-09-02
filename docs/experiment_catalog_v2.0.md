# Experiment Artifact Catalog — v2.0

CSV datasets: **122**  
Figures: **213**

## New v2.0 datasets

- `results/data/v20_capture_irsa.csv` — 33 rows; columns: power_spread_db, offered_load, throughput, packet_loss_rate, sic_iterations
- `results/data/v20_cellfree_aircomp.csv` — 5 rows; columns: n_aps, single_ap_median_mse, cellfree_median_mse, single_ap_weakest_gain, cellfree_weakest_gain
- `results/data/v20_federated_aircomp_convergence.csv` — 81 rows; columns: round, ideal_loss, orthogonal_loss, full_inversion_loss, truncated_loss
- `results/data/v20_federated_aircomp_threshold.csv` — 10 rows; columns: threshold, final_loss, parameter_error, active_fraction, aggregation_mse
- `results/data/v20_ris_aircomp_learning.csv` — 3 rows; columns: ris_objective, weakest_gain, sum_channel_power, aircomp_median_mse, fl_final_loss, fl_parameter_error
- `results/data/v20_task_oriented_semcom.csv` — 6 rows; columns: snr_db, raw_accuracy, task_accuracy, raw_reconstruction_mse, task_reconstruction_mse, raw_channel_uses, task_channel_uses

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v20_suite.py
python tools/build_results_manifest_v20.py
python tools/verify_release_v20.py
```
