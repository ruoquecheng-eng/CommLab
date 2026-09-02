# CommLab v1.8 — Portfolio Summary

## Positioning

**CommLab — Wireless Communication Systems Laboratory** is a reproducible Python research platform spanning waveform/receiver design, coding/HARQ, MIMO/Cell-Free/RIS, RF impairments, high mobility/OTFS, cross-layer scheduling, sensing and random access. v1.8 focuses on a common systems question: **when resources are limited, what information/control action is actually worth spending them on?**

## Strongest v1.8 stories

### 1. Joint CSI refresh and precision allocation
Under one Cell-Free fronthaul bit budget, the controller jointly chooses which AP innovations to refresh and how many scalar bits to use. At correlation `.98` and `96 bit/slot`, mean CSI NMSE is about `0.0324`, versus `0.0749` for fixed-bit uncertainty scheduling and `0.0913` for round-robin. The branch also exposes a structural failure of fixed-bit refresh under very tight budgets: APs with many served links may not fit one nominal refresh at all.

### 2. Deadline-aware short-packet HARQ
Packets now have explicit expiry times. PF favors long-run service efficiency, EDF protects imminent deadlines, and a risk-aware score combines urgency with estimated next-round finite-blocklength success. At load `.16/user/slot`, PF misses about `5.73%` of deadlines, EDF `1.95%`, and risk-aware scheduling `2.56%`; risk has the highest goodput in the current trace.

### 3. Age of Information
A status-update simulator measures freshness rather than only throughput. Max-SNR produces almost one successful update transmission per slot but mean AoI around `139 slots` because the weakest users are rarely selected. At `1 bit/use`, fresh age×reliability scheduling gives mean AoI about `9.90`; Chase HARQ with max-age gives about `5.22`, showing that retransmission structure changes the best freshness policy.

### 4. Event-triggered RIS control
Instead of a fixed refresh clock, the RIS holds its phase profile until measured sum-rate falls by a configured fraction or a maximum control age is reached. On a trace with a fast-fading middle segment, a 3% trigger reaches about `3.811 bit/s/Hz` at `3.73 control bit/slot`, versus fixed-4 refresh at `3.751` and `4 bit/slot`.

### 5. Budgeted ISAC sensing
A cumulative token budget enforces a long-run sensing ceiling while the controller chooses sensing fraction and active array aperture online. Under a 5% ceiling, average sensing is about `3.96%`, but the controller spends roughly `9.7%` during rising maneuver uncertainty and below 1% in calm intervals.

### 6. Grant-free NOMA / SIC random access
A new access-layer branch models autonomous device activity and random resource selection. Ideal SIC only improves collisions when received powers are separable: with 8 dB power spread and offered load about `.90/resource/slot`, throughput increases from `7.40` collision-only to `14.54 packets/slot`; with zero spread, no gain appears.

## Suggested CV bullet

> Developed CommLab, a modular Python wireless-systems research platform with 145 automated tests and 111 reproducible datasets; implemented budget-aware Cell-Free CSI control, finite-blocklength deadline/HARQ scheduling, Age-of-Information policies, event-triggered RIS control, constrained ISAC sensing, and grant-free NOMA/SIC random-access studies.

## Best v1.8 figures

- `joint_csi_budget_nmse.png`
- `joint_csi_budget_edge_rate.png`
- `deadline_harq_miss_rate.png`
- `aoi_policy_comparison.png`
- `event_triggered_ris_tradeoff.png`
- `budget_isac_adaptive_trace.png`
- `grant_free_noma_throughput.png`

## Scope boundaries

Do not claim an optimal CSI integer allocator, optimal deadline scheduler, Whittle-index AoI policy, globally optimal event-triggered RIS controller, constrained-MDP ISAC optimum, standards grant-free random access, activity detection, channel coding, or non-ideal SIC cancellation. These are transparent baselines designed to expose trade-offs.
