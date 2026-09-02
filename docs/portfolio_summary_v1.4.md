# CommLab v1.4 — Portfolio Summary

## One-line positioning
A reproducible Python wireless-systems laboratory spanning PHY receivers, MIMO/FEC/HARQ, RF/DPD, high-mobility/OTFS, distributed Cell-Free/RIS networks, system-level scheduling, and communication-centric sensing.

## Strong v1.4 case studies

### 1. Pilot contamination-aware Cell-Free CSI
**Question:** How does pilot reuse corrupt distributed channel estimates, and can large-scale geometry guide a low-cost assignment?

Representative result (12 users, 6 pilots): random reuse NMSE `0.0823`; contamination-aware `0.0276`. Mean 5%-tile rate `0.537 -> 0.715 bit/s/Hz`.

Best figures:
- `results/figures/cell_free_pilot_nmse.png`
- `results/figures/cell_free_pilot_edge_rate.png`

### 2. Cell-Free + RIS fairness/throughput co-design
**Question:** Should a programmable surface maximize network sum rate or explicitly protect the weakest distributed user?

Representative result: random RIS total rate `4.69`; sum-rate optimized `7.48`; min-rate optimized total `6.73` but weakest-user rate `1.64` versus `1.57` for the sum-rate objective.

Best figure:
- `results/figures/cellfree_ris_sum_min_tradeoff.png`

### 3. Cross-layer OLLA + HARQ + queues
**Question:** What changes when MCS selection, feedback adaptation, retransmission and packet delay are evaluated on the same fading trace?

Representative result: HARQ removes drops on the current trace; OLLA cuts NACK rate approximately `19.8% -> 10.7%` and P95 delay `4 -> 3` slots.

Best figures:
- `results/figures/cross_layer_delay_goodput_tradeoff.png`
- `results/figures/cross_layer_backlog.png`

### 4. Joint ISAC beam Pareto
**Question:** How much communication rate must be traded for sensing gain when one spatial beam serves both objectives?

Best figure:
- `results/figures/isac_comm_sensing_pareto.png`

### 5. Energy-aware Cell-Free AP activation
**Question:** Is activating every distributed AP always energy-efficient?

Representative result: in the explicit normalized circuit-power model, energy efficiency peaks around 12 active APs while user rate continues increasing toward all-AP operation.

Best figures:
- `results/figures/cell_free_ap_activation_energy_efficiency.png`
- `results/figures/cell_free_ap_activation_edge_rate.png`

## Suggested CV bullet
Developed **CommLab**, a modular and reproducible Python wireless-systems laboratory covering OFDM/MIMO/FEC/HARQ, high-mobility ICI/OTFS, RF impairment/DPD, Cell-Free/RIS distributed architectures, cross-layer OLLA/queue scheduling, and OFDM-ISAC; implemented quantitative trade-off studies with automated tests, interactive labs, and hashed experiment artifacts.

## Claims to avoid
- Do not call the pilot heuristic globally optimal.
- Do not describe the cross-layer HARQ abstraction as 3GPP NR HARQ.
- Do not present normalized synthetic rate figures as commercial-network throughput.
- Do not call the ISAC eigen-beam solution a full waveform-level joint optimizer.
- Do not interpret the AP circuit-power model as measured hardware power consumption.
