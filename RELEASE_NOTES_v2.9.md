# CommLab v2.9 Release Notes

v2.9 extends the state-aware runtime branch toward **task-conditioned model repair, congestion-aware model refresh, energy-causal sustainable FL, digital-twin-guided model prefetch, and networked feedback control**. The release remains a transparent educational/research simulator rather than a production edge-AI, carbon-accounting, digital-twin, or control platform.

## New capability groups

### Task-aware differential model repair
- Dynamic per-client inference demand rather than static client importance only.
- Chained model deltas, rare global keyframes, and client-specific repair snapshots.
- Age-only, static-importance, and task-demand-aware repair priorities.
- Nearly matched normalized downlink load across policies.
- Application utility decays explicitly with model-version age.

### Congestion-aware model refresh
- Cached model version and refresh completion are separate state variables.
- Refreshes are queued and complete only after their bytes traverse a finite-rate backhaul.
- Eager, periodic value-density, and congestion-aware refresh admission.
- Queue backlog, refresh bytes requested/delivered, served model age, and task utility are reported together.
- The congestion-aware heuristic may deliberately leave a refresh opportunity unused rather than flooding the queue.

### Battery-carbon-fair FL orchestration
- Finite device batteries and stochastic energy harvesting.
- Per-round communication/compute energy causality.
- Carbon-only, virtual-debt, and battery-aware debt/carbon client selection.
- Persistent participation fairness, learning bias, carbon proxy, energy infeasibility, and under-filled rounds exposed jointly.

### Digital-twin-guided edge-model prefetch
- A mode-switching physical process whose next operating mode determines the needed AI model.
- A noisy digital twin predicts transition direction and timing.
- Reactive, blind predictive, and uncertainty-gated prefetch policies.
- Wrong-prefetch fraction and model-transfer backhaul are first-class metrics rather than hidden costs.

### Networked control scheduling
- Multiple mildly unstable scalar plants share one wireless sensor-update slot.
- A remote controller predicts plant state between successful wireless updates.
- Round-robin, Max-Age, Max-Error, and control-value scheduling.
- Closed-loop physical cost, estimation error, state excursion, information age, and scheduling fairness are measured together.
- Sensor-side error magnitude is assumed available as small trigger/priority metadata; this is a networked-control abstraction, not a deployed industrial controller.

## Selected v2.9 results

- **Task workload changes the value of model freshness.** At task-burst strength 2.4 and almost identical normalized downlink load (~0.290/round), age-only repair achieves task utility ratio about **0.697**, static-importance about **0.732**, and task-aware repair about **0.792**. The task-weighted model age falls to roughly **7.43 rounds** for task-aware repair.
- **Eager freshness can create its own staleness.** With only 0.8 MB of model-refresh backhaul service per inference request, eager refresh serves models about **10.36 versions old** on average with a P95 refresh queue about **579 MB**. Congestion-aware refresh lowers age to about **7.75 versions** and the queue to about **416 MB**. At 5 MB/request, however, periodic value-density refresh gives higher task utility than the congestion-aware heuristic, preserving a high-capacity crossover.
- **Energy scarcity changes which FL objective matters.** At harvest scale 0.12, roughly **89%** of client-round states are energy-infeasible and over **93%** of rounds are under-filled, so carbon/fairness heuristics have little room to act. Around harvest scale 0.50, carbon-only selection begins to reduce participation fairness and increase excess loss; debt/battery-aware orchestration restores much of the learning/fairness performance while accepting higher modeled carbon cost.
- **Digital-twin prediction needs uncertainty gating.** At twin uncertainty 0.8, blind predictive prefetch reaches mean inference latency about **12.32 ms** but generates roughly **97,163 MB** of model-transfer backhaul and about **45.6%** wrong prefetches. Uncertainty gating improves latency further to about **11.82 ms** while reducing backhaul to roughly **12,082 MB** and wrong prefetches to about **15.4%**. Pure reactive inference is slower at about **14.72 ms** but uses only about **6,977 MB**.
- **Freshest information is not necessarily the most valuable information for control.** At mean sensor-link SNR -4 dB, Max-Age scheduling keeps mean information age near **18.8 slots** but produces mean closed-loop cost about **124.3**. Control-value scheduling accepts older information (~**22.2 slots**) yet lowers cost to about **14.3**. Max-Error reaches about **21.7**, while round-robin becomes severely unstable in the same regime.

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v29_suite.py
python tools/build_results_manifest_v29.py
python tools/verify_release_v29.py
```

## Final release validation
- Package/runtime version: **2.9.0 / 2.9.0**
- Automated regression: **207/207 tests passed**
- Result inventory: **174 CSV datasets + 299 PNG figures = 473 SHA-256 verified artifacts**
- Single-command v2.9 experiment suite completed successfully.
- Dashboard/source/experiment/tool compile checks passed.
- Validation also passes after clearing `PYTHONPATH`, confirming the installed package imports the v2.9 source tree rather than a previous editable installation.
