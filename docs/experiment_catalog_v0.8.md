# Experiment Artifact Catalog — v0.8

CSV datasets: **45**  
Figures: **81**

## New v0.8 datasets

- `results/data/adaptive_memory_dpd.csv` — 18 rows; columns: block, drift_fraction, pa_only_evm_pct, static_dpd_evm_pct, adaptive_ewls_dpd_evm_pct
- `results/data/fec_rate_half_benchmark.csv` — 6 rows; columns: ebn0_db, conv_soft_ber, custom_ldpc_min_sum_ber, polar_sc_ber, ldpc_mean_iterations, ldpc_failed_blocks
- `results/data/generalized_memory_dpd.csv` — 5 rows; columns: backoff_db, pa_only_evm_pct, standard_memory_dpd_evm_pct, cross_term_gmp_dpd_evm_pct
- `results/data/ici_cg_equalization.csv` — 5 rows; columns: snr_db, ici_energy_fraction, one_tap_ber, cg_bw1_ber, cg_bw1_iterations, cg_bw1_relres, cg_bw1_nnz, cg_bw2_ber, cg_bw2_iterations, cg_bw2_relres, cg_bw2_nnz, cg_bw4_ber, cg_bw4_iterations, cg_bw4_relres, cg_bw4_nnz
- `results/data/limited_feedback_beamforming.csv` — 8 rows; columns: feedback_bits, codebook_size, mean_rate_bphz, p05_rate_bphz, loss_to_perfect_mrt
- `results/data/mimo_kbest_detection.csv` — 5 rows; columns: snr_db, zf_ber, mmse_ber, k1_ber, k4_ber, k16_ber, ml_ber, k1_nodes, k4_nodes, k16_nodes, ml_vectors
- `results/data/mimo_spatial_correlation.csv` — 6 rows; columns: rho, zf_ber, mmse_ber, mean_capacity_bphz, median_condition_number, p90_condition_number
- `results/data/proportional_fair_ofdma.csv` — 3 rows; columns: scheme, sum_rate, jain_fairness, user0, user1, user2, user3

## Validation

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python experiments/run_v08_suite.py
python tools/build_results_manifest_v08.py
```
