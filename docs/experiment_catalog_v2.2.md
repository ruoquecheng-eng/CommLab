# Experiment Artifact Catalog — v2.2

CSV datasets: **134**  
Figures: **233**

## New v2.2 datasets

- `results/data/v22_aircomp_adc_agc.csv` — 10 rows; columns: adc_bits, agc, median_mse, p90_mse, adc_overload_fraction
- `results/data/v22_aircomp_pa_clipping.csv` — 6 rows; columns: pa_saturation, median_mse, p90_mse, clip_fraction
- `results/data/v22_budgeted_gradient_compression.csv` — 21 rows; columns: strategy, selected_clients, final_loss, parameter_error, nominal_equal_topk, coordinates_per_round, sd_final_loss, sd_parameter_error
- `results/data/v22_importance_random_access_fl.csv` — 14 rows; columns: frame_slots, mode, final_loss, decoded_fraction, decoded_gradient_mass, mean_repetition_degree, empty_round_fraction
- `results/data/v22_layered_semantic_angle.csv` — 6 rows; columns: task_angle_deg, base_accuracy, adaptive_accuracy, full_accuracy, adaptive_mean_uses, enhancement_fraction
- `results/data/v22_layered_semantic_threshold.csv` — 7 rows; columns: confidence_threshold, adaptive_accuracy, mean_uses, enhancement_fraction
- `results/data/v22_two_timescale_ris_fl.csv` — 15 rows; columns: rho, update_interval, median_final_loss, mean_final_loss, mean_weakest_gain, mean_p10_weakest_gain, control_bits_per_round

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v22_suite.py
python tools/build_results_manifest_v22.py
python tools/verify_release_v22.py
```
