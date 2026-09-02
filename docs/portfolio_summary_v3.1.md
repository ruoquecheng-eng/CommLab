# CommLab v3.1 — Portfolio Summary

## Recommended title
**CommLab: Cross-Layer Wireless, Edge Intelligence, Goal-Oriented Communication, and Networked Control Laboratory**

## One-line description
A reproducible Python research platform that connects PHY/network behavior to edge inference, model serving, failure recovery, state value, safety risk, and closed-loop cyber-physical objectives.

## Strongest v3.1 evidence
1. `results/figures/v31_safety_violation.png` — safety-boundary scheduling has a real operating region rather than universal dominance.
2. `results/figures/v31_adaptive_depth_accuracy.png` — feature precision and edge inference depth should be adapted jointly to the channel/latency regime.
3. `results/figures/v31_failure_recovery_p95.png` — restart, checkpoint, and replication occupy different recovery-overhead/tail-latency regimes.
4. `results/figures/v31_model_replication_weighted_outage.png` — raw model-outage count and task-weighted outage are different placement objectives.
5. `results/figures/v31_component_control_cost.png` — a tiny component-selective feedback budget can beat uniform low-precision state transport when state coordinates have unequal downstream control value.

## CV-ready bullets
- Extended a modular wireless/edge/control simulator to **218 automated tests** and a release-verified result catalog covering safety-aware feedback, adaptive inference, failure recovery, model replication, and goal-oriented state transmission.
- Developed a channel-adaptive edge-inference baseline that jointly selects feature precision and model depth under an end-to-end latency constraint, exposing the regime where adaptive compute/communication co-design is useful.
- Implemented restart/checkpoint/replication recovery baselines and risk-aware AI-model replica placement, separating raw availability from task-critical availability.
- Added component-selective and safety-aware wireless control experiments showing that task/control value can disagree with freshness, uniform fidelity, or raw packet-level objectives.

## Claims to avoid
- Do not call the safety scheduler a formally verified safety controller.
- Do not describe the analytic adaptive-depth task model as a DNN/LLM benchmark.
- Do not interpret synthetic failure, checkpoint, storage, or latency values as measurements from a production edge cluster.
- Do not claim risk-aware replication or component selection is globally optimal.
