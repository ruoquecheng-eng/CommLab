# CommLab v0.8 — Portfolio Summary

## Positioning

**CommLab — Wireless Communication Systems Laboratory** is a modular Python link/system simulation project covering OFDM, MIMO, coding, synchronization, high mobility, RF nonlinearity, beamforming, and multiuser resource scheduling.

The strongest v0.8 story is no longer “I implemented many communication algorithms.” It is:

> I built reproducible experiments that expose how receiver complexity, channel conditioning, CSI overhead, nonlinear-model mismatch, adaptation, coding architecture, and multiuser fairness change quantitative system performance.

## Best v0.8 figures to show

1. `mimo_kbest_detection_ber.png` — MMSE -> K-best -> exhaustive-ML performance ladder.
2. `mimo_spatial_correlation_capacity.png` — correlation reduces capacity and worsens conditioning.
3. `limited_feedback_beamforming_rate.png` — CSI feedback bits versus beamforming rate.
4. `ici_cg_equalization_ber.png` — iterative banded ICI cancellation under high Doppler.
5. `adaptive_memory_dpd_tracking.png` — frozen versus adaptive DPD under coefficient drift.
6. `generalized_memory_dpd_evm.png` — standard MP versus cross-term GMP under model mismatch.
7. `fec_rate_half_benchmark.png` — convolutional, custom LDPC, and educational polar baseline.
8. `proportional_fair_fairness.png` plus `proportional_fair_sum_rate.png` — system-level scheduling trade-off.

## CV bullet options

- Built **CommLab**, a modular Python wireless-communications laboratory spanning OFDM/MIMO, channel estimation, synchronization, FEC, RF impairment/DPD modeling, high-Doppler ICI equalization, beamforming, and multiuser OFDMA scheduling, with 66 automated tests and reproducible experiment artifacts.
- Designed quantitative receiver/system studies including QR K-best MIMO detection, correlated-channel capacity analysis, limited-feedback beamforming, CG-based ICI equalization, adaptive/cross-memory DPD, polar/LDPC/Viterbi coding benchmarks, and proportional-fair scheduling.

## Do not overclaim

Do **not** describe the project as:

- a 5G NR or Wi-Fi implementation;
- a hardware SDR or RF measurement platform;
- a standards-compliant LDPC/polar/beamforming implementation;
- a production base-station scheduler;
- evidence that OTFS, polar, GMP, or any detector is universally superior.

The project's value is the transparent model assumptions, quantitative experiments, failure cases, and reproducibility.
