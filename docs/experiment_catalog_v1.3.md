# Experiment Artifact Catalog — v1.3

CSV datasets: **83**  
Figures: **136**

## New v1.3 datasets

- `results/data/cell_free_power_control.csv` — 3 rows; columns: scheme, mean_rate, mean_5pct, mean_min_rate, mean_jain
- `results/data/cell_free_user_centric.csv` — 4 rows; columns: scheme, mean_user_rate, mean_5pct_user_rate, mean_jain, mean_ap_user_links
- `results/data/isac_predictive_beam_trace.csv` — 360 rows; columns: time_s, true_angle_deg, measurement_deg, reactive_beam_deg, cv_beam_deg, ca_beam_deg
- `results/data/isac_predictive_beam_tracking.csv` — 4 rows; columns: scheme, mean_rate, p10_rate, angle_mae_deg, outage_prob
- `results/data/isac_uncertainty_aware_beamwidth.csv` — 36 rows; columns: angle_std_deg, elements, expected_rate, selected
- `results/data/ris_coordinate_convergence.csv` — 630 rows; columns: trial, bits, iteration, sum_rate
- `results/data/ris_multiuser_coordinate.csv` — 4 rows; columns: scheme, mean_sum_rate, p10_sum_rate

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v13_suite.py
python tools/build_results_manifest_v13.py
python tools/verify_release_v13.py
```
