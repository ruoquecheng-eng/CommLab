# CommLab v3.3 Release Notes

## Theme: Unified Resilience-Budget Orchestration

v3.3 turns several reliability mechanisms that previously lived in separate experiments into one cross-layer decision problem. A runtime receives a finite **normalized resilience-credit budget** and must decide whether to spend it on:

- proactive edge-service migration,
- cross-failure-domain execution replication,
- dual-link packet duplication,
- or no proactive action.

The normalized credit is deliberately only a decision-accounting device. CommLab separately reports physical radio transmissions, replica execution rate, migration rate, migration traffic, latency, deadline misses, and task-weighted deadline misses. v3.3 does **not** claim that a radio transmission, a replica execution, and a migration are physically interchangeable units of energy or monetary cost.

All v3.2 modules, tests, experiments, CSVs, figures, Dashboard Labs, and release documentation are preserved.

## New capability

### 1. Unified risk-budget orchestration

`simulate_unified_risk_orchestration` combines edge degradation, shared failure domains, correlated dual radio paths, task criticality, deadline tails, state migration, and parallel replicas. Policies see only noisy one-step edge-risk forecasts and pre-transmission link-quality estimates. Realized edge failures and packet outcomes are not available at decision time.

Baselines:

- `reactive`
- `radio_first`
- `edge_first`
- `risk_budget`
- `risk_budget_unweighted`
- `uncertainty_gated`

### 2. Reliability-budget sweep

At the supplied mixed regime, reactive operation has about **22.17% task-weighted deadline misses**. A risk-budget policy reduces this to roughly **12.28% at 0.6 credit/task**, **9.57% at 1.0**, and **7.47% at 1.2**. The additional reliability is not free: at 1.2 credit/task the runtime averages about **1.89 radio transmissions/task**, executes a replica on about **46.7%** of tasks, and proactively migrates about **2.7%** of tasks.

### 3. Failure-mode-dependent budget allocation

The same risk-budget policy changes mechanism rather than using one fixed redundancy rule:

- **radio-limited:** duplication rate ≈ **100%**, replica ≈ **0%**;
- **mixed:** duplication ≈ **96.6%**, replica ≈ **2.2%**;
- **edge-limited / radio-good:** duplication ≈ **3.8%**, replica ≈ **62.6%**.

This is the core v3.3 systems result: the useful form of redundancy depends on which layer currently dominates failure risk.

### 4. Forecast uncertainty gating

Point-estimate risk orchestration begins to spend credits on speculative migration as edge forecasts become noisy. At forecast-noise **1.1**, the ungated policy proactively migrates about **1.68%** of tasks and carries about **5.14 MB/task** of total migration traffic. The uncertainty-gated policy drives proactive migration to effectively **0%** and traffic to about **3.70 MB/task**, while reducing task-weighted deadline misses from about **6.81% to 6.12%** in that regime.

The gate is not universally superior. At forecast-noise **0.25**, it is slightly worse in task-weighted deadline reliability because it rejects some useful edge actions. The crossover is retained rather than hidden.

### 5. Correlation-aware budget reallocation

As radio-path correlation rises from **0 to 0.95**, the runtime cuts duplication from about **96.9% to 65.2%** of tasks and increases cross-domain replica execution from about **2.0% to 22.3%**. Even after this reallocation, task-weighted deadline misses rise from about **11.7% to 21.9%**. Reallocation helps avoid wasting all credits on correlated radio redundancy, but it cannot manufacture missing radio diversity.

### 6. Excess-budget saturation and negative result

More available credits do not imply that every credit should be spent. With forecast noise 0.4:

- ungated risk-budget orchestration spends about **1.84 credit/task** when offered 2.2, with proactive migration rising to about **15.5%** and migration traffic to about **13.8 MB/task**;
- uncertainty gating saturates near **1.48 credit/task**, proactive migration stays around **0.7%**, and migration traffic stays near **3.2 MB/task**.

The ungated curve also stops improving monotonically at the high-budget end: task-weighted misses are about **7.76% at 1.8 credits** and **8.79% at 2.2**. This is retained as a resource-churn counterexample rather than tuned away.

### 7. Task weighting is not automatically enough

A criticality-weighted greedy risk proxy and its unweighted counterpart are both retained. Their ordering changes with budget. The result is intentionally negative: simply multiplying instantaneous failure reduction by task criticality does not guarantee better task-weighted deadline performance when latency/deadline risk is only imperfectly represented by the proxy. A stronger future policy would need a better calibrated end-to-end completion-risk model rather than a larger heuristic weight.

## Dashboard

A new **Unified Resilience Budget** Lab exposes:

- budget per task,
- orchestration policy,
- forecast noise,
- mean SNR,
- radio-path correlation,
- edge-risk scale,
- task-weighted deadline miss,
- latency,
- credits spent,
- radio transmissions,
- replica execution,
- proactive migration.

The Dashboard uses a short interactive Monte Carlo run; release figures come from the deterministic experiment scripts.

## Scientific boundaries

- Synthetic NumPy simulation; no real edge-cluster failure trace.
- Normalized resilience credits are not physical joules, dollars, or CPU-seconds.
- Failure forecasts are synthetic and explicitly noisy.
- Multi-connectivity is a correlated Bernoulli abstraction, not 3GPP bit-exact PDCP duplication.
- Cross-domain replica execution is an availability abstraction, not Kubernetes/VM live-replication validation.
- No RL, Transformer, production Digital Twin, safety certification, or real-hardware benchmark is claimed.

## Formal validation

- package/runtime: **3.3.0**
- **236 / 236 tests passed**
- **236 / 236 tests passed with manual `PYTHONPATH` removed**
- six-experiment v3.3 suite completed
- editable install / distribution-version / import-path checks passed
- `compileall -q src app experiments tools` passed
- **202 CSV + 354 PNG = 556 SHA-256 verified result artifacts**
- release manifest verification passed

ZIP CRC and the final archive SHA-256 are checked during packaging and distributed alongside the release archive.
