# CommLab v3.2 Release Notes

## Theme: Predictive Resilience and Reliability Orchestration

v3.2 extends the v3.1 safety/recovery milestone from reactive reliability toward **prediction-aware edge resilience, deadline-tail-aware inference, failure-domain diversity, unequal control-state protection, and correlation-aware multi-connectivity**. The five already-completed reliability-oriented experiments from the earlier v3.2 draft are preserved as additional capability groups rather than discarded.

## New v3.2 main line

1. **Predictive failure migration**
   - sticky, reactive, and predictive-risk migration;
   - noisy degradation forecasts, state-transfer traffic, P95 latency, deadline misses, and migration churn;
   - explicit prediction-churn crossover rather than assuming better forecasts always help.

2. **Failure-domain-aware model replication**
   - popularity, criticality, and diversity-risk placement;
   - shared zone failures separated from node-local failures;
   - task-weighted outage, raw outage, replica count, and distinct failure domains/model.

3. **Chance-constrained real-time inference admission**
   - mean-latency versus `P(T <= deadline)` admission;
   - raw utility, on-time utility, rejection/admission, and deadline-tail reliability;
   - local fallback for rejected tasks so rejection cost remains visible.

4. **Unequal error protection for control state**
   - equal versus critical-component repetition under the same fixed radio budget;
   - component delivery, control cost, safety violations, and high-SNR convergence;
   - UEP is valuable primarily in the communication-limited region.

5. **Correlation-aware multi-connectivity**
   - single link, full packet duplication, and adaptive duplication;
   - explicit link-failure correlation and radio-use accounting;
   - no realized-outcome genie information in the adaptive policy.

6. **Adaptive duplication reliability-resource frontier**
   - exposes the pre-transmission duplication-risk threshold instead of hard-coding one operating point;
   - sweeps threshold under low, medium, and high link correlation;
   - makes the radio-cost/reliability Pareto frontier explicit rather than treating ~1.73 tx/packet as universally optimal.

7. **Multi-connectivity × safety-aware networked control**
   - couples the v3.2 dual-link model to the v3.1 safety-control branch;
   - compares safety violation/control cost against transmissions per control slot;
   - makes packet reliability valuable only through a downstream control outcome.

## Preserved v3.2 extensions

The earlier v3.2 work remains in the release:

- reliability-oriented semantic HARQ;
- mixed control + inference shared-radio scheduling;
- the original storage-sweep correlated failure-domain experiment;
- checkpoint-aware stateful service migration;
- safety-value component/bit allocation.

These are retained with their original modules, tests, CSV/PNG artifacts, Dashboard Labs, and negative/crossover results.

## Selected results

- **Prediction-churn crossover:** with forecast-noise scale 0, predictive migration gives about **22.38 ms** mean latency and **4.55%** migration rate. At noise 1.0, migration rate rises to about **21.30%** and mean latency reaches **24.22 ms**, worse than reactive migration at about **22.99 ms**. The predictive policy still has a slightly lower deadline-miss rate, so mean latency and reliability do not cross at exactly the same point.
- **Failure-domain diversity:** at **10% shared zone-failure probability**, task-weighted model outage is about **8.88%** for popularity placement and **8.23%** for criticality placement, versus **3.55%** for diversity-risk placement. The diversity policy uses fewer replicas on average but spreads them across about **2.33 distinct domains/model**.
- **Chance admission:** at jitter scale **0.75**, mean-latency admission accepts all tasks and misses about **1.26%** of admitted deadlines. The 99%-chance policy admits about **55.2%**, holds admitted deadline misses to about **0.38%**, and makes the utility/rejection trade-off explicit.
- **Control UEP:** at **-4 dB**, equal protection has mean control cost about **1.95**, while critical-component UEP is about **0.55** under the same five-repetition budget. By **12 dB**, the costs converge to about **0.116 vs 0.115**, so the low-SNR advantage largely disappears.
- **Multi-connectivity correlation:** with independent paths, full duplication reduces packet outage from roughly **66.6% single-link** to **45.1%** in this deliberately communication-limited stress setup. At correlation **0.95**, full-duplication outage rises to about **60.9%**. Adaptive duplication uses about **1.73 transmissions/packet**; at zero correlation its outage is about **48.8%**, accepting a modest gap to full duplication to avoid unconditional 2x radio use.
- **Duplication-budget frontier:** at correlation 0.1, moving from ~1.00 to ~1.73 tx/packet reduces outage from about **66.5% to 50.2%**; at correlation 0.9 the same radio increase only reduces outage from about **66.8% to 60.9%**. The frontier therefore flattens sharply as path failures become correlated.
- **Downstream safety coupling:** at zero link correlation, adaptive control-packet duplication uses about **1.58 transmissions/slot** and reaches essentially the same finite-run safety-violation rate as full duplication in the supplied trace, while full duplication uses exactly **2.0 transmissions/slot**. As correlation increases, both lose safety benefit.

## Negative results and operating boundaries

- Predictive migration becomes worse in mean latency once forecast error creates excessive migration churn.
- A replica count is not a reliability metric when replicas share a failure domain.
- Chance constraints can protect the deadline tail only by rejecting/offloading fewer tasks; at very high jitter, the policy becomes deliberately conservative.
- UEP does not retain a meaningful advantage once one-shot component delivery is already reliable.
- Full packet duplication is not equivalent to independent-path diversity; correlation can erase much of its reliability gain.
- Adaptive duplication is not universally equal to full duplication; it intentionally accepts a small reliability gap to save radio resources.


## Release acceptance

- one-command release acceptance: **passed**;
- v3.2 experiment suite: **12 / 12 completed**;
- full pytest: **230 / 230 passed**;
- pytest with manually supplied `PYTHONPATH` removed: **230 / 230 passed**;
- distribution/runtime version: **3.2.0 / 3.2.0**;
- `compileall`: **passed**;
- result inventory: **196 CSV + 343 PNG = 539 SHA-256 verified artifacts**.

## Scientific boundaries

All v3.2 additions are transparent NumPy/SciPy simulation baselines. Failure forecasts, edge latency distributions, zone failures, control plants, and dual-link correlation are synthetic. CommLab does not claim 3GPP/IEEE conformance, production edge traces, real industrial Digital Twin measurements, certified safety control, or trained large-model benchmarks.
