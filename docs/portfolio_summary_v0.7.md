# CommLab-OFDM v0.7 — Portfolio Summary

## One-line project description

**CommLab-OFDM is a modular Python wireless-communication laboratory for OFDM/MIMO receiver design, channel estimation, FEC, RF impairments/DPD, high-Doppler ICI, OTFS prototypes, and reproducible link-level evaluation.**

## Strongest evidence to show

### 1. High-Doppler ICI-aware receiver
Use `results/figures/ici_aware_equalization_ber.png` and `ici_energy_vs_doppler.png`.

Key point: at 1.5 normalized Doppler, ~23.6% of effective OFDM channel energy is off-diagonal. One-tap BER ~4.21e-2 falls to ~1.20e-3 with only a +/-2 coupling band.

This is probably the strongest v0.7 receiver-design story because it starts from a failure mechanism, builds an explicit matrix model, and quantifies the complexity/performance trade-off.

### 2. Lower-overhead MIMO pilot design
Use `mimo_pilot_efficiency_nmse.png`.

Key point: replace two full training symbols (104 pilot RE) with one frequency-orthogonal symbol (52 pilot RE) and reconstruct each link through a finite-CIR LS model. At 12 dB, NMSE improves from ~0.144 to ~0.0508 in the current sparse-channel family.

### 3. Memory PA / DPD
Use `memory_polynomial_dpd_evm.png` and `memory_polynomial_dpd_guard.png`.

At 8 dB back-off, EVM improves ~10.77% -> ~0.85% and guard leakage ~-29.9 -> ~-44.2 dB. Also mention that the learned inverse becomes unstable at very aggressive drive; this is an important limitation, not a result to hide.

### 4. MIMO detector hierarchy
Use `mimo_ml_detection_ber.png`.

At 12 dB, 2x2 QPSK BER is approximately:
- ZF: 3.00e-2
- MMSE: 2.02e-2
- exhaustive ML: 4.29e-3

Use this to discuss optimality versus exponential complexity.

### 5. Sparse OTFS iterative detector
Use `otfs_sparse_cg_ber.png` and `otfs_sparse_cg_complexity.png`.

Five coefficients per row retain ~99.1% channel energy and reach ~4.96e-5 BER at 14 dB, while two coefficients retain ~92.2% and give ~5.51e-3. This shows sparsity/performance/iteration trade-offs.

### 6. Statistically defensible BER
Use `ber_confidence_intervals.png`.

At 10 dB Eb/N0, 10 errors in 4 million bits give 2.5e-6 BER with 95% Wilson CI approximately [1.36e-6, 4.60e-6], close to QPSK theory 3.87e-6.

## Suggested CV bullets

- **Developed CommLab-OFDM**, a modular Python link-level wireless laboratory covering QAM/OFDM, synchronization, channel estimation, MIMO, FEC, RF impairments, digital predistortion, and high-mobility channels, with **54 automated tests** and reproducible experiment exports.
- Built an **ICI-aware high-Doppler OFDM receiver** using explicit frequency-domain coupling matrices and banded/full LMMSE detection, reducing BER from ~4.2e-2 to ~1.2e-3 with a narrow +/-2 coupling model in a controlled Doppler experiment.
- Designed a **one-symbol frequency-orthogonal 2x2 MIMO training scheme** with finite-CIR LS reconstruction, halving pilot resource elements versus the earlier two-slot baseline while improving channel NMSE in the simulated sparse multipath family.
- Implemented **memory-polynomial PA identification and indirect-learning DPD**, plus ZF/MMSE/ML MIMO detection, sparse CG-LMMSE OTFS detection, and confidence-aware BER Monte Carlo analysis.

## Claims to avoid

Do not claim:
- IEEE 802.11 / 5G NR compliance;
- over-the-air SDR validation;
- measured RF hardware DPD;
- a production online ICI estimator;
- standard-compliant MIMO pilots;
- scalable ML detection;
- a fair standards-level OFDM-vs-OTFS benchmark.

The portfolio is strongest when it shows **model -> failure mechanism -> receiver/algorithm -> controlled experiment -> quantitative limitation**.

### 7. Frequency-selective IQ compensation
Use `frequency_selective_iq_ber.png` and `frequency_selective_iq_evm.png`.

At 26 dB, raw 64-QAM BER is ~2.55e-2, a frequency-flat IQ model leaves ~1.03e-3, and the learned direct/image FIR + mirror-pair inverse has 0 observed errors in the current run. This is useful because it demonstrates an explicit progression from an earlier simplified model to a more realistic frequency-dependent one.
