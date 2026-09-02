# CommLab v1.2 — Portfolio Summary

## Positioning
**CommLab — Wireless Communication Systems Laboratory** is a from-scratch Python platform for reproducible link-, array-, RF-, sensing-, and system-level wireless experiments. v1.2 deliberately expands beyond receiver algorithms into controllable propagation, scheduler-side spatial compatibility, source-count-aware sensing, multi-target data association, and RF-chain-constrained sparse precoding.

## Strong v1.2 additions
1. **RIS phase-control study** — continuous versus 1/2/3-bit phase quantization across 4–128 reflecting elements.
2. **Semi-orthogonal MU-MIMO user selection** — channel-strength versus spatial-compatibility trade-off before ZF precoding.
3. **MDL + MUSIC model order** — source-count estimation reliability versus SNR/snapshots instead of genie source count.
4. **Multi-target Kalman tracking** — range/velocity tracking with missed detections, sparse clutter, and explicit fragmentation limitations.
5. **OMP hybrid beamforming** — sparse analog-beam selection approximating the full-digital singular subspace under RF-chain constraints.

## Recommended v1.2 figures
- `results/figures/ris_phase_quantization_rate.png`
- `results/figures/mu_mimo_user_selection_rate.png`
- `results/figures/mu_mimo_user_selection_condition.png`
- `results/figures/music_mdl_source_count_accuracy.png`
- `results/figures/music_mdl_close_angle_spectrum.png`
- `results/figures/isac_multitarget_kalman_tracking.png`
- `results/figures/hybrid_omp_precoding_rate.png`

## Best compact story for applications
A useful v1.2 narrative is not “I implemented many algorithms.” It is:

> I built a reproducible wireless-systems laboratory and used it to study design trade-offs at several layers: finite-resolution RIS phase control, spatially compatible MU-MIMO scheduling, source-count-aware subspace sensing, missed-detection/clutter tracking, and sparse hybrid precoding under RF-chain limits. Each branch includes quantitative Monte Carlo evaluation, failure cases, and automated regression tests.

## CV bullet
> Developed CommLab, a modular Python wireless-systems laboratory spanning OFDM/OTFS, coded MIMO/HARQ, RF impairments/DPD, multiuser precoding/scheduling, RIS-assisted links, and OFDM-ISAC; evaluated finite-resolution RIS control, semi-orthogonal MU-MIMO user selection, MDL/MUSIC source-count estimation, multi-target Kalman tracking, and OMP hybrid precoding with reproducible Monte Carlo experiments and automated tests.

## Claims to avoid
Do not describe the RIS model as measured/3GPP-calibrated; SUS as a production scheduler; MDL/MUSIC as robust to arbitrary colored noise/coherent sources; the tracker as JPDA/MHT; or the OMP hybrid branch as a measured mmWave RF front end.
