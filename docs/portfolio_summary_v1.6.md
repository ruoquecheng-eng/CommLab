# CommLab v1.6 — Portfolio Summary

## Positioning
**CommLab — Wireless Communication Systems Laboratory** is a reproducible Python platform spanning OFDM/MIMO, coding/HARQ, RF/DPD, high mobility/OTFS, Cell-Free/RIS, ISAC, packet scheduling and deployment-aware control. v1.6 emphasizes coupled system trade-offs rather than new waveform labels.

## Strongest v1.6 stories

### 1. RIS control with aged and quantized CSI
I separated **RIS phase quantization** from **CSI-fronthaul quantization** and evaluated phase control after CSI aging. With common channel draws at five aging steps, mean sum-rate rises from about **2.83 (2-bit CSI)** to **3.15 (4-bit)** and **3.19 (6-bit)**, after which gains saturate. At severe age, sample-average robust control can lower mean rate while improving the 10%-tail, so robustness is presented as a risk/mean trade-off rather than a universal win.

### 2. Finite-blocklength queue + Chase HARQ + OLLA
A multi-user event loop now makes each retransmission consume channel uses and maps combined SNR to packet error using the finite-blocklength normal approximation. At blocklength 120, open loop produces roughly **182 packet drops**; Chase HARQ removes the drops in the current run and raises goodput to about **0.370 bit/use**. OLLA reduces NACK to about **8.9%** but operates more conservatively, exposing reliability/goodput/latency coupling.

### 3. Predictive sensing-on-demand
A two-step value-of-information controller looks beyond immediate payload loss when allocating sensing time. It improves mean net rate from the myopic policy's **2.49** to **2.60**, while using sensing mainly in the maneuver segment. A hindsight-tuned fixed 5% policy still reaches **2.72**, which is retained as evidence that shallow lookahead is useful but not globally optimal.

### 4. Cell-Free fronthaul-energy control
Periodic quantized CSI updates now incur explicit modeled fronthaul power while stale CSI degrades true-channel MRT. For 16 active APs / 6-bit CSI, the energy-efficiency maximizing refresh changes from about **8 slots at rho=.995** to **4 slots at rho=.98/.95**. Across a joint grid, the best tested point is **12 active APs, 6-bit CSI, 4-slot refresh**, not full activation.

## Suggested CV bullet
> Developed CommLab, a modular Python wireless-systems laboratory with 124 automated tests and 100 reproducible experiment datasets; implemented coupled studies of finite-blocklength HARQ queues, Cell-Free fronthaul/energy/CSI aging, RIS control under stale quantized CSI, and predictive ISAC sensing-resource allocation.

## Best v1.6 figures
- `cellfree_ris_aged_quantized_mean_rate.png`
- `cellfree_ris_csi_quantization_sweep.png`
- `fbl_harq_queue_goodput.png`
- `fbl_harq_queue_delay.png`
- `isac_predictive_sensing_fraction.png`
- `isac_predictive_sensing_net_rate.png`
- `cellfree_fronthaul_energy_vs_interval.png`
- `cellfree_fronthaul_joint_pareto.png`

## Scope boundaries
Do not claim globally optimal robust RIS, standards HARQ/rate matching, measured fronthaul power, a globally optimal sensing policy, or OTA validation. The new models are transparent research baselines designed to expose system couplings.
