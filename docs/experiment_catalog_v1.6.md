# Experiment Artifact Catalog — v1.6

CSV datasets: **100**  
Figures: **172**

## New v1.6 datasets

- `results/data/cellfree_fronthaul_energy_joint.csv` — 66 rows; columns: sweep, rho, active_aps, bits, update_interval, mean_user_rate, edge_rate, mean_sum_rate, fronthaul_power_w, total_power_w, energy_efficiency
- `results/data/cellfree_ris_aged_quantized_csi.csv` — 20 rows; columns: delay_steps, effective_correlation, method, mean_sum_rate, p10_sum_rate, samples
- `results/data/cellfree_ris_csi_quantization_sweep.csv` — 10 rows; columns: csi_bits, method, mean_sum_rate, p10_sum_rate
- `results/data/fbl_harq_queue_coupled.csv` — 16 rows; columns: blocklength, scheme, goodput_bits_per_use, nack_rate, p95_delay_slots, drops, mean_attempts
- `results/data/isac_predictive_sensing_summary.csv` — 4 rows; columns: scheme, mean_net_rate, mean_sensing_fraction, mean_posterior_std_deg
- `results/data/isac_predictive_sensing_trace.csv` — 960 rows; columns: scheme, slot, prior_std_deg, sensing_fraction, elements, posterior_std_deg, raw_rate, net_rate, score

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v16_suite.py
python tools/build_results_manifest_v16.py
python tools/verify_release_v16.py
```

The v1.6 suite may exceed restrictive single-command sandbox timeouts; each constituent script is independently deterministic and can be run separately.
