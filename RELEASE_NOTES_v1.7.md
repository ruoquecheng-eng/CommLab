# CommLab v1.7 Release Notes

v1.7 deepens **fronthaul scheduling, temporal CSI compression, retransmission structure, passive-control timescales, and ISAC queue coupling**. The release deliberately keeps several negative results: minimizing CSI NMSE alone can damage edge rate, predictive sensing is not automatically superior at light load, and slow RIS control trades control bandwidth for a measurable rate loss.

## New modules

- `commlab.mimo.async_csi`
  - asynchronous AP-local CSI refresh under a fixed per-slot update budget;
  - round-robin, pure uncertainty, and bounded-uncertainty policies;
  - AP-age, CSI-NMSE, sum-rate, and edge-rate accounting.
- `commlab.mimo.predictive_csi`
  - Gauss-Markov predictive/differential CSI quantization;
  - full-CSI versus innovation-only quantization at identical scalar bit depth.
- `commlab.scheduling.ir_harq_fbl`
  - finite-blocklength block-fading normal approximation for accumulated incremental redundancy;
  - queue-level IR-HARQ versus Chase combining with explicit channel-use cost.
- `commlab.ris.two_timescale`
  - fast per-slot RIS control versus slow sample-average RIS updates;
  - explicit RIS control-bit overhead and phase-noise perturbation.
- `commlab.sensing.queue_control`
  - communication-queue-aware sensing/resource control;
  - two-slot predictive queue-aware baseline.

## New v1.7 experiments

1. `async_cellfree_csi.py`
2. `predictive_csi_quantization.py`
3. `fbl_ir_harq.py`
4. `two_timescale_ris.py`
5. `queue_aware_isac.py`

## Headline observations

- **Asynchronous Cell-Free CSI:** pure expected-MSE scheduling obtains lower average CSI NMSE but can starve low-priority APs for hundreds of slots, severely degrading edge rate. A maximum-age constraint removes most starvation while retaining much of the NMSE advantage.
- **Predictive CSI compression:** at 3-bit/component, innovation quantization improves mean CSI NMSE by about **4.2 dB at rho=.8**, **9.1 dB at rho=.95**, **13.1 dB at rho=.98**, and **19.1 dB at rho=.995** relative to absolute CSI quantization in the current normalized model.
- **Finite-blocklength IR-HARQ:** at mean SNR `-2 dB`, IR raises payload goodput from about **0.452 to 0.581 bit/channel-use**, removes the 10 observed packet drops, and reduces mean transmission rounds from **3.32 to 2.58** versus Chase. At high SNR the schemes converge because retransmissions become rare.
- **Two-timescale RIS:** updating a 6-element 2-bit RIS every 4 slots reduces passive-control overhead from **12 to 3 bit/slot** while mean sum-rate changes from **4.67 (fast current-CSI control)** to about **4.56**. At 16-slot updates the control overhead falls to **0.8 bit/slot**, but mean sum-rate falls to about **4.08**.
- **Queue-aware ISAC:** under moderate load the controllers are nearly identical because queues remain short. Under the overloaded trace, queue-aware sensing reduces mean sensing from **15% to about 9.2%**, raises delivered payload from about **18.6k to 19.2k bits**, and reduces final backlog from about **4.42k to 3.76k bits**, at the cost of worse mean angle uncertainty. Two-step lookahead recovers some tracking quality while preserving most payload benefit.

## Validation

- **134/134 tests passed**
- package version **1.7.0**
- **105 CSV datasets / 182 figures / 287 hashed result artifacts** in the v1.7 release manifest
