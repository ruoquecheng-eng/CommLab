# CommLab v1.5 — Portfolio Summary

## Positioning
**CommLab — Wireless Communication Systems Laboratory** is a modular Python platform for reproducible PHY/link/system experiments spanning OFDM, MIMO, FEC/HARQ, RF impairments, high mobility/OTFS, distributed Cell-Free networks, RIS, ISAC, scheduling, and information-theoretic abstractions.

## Strongest new v1.5 stories

### 1. Cell-Free CSI fidelity versus fronthaul
I modeled quantized distributed CSI together with user-centric AP clustering. The same true channel is evaluated under 2/3/4/6/8-bit complex-CSI quantization so performance differences are not Monte-Carlo sampling artifacts. A representative UC-8 point reaches roughly **1.49 bit/s/Hz 5%-tile rate at 4-bit/component and 512 bits/update**, while 6-bit improves to about **1.57 at 768 bits/update**.

### 2. CSI aging and update-rate cost
A proper-complex Gauss-Markov channel evolves between fronthaul updates while the AP precoder remains frozen. Under correlation `rho=0.97`, extending the update interval from 1 to 32 slots reduces cell-edge rate about **1.82 -> 1.05 bit/s/Hz**, while modeled CSI traffic falls **768 -> 24 bits/slot**.

### 3. Robust Cell-Free RIS under imperfect CSI
Finite-bit RIS phases are optimized either on one noisy CSI estimate or over a small uncertainty ensemble. At CSI NMSE `0.20`, sample-average optimization improves held-out mean sum-rate about **4.02 -> 4.56 bit/s/Hz**. At low uncertainty it is not guaranteed to win, which is explicitly retained.

### 4. Finite-blocklength short-packet adaptation
The normal approximation is inverted into a packet-error model at fixed rate and blocklength. Under a +2.2 dB SNR bias, blocklength 120 open-loop selection gives about **39% NACK and 1.12 bit/use goodput**; FBL-aware selection gives **27% / 1.27**, while FBL+OLLA reaches roughly **1% NACK / 1.31 bit/use**.

### 5. ISAC sensing-time / beamwidth scheduling
A simple Bayesian precision-fusion model converts sensing overhead into posterior angle uncertainty, then the system searches over sensing fraction and 8/16/32/64 active ULA elements. With `0.5°` prior uncertainty, the optimum is **0% sensing, 64 elements**; around `4°` it shifts to **15% sensing, 32 elements**.

## Suggested CV bullet
> Developed CommLab, a reproducible Python wireless-systems laboratory spanning OFDM/MIMO, coding/HARQ, RF/DPD, Cell-Free/RIS, high-mobility/OTFS, ISAC and cross-layer scheduling; implemented 116 automated tests and 94 reproducible experiment datasets, including CSI-fronthaul/aging, robust RIS, finite-blocklength adaptation and sensing-resource trade-off studies.

## Best v1.5 figures for a portfolio page
- `cell_free_fronthaul_edge_rate.png`
- `cell_free_csi_aging_edge_rate.png`
- `cellfree_ris_robust_mean_rate.png`
- `short_packet_fbl_goodput.png`
- `isac_sensing_optimal_overhead.png`
- `isac_sensing_optimal_aperture.png`

## Scope boundaries
Do not claim standards compliance, measured fronthaul traffic, over-the-air validation, globally optimal robust RIS, or code-specific finite-blocklength accuracy. All fronthaul, channel aging, and sensing-resource models are transparent educational/research baselines.
