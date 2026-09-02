# CommLab v1.9 Release Notes

v1.9 expands CommLab into four additional system directions that are deliberately different from the existing OFDM/MIMO/RIS/ISAC branches: **graph-based coded random access, over-the-air computation, eMBB/URLLC coexistence, and energy-harvesting information freshness**. The release keeps the same scope discipline as earlier versions: every new branch is a transparent educational/research baseline rather than a standards-compliant protocol implementation.

## New modules

- `commlab.random_access.irsa`
  - frame-based repetition slotted ALOHA;
  - configurable repetition-degree distribution;
  - iterative singleton peeling / replica cancellation;
  - throughput, PLR, SIC-iteration and replica-cost accounting.
- `commlab.computation.aircomp`
  - analog over-the-air arithmetic-mean aggregation;
  - orthogonal per-device baseline;
  - full channel inversion and truncated inversion;
  - communication/computation MSE versus one-use / K-use channel cost.
- `commlab.scheduling.network_slicing`
  - mini-slot eMBB/URLLC coexistence;
  - fixed reservation, EWMA adaptive reservation, and immediate preemption;
  - EDF-style URLLC service, deadlines, reservation waste and eMBB payload accounting.
- `commlab.scheduling.energy_aoi`
  - Bernoulli energy harvesting and finite batteries;
  - generate-at-will status updates;
  - max-age, max-SNR, age×reliability and battery-aware scheduling;
  - AoI, delivery rate, energy outage and overflow accounting.

## New experiments

1. `irsa_coded_random_access.py`
2. `aircomp_aggregation.py`
3. `embb_urllc_slicing.py`
4. `energy_harvesting_aoi.py`

## Headline observations

- **IRSA peeling threshold:** the tested `{2:0.50, 3:0.28, 8:0.22}` repetition distribution reaches about `0.651 packet/slot` around offered load `G=0.673` with PLR `~3.5%`; the slotted-ALOHA baseline peaks around `0.369 packet/slot`. Above the SIC threshold, however, the graph stops peeling and IRSA collapses sharply rather than improving indefinitely.
- **AirComp bandwidth/MSE trade-off:** 20 devices aggregate a 24-dimensional vector in one simultaneous channel use rather than 20 orthogonal uses. Full channel inversion is heavy-tailed because the weakest Rayleigh fade controls the common gain. At 12 dB the tested truncated-inversion threshold sweep has its lowest mean MSE near `|h|=0.211`, retaining about `95.4%` of devices; raising the threshold further reduces deep-fade noise but participant-dropout error dominates.
- **eMBB/URLLC slicing:** fixed 6-PRB reservation wastes about `69.6%` of its reserved resources at `0.6 URLLC arrivals/minislot`; preemption instead achieves eMBB payload proxy `~66.8` with zero observed deadline misses in the same trace. At load `2.1`, preemption still protects URLLC but eMBB falls to `~53.3`, slightly below fixed reservation (`~54.0`), exposing the high-load puncturing cost.
- **Energy-harvesting freshness:** at low harvest scale `.08`, all policies suffer energy outage around `61%` and mean AoI around `20–22 slots`. Around scale `.243`, age×reliability / energy-aware scheduling lowers mean AoI to about `4.1 / 3.9` slots. When energy becomes abundant (`.65`), max-SNR achieves almost one successful delivery per slot but mean AoI explodes to about `58 slots` because weak-channel users are starved; age×reliability stays near `3.3 slots`.
- **AirComp tail-risk reporting:** v1.9 reports median and p90 aggregation MSE in addition to the mean because ZF/full-inversion operation over Rayleigh fading has rare deep-fade outliers. The main SNR figure uses medians instead of hiding this heavy-tail behavior behind an unstable sample mean.

## Scope / limitations

- IRSA is graph/collision based; there is no activity detector, capture model, channel estimator or residual-SIC error.
- AirComp assumes ideal synchronization and analog superposition; no quantization, coding, FL optimizer or hardware impairments are modeled.
- The slicing experiment is an abstract mini-slot resource model, not 3GPP NR MAC/RLC behavior.
- Energy-harvesting AoI uses Bernoulli energy arrivals and one-unit transmission cost; battery leakage and energy-dependent transmit power are not modeled.

## Validation

- package version **1.9.0**
- **149/149 automated tests passed**
- **116 CSV datasets / 202 figures / 318 hashed result artifacts**
- deterministic v1.9 experiment suite available via:

```bash
python experiments/run_v19_suite.py
```
