# CommLab v2.8 Release Notes

v2.8 extends the runtime-orchestration branch toward **state recovery, model-version freshness, persistent fairness constraints, overload admission control, and digital-twin synchronization**. The release remains an educational/research simulation platform rather than a standards-compliant network or production edge-AI stack.

## New capability groups

### Selective differential-downlink repair
- ACK-aware per-client chain state and model-version age.
- Common chained deltas every round, rare global keyframes, and client-specific repair snapshots.
- Age-only and task-importance-weighted repair ranking.
- Long-run repair/keyframe airtime matched closely to the periodic-keyframe baseline.
- Explicit negative operating region: when many receivers desynchronize together, a common keyframe is more efficient than individual repair.

### Version-aware edge model caching
- Cached model version tracked separately from cache hit/miss state.
- Task utility decays with stale model versions.
- Model evolution rates and task sensitivity differ by model.
- A hard per-refresh backhaul budget prevents version-aware refresh from winning by downloading every new version.
- Differential model refresh cost and value-per-MB prioritization.

### Persistent fairness/carbon FL orchestration
- Virtual participation-debt queues provide long-horizon fairness state.
- Clients accumulate debt when their achieved participation falls below a target rate.
- Scheduling trades gradient utility, time-varying regional carbon proxy, and virtual debt.
- Debt-weight sweep exposes an explicit fairness-versus-carbon Pareto.

### Admission control for progressive split inference
- Low-confidence requests can finish locally rather than entering an overloaded enhancement queue.
- Admit-all, backlog-gate, and task-value/backpressure admission policies.
- Completion-aware radio scheduling is retained after admission.
- Metrics include on-time task utility, deadline misses, admission fraction, radio use, and queue backlog.

### Digital-twin semantic synchronization
- A physical position/velocity process with stable and maneuver intervals.
- Edge twin predicts with a constant-velocity model between received updates.
- Periodic full-state, error-triggered full-state, and quantized semantic-innovation updates.
- Age-of-Incorrect-Information (AoII) proxy plus synchronization RMSE and radio load.
- Small semantic deltas are easier to deliver but introduce quantization error; this is a transparent state-sync baseline, not a production digital-twin codec.

## Selected v2.8 results

- **Selective repair has a regime boundary.** At mean client SNR 4 dB, periodic common keyframes remain better because desynchronization is broad. At 10 dB and nearly identical normalized downlink load (~0.274/round), age-selective repair reduces weighted version age from about **8.87 to 7.45 rounds** and weighted model MSE from **0.704 to 0.579**. At 12 dB it reduces weighted age to about **2.09 rounds** versus **4.66** for periodic keyframes.
- **Cache hit rate is not model freshness.** Popularity caching reaches about **79.9%** hit rate but serves models roughly **10.3 versions old** on average and task utility about **0.54**. With a 180 MB/refresh-epoch version-aware budget, hit rate falls to about **63.8%**, but mean task utility rises to about **0.86** and served version age falls to about **6.25**. Fully reactive LRU keeps versions fresh but incurs roughly **163 GB** modeled backhaul in the same workload.
- **Persistent participation has an environmental cost.** Carbon-only selection lowers the modeled carbon proxy to about **207** but yields Jain participation around **0.27** and large learning bias. With debt weight 8, virtual-debt orchestration reaches Jain fairness about **0.99**, minimum participation about **0.227/round**, and excess loss about **0.0017**, while carbon rises to about **523**.
- **Admission control prevents queue collapse.** At 0.8 arrivals/slot, admit-all has on-time task utility about **0.528** and deadline miss rate **41%**. Backpressure raises utility to about **0.676** and lowers misses to **21%** by admitting roughly **80%** of candidate refinements. At extreme load 1.5, the simpler backlog gate becomes more robust than the value-backpressure heuristic, an intentional negative result.
- **Semantic state deltas can dominate full updates under packet-size-dependent outage.** With error trigger 1.5, full-state event updates give position RMSE about **0.84** at load **0.090/slot**; 5-bit semantic deltas give RMSE about **0.63** at load only **0.0068/slot**, because the smaller innovation packets succeed much more often. The result depends on the explicit link-abstraction and quantization assumptions and is not a standards claim.

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v28_suite.py
python tools/build_results_manifest_v28.py
python tools/verify_release_v28.py
```

## Final release validation
- Package/runtime version: **2.8.0 / 2.8.0**
- Automated regression: **200/200 tests passed**
- Result inventory: **169 CSV datasets + 289 PNG figures = 458 SHA-256 verified artifacts**
- Dashboard/source/experiment/tool compile checks passed.
- Validation also passed after clearing `PYTHONPATH`, confirming the installed editable package imports the v2.8 source tree rather than an older release.
