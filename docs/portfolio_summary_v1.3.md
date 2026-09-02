# CommLab v1.3 — Portfolio Summary

## One-line positioning
A modular Python wireless-systems laboratory spanning OFDM receivers, MIMO/FEC/HARQ, RF/DPD, high mobility/OTFS, multiuser scheduling, RIS/Cell-Free architectures, and communication-centric sensing/beam tracking.

## Best v1.3 case studies

### 1. Cell-Free user-centric clustering
**Question:** How much cell-edge/fairness gain is obtained by letting each user cooperate with more distributed APs, and what coordination cost follows?

Representative result: nearest-AP 5%-tile user rate `0.345 bit/s/Hz`; UC-4 `0.936`; UC-8 `1.137`; all-AP `1.278`, while AP-user service links rise from `8` to `192`.

Best figures:
- `results/figures/cell_free_user_centric_rates.png`
- `results/figures/cell_free_fronthaul_tradeoff.png`

### 2. Cell-Free max-min power control
**Question:** Can the weakest users be protected after user-centric clustering without changing beam directions?

Representative result: UC-4 minimum-user rate `0.873 -> 1.286 bit/s/Hz`, at the cost of mean rate `2.126 -> 1.286`.

Best figure:
- `results/figures/cell_free_power_control_rates.png`

### 3. Multi-user RIS joint passive/digital optimization
**Question:** Does finite-bit RIS control still matter once multiple users and ZF precoding are coupled?

Representative result: random phase `1.84` mean 3-user sum rate; 1/2/3-bit coordinate optimization `4.52 / 5.10 / 5.32 bit/s/Hz`.

Best figures:
- `results/figures/ris_multiuser_coordinate_rate.png`
- `results/figures/ris_coordinate_convergence.png`

### 4. Predictive ISAC beam tracking
**Question:** When do sensing-based predictions improve communication beam alignment, and what happens when the motion model is wrong?

Representative result: reactive hold `2.996 bit/s/Hz`; mismatched constant-velocity prediction `2.489`; matched constant-acceleration prediction `3.981`, close to oracle `4.075`.

Best figures:
- `results/figures/isac_predictive_beam_trace.png`
- `results/figures/isac_predictive_beam_rate.png`

### 5. Uncertainty-aware beam aperture
**Question:** Should a base station always use the largest possible array aperture?

Representative result: optimal aperture moves `64 -> 32 -> 16 -> 8` elements as angle standard deviation grows from sub-degree to several degrees in the normalized array-gain model.

Best figures:
- `results/figures/isac_uncertainty_beamwidth_rate.png`
- `results/figures/isac_uncertainty_selected_aperture.png`

## Suggested CV bullet
Developed **CommLab**, a reproducible Python wireless-systems laboratory spanning OFDM/MIMO/FEC/HARQ, high-mobility ICI/OTFS, RF impairment/DPD, multiuser scheduling, RIS and Cell-Free abstractions, and OFDM-ISAC; implemented and quantitatively evaluated receiver, resource-allocation, distributed-beamforming, and predictive beam-management algorithms with automated tests and reproducible experiment artifacts.

## Claims to avoid
- Do not call the Cell-Free model a standards-compliant network simulator.
- Do not claim global optimality for RIS coordinate ascent.
- Do not call synthetic Kalman beam tracking a field-validated vehicular beam-management system.
- Do not imply the normalized rate numbers predict commercial 5G/6G throughput.
