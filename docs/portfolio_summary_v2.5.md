# CommLab v2.5 — Portfolio Summary

**Recommended title:** CommLab — Wireless Communication & Edge-Intelligence Systems Laboratory

**One-line description:** A reproducible Python simulation laboratory spanning OFDM/MIMO/RF/sensing/network control and wireless edge intelligence, with v2.5 adding resilient asynchronous learning, hierarchical personalization, joint AirComp privacy/hardware impairments, energy-aware split inference and heterogeneous downlink model multicast.

## Strong v2.5 evidence

- **Robust asynchronous FL:** coordinate median remains stable under combined staleness + Byzantine sign-flip attacks where naive averaging diverges; a more elaborate conflict/staleness heuristic does not beat the simpler robust baseline.
- **Hierarchical personalization:** cluster models exploit structured non-IID data when grouping is accurate, but mis-clustering can erase the gain and even make local fitting preferable.
- **Private hardware AirComp:** privacy perturbation creates an aggregation floor beyond which increasing ADC resolution produces diminishing returns.
- **Real-time split inference:** raw accuracy can be misleading when late predictions are unusable; energy/deadline-aware offloading optimizes on-time task success instead.
- **Downlink model delivery:** scalable base/enhancement multicast reduces the weakest-user bottleneck as receiver SNR dispersion increases.

## Safe claims

- Reproducible educational/research simulator with deterministic tests and stored CSV/figure artifacts.
- Implements transparent baselines and reports negative results / failure regions.
- Supports cross-layer experiments linking PHY impairments to learning, sensing, latency, energy and task utility.

## Avoid overclaiming

Do not call the Byzantine heuristic production-secure, the privacy perturbation formally DP, the energy model hardware-calibrated, or the layered multicast a standards-compliant scalable neural-model codec.
