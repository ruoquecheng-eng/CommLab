# Experiment Artifact Catalog — v2.1

CSV datasets: **127**  
Figures: **223**

## New v2.1 datasets

- `results/data/v21_cellfree_aircomp_imperfect_csi.csv` — 6 rows; columns: max_ap_csi_error, naive_median_mse, lcb_median_mse, naive_p90_mse, lcb_p90_mse, lcb_win_fraction
- `results/data/v21_multitask_semantic.csv` — 7 rows; columns: task_angle_deg, raw_mean_accuracy, task_specific_mean_accuracy, shared_rank1_mean_accuracy, shared_rank2_mean_accuracy, raw_uses, task_specific_uses, shared_rank1_uses, shared_rank2_uses
- `results/data/v21_non_iid_client_selection.csv` — 16 rows; columns: channel_disparity_db, strategy, final_loss, parameter_error, group_loss_gap, participation_jain, strong_group_selection_fraction, mean_selected_weakest_gain, sd_final_loss, sd_parameter_error, sd_group_loss_gap, sd_participation_jain, sd_strong_group_fraction, sd_weakest_gain
- `results/data/v21_random_access_federated.csv` — 19 rows; columns: frame_slots, access, decoded_fraction, empty_round_fraction, final_loss, channel_uses, loss_reduction_per_1000_uses
- `results/data/v21_robust_ris_aircomp.csv` — 6 rows; columns: relative_csi_error, naive_mean_weakest_gain, robust_mean_weakest_gain, naive_p10_weakest_gain, robust_p10_weakest_gain, robust_win_fraction

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v21_suite.py
python tools/build_results_manifest_v21.py
python tools/verify_release_v21.py
```
