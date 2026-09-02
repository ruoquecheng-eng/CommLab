# CommLab v1.4 Release Notes

v1.4 focuses on distributed CSI acquisition, propagation/network co-design, cross-layer feedback loops, ISAC beam trade-offs, and energy-aware distributed access.

## New capabilities

- Pilot-reuse Cell-Free channel acquisition with per-AP LMMSE estimation.
- Greedy contamination-aware pilot assignment based on large-scale fading overlap.
- RIS-assisted Cell-Free distributed channel model and finite-bit coordinate ascent for sum-rate or min-rate objectives.
- Event-driven packet queues with PF/delay-PF scheduling, OLLA, MCS selection, abstract Chase HARQ, retransmission state, packet delay, NACK rate, drops, and backlog.
- Joint communication/sensing beamforming via principal eigenvector of a weighted quadratic utility.
- Cell-Free AP activation/sleep-mode baselines: aggregate-strength versus coverage-aware selection and a simple circuit-power energy-efficiency metric.
- Five new Streamlit labs exposing the above branches.

## Representative findings

### Pilot contamination
With 12 users and 6 available pilots, the contamination-aware heuristic lowers mean channel-estimation NMSE from about 0.0823 to 0.0276 and increases the mean 5%-tile user rate from about 0.537 to 0.715 bit/s/Hz in the normalized model. With 12 pilots, the greedy assignment becomes orthogonal and removes the modeled co-pilot overlap.

### Cell-Free + RIS
Random RIS phases give mean total rate about 4.69 bit/s/Hz. Two-bit coordinate ascent targeting sum rate reaches about 7.48. A weakest-user objective sacrifices total rate (about 6.73) while slightly raising the weakest-user mean rate (about 1.64 versus 1.57).

### Cross-layer feedback
On one fixed biased-SNR, correlated-fading packet trace, open-loop/no-HARQ drops 294 packets. Chase HARQ eliminates drops; OLLA additionally reduces NACK rate from about 19.8% to 10.7% and P95 delay from 4 to 3 slots. This is a system-level abstraction, not standards HARQ rate matching.

### ISAC beam Pareto
A single normalized ULA beam is selected from a weighted communication/sensing quadratic objective. Weight one is communication MRT and weight zero is the sensing steering vector. Angular separation controls how costly it is to serve both objectives with one beam.

### AP activation
Under the selected circuit-power abstraction, the energy-efficiency curve peaks before all APs are enabled. More APs continue to improve user rate, but per-AP circuit power eventually dominates the rate gain.

## Validation

- 108 automated tests.
- v1.4 experiment suite reproducibly generates the new datasets/figures.
- Result artifact manifest uses SHA-256 hashes.
- Package version 1.4.0.

## Deliberate limitations

- Pilot assignment is greedy, not a globally optimal joint pilot/AP optimizer.
- Cell-Free/RIS models use normalized synthetic channels, not a standards-calibrated deployment model.
- Cross-layer HARQ uses abstract Chase SNR combining; it is not NR/LTE redundancy-version rate matching.
- ISAC joint beamforming is a compact quadratic Pareto baseline, not waveform-level multi-constraint optimization.
- AP energy efficiency uses a simple explicit circuit-power model; it is not a hardware power budget.
