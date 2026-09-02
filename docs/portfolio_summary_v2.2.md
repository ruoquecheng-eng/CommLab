# CommLab v2.2 — Portfolio Summary

## Suggested project title

**CommLab — Wireless Systems and Edge Intelligence Simulation Laboratory**

## One-line description

A reproducible Python research simulator spanning OFDM/MIMO/RIS/ISAC, coding and scheduling, random access, over-the-air computation, federated learning, and task-oriented communication, with explicit experiments on when communication-layer optimization conflicts with learning, sensing, fairness, hardware, and control objectives.

## Strongest v2.2 evidence

- **Fixed communication-budget FL:** under the same 32-coordinate/round budget, an intermediate 3-4 client operating point with error feedback strongly outperforms both one-client dense updates and excessive per-client sparsification; residual-aware allocation further improves highly distributed participation.
- **AirComp hardware realism:** AGC materially reduces low-resolution ADC error; 6-8 bit conversion approaches the normalized analog/noise floor, while PA clipping creates a separate aggregation-distortion floor.
- **Progressive task communication:** at 60-degree task separation, confidence-triggered enhancement reaches about 88.9% mean accuracy with only 1.42 channel uses versus 90.3% with two always-on layers.
- **Importance-aware random access:** at moderate contention, differentiated repetition protects a larger fraction of total gradient importance; under severe overload it cannot avoid graph collapse.
- **Two-timescale RIS-AirComp-FL:** slow channel evolution permits a roughly 4x reduction in RIS control rate with negligible learning degradation, whereas faster mobility shortens the usable slow-control timescale.

## Recommended figures

1. `results/figures/v22_budgeted_fl_parameter_error.png`
2. `results/figures/v22_aircomp_adc_agc.png`
3. `results/figures/v22_layered_semantic_accuracy.png`
4. `results/figures/v22_importance_ra_gradient_mass.png`
5. `results/figures/v22_two_timescale_ris_fl_loss.png`

## CV-ready bullets

- Built a modular wireless-systems simulator with 160+ automated regression tests spanning PHY, MIMO, coding/HARQ, RIS, ISAC, random access, cross-layer scheduling, AirComp, and wireless edge intelligence.
- Developed fixed-budget federated-learning experiments that jointly expose client-participation diversity, top-k gradient compression, error feedback, and residual-aware communication allocation.
- Modeled analog AirComp under PA clipping, finite-resolution ADCs, and AGC to connect RF dynamic range directly to distributed-computation distortion.
- Designed a progressive task-oriented communication baseline that dynamically requests an enhancement layer based on task confidence, quantifying accuracy versus channel-use cost.
- Coupled time-varying finite-bit RIS control with AirComp-based federated optimization to study passive-control overhead versus learning robustness under mobility.

## Safe claims

- Reproducible educational/research simulation platform.
- Transparent algorithmic baselines with stated assumptions and negative results.
- Communication-learning/task co-design experiments.

## Claims to avoid

- Standards compliance with 5G/6G, IEEE 802.11, O-RAN, or commercial RIS/ISAC systems.
- Hardware validation or calibrated RF performance.
- State-of-the-art federated/semantic learning performance.
- Globally optimal robust/resource-allocation solutions unless formally established.
