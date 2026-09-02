# CommLab v3.0 — Portfolio Summary

## Recommended title
**CommLab: Cross-Layer Wireless Systems, Edge Intelligence, and Networked Control Laboratory**

## One-line description
A reproducible Python research simulator connecting waveform/PHY behavior to distributed learning, edge runtime orchestration, digital-twin state, reliability, tail risk, and closed-loop physical control.

## Strongest v3.0 evidence
1. `results/figures/v30_risk_cvar.png` — tail-risk protection has a real operating region rather than universal dominance.
2. `results/figures/v30_edge_latency_reliability.png` — lowest latency and lowest execution risk are different objectives.
3. `results/figures/v30_cache_hit_latency.png` — high cache hit rate can coexist with severe edge-queue imbalance.
4. `results/figures/v30_semantic_control_tradeoff.png` — payload precision and state-update deliverability trade directly against control performance.
5. `results/figures/v30_cooperative_cost.png` — global system-value scheduling is most useful in the communication-limited regime.

## CV-ready bullets
- Built a modular wireless/edge/control simulator spanning PHY, MIMO, coding, ISAC, distributed learning, edge caching/offloading, digital twins, and networked control, with **213 automated tests** and **488 hashed result artifacts**.
- Added empirical CVaR-based wireless control experiments demonstrating that minimizing mean cost and minimizing tail control risk can require different sensor schedules.
- Implemented reliability-aware multi-edge task orchestration and joint AI-model caching/offloading baselines, exposing failure-recovery and queue-concentration effects hidden by latency or hit-rate-only metrics.
- Developed variable-rate predictive state updates and coupled multi-agent feedback scheduling to connect wireless payload design directly to closed-loop physical-system objectives.

## Claims to avoid
- Do not claim formally optimal CVaR control or production edge orchestration.
- Do not describe scalar linear plants as safety-certified robotics/vehicle control.
- Do not interpret synthetic reliability, energy, or latency numbers as measurements from a commercial edge platform.
