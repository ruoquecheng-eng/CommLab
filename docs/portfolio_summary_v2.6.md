# CommLab v2.6 — Portfolio Summary

**Recommended title:** CommLab — Wireless Communication & Edge-Intelligence Systems Laboratory

**One-line description:** A reproducible Python wireless-systems laboratory linking PHY/MAC/network constraints to edge learning and inference; v2.6 adds learning-aware OTA client selection, progressive split inference, loss-resilient differential model broadcast, energy-harvesting OTA-FL, and importance-aware downlink model distribution.

## Strong v2.6 evidence

- **Physical-layer optimum can be learning-suboptimal:** strongest-channel AirComp selection obtains the cleanest selected-client analog sum yet creates severe non-IID participation bias and worse global loss when channel quality correlates with data group.
- **On-time inference beats raw accuracy as a real-time metric:** at poor SNR, full residual offload returns many correct results after the deadline, while progressive transmission stops early and achieves higher usable task accuracy with far fewer feature channel uses.
- **Downlink synchronization is stateful:** small chained deltas save bandwidth but a missed packet can break the reconstruction chain; periodic keyframe anchoring trades more overhead for faster recovery.
- **Energy scarcity changes the scheduling objective:** when batteries are nearly empty, all policies are energy-limited; once energy is plentiful, selection fairness and data diversity matter again.
- **Task importance can justify serving weak receivers:** downlink model enhancement chosen only from SNR can under-serve high-value clients; weighted layered multicast explicitly trades airtime for application utility.

## Suggested portfolio figures

1. `results/figures/v26_aircomp_selection_loss.png`
2. `results/figures/v26_progressive_split_ontime.png`
3. `results/figures/v26_downlink_differential_mse.png`
4. `results/figures/v26_eh_aircomp_loss.png`
5. `results/figures/v26_importance_multicast_utility.png`

## CV-safe bullet

Built and validated a modular Python wireless-systems laboratory with 190 automated tests and 400+ hashed experiment artifacts; designed cross-layer experiments showing how wireless client selection, downlink packet loss, energy availability and real-time feature transmission alter federated-learning/inference performance rather than optimizing PHY metrics in isolation.

## Avoid overclaiming

Do not describe the Gaussian split-inference task as a deployed neural network, the differential broadcast baseline as MTDC itself, the energy model as hardware calibrated, the diversity selector as globally optimal, or the layered multicast utility model as a trained scalable-model codec.
