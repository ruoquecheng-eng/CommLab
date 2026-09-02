# Portfolio Summary — CommLab v1.9

## Suggested project title

**CommLab — Modular Wireless Communication Systems Laboratory**

## v1.9 portfolio additions

### Coded random access / IRSA
Built a graph-based repetition slotted-ALOHA simulator with iterative singleton peeling and replica cancellation. The tested irregular repetition distribution reaches roughly **0.65 decoded packet/slot**, versus roughly **0.37** peak throughput for conventional slotted ALOHA, while also exposing the abrupt SIC/graph threshold at excessive load.

### Over-the-Air Computation
Implemented analog wireless mean aggregation in which **20 devices aggregate a vector in one shared channel use**, compared with 20 orthogonal transmissions. Evaluated full channel inversion and truncated inversion, including the heavy-tail risk from the weakest Rayleigh channel and the optimum between deep-fade suppression and participant dropout.

### eMBB / URLLC coexistence
Implemented an abstract mini-slot slicing simulator comparing fixed reservation, traffic-adaptive reservation and immediate URLLC preemption. Quantified **URLLC deadline misses, reserved-resource waste and eMBB throughput loss** across random URLLC load.

### Energy-harvesting AoI
Extended status-update scheduling with finite batteries and stochastic harvested energy. Showed that a max-SNR scheduler can achieve almost one successful update per slot yet have **tens of slots of mean AoI** because weak users are starved, while freshness/reliability-aware scheduling keeps information substantially newer.

## Recommended v1.9 figures

- `results/figures/irsa_throughput.png`
- `results/figures/irsa_packet_loss.png`
- `results/figures/aircomp_mse_snr.png`
- `results/figures/aircomp_threshold_tradeoff.png`
- `results/figures/slicing_embb_throughput.png`
- `results/figures/slicing_urllc_deadline.png`
- `results/figures/energy_aoi_mean.png`

## CV bullet candidate

> Developed CommLab, a modular Python wireless-systems research simulator spanning OFDM/MIMO/RIS/ISAC, coding/HARQ and system-level scheduling; extended it with graph-based IRSA random access, analog over-the-air aggregation, eMBB/URLLC preemption, and energy-harvesting AoI experiments, with automated tests and reproducible result manifests.

## Claims to avoid

Do not describe the new branches as standards-compliant 5G/6G random access, production AirComp/Federated Learning, 3GPP network slicing, or optimal AoI control. They are transparent research baselines designed to expose system trade-offs.
