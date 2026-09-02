# CommLab v2.9 — Portfolio Summary

## Recommended title
**CommLab: State-Aware Wireless Edge Intelligence and Networked Control Simulator**

## One-line description
A reproducible Python research simulator connecting wireless PHY/MAC behavior to model synchronization, edge-model freshness, federated-learning orchestration, digital-twin prediction, and closed-loop control objectives.

## What v2.9 adds
- **Task-aware model repair:** wireless synchronization resources are allocated according to current application demand, not age alone.
- **Congested model refresh:** refresh traffic is an explicit queue, so chasing freshness can itself create stale edge models.
- **Battery/carbon/fairness FL:** client selection obeys battery energy causality while balancing learning contribution, long-term participation debt, and carbon proxy.
- **Twin-guided model prefetch:** speculative edge-model loads are driven by digital-twin state prediction and suppressed when uncertainty is high.
- **Networked control:** wireless sensor scheduling is evaluated by physical closed-loop cost, not only packet age or link success.

## Strongest evidence to show
1. `results/figures/v29_control_age_value.png` — the clearest v2.9 research result: lower information age can coexist with much worse control cost.
2. `results/figures/v29_twin_prefetch_backhaul.png` — blind prediction causes speculative model-transfer explosion as twin uncertainty rises; gating controls it.
3. `results/figures/v29_cache_refresh_queue.png` — eager model freshness can overload the refresh queue and create its own staleness.
4. `results/figures/v29_task_repair_utility.png` — task demand changes where synchronization budget should be spent.
5. `results/figures/v29_battery_carbon_pareto.png` — energy causality and persistent fairness expose sustainability trade-offs in FL orchestration.

## CV-ready bullets
- Built a modular Python wireless/edge-intelligence simulator with **207 automated tests** and **473 hashed experimental artifacts**, spanning PHY/MIMO/ISAC through FL, model distribution, edge inference, digital-twin synchronization, and networked control.
- Designed state-aware edge orchestration experiments showing that **minimum information age, minimum analog aggregation error, maximum cache-hit rate, and minimum carbon cost can each be misaligned with application-level utility**.
- Implemented an uncertainty-gated digital-twin model-prefetch baseline that suppresses speculative model-transfer churn while preserving most predictive latency gain.
- Added a multi-loop networked-control testbed where wireless sensor scheduling is evaluated by **closed-loop physical cost**; at low SNR, control-value scheduling dramatically outperforms Max-Age despite using older information on average.

## Safe claims
- Reproducible research/education simulator with explicit assumptions and negative operating regions.
- Implements transparent heuristic and model-based baselines for cross-layer communication-computation-control questions.
- Demonstrates metric misalignment and resource/state trade-offs through deterministic code and Monte Carlo experiments.

## Claims to avoid
- Do not call the digital-twin model an industrial or high-fidelity digital twin.
- Do not claim formal optimality for task-aware repair, congestion-aware refresh, FL orchestration, or control-value scheduling.
- Do not present the carbon metric as audited CO2e accounting.
- Do not describe the networked-control branch as safety-certified or hardware validated.
