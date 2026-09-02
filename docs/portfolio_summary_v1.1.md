# CommLab v1.1 — Portfolio Summary

## Positioning
**CommLab — Wireless Communication Systems Laboratory** is a from-scratch Python simulation platform spanning waveform/receiver design, MIMO, coding/HARQ, RF impairments, high mobility/OTFS, system scheduling, information theory, and communication-centric sensing.

## Strong v1.1 additions
1. **Ordered MMSE-SIC MIMO** — demonstrates cancellation/order trade-offs between linear MMSE and K-best.
2. **Massive/MU-MIMO scaling** — MRT/ZF, favorable propagation, channel hardening, and pilot contamination.
3. **Sparse-mmWave hybrid beamforming** — RF-chain constraint versus full-digital spectral efficiency.
4. **OFDM-ISAC angle sensing** — receive-array Bartlett processing on top of range-Doppler sensing.
5. **MUSIC close-angle DOA** — multi-snapshot subspace processing versus Bartlett resolution.
6. **Multi-frame target tracking** — noise/missed-detection robustness with a simple alpha-beta tracker.
7. **Joint fractional OTFS refinement** — local delay/Doppler grid-mismatch correction.
8. **Circular-RV HARQ** — transparent redundancy-version soft combining.

## Recommended new figures
- `results/figures/massive_mimo_sum_rate.png`
- `results/figures/massive_mimo_hardening.png`
- `results/figures/massive_mimo_pilot_contamination.png`
- `results/figures/mimo_mmse_sic_ber.png`
- `results/figures/hybrid_beamforming_rate.png`
- `results/figures/ofdm_isac_angle_resolution.png`
- `results/figures/isac_music_superresolution.png`
- `results/figures/isac_range_tracking.png`
- `results/figures/otfs_fractional_delay_refinement.png`

## CV bullet
> Built CommLab, a modular Python wireless-systems laboratory implementing OFDM/OTFS, synchronization and channel estimation, soft-output/coded MIMO, HARQ/FEC, RF impairments/DPD, multiuser precoding/scheduling, and OFDM-based sensing; added massive-MIMO MRT/ZF and pilot-contamination studies plus range-Doppler-angle array processing and multi-frame tracking, with reproducible Monte Carlo experiments and automated tests.

## Claims to avoid
Do not call the current platform standards-compliant 5G/802.11, a calibrated radar, an over-the-air SDR system, or a production massive-MIMO implementation. The array, contamination, HARQ RV, and fractional OTFS models are transparent educational/research baselines.
