# CommLab — Wireless Communication Systems Laboratory

> **v3.7.1 Desktop:** Windows double-click launcher, localhost lifecycle control, PyInstaller portable build, Inno Setup installer, and automated Windows artifact workflow. The v3.7 numerical research results are unchanged.

**Current package/runtime:** `3.7.1`. Windows packaging acceptance is recorded in `docs/release_acceptance_v3.7.1.md`.

> **v3.7:** propensity uncertainty, logging drift, hidden-confounding stress tests, cross-fitted nuisance estimation, empirical odds-envelope sensitivity diagnostics, and baseline-aware fallback selection.

**v3.7 research baseline:** package/runtime `3.7.0`; formal acceptance passed with 287/287 tests twice, a six-experiment suite, compileall, and 628 SHA-256-verified result artifacts.

> **v3.6:** safe offline counterfactual reliability evaluation. v3.6 logs known action propensities and compares DM, IPS, SNIPS, DR, and clipped DR while explicitly reporting effective sample size, support violations, temporal-estimand drift, and policy-selection regret. Critical tasks are never logged without protection.

**Current package/runtime:** `3.6.0`. Formal acceptance passed with 268/268 tests twice, a six-experiment suite, compileall, and 610 SHA-256-verified result artifacts.

> **v3.5:** counterfactual observability and protected-outcome masking. v3.5 separates final protected outcomes, hidden unprotected evaluation outcomes, delayed component telemetry, and routine-only audits to test whether a resilience controller can still perceive primary risk after its own protection actions hide failures.

**Current package/runtime:** `3.5.0`. Formal acceptance passed with 252/252 tests twice, a six-experiment suite, compileall, and 592 SHA-256-verified result artifacts.

> **v3.4:** adaptive risk-control orchestration. v3.4 closes the loop around the v3.3 resilience budget: delayed observed misses update global or per-criticality risk debt under distribution drift, while feedback delay, adaptation gain, tail latency, calibration error, resource feasibility, and radio correlation are measured explicitly.

**Current package/runtime:** `3.4.0`. Formal v3.4 acceptance passed with 243/243 tests (twice, including no-manual-`PYTHONPATH`), a six-experiment suite, compileall, and 574 SHA-256-verified result artifacts.

> **v3.3:** unified resilience-budget orchestration. The v3.2 release is preserved intact; v3.3 couples proactive migration, failure-domain replicas, and correlation-aware radio duplication under one finite reliability budget, with explicit forecast-uncertainty and excess-budget failure regions.

> **v3.2:** predictive resilience and reliability orchestration. The release adds forecast-aware failure migration, failure-domain diversity, chance-constrained inference admission, control-state UEP, correlation-aware multi-connectivity, and multi-connectivity × safety-control coupling, while preserving the earlier v3.2 semantic HARQ / mixed-service / checkpoint / precision-allocation work.

**CommLab** (Python package/repository name: `commlab-ofdm`) is a modular wireless-communication research and engineering simulator. OFDM remains the backbone, but the platform now spans waveform/receiver design, MIMO, coding/HARQ, RF impairments and linearization, high mobility/OTFS, link adaptation, packet scheduling, information-theoretic studies, communication-centric sensing, edge intelligence, semantic/task-oriented communication, and networked control.

Current release: **v3.7.1 Desktop / package 3.7.1**.

## Windows desktop edition

CommLab now includes a double-click desktop launcher. It starts the local simulation server on a dynamically selected `127.0.0.1` port, waits for a health check, opens the Dashboard, exposes reopen/copy-address controls, writes a local diagnostic log, and stops the child process when the control window closes. The Windows build workflow produces a portable ZIP and an installer with Start Menu and optional Desktop shortcuts. See [the Windows desktop guide](docs/windows_desktop_v3.7.1.md).

## v3.7 at a glance

v3.7 asks what happens when the propensity used by offline evaluation is not known exactly. It compares synthetic true, nominal recorded, stale recorded, fully estimated, cross-fitted, and misspecified propensities while a hidden severity variable can affect both protection choice and outcome.

At hidden-confounding strength 0.8, true-propensity DR has about **0.31 percentage-point** mean error, nominal recorded propensity about **0.54**, cross-fitting about **0.63**, and stale metadata about **1.02**. Observable drift can be re-fit, but hidden confounding remains. The sensitivity envelope can recover aggregate empirical coverage at modest gamma only by widening rapidly, and its strict policy selector falls back to baseline in all supplied runs. These are diagnostics, not causal or safe-improvement guarantees.

## v3.6 at a glance

v3.6 evaluates alternate protection policies from historical, action-dependent logs. It distinguishes a plausible numerical estimate from an identified value: deterministic logging and the critical-task safety rule can leave target actions outside support, and no estimator silently repairs that absence.

At 0.5% exploration, effective sample fraction is only about **4.53%** and maximum importance weight about **110.8**; at 10% exploration they improve to **43.98% / 6.04**. Under strong drift, a full-history estimate misses current weighted risk by about **14.39 percentage points**, while the latest 20% window reduces the error to about **0.54 points**. A conservative selection heuristic avoids some small-sample errors but falls back to baseline in every supplied run, exposing the opportunity cost of excessive caution.

## v3.5 at a glance

v3.5 studies action-dependent feedback. Outcome-only learning sees a task success when duplication or a replica rescues a failed primary component, while component telemetry and routine-only audits can reveal more of the underlying risk. Critical tasks are never audited, and hidden counterfactual outcomes remain evaluation-only.

Selected findings: protection budget raises the fraction of masked base failures from about **8.1% to 28.5%** while outcome-only learned debt falls from **0.086 to 0.037**; component telemetry improves radio-drift weighted miss from about **18.80% to 16.81%**, but does not dominate under edge or mixed drift; and when telemetry is absent, a hybrid controller using about **5.37% routine audits** improves weighted miss from **27.16% to 25.77%**. At high radio correlation, richer feedback cannot replace missing path diversity.

## v3.4 at a glance

v3.4 adds a transparent online feedback layer to the unified resilience orchestrator. `point_greedy` trusts stale risk estimates, `static_guard` adds a fixed margin, `adaptive_global` updates one delayed risk debt, `adaptive_local` keeps separate routine/important/critical debts, and `oracle` is a clairvoyant-risk diagnostic that still cannot see realized outcomes.

The feedback structure is inspired by adaptive/conformal risk-control research, but CommLab makes no conformal guarantee: actions change the losses, feedback is delayed, tasks are temporally dependent, and all traces are synthetic.

### Selected v3.4 findings

- At drift strength **0.8**, adaptive-local lowers post-drift weighted miss from about **20.62%** for point-greedy to **16.56%**, but spends about **0.636 vs 0.223 credits/task**. At zero drift the reliability gap is small while adaptive spend is roughly doubled.
- Localized control is not universally better. At only **0.35 available credits/task**, adaptive-local is worse than point-greedy (**34.73% vs 31.58%** weighted miss). At 1.0 credits it becomes better than global feedback (**24.22% vs 27.44%**) and protects the critical class more effectively than global debt.
- Adaptation gain has an interior operating region. A gain around **0.015** gives about **22.91%** post-drift weighted miss; no adaptation is about **30.17%**, while more aggressive gains increase spend and switching without monotonic reliability improvement.
- One-task feedback is not automatically best: an 8-task delay slightly outperforms immediate feedback in the supplied stochastic trace, while very long delay degrades early post-drift response. Feedback can act as both information and noise.
- Tightening the requested miss target can backfire under a hard resource cap. The 5% setting spends about **0.92 credits/task** yet performs worse than the 13–16% settings; requested risk is not the same as feasible risk.
- As radio correlation rises from **0 to 0.95**, adaptive-local cuts duplication from about **66.0% to 6.9%** and raises replica use, yet post-drift weighted miss worsens from about **17.87% to 26.50%**. Online feedback cannot manufacture absent diversity.

## v3.3 at a glance

v3.3 couples proactive edge migration, cross-failure-domain replica execution, and correlation-aware dual-radio duplication under one finite normalized resilience budget. The runtime reports physical resource proxies separately and can refuse to spend low-confidence excess credits.

Formal validation: **236/236 tests passed**, including a second run with manual `PYTHONPATH` removed. Result inventory: **202 CSV datasets, 354 PNG figures, 556 SHA-256 verified result artifacts**. The six new v3.3 Monte Carlo experiments run as isolated subprocesses in one suite.

### Selected v3.3 findings

- In the mixed budget sweep, task-weighted deadline misses fall from about **22.17%** without proactive credits to **12.28% at 0.6 credit/task**, **9.57% at 1.0**, and **7.47% at 1.2**, while radio/compute/migration overhead rises.
- The unified policy changes mechanism with the failure regime: the radio-limited case spends essentially all actions on duplication; in the edge-limited/radio-good case duplication falls to about **3.8%** while cross-domain replica execution rises to about **62.6%**.
- At forecast-noise **1.1**, uncertainty gating suppresses proactive migration from about **1.68%** to essentially zero and reduces migration traffic from about **5.14 to 3.70 MB/task**, with better task-weighted deadline reliability in that noisy regime. At low noise the same gate can be slightly worse.
- Raising radio-path correlation from **0 to 0.95** redirects budget: duplication drops from about **96.9% to 65.2%**, while replica execution rises from about **2.0% to 22.3%**. Reliability still worsens because the runtime cannot manufacture missing radio diversity.
- Excess budget exposes a failure region. At **2.2 available credits/task**, ungated orchestration spends about **1.84**, proactively migrates about **15.5%** of tasks, and performs worse than at 1.8 credits; uncertainty gating saturates near **1.48 credits/task** and refuses low-confidence extra actions.
- Task-criticality weighting alone does **not** dominate its unweighted counterpart across all budgets; the myopic failure-risk proxy does not fully represent deadline consequence.

## v3.2 at a glance

v3.2 is organized around a single systems question: **what happens when reliability decisions depend on imperfect forecasts, correlated failures, deadline tails, unequal task value, and non-independent radio paths?** Existing v3.2 work is retained rather than replaced.

Formal release validation: **230/230 tests passed**. Result inventory: **196 CSV datasets, 343 PNG figures, 539 SHA-256 verified result artifacts**. The 12-experiment v3.2 suite, editable-install validation, no-`PYTHONPATH` regression, compileall, manifest verification, and ZIP integrity checks are part of the release process.

### Selected v3.2 findings

- Predictive migration has a real **prediction-churn crossover**. At forecast-noise 0, mean latency is about **22.38 ms** with **4.55%** migrations. At noise 1.0, migration rate rises to about **21.30%** and mean latency to **24.22 ms**, worse than reactive migration at about **22.99 ms**.
- At **10% shared zone-failure probability**, task-weighted model outage is about **8.88% popularity / 8.23% criticality / 3.55% diversity-risk**. The diversity policy achieves this with about **2.33 distinct failure domains/model**, showing that replica count and reliability are not equivalent.
- At latency-jitter scale **0.75**, mean-latency inference admission accepts every task and misses about **1.26%** of admitted deadlines. A 99%-chance policy admits about **55.2%** and holds admitted deadline misses to about **0.38%**.
- With the same five-repetition control-state budget at **-4 dB**, equal protection has mean control cost about **1.95** while critical UEP is about **0.55**. By **12 dB**, both are near **0.115**, so the UEP advantage nearly disappears.
- In a deliberately communication-limited dual-link stress test, full duplication outage rises from about **45.1% at zero link correlation** to **60.9% at correlation 0.95**. Adaptive duplication uses about **1.73 transmissions/packet**, accepting a small reliability gap to avoid unconditional 2x radio use.
- The adaptive duplication threshold exposes a reliability-resource frontier: at correlation **0.1**, moving from about **1.00 to 1.73 tx/packet** reduces outage from roughly **66.5% to 50.2%**; at correlation **0.9**, the same radio increase only reaches about **60.9%** outage. Extra redundancy has sharply diminishing value when path failures are correlated.
- Coupling multi-connectivity to safety-aware control shows why packet outage is not the final objective: at zero correlation, adaptive duplication uses about **1.58 transmissions/control slot** and reaches the same finite-run safety-violation count as full duplication, which uses **2.0 transmissions/slot**.

### Preserved v3.2 extensions

The earlier v3.2 semantic HARQ, mixed control/inference scheduling, storage-sweep failure-domain replication, checkpoint-aware service migration, and safety-value bit allocation remain included with their modules, tests, experiments, figures, Dashboard Labs, and documented negative results.

## Selected v3.1 findings

- Safety-aware feedback is **regime dependent**. Around -3 to +1 dB it slightly reduces explicit state-bound violation probability versus max-error scheduling, while extreme communication scarcity can erase that advantage.
- At 0 dB, adaptive feature precision + model depth reaches about **83.1% on-time task accuracy**, compared with about **67.9%** for fixed-light and **65.3%** for fixed-deep operation; at 10 dB the fixed deep model catches up.
- At 12% task failure probability, restart/checkpoint/dual-execution P95 completion latency is roughly **226.7 / 162.0 / 132.7 ms**. Dual execution is fastest but consumes about **2x compute**; checkpointing is not worthwhile when failures are very rare.
- With a 3.2 GB model-replica budget, risk-aware placement cuts **task-weighted model outage from about 1.35% to 0.46%** by protecting critical models rather than only popular ones.
- At -3 dB, component-value feedback obtains mean control cost about **0.61** with 7 bit/slot, versus about **9.88** for round robin and **3.59** for uniform low-precision whole-state transport.

## v3.0 at a glance

v3.0 extends CommLab toward **risk-sensitive and reliability-aware communication-computation-control orchestration**: empirical CVaR wireless scheduling, variable-rate predictive state updates, failure/trust-aware edge placement, joint model caching/inference offloading, and cooperative multi-agent feedback control.

Validation: **213/213 automated tests passing**. Release inventory: **179 CSV datasets, 309 figures, 488 SHA-256 verified result artifacts**. The v3.0 experiment suite reproduces in one command, with independent package-version/import and compile checks.

### Selected v3.0 findings

- Tail-risk protection has a **regime** rather than universal dominance: the risk scheduler lowers empirical CVaR in the intermediate/high shock-severity region, while mild and extreme settings expose the cost of unnecessary or over-aggressive protection.
- Predictive innovation updates create a real precision/deliverability crossover: adaptive 3/6/10-bit state packets help under constrained links, while fixed high precision becomes preferable once SNR is ample.
- Risk-aware edge placement reduces execution failures/deadline misses when the lowest-radio-latency node is deliberately less reliable, at a modest average-latency premium.
- Cache hit rate can be misleading: cache-first inference routing can concentrate requests and create severe edge queues; joint cache/offload control prices both cache misses and compute congestion.
- In coupled multi-agent control, system-level update value helps mainly in the communication-limited regime; with reliable links, simpler local-error scheduling can be the better baseline.

## v2.9 at a glance

v2.9 extends CommLab toward **state-value-aware edge orchestration and networked control**: task-conditioned model repair, explicitly congested model refresh, battery/carbon/fairness-constrained federated learning, digital-twin-guided model prefetch, and wireless scheduling for multiple feedback-control loops.

Validation: **207/207 automated tests passing**. Release inventory: **174 CSV datasets, 299 figures, 473 SHA-256 verified result artifacts**.

### Selected v2.9 findings

- At matched downlink load around **0.290/round**, task-aware repair reaches realized/ideal task utility about **0.792** at burst strength 2.4 versus **0.697** for age-only repair, because current inference demand changes the value of model freshness.
- With only **0.8 MB/request** refresh-backhaul service, eager refresh serves models about **10.36 versions old** and builds a **~579 MB** P95 queue; congestion-aware refresh reduces these to about **7.75 versions / 416 MB**. At high backhaul capacity, the simpler periodic-value policy can again be competitive or better.
- Under severe battery starvation, scheduling heuristics have little freedom because most clients are energy-infeasible. Once harvesting becomes adequate, carbon-only client selection can reintroduce persistent data/participation bias; virtual-debt/battery-aware scheduling restores learning quality and fairness at higher carbon cost.
- At digital-twin uncertainty **0.8**, blind model prefetch produces about **45.6% wrong prefetches** and roughly **97 GB** of modeled transfer, whereas uncertainty gating cuts them to about **15.4% / 12 GB** while retaining most latency benefit over reactive loading.
- At **-4 dB** sensor-link SNR, Max-Age scheduling achieves fresher information (~**18.8 slots**) than control-value scheduling (~**22.2**) yet incurs mean closed-loop cost about **124** versus **14.3**. Freshness and physical control value can be sharply misaligned.

## v2.8 at a glance

v2.8 extends CommLab toward **state-aware closed-loop runtime control**: selective FL downlink repair, model-version-aware edge caching, persistent fairness/carbon orchestration, admission control for progressive inference, and digital-twin semantic synchronization.

Validation: **200/200 automated tests passing**. Release inventory: **169 CSV datasets, 289 figures, 458 SHA-256 verified result artifacts**.

### Selected v2.8 findings

- Selective per-client model repair is **regime dependent**. At low/mid SNR, broad differential-chain failure makes common keyframes more efficient. Around 10 dB and at essentially the same downlink load (~0.274/round), selective-age repair lowers weighted model-version age from about **8.87 to 7.45 rounds** and weighted model MSE from **0.704 to 0.579**.
- Edge cache hits can be stale. Popularity caching reaches about **80% hit rate** but serves versions roughly **10.3 updates old** on average. A version-aware policy with a hard 180 MB refresh budget/epoch raises task utility from about **0.54 to 0.86**, while fully reactive LRU achieves freshness only by incurring roughly **163 GB** modeled backhaul in the same workload.
- Persistent virtual participation debt exposes the carbon price of long-run fairness. With debt weight 8, participation Jain fairness is about **0.99** and excess loss about **0.0017**, but the carbon proxy rises from the carbon-only policy's ~207 to about **523**.
- Progressive-inference admission control prevents overload collapse. At 0.8 arrivals/slot, backpressure admission raises on-time task utility from about **0.528 to 0.676** and cuts deadline miss rate from **41% to 21%**; at extreme overload a simple hard backlog gate becomes more robust.
- In the digital-twin toy system, a 1.5-error-trigger semantic delta gives position RMSE about **0.63** at normalized radio load **0.0068/slot**, versus about **0.84** at load **0.090/slot** for triggered full-state packets under the same packet-size-dependent outage abstraction.

## v2.7 at a glance

v2.7 turns the Wireless Edge Intelligence branch toward **runtime orchestration and state-aware control**: budgeted differential downlink resynchronization, carbon-aware FL client orchestration, AI-model caching and inference routing, queue-aware progressive split inference, and importance-aware multicast repair.

Validation: **195/195 automated tests passing**. Release inventory: **162 CSV datasets, 279 figures, 441 SHA-256 verified result artifacts**.

### Selected v2.7 findings

- At a common 7 dB blockage penalty, fixed 5-round keyframes and the budgeted-age controller use almost the same normalized downlink size (`~0.354/round`), but the adaptive controller reduces mean client model age from about **19.27 to 16.20 rounds** and model MSE from about **1.55 to 1.27**, while sending fewer full keyframes.
- Carbon-only FL orchestration cuts the modeled carbon proxy from roughly **325 to 136**, but creates severe participation/data-group bias and raises excess optimization loss to about **0.50**. A balanced controller around carbon weight `0.75-1.0` lowers carbon cost while keeping excess loss near **0.009-0.010**.
- Under drifting AI-model popularity, periodic value-density caching reaches about **32.6 ms** mean inference latency versus **33.4 ms** for popularity-only caching, while using less model-loading backhaul. Pure LRU incurs extremely large cache churn/backhaul despite a reasonable hit rate.
- In a shared progressive-inference radio queue, naive deadline/value preemption can fragment many partially served requests. A completion-aware controller improves on-time task utility in the moderate-load region and exposes a completion-locality effect absent from ordinary packet scheduling.
- Aggressive multicast without repair uses only about **11%** of conservative full-common airtime but increasingly underserves high-value weak clients. Selective importance-aware repair recovers weighted task utility to roughly **0.65-0.84** while staying within the full-common airtime budget; repairing every miss can exceed **3.8x** that airtime.

## v2.6 at a glance

v2.6 extends the Wireless Edge Intelligence branch toward **learning-aware AirComp user selection, progressive real-time split inference, differential downlink model synchronization, energy-harvesting OTA-FL, and task-importance-aware model multicast**.

Validation: **190/190 automated tests passing**. Release inventory: **155 CSV datasets, 269 figures, 424 SHA-256 verified result artifacts**.

### Selected v2.6 findings

- Strongest-channel OTA client selection can minimize analog aggregation noise yet heavily bias non-IID participation and worsen global learning loss.
- Progressive split inference can outperform full residual offload on **on-time accuracy** when a poor wireless link makes full offload miss hard deadlines.
- Differential model broadcast creates a state-synchronization problem: chained deltas are cheap but fragile to a missed update; periodic anchor/keyframe packets trade more downlink load for faster recovery.
- Energy-harvesting OTA-FL changes operating regimes: under starvation all schedulers are battery-limited; with abundant energy, fairness/data-diversity control becomes important again.
- Importance-aware layered model multicast can justify a small airtime increase to serve weak but high-value clients instead of treating SNR as the only scheduling objective.

## v2.4 at a glance

v2.4 extends the Wireless Edge Intelligence branch toward **personalization, straggler resilience, knowledge distillation, hard real-time inference, and one-bit distributed aggregation**:

- **Personalized FL** blends a pooled global model with finite-sample client-local models and evaluates held-out generalization as non-IID heterogeneity changes.
- **Straggler-resilient coded compute** compares uncoded synchronization, task replication, and MDS-style K-of-N recovery using mean/P95/P99 round latency plus redundant-compute cost.
- **Federated distillation** replaces full parameter-vector upload with noisy logits on a shared public probe set and measures task accuracy against scalar communication budget.
- **Channel-aware split inference** includes per-sample wireless quality and a hard deadline, separating raw accuracy from on-time task accuracy.
- **One-bit OTA sign aggregation** studies client-count/SNR scaling and sign-flipping-client breakdown of a synchronous analog majority vote.
- Streamlit adds **Personalized FL**, **Straggler-Resilient FL**, **Federated Distillation**, **Channel-Aware Split**, and **OTA Sign Aggregation** labs.

Validation: **180/180 automated tests passing**. Release inventory: **144 CSV datasets, 253 figures, 397 SHA-256 verified result artifacts**.

### Selected v2.4 findings

- The optimal personalization weight rises with client heterogeneity: homogeneous data favor the global model, while moderate heterogeneity produces an interior global/local blend and strong heterogeneity moves toward local specialization.
- At 15% modeled stragglers, uncoded P95 round latency is about **276 ms**; MDS-style K+4 recovery reduces it to about **43.7 ms** at **1.33x** compute load.
- At 10 dB, eight public-probe logits/client use one third of the scalar upload of a 24-D model vector and achieve about **92.6%** accuracy versus about **95.5%** for full model averaging; twelve probes reach about **94.3%** at half the scalar count.
- Under a 1.8 ms deadline and 5 dB mean residual-link SNR, static confidence offload has about **85.9% raw accuracy** but roughly **57.6% deadline misses**, giving only **36.9% on-time accuracy**. The channel-aware policy produces about **72.5% on-time accuracy** with zero modeled misses.
- With 31 clients at 5 dB, one-bit OTA sign error is roughly **5.7%** without sign-flipping clients, **12.7%** around 30% sign flips, and **20.7%** around 40%, showing that statistical majority gain is not Byzantine immunity.

## v2.3 at a glance

v2.3 turns the Wireless Edge Intelligence branch toward **resilience, staleness, privacy perturbations, semantic scheduling, and split computing**:

- **Asynchronous FL** evaluates naive stale gradients, exponential staleness weighting, and an exact quadratic correction baseline on delayed client updates.
- **Byzantine-robust FL** compares mean, coordinate median, and trimmed-mean aggregation under sign-flip/scaling attacks and exposes their breakdown regions.
- **Private AirComp FL** combines clipped client gradients, DP-style Gaussian perturbations, and analog wireless aggregation while explicitly avoiding unsupported epsilon/delta claims.
- **Semantic resource scheduling** compares channel-first, importance-first, value-per-resource, and urgency-aware policies for expiring task packets.
- **Split inference** uses local early classification and confidence-triggered residual-feature offload to expose accuracy, channel-use, and latency trade-offs.
- Streamlit adds **Async Federated Learning**, **Byzantine-Robust FL**, **Private AirComp FL**, **Semantic Resource Scheduler**, and **Split Inference** labs.

Validation: **175/175 automated tests passing**. Release inventory: **139 CSV datasets, 243 figures, 382 SHA-256 verified result artifacts**.

### Selected v2.3 findings

- **Stale gradients rotate away from the current descent direction:** with mean modeled staleness 8 updates, the stale/current gradient cosine falls to about `0.67`; naive asynchronous FL worsens, while exponential staleness weighting remains close to the fresh-update operating point.
- **Robust aggregation has a breakdown point:** at about 13% sign-flip/scaling attackers, ordinary mean aggregation diverges dramatically, while coordinate median and trimmed mean remain near the no-attack objective. At larger attacker fractions, trimmed mean eventually fails as expected.
- **Privacy perturbation becomes the high-SNR floor:** once wireless AirComp noise is small, increasing client Gaussian perturbation dominates aggregation MSE and learning loss. The experiment is a privacy-noise utility baseline, not a formal differential-privacy accountant.
- **Semantic priority matters most under scarcity:** with only 3-6 resources/slot, value-per-resource and urgency-aware scheduling deliver higher task utility than channel-first scheduling; once resources become plentiful, channel-first catches up and can become best.
- **Split inference exposes an accuracy/communication/latency Pareto:** around 10 dB, local-only accuracy is roughly `77.3%`, full residual offload about `91.3%`, while a mid confidence threshold reaches about `88.9%` using roughly `5.43/12` residual feature uses on average.


## v2.1 at a glance

v2.1 asks what happens when **communication efficiency, client participation, learning objectives, CSI uncertainty, and multiple downstream tasks do not align**:

- **Non-IID FL client selection** deliberately correlates local-data groups with long-term channel quality and compares random, strongest-channel, gradient×channel, and participation-age-aware selection.
- **Random-access FL** lets ALOHA/IRSA decoding determine which client updates actually enter a federated round.
- **Robust RIS-AirComp** evaluates point-estimate versus uncertainty-sampled finite-bit phase control under imperfect CSI.
- **Cell-Free AirComp CSI-risk control** adds heterogeneous AP estimation quality and lower-confidence-bound combining.
- **Multi-task task-oriented communication** compares raw features, task-specific sufficient statistics, and shared rank-1/rank-2 semantic subspaces.
- Streamlit adds **Non-IID FL Client Selection**, **Random-Access FL**, **Robust RIS AirComp**, **Cell-Free AirComp CSI Risk**, and **Multi-Task Semantic** labs.

Validation: **160/160 automated tests passing**. Release inventory: **127 CSV datasets, 223 figures, 350 SHA-256 verified result artifacts**.

### Selected v2.1 findings

- **Wireless-quality selection can bias non-IID learning:** with a 12 dB channel disparity correlated with two client groups, strongest-channel selection gives about **98.3%** of participation to the stronger group and raises the final global objective to about **0.464**, versus about **0.257** for random participation. Participation-age weighting recovers much of the fairness and brings the objective back to about **0.281**, at the cost of weaker selected links.
- **Access graphs have a learning threshold:** the tested IRSA repetition law completely collapses in an 8-slot / 20-client high-load regime, but decodes about **87%** of active clients by 24 slots. The convex FL toy remains tolerant to random subsampling until empty-round probability becomes dominant.
- **Robust RIS is not automatically better:** uncertainty-sampled max-min control improves mean true weakest-device gain around relative CSI errors `0.2-0.3` in the tested Monte Carlo, but at very high uncertainty its lower tail can still degrade.
- **Cell-Free tail-risk control:** under strongly heterogeneous AP CSI quality, a lower-confidence-bound combiner can reduce p90 aggregation MSE (for example around worst-AP error `.5`, from roughly `1.35e-3` to `1.00e-3`) while smaller-error regimes can show negligible median gains.
- **Multi-task semantic conflict:** at 10 dB, one shared scalar retains about **90.5%** mean accuracy when two tasks align, but falls to about **70.0%** when task directions become orthogonal. A rank-2 shared subspace remains around **90.1%** using two modeled channel uses instead of 16 raw-feature uses.



## v2.0 at a glance

v2.0 is the first release organized around **wireless edge intelligence and task-oriented communication** rather than only adding another PHY/MAC algorithm:

- **Federated learning over AirComp** couples analog gradient aggregation noise, channel-use cost, client truncation, and optimization convergence in a transparent convex linear-regression problem.
- **RIS-assisted AirComp** compares random, sum-channel-power, and AirComp-aware max-min passive-phase objectives and propagates the resulting aggregation quality into FL convergence.
- **Cell-Free AirComp** uses distributed AP reception and a transparent max-min candidate combiner to mitigate the weakest-device bottleneck.
- **Task-oriented communication** uses an analytically controlled Gaussian classification problem to separate task utility from source-reconstruction fidelity.
- **Capture-aware IRSA** combines graph repetition/SIC with a power-domain SINR capture rule, connecting the prior IRSA and grant-free NOMA branches.
- Streamlit adds **AirComp Federated Learning**, **RIS AirComp**, **Cell-Free AirComp**, **Task-Oriented Communication**, and **Capture IRSA** labs.

Validation: **154/154 automated tests passing**. Release inventory: **122 CSV datasets, 213 figures, 335 SHA-256 verified result artifacts**.

### Selected v2.0 findings

- **AirComp-FL communication efficiency:** in the 12-client, 80-round 10 dB toy problem, orthogonal noisy gradient upload consumes `960` modeled channel uses and finishes near loss `0.0476`; full-inversion AirComp consumes `80` uses and finishes near `0.0205`, close to the ideal `0.0201` objective. This is a normalized analog-aggregation experiment, not a wireless FL standard benchmark.
- **Truncation has an interior operating point:** at 5 dB, raising the inversion threshold suppresses deep-fade noise but removes clients. In the tested trace, final loss improves from about `0.0244` at threshold `.1` to about `0.0206` around `.5-.7`, then worsens as participation falls below roughly half the clients.
- **RIS objective mismatch matters:** on the fixed 12-device/24-element channel, 2-bit max-min RIS achieves weakest effective gain about `0.226`, versus `0.146` for sum-gain optimization. The max-min design also gives the best AirComp aggregation MSE and FL convergence, showing that maximizing total channel power is not the correct objective for a weakest-user-limited computation link.
- **Cell-Free AirComp:** with 8 distributed APs, cooperative receive combining lowers median aggregation MSE from about `1.05e-3` for the best single AP to about `4.65e-4`, while remaining a one-shared-use computation abstraction.
- **Task utility vs source fidelity:** at 20 dB, the one-scalar task statistic reaches about `97.6%` classification accuracy versus `97.8%` for all 16 raw features, using 1 versus 16 modeled channel uses. However, the task representation has far worse source reconstruction, deliberately exposing the distinction between task success and signal fidelity.
- **Capture-aware IRSA:** with no received-power spread, capture adds almost nothing to singleton peeling; around 9 dB spread the tested throughput peaks near `0.762 packet/slot`, but excessive load still causes graph/SIC collapse.


## v1.9 at a glance

v1.9 adds four system directions that are intentionally different from the existing OFDM/MIMO/RIS/ISAC branches:

- **IRSA / coded random access** with irregular packet repetition and iterative singleton peeling/SIC.
- **Over-the-Air Computation (AirComp)** for one-shot analog arithmetic-mean aggregation under Rayleigh fading.
- **eMBB / URLLC mini-slot coexistence** with fixed reservation, forecast-based reservation and immediate preemption.
- **Energy-harvesting AoI** with finite batteries and freshness/reliability-aware status scheduling.
- Streamlit adds **IRSA Random Access**, **AirComp Aggregation**, **eMBB-URLLC Slicing**, and **Energy-Harvesting AoI** labs.

Validation: **149/149 automated tests passing**. Release inventory: **116 CSV datasets, 202 figures, 318 SHA-256 verified result artifacts**.

### Selected v1.9 findings

- **IRSA threshold behavior:** the tested `{2:.50, 3:.28, 8:.22}` repetition distribution reaches about `0.651 packet/slot` near `G=.673`, compared with about `0.369` peak throughput for slotted ALOHA. Beyond the peeling threshold, unresolved collision graphs cause a sharp collapse rather than indefinite gain.
- **AirComp:** 20 devices aggregate a 24-D vector in one shared channel use instead of 20 orthogonal uses. At 12 dB, truncated inversion has its best tested mean MSE near channel threshold `|h|=.211`, retaining about `95.4%` of devices. Full inversion is heavy-tailed because the weakest Rayleigh fade controls the common gain.
- **eMBB/URLLC coexistence:** at `0.6 URLLC arrivals/minislot`, fixed 6-PRB reservation wastes about `69.6%` of reserved PRBs, while preemption retains eMBB payload proxy about `66.8` with zero observed deadline misses. At load `2.1`, preemption still protects URLLC but eMBB drops to roughly `53.3`, revealing puncturing cost.
- **Energy-harvesting AoI:** around harvest scale `.243`, age×reliability / energy-aware scheduling reaches mean AoI about `4.1 / 3.9 slots`. With abundant energy (`.65`), max-SNR still delivers almost every slot but mean AoI grows to about `58 slots` because weak users are starved.

## v1.8 at a glance

v1.8 turns several previously separate resource-control ideas into explicit **budget, deadline, freshness, event-trigger, and random-access** studies:

- **Joint Cell-Free CSI refresh + bit allocation** under one hard fronthaul bit budget, with predictive innovation feedback.
- **Deadline-aware finite-blocklength IR-HARQ scheduling**, comparing PF, EDF, and a reliability/urgency risk score.
- **Age of Information (AoI)** status-update scheduling with fresh retransmission versus Chase-style HARQ state.
- **Event-triggered RIS control**, refreshing passive phases only after measured utility degradation or a maximum control age.
- **Long-term budget-constrained ISAC sensing**, using a cumulative sensing-token constraint and adaptive allocation across maneuver phases.
- **Grant-free random access / ideal power-domain NOMA-SIC** for massive short-packet access.
- Streamlit adds **Joint CSI Budget**, **Deadline HARQ**, **Age of Information**, **Event-triggered RIS**, **Budgeted ISAC**, and **Grant-free NOMA** labs.

Validation: **145/145 automated tests passing**. Release inventory: **111 CSV datasets, 194 figures, 305 SHA-256 verified result artifacts**.

### Selected v1.8 findings

- **Joint CSI control:** at channel correlation `.98` and a `96 bit/slot` budget, mean CSI NMSE is about `0.0913` for round-robin, `0.0749` for fixed-bit uncertainty scheduling, and **`0.0324` for joint refresh/bit allocation**. The joint scheme also reaches edge rate about `0.916 bit/s/Hz` while respecting the same hard budget.
- **Deadline-aware HARQ:** at arrival probability `.16/user/slot`, PF has about `5.73%` deadline misses and goodput `0.942`; EDF cuts misses to `1.95%` but goodput is `0.943`; the risk-aware score gives `2.56%` misses and the highest of the three goodputs in that trace, about `0.950 bit/channel-use`.
- **AoI:** at status rate `1 bit/use`, fresh max-age scheduling has mean AoI about `29.8 slots`, while fresh age×reliability scheduling lowers it to `9.90`. Chase retransmission changes the operating point again: max-age reaches about `5.22`. Max-SNR has near-one successful transmission per slot but mean AoI around `139` because weak users are starved.
- **Event-triggered RIS:** on a trace with a fast-fading middle segment, a 3% rate-drop trigger reaches mean sum-rate about `3.811 bit/s/Hz` at `3.73 control bit/slot`, outperforming fixed 4-slot refresh (`3.751` at `4 bit/slot`).
- **Budgeted ISAC:** with a 5% long-term sensing ceiling, actual average use is about `3.96%`, but sensing concentrates strongly in the rising-maneuver segment (`~9.7%`) and falls below 1% in calm segments.
- **Grant-free NOMA:** with received-power spread `8 dB` and offered load about `.90 attempt/resource/slot`, collision-only access decodes about `7.40 packets/slot`; ideal SIC decodes about **`14.54`**. With zero power spread, the two schemes coincide, exposing the need for power-domain separability.






## v1.7 at a glance

v1.7 focuses on **temporal information management and cross-layer resource timing** rather than adding more waveform names:

- **Fixed-budget asynchronous Cell-Free CSI refresh** with round-robin, pure uncertainty, and age-bounded uncertainty scheduling.
- **Predictive / differential CSI quantization**, exploiting Gauss-Markov temporal correlation at the same scalar bit depth.
- **Finite-blocklength incremental-redundancy HARQ** versus Chase combining with explicit channel-use and queue-delay costs.
- **Two-timescale RIS-assisted Cell-Free control**, separating fast AP precoding from slower passive-phase updates and adding RIS phase noise.
- **Queue-aware ISAC sensing-on-demand**, including a two-slot predictive controller that trades packet backlog against future angle uncertainty.
- Streamlit adds **Async Cell-Free CSI**, **Predictive CSI Compression**, **Two-timescale RIS**, **FBL IR-HARQ**, and **Queue-aware ISAC** labs.

Validation: **134/134 automated tests passing**. Release inventory: **105 CSV datasets, 182 figures, 287 SHA-256 verified result artifacts**.

### Selected v1.7 findings

- **Asynchronous CSI:** at 4 AP refreshes/slot, round-robin gives edge rate `0.777` with CSI NMSE `0.245`; pure uncertainty reduces NMSE to `0.060` but collapses edge rate to `0.319` because some APs age for hundreds of slots. The bounded-uncertainty variant recovers edge rate to `0.721` while keeping NMSE at `0.076`.
- **Predictive CSI compression:** with 3-bit/component scalar quantization, innovation coding improves CSI NMSE by about `4.2 dB` at correlation `.8`, `9.1 dB` at `.95`, `13.1 dB` at `.98`, and `19.1 dB` at `.995`.
- **IR-HARQ:** at mean SNR `-2 dB`, Chase goodput is about `0.452 bit/channel-use` with 10 observed drops; incremental redundancy reaches `0.581`, zero observed drops, and mean rounds `3.32 -> 2.58`. At high SNR the curves merge because retransmissions are rare.
- **Two-timescale RIS:** per-slot 2-bit control of 6 RIS elements costs `12 control bit/slot` and reaches mean sum-rate `4.67`; updating every 4 slots reduces control to `3 bit/slot` while retaining about `4.56`.
- **Queue-aware ISAC:** under the overloaded trace, tracking-only control uses `15%` sensing and leaves about `4.42k` final backlog bits; queue-aware control uses about `9.2%`, raises delivered payload, and reduces final backlog to about `3.76k` at the cost of higher angle uncertainty.

## v1.6 at a glance

v1.6 couples uncertainty, mobility, packet reliability, sensing resource control, and deployment energy into four deeper system studies:

- **Aged + quantized CSI for RIS-assisted Cell-Free control**, separating RIS phase resolution from CSI-fronthaul precision and evaluating stale, sample-average robust, random, and current-CSI baselines.
- **Finite-blocklength multi-user queue + Chase HARQ + OLLA**, where each retransmission consumes explicit channel uses and packet success follows the normal approximation rather than a free reliability flag.
- **Predictive sensing-on-demand**, adding a transparent two-step value-of-information lookahead to the prior myopic sensing/beamwidth controller.
- **Joint Cell-Free fronthaul-energy simulation**, combining AP activation, quantized periodic CSI updates, channel aging, circuit power and per-bit fronthaul energy.
- Streamlit adds **Cell-Free Fronthaul Energy**, **Cell-Free RIS Aging**, **Predictive Sensing-on-Demand**, and **FBL HARQ Queue** labs.

Validation: **124/124 automated tests passing**. Release inventory: **100 CSV datasets, 172 figures, 272 SHA-256 verified result artifacts**.

### Selected v1.6 findings

- **RIS CSI precision / aging:** with common channel draws at 5-step age, mean sum-rate rises from about `2.83` at 2-bit CSI to `3.15` at 4-bit and `3.19` at 6-bit, then saturates near 8-bit. Under 20-step aging, the sample-average robust design has slightly lower mean rate than stale-CSI coordinate ascent (`2.44` vs `2.49`) but a better 10%-tile (`1.88` vs `1.80`), exposing a mean-versus-tail trade-off rather than universal dominance.
- **FBL queue / HARQ:** at blocklength 120, open-loop operation gives about `0.287 bit/use`, `52.3%` NACK and 182 drops; Chase HARQ reaches `0.370 bit/use`, `24.5%` NACK and zero drops. Adding OLLA lowers NACK to about `8.9%` and keeps zero drops, but its conservative operating point reduces goodput to about `0.289 bit/use`.
- **Predictive sensing:** on a three-segment uncertainty trace, no sensing gives mean net rate `1.64`; myopic sensing `2.49`; two-step predictive `2.60`; a hindsight-tuned fixed 5% sensing policy reaches `2.72`. The predictive controller improves on myopia but is explicitly not globally optimal.
- **Fronthaul-energy / mobility:** for 16 active APs and 6-bit CSI, the modeled energy-efficiency optimum moves from roughly 8-slot updates at `rho=.995` to 4-slot updates at `rho=.98/.95`. In the joint grid at `rho=.98`, the best tested energy-efficiency point is 12 active APs, 6-bit CSI and 4-slot updates (`~5.37 sum-rate/W`), not all-AP/full-refresh operation.

## v1.5 at a glance

v1.5 couples previously separate branches into deployment- and uncertainty-aware system studies:

- **Cell-Free CSI compression / fronthaul accounting** with user-centric clustering and 2/3/4/6/8-bit complex-CSI scalar quantization.
- **CSI aging / update-interval study** using Gauss-Markov channel evolution, exposing CSI freshness versus fronthaul load under slow and fast fading.
- **Robust RIS-assisted Cell-Free optimization under imperfect CSI** using sample-average finite-bit coordinate ascent over an uncertainty ensemble.
- **Finite-blocklength short-packet link adaptation** with an inverted normal approximation, explicit successful-block goodput, and optional OLLA for biased SNR estimates.
- **ISAC sensing-overhead / beamwidth scheduling** that jointly selects sensing time and active ULA aperture from angle uncertainty.
- Streamlit adds **Cell-Free Fronthaul CSI**, **Robust Cell-Free RIS**, **Short-Packet FBL**, and **ISAC Sensing Budget** labs.

Validation: **116/116 automated tests passing**. Release inventory: **94 CSV datasets, 160 figures, 254 SHA-256 verified result artifacts**.

### Selected v1.5 findings

- **CSI compression / clustering:** UC-8 with 4-bit real/imag CSI uses `512 bits/update` and reaches mean 5%-tile rate about `1.49 bit/s/Hz`; 6-bit raises it to `1.57` at `768 bits/update`. Full 24-AP service reaches about `1.69` with 8-bit CSI but costs `3072 bits/update`.
- **CSI aging:** with slow correlation `rho=0.995`, stretching updates from every slot to every 32 slots reduces mean 5%-tile rate `1.79 -> 1.62` while cutting modeled CSI fronthaul `768 -> 24 bits/slot`; under faster `rho=0.97`, the same edge rate falls `1.82 -> 1.05`.
- **Robust RIS:** at CSI uncertainty NMSE `0.20`, naive single-estimate optimization gives held-out mean sum-rate about `4.02`, while sample-average robust optimization gives about `4.56 bit/s/Hz`; at very small uncertainty the robust method is not automatically better.
- **Short packets:** under a `+2.2 dB` SNR-estimation bias and blocklength 120, open-loop goodput is about `1.12 bit/use` with `39.1%` NACK; FBL-aware selection improves to `1.27` with `26.7%` NACK; adding OLLA reaches `1.31 bit/use` near the `1%` target NACK.
- **Sensing budget:** when prior angle uncertainty is `0.5°`, the net-rate optimum uses `0%` extra sensing and 64 elements. At `4°`, the optimum moves to about `15%` sensing and 32 active elements, explicitly trading payload time for beam robustness.

## v1.4 at a glance

v1.4 moves CommLab further toward distributed-network and cross-layer studies rather than adding more modulation formats:

- **Pilot-contamination-aware Cell-Free CSI acquisition** with pilot reuse, per-AP LMMSE estimation, and a transparent large-scale-overlap pilot assignment heuristic.
- **RIS-assisted Cell-Free distributed access** with finite-bit coordinate optimization for either sum-rate or weakest-user rate.
- **Event-driven OLLA + Chase-HARQ + queue scheduling** linking biased SNR estimates, MCS choice, ACK/NACK feedback, retransmission evidence, PF/delay-PF scheduling, and packet delay.
- **Joint communication/sensing beamforming Pareto baseline** using a weighted quadratic communication/sensing objective.
- **Cell-Free AP activation / sleep-mode study** exposing coverage and energy-efficiency trade-offs under a simple circuit-power model.
- Streamlit adds **Cell-Free Pilot CSI**, **Cell-Free RIS**, **Cell-Free AP Energy**, **ISAC Joint Beam**, and **Cross-layer OLLA/HARQ** labs.

Validation: **108/108 automated tests passing**. Release inventory: **88 CSV datasets, 148 figures, 236 SHA-256 verified result artifacts**.

### Selected v1.4 findings

- **Pilot reuse, 6 pilots / 12 users:** contamination-aware assignment reduces channel NMSE from `0.0823` to `0.0276` and raises mean 5%-tile rate from `0.537` to `0.715 bit/s/Hz` in the current normalized Cell-Free model.
- **Cell-Free + RIS:** random RIS mean total rate `4.69`; 2-bit sum-rate coordinate optimization `7.48 bit/s/Hz`. Optimizing weakest-user rate instead gives lower total rate (`6.73`) but slightly higher weakest-user rate (`1.64` vs `1.57`).
- **Cross-layer loop:** HARQ removes packet drops on the current biased-SNR trace; adding OLLA reduces NACK rate from about `19.8%` to `10.7%` and P95 delay from `4` to `3` slots while preserving delivered goodput.
- **AP activation:** under the current `0.12 W/AP` circuit-power abstraction, energy efficiency peaks around `12` active APs; activating all 32 raises user rate but reduces rate-per-modeled-watt.
- **Joint ISAC beam:** increasing angular separation between the communication user and sensing direction makes the rate-versus-sensing-gain Pareto trade-off progressively sharper.


## v1.3 at a glance

v1.3 adds distributed-network, multi-user propagation-control, and predictive sensing/beam-management branches:

- **Cell-Free / User-Centric Massive MIMO abstraction** with geometry-based large-scale fading, strongest-AP clustering, distributed MRT, fronthaul-link accounting, and user-rate/fairness metrics.
- **Max-min fixed-beam power control** for user-centric Cell-Free service, exposing average-rate versus weakest-user fairness.
- **Multi-user RIS coordinate optimization** that alternates finite-bit passive phase updates with recomputed digital ZF precoding.
- **Predictive ISAC beam tracking** with reactive hold, constant-velocity Kalman, and constant-acceleration Kalman models under sparse/missed sensing updates.
- **Uncertainty-aware ULA aperture selection**, trading peak array gain against robustness to angle-estimation error.
- Streamlit adds **Cell-Free Network**, **Multi-user RIS**, and **Predictive ISAC Beam** labs.

Validation: **101/101 automated tests passing**.

### Selected v1.3 findings

- **24-AP / 8-user distributed network:** mean 5%-tile user rate rises from `0.345` with nearest-AP service to `0.936` with UC-4, `1.137` with UC-8, and `1.278 bit/s/Hz` with all-AP Cell-Free service; AP-user service links rise `8 -> 32 -> 64 -> 192`.
- **UC-4 max-min power control:** average minimum-user rate rises `0.873 -> 1.286 bit/s/Hz`, while mean rate falls `2.126 -> 1.286` and Jain fairness reaches `1.0` in the fixed-direction model.
- **3-user MU-RIS @10 dB:** random phase mean sum rate `1.84`; 1/2/3-bit coordinate ascent reaches `4.52 / 5.10 / 5.32 bit/s/Hz`.
- **Sparse sensing, accelerating angle track:** reactive-hold mean rate `2.996`; mismatched CV prediction `2.489`; matched constant-acceleration Kalman prediction `3.981 bit/s/Hz`, with angle MAE `2.33° -> 0.58°`.
- **Robust beam aperture:** the expected-rate-optimal active ULA shrinks from `64` elements at `0.2°` angle uncertainty to `32` around `1–2°`, `16` around `3–4°`, and `8` above roughly `6°` in the normalized model.

## v1.2 at a glance

v1.2 adds five intentionally different research branches:

- **RIS-assisted SISO links** with continuous and 1/2/3-bit phase control.
- **Semi-orthogonal MU-MIMO user selection** before ZF precoding.
- **MDL source-count estimation** before MUSIC DOA processing.
- **Multi-target range/velocity Kalman tracking** with missed detections and sparse clutter.
- **OMP hybrid precoding** to approximate the full-digital transmit subspace under RF-chain limits.
- Streamlit adds **RIS Link**, **MU-MIMO User Selection**, **Hybrid OMP**, and **ISAC MUSIC + MDL** labs.

Validation: **93/93 automated tests passing**.

### Selected v1.2 findings

- **RIS @ 10 dB, 128 elements:** random phases `1.05`, 1-bit `5.10`, 2-bit `5.97`, 3-bit `6.17`, continuous `6.24 bit/s/Hz` mean spectral efficiency in the normalized model.
- **24 candidate / 4 scheduled users, 8-Tx ZF:** strongest-norm mean sum rate `20.33`; SUS `20.61 bit/s/Hz`, with median `cond(HH^H)` improving `7.69 -> 6.37`.
- **MDL for three sources at -5 dB:** correct source-count probability `0.558` with 30 snapshots, `0.983` with 60, and `1.0` with 120 in the current Monte Carlo.
- **Two-target range/velocity tracking:** raw measurement range RMSE `2.01 m -> 0.659 m` tracked under missed detections and sparse clutter; one identity fragmentation remains visible.
- **32x8 sparse MIMO, 2 streams, 10 dB:** OMP hybrid retains about `92.7%` of full-digital mean rate with 2 RF chains and `97.4%` with 4.

## v1.1 at a glance

v1.1 deepens spatial processing, sensing, retransmission design, and off-grid delay-Doppler estimation:

- **Ordered MMSE-SIC** fills the MIMO detection ladder between linear MMSE and K-best tree search.
- **Massive/MU-MIMO precoding** adds 4-user MRT/ZF downlink studies, favorable propagation, and channel hardening as the base-station array grows.
- **Pilot-contamination stress test** demonstrates coherent leakage that does not vanish simply by adding more antennas when pilots are reused.
- **Sparse-mmWave hybrid beamforming** compares DFT analog beam selection + low-dimensional digital SVD against full-digital SVD as RF-chain count changes.
- **OFDM-ISAC receive-array processing** adds ULA steering and Bartlett angle estimation on top of range-Doppler sensing.
- **MUSIC subspace DOA** uses multi-snapshot covariance to resolve close same-range/same-Doppler targets beyond the current Bartlett beamwidth in a controlled source-count-known experiment.
- **Multi-frame sensing tracking** adds an alpha-beta constant-velocity tracker with missed detections.
- **Joint fractional delay/Doppler OTFS refinement** closes another grid-mismatch limitation of the sparse path estimator.
- **Circular redundancy-version HARQ** repeats systematic evidence while rotating through parity subsets in a transparent circular-buffer mapping.
- Streamlit adds **MIMO MMSE-SIC**, **Massive MU-MIMO**, and **ISAC Angle** labs.

Validation: **88/88 automated tests passing**.

### Selected v1.1 findings

- **2x2 16-QAM @ 18 dB:** ZF BER `2.76e-2`, MMSE `2.48e-2`, ordered MMSE-SIC `1.53e-2`, K-best K=4 `1.00e-2`.
- **4-user MU-MIMO @ 10 dB:** increasing base-station antennas `4 -> 64` reduces mean normalized inter-user correlation `0.453 -> 0.111`; ZF sum spectral efficiency rises `5.08 -> 28.96 bit/s/Hz`.
- **Pilot contamination:** with a reused pilot, median desired/leakage ratio stays near `6 dB` from 8 to 128 antennas, whereas the orthogonal-pilot-like baseline rises about `13.4 -> 25.6 dB`.
- **32x8 sparse MIMO hybrid beamforming @ 10 dB:** 2 RF chains retain about `84%` of full-digital SVD mean rate; 4 chains about `96%`; 8 chains about `99%`.
- **ISAC angle resolution:** two targets sharing one range-Doppler cell at `-18°` and `22°` are not resolved by the 4-element ULA in the current Bartlett experiment, but are recovered by 8/16 elements.
- **MUSIC close-angle test:** with 10 Rx elements and multi-snapshot decorrelation, Bartlett fails to separate `-6°/+6°` in the current run while MUSIC recovers both exact grid angles.
- **Multi-frame range tracking:** noisy measurement RMSE `3.11 m -> 1.80 m` despite roughly 12% missed detections.
- **OTFS fractional refinement:** coarse errors `(0.35 delay bins, 0.42 Doppler bins)` reduce to about `(0.04, 0.00)` in the controlled local-search model.
- **Circular-RV HARQ @ 2 dB:** same-RV punctured repetition succeeds in `20%` of packets in this small run, while rotating parity RVs reaches `100%` and payload goodput about `0.236 bit/tx-bit`.

## v1.0 at a glance

v1.0 is the first milestone positioned explicitly as a **wireless communication systems laboratory** rather than only an OFDM receiver simulator:

- **Incremental-redundancy HARQ** for the custom sparse LDPC mother code, with zero-LLR puncturing, soft buffering, retransmission cost, and goodput accounting.
- **LDPC-coded soft-output 2x2 MIMO**, coupling K-best/exact max-log bit LLRs to normalized Min-Sum decoding.
- **Off-grid OTFS Doppler refinement** after coarse sparse support acquisition, reducing grid-mismatch residuals.
- **ACK/NACK-driven OLLA**, exposing SNR-estimator bias, target-BLER tracking, and goodput trade-offs.
- **Communication-centric OFDM sensing / ISAC**, with range-Doppler processing, coherent-processing resolution, and 2-D CA-CFAR.
- **Composite receiver stress test**, combining timing offset, CFO, IQ imbalance, phase noise, and AWGN in one long 16-QAM frame.
- Streamlit adds interactive **OLLA Link Adaptation** and **OFDM Sensing / ISAC** labs.

Validation: **79/79 automated tests passing**.

### Selected v1.0 findings

- **IR-HARQ @ 4 dB:** observed packet success 1.0 for both tested schemes; average coded-bit cost `96.0 -> 76.5` and payload goodput `0.333 -> 0.418` for Chase -> incremental redundancy.
- **2x2 QPSK + custom LDPC @ 4 dB:** K-best K=4 BER `6.37e-2`; exact max-log BER `4.45e-2`; average Min-Sum iterations `35.8 -> 26.4`.
- **OTFS off-grid refinement @ 20 dB pilot SNR:** Doppler MAE `0.385 -> 0.011 bins`; relative pilot residual `0.612 -> 0.099`.
- **OLLA with biased/noisy SNR estimates:** steady BLER `0.250 -> 0.0999`, while goodput rises `2.102 -> 2.217 bit/use`.
- **OFDM-ISAC:** exact-bin two-target recovery in the current 12 dB synthetic snapshot; a weak target's CA-CFAR detection probability rises from `0 @ -20 dB` to `0.857 @ -4 dB` and `1.0 @ 0 dB`.
- **Composite receiver stress:** long-frame 16-QAM BER falls from `0.424` after timing-only alignment to `9.70e-3` after staged CFO/IQ/pilot phase processing.

## v0.9 at a glance

v0.9 closes several former genie/algorithm-isolation gaps and adds packet-level reliability/system analysis:

- **Soft-output coded MIMO**: exact max-log and QR K-best list LLRs feed soft Viterbi decoding.
- **CRC-gated Chase HARQ**: repeated coded packets accumulate LLR evidence; retransmission cost is included in goodput.
- **Training-based ICI acquisition**: structured banded LS estimates high-Doppler OFDM coupling matrices from random training symbols.
- **Sparse OTFS physical-path acquisition**: one DD-domain pilot plus OMP estimates grid-aligned delays, Dopplers, and complex gains.
- **Queued OFDMA**: FIFO packets, stochastic arrivals, backlog, packet-delay statistics, and delay-aware PF scheduling.
- **Finite-blocklength AWGN**: channel dispersion and normal-approximation rate expose the short-packet penalty relative to Shannon capacity.

Validation: **73/73 automated tests passing**.

## v0.8 at a glance

v0.8 adds algorithmic complexity ladders, realistic channel correlation/feedback effects, adaptive RF calibration, a second modern FEC family, and a first multiuser system-level scheduler:

- **QR K-best MIMO detection**: a tunable tree-search bridge between linear MMSE and exhaustive ML for 2x2 16-QAM.
- **Spatially correlated MIMO**: Kronecker correlation, condition-number statistics, BER degradation, and equal-power MIMO capacity.
- **Limited-feedback beamforming**: 4x1 MISO MRT versus finite random codebooks, quantifying CSI-feedback bits against rate loss.
- **Iterative ICI equalization**: conjugate-gradient LMMSE on band-limited high-Doppler OFDM coupling matrices, avoiding explicit inverse solves.
- **Adaptive memory DPD**: block exponentially-weighted LS tracks a drifting memory-polynomial PA and is compared against a frozen predistorter.
- **Generalized cross-memory PA/DPD**: causal cross-envelope GMP terms expose when a standard memory polynomial is structurally mismatched.
- **Polar coding baseline**: self-contained N=128, K=64 polar encoder with min-sum successive-cancellation decoding and BEC-designed reliability ordering.
- **Multiuser OFDMA scheduling**: round-robin, max-rate, and proportional-fair allocation with Jain fairness and per-user throughput.

Validation: **66/66 automated tests passing**.

## Main capabilities

### Modulation and waveform
- Gray-coded QPSK / 16-QAM / 64-QAM
- max-log QAM bit LLRs
- 64-point OFDM with configurable pilots and cyclic prefix
- PAPR, clipping, and selective mapping (SLM)
- small-grid OTFS modulation/demodulation prototype

### Channels and RF impairments
- complex AWGN
- deterministic / Rayleigh frequency-selective multipath
- independent per-path Doppler
- timing offset, CFO, Wiener phase noise
- **IQ gain/phase imbalance**
- **sampling-clock offset by fractional resampling**
- **narrowband sinusoidal interference**
- Rapp memoryless PA nonlinearity

### SISO receiver
- known-preamble frame detection
- Schmidl-Cox-style timing/CFO estimator
- coarse CFO correction
- pilot common-phase tracking
- **pilot affine phase-vs-subcarrier tracking**
- pilot LS + frequency interpolation
- finite-CIR time-domain LS channel estimation
- ZF / MMSE equalization
- **training-LS IQ compensation**
- **two-burst SCO estimation + inverse resampling**

### Coding
- rate-1/2, K=3 `(7,5)_oct` convolutional code
- hard and soft-input Viterbi
- **custom rate-1/2 sparse accumulator-LDPC**
- **normalized Min-Sum iterative decoder**
- **educational N=128, K=64 polar code with SC decoding**

### MIMO
- narrowband 2x2 Rayleigh ZF/MMSE baseline
- time-domain frequency-selective 2x2 MIMO-OFDM
- time-orthogonal MIMO training + LS channel estimation
- 2x1 Alamouti transmit diversity
- QR K-best tree-search detection
- spatial-correlation / capacity studies
- limited-feedback 4x1 MISO beamforming

### RF linearization
- known-model inverse Rapp DPD
- **data-fitted odd-polynomial indirect-learning DPD**
- block-EWLS adaptive memory DPD
- generalized cross-memory polynomial PA / indirect DPD
- EVM and guard-bin spectral-regrowth evaluation

### Reliability / link adaptation
- CRC-16 gated Type-I / Chase HARQ
- **custom incremental-redundancy LDPC puncturing + soft buffer**
- **ACK/NACK-driven OLLA target-BLER controller**

### Sensing / ISAC
- **communication-centric QPSK-OFDM sensing model**
- **range-Doppler FFT processing**
- **2-D CA-CFAR target detection**
- coherent processing length vs velocity resolution

### Link/system studies
- CP-length robustness/overhead
- pilot-density estimation/overhead
- adaptive QAM under BER constraint
- water-filling parallel-channel power allocation
- multiuser OFDMA proportional-fair scheduling
- Doppler tracking vs within-symbol ICI
- oscillator phase noise and CPE tracking
- **coded OFDM under detected narrowband interference**
- **illustrative high-Doppler OFDM/OTFS receiver comparison**

## Selected v0.6 findings

### IQ imbalance
64-QAM OFDM at 30 dB SNR with approximately **4 dB gain imbalance + 15° quadrature error** gives raw BER about **0.134** and EVM about **27.1%**. Four known training OFDM symbols are enough for the current LS widely-linear compensator to produce **0 observed errors** in the simulated payload and EVM about **3.29%**.

### Sampling-clock offset
For a 900-symbol 64-QAM frame, an SCO of **500 ppm** drives the uncorrected BER to about **0.470**. Two separated training bursts estimate **500.25 ppm**; cubic inverse resampling lowers BER to about **0.0286**. Pilot-only affine phase tracking is much weaker because SCO changes the sampling time axis and eventually produces ICI/window drift, not only a phase ramp.

### Narrowband interference
A persistent single-carrier interferer is detected from robust median carrier power. With rate-1/2 convolutional coding, QPSK-OFDM, 18 dB SNR, and **-5 dB SIR**, raw soft-Viterbi BER is about **2.09e-2** while marking the detected carrier's LLRs as erasures yields **0 observed information-bit errors** in the current 20k-bit run.

### Sparse iterative FEC
The custom rate-1/2 sparse code maps one **96-bit information block -> 192 coded bits**, exactly two QPSK OFDM payload symbols in the default layout. At 2 dB, normalized Min-Sum gives BER about **3.44e-3**, slightly below the existing soft-Viterbi baseline (**3.96e-3**). At 4 dB it reaches **0 observed errors** in 9600 information bits, and average decoder iterations fall from 40 at very low SNR to about 1 at high SNR.

> This is a custom educational LDPC/accumulator construction, not a 5G NR or DVB LDPC code.

### Data-fitted polynomial DPD
At 8 dB back-off, PA-only EVM is about **3.40%**. A ninth-order memoryless polynomial fitted only from Rapp PA input/output samples reduces EVM to about **1.23%** and guard/occupied leakage from about **-31.6 dB to -39.1 dB**. The result is close to the known-model inverse baseline without using the analytic Rapp inverse during training.

### High-Doppler OTFS prototype
In the current small deterministic two-path model, the OFDM effective channel's off-diagonal energy grows from **0% to about 15.1%** as the moving path reaches 2.25 normalized delay-Doppler bins. A conventional one-tap OFDM receiver degrades to BER about **3.79e-2** at 18 dB, while the OTFS branch has no observed errors in the small Monte-Carlo run with a **full known effective-channel LMMSE detector**.

This result is intentionally labeled **illustrative**: the OTFS detector is more expensive and is not a complexity-matched standards benchmark. The useful result is the explicit visualization of how high Doppler changes channel structure and breaks OFDM's diagonal one-tap assumption.

## Selected v0.7 findings

### High-Doppler ICI-aware equalization
At 18 dB with a three-path time-varying channel and a moving path at **1.5 subcarrier spacings**, about **23.6%** of the effective OFDM channel energy is off the diagonal. The conventional one-tap detector gives BER about **4.21e-2**. A band-limited LMMSE model retaining only the main diagonal plus/minus two neighboring couplings lowers BER to about **1.20e-3**; the full known-matrix LMMSE detector has **0 observed errors** in the current Monte Carlo run.

### Memory-polynomial PA and indirect-learning DPD
The new PA contains nonlinear memory rather than only a memoryless AM/AM curve. At **8 dB input back-off**, PA-only EVM is about **10.8%** after scalar gain alignment; a ninth-order, four-memory-tap indirect-learning predistorter lowers EVM to about **0.85%** and improves guard/occupied leakage from roughly **-29.9 dB to -44.2 dB**. At very aggressive **4 dB back-off**, the fitted inverse becomes unstable, which is retained as an explicit operating-range limitation.

### MIMO channel estimation and pilot overhead
A simple scalar-prior LMMSE shrinker lowers 2x2 training NMSE from about **0.698 to 0.410** at 0 dB and converges toward LS at high SNR. Separately, replacing two time-orthogonal full-active training symbols with **one frequency-orthogonal pilot symbol** and finite-CIR LS reduces training resource elements from **104 to 52**. In the current channel family at 12 dB, NMSE is about **0.144** for the two-slot full-carrier LS baseline and **0.0508** for the one-slot finite-CIR estimator.

### Linear versus maximum-likelihood MIMO detection
For 2x2 QPSK Rayleigh MIMO at 12 dB, BER is about **3.00e-2 (ZF)**, **2.02e-2 (MMSE)**, and **4.29e-3 (exhaustive ML)**. The ML result is a small-system performance reference only: its candidate count grows as `M**n_tx`.

### Sparse iterative OTFS detector
On the current 6x12 delay-Doppler grid, retaining the strongest **5 coefficients per observation row** preserves about **99.1%** of effective channel energy and gives BER about **4.96e-5** at 14 dB with conjugate-gradient LMMSE. Keeping only 2 coefficients retains about **92.2%** and gives BER about **5.51e-3**. This exposes a sparsity/performance/iteration trade-off without claiming a standards-level OTFS receiver.

### Confidence-aware BER reporting
The QPSK AWGN validation now reports **95% Wilson intervals** and runs until either a target error count or a maximum bit budget is reached. At 10 dB Eb/N0, 10 errors were observed in 4,000,000 bits: BER **2.5e-6** with a 95% interval approximately **[1.36e-6, 4.60e-6]**, consistent with the theoretical **3.87e-6**.

### Frequency-selective IQ imbalance
The front-end IQ model now includes separate direct and image FIR filters. At 26 dB with 64-QAM OFDM, raw BER is about **2.55e-2**; compressing the impairment into one frequency-flat `(alpha,beta)` pair leaves about **1.03e-3** BER, while the learned FIR model plus mirror-subcarrier pairwise inversion has **0 observed errors** in the current run. EVM falls from about **13.0% raw -> 8.38% flat compensation -> 4.66% FIR compensation**.


## Selected v0.9 findings

### Soft-output detection changes coded-MIMO behavior
For 2x2 QPSK with a terminated rate-1/2 `(7,5)_oct` convolutional code, hard K=4 detection followed by hard Viterbi gives BER about **1.07e-2 at 8 dB**. Keeping the same K=4 tree list but computing approximate max-log bit LLRs and using soft Viterbi lowers BER to about **3.90e-3**. An exact small-system max-log reference reaches about **2.44e-4**. The result demonstrates why detector reliability information matters once MIMO detection is connected to FEC.

### Chase HARQ turns repeated failures into accumulated evidence
A CRC-16-gated block-Rayleigh link retransmits the same convolutionally coded QPSK packet up to four times. At **0 dB**, Type-I HARQ succeeds on about **59.2%** of packets while Chase combining reaches about **91.7%** by summing coded-bit LLRs across independent retransmissions. Payload goodput rises from about **0.186 to 0.327 bit/QPSK-symbol** even after counting retransmission cost.

### High-Doppler ICI matrices are now estimated from training
The previous ICI-aware branch assumed a known effective matrix. v0.9 fits only the main diagonal ±2 neighboring couplings from random full-band OFDM training. With about **23.6% off-diagonal channel energy** at 18 dB, 12 training symbols give matrix NMSE about **2.81e-2** and BER about **4.77e-3**; 32 symbols give NMSE about **8.07e-3** and BER about **1.60e-3**, close to the genie-band result near **1.1e-3**.

### OTFS sparse channel acquisition uses one delay-Doppler pilot
A known DD impulse is passed through a candidate delay/Doppler dictionary and OMP estimates three physical paths. Exact support recovery rises from **20% at 15 dB pilot SNR** to **82.5% at 20 dB** and **100% at 25 dB** in the current grid-aligned experiment. At 25 dB pilot SNR the estimated-path LMMSE detector gives BER about **5.21e-5**, close to the genie-path run.

### Queue-aware OFDMA adds packet delay and backlog
Under the same four-user fading/arrival trace, ordinary PF delivers about **22.28 kbit/slot**, Jain fairness **0.987**, and P95 completed-packet delay **155 slots**. Delay-aware PF reaches about **23.36 kbit/slot**, fairness **0.999**, and P95 delay **18 slots**, while final backlog falls from **1.42 Mbit to 0.124 Mbit**. This is an abstract queue-aware scheduler, not a 3GPP MAC.

### Finite-blocklength analysis quantifies short-packet rate loss
For complex AWGN at **10 dB** and target error probability **1e-3**, Shannon capacity is about **3.459 bit/use**. The normal approximation gives about **3.049** at blocklength 100, **3.217** at 300, and **3.324** at 1000 complex channel uses.

## Selected v0.8 findings

### K-best MIMO: tunable search between MMSE and ML
For 2x2 16-QAM Rayleigh MIMO, K-best uses a QR-transformed tree and retains only the K lowest partial Euclidean metrics per layer. At 18 dB, BER is about **2.41e-2 (MMSE)**, **9.52e-3 (K=4)**, and **7.69e-3 (K=16 / exhaustive ML)**. In this 2x2 case, K=16 reproduces ML exactly while making the complexity ladder explicit rather than treating ML as a single opaque reference.

### Spatial correlation: MIMO rank/conditioning loss
At 12 dB, increasing equal Tx/Rx exponential correlation from rho=0 to rho=0.95 raises median channel condition number from about **2.93 to 28.97**. ZF BER degrades from about **2.87e-2 to 3.46e-1**, MMSE from **1.92e-2 to 1.79e-1**, and mean equal-power 2x2 capacity falls from about **6.59 to 4.52 bit/s/Hz**.

### Limited CSI feedback for beamforming
For 4x1 Rayleigh MISO at 5 dB, a single transmit antenna gives mean spectral efficiency about **1.71 bit/s/Hz**, while perfect-CSI MRT gives **3.61**. A finite codebook improves smoothly with feedback: **4 bits -> 3.06**, **6 bits -> 3.28**, and **8 bits -> 3.42 bit/s/Hz**. The experiment isolates the feedback-overhead / beamforming-gain trade-off without claiming a WLAN/NR codebook implementation.

### Iterative high-Doppler ICI equalization
With about **25.3%** effective OFDM channel energy off the diagonal, the 18 dB one-tap BER is about **5.01e-2**. Conjugate-gradient LMMSE using only the main diagonal plus/minus two neighboring couplings lowers BER to about **2.48e-3** in roughly **27 iterations** on average. The receiver avoids an explicit dense matrix inverse and exposes bandwidth / BER / iteration trade-offs.

### Adaptive DPD under PA drift
A static memory DPD calibrated at block 0 degrades from about **0.85% EVM to 4.04%** as the synthetic PA coefficients drift. A block exponentially-weighted LS indirect learner tracks the changing inverse and finishes around **2.27%**, with most intermediate blocks near 1--1.5%. A more aggressive sample-wise RLS attempt was found numerically unstable and is not used for the headline result.

### Cross-memory generalized polynomial modeling
A synthetic PA containing causal cross-envelope memory terms is structurally mismatched by the ordinary memory-polynomial basis. At the 8 dB calibration region, standard memory-DPD gives about **1.29% EVM**, while the cross-term generalized memory polynomial gives about **0.74%**. The forward-model held-out NMSE improves from roughly **-41.4 dB** to numerical precision in this deliberately matched synthetic experiment. At 6 dB back-off both learned inverses become poor, preserving the low-back-off limitation rather than hiding it.

### Three rate-1/2 FEC families
A common BPSK/AWGN information-bit benchmark now compares soft Viterbi, the project-specific sparse LDPC/Min-Sum code, and an educational N=128/K=64 polar SC code. At 3 dB Eb/N0, measured BER is approximately **5.68e-3 (convolutional)**, **3.98e-3 (LDPC)**, and **1.39e-3 (polar)** in the current finite runs. The polar construction uses a self-contained BEC-derived reliability order and is **not** a 5G NR polar profile.

### Proportional-fair OFDMA scheduling
With four users having unequal average SNRs, pure max-rate scheduling reaches mean aggregate rate about **248.2** in the experiment's normalized slot units but Jain fairness is only **0.344**. Fixed round-robin gives about **157.0** with fairness **0.865**. Proportional-fair scheduling reaches about **200.5** while raising fairness to **0.890**, demonstrating the expected opportunism/fairness compromise.

## Architecture

```text
Information bits
   ├─ optional convolutional / sparse iterative FEC
   ↓
QAM → OFDM/IFFT → CP → optional Preamble → RF / oscillator / channel impairments
                                            ↓
 Timing/CFO/SCO/IQ correction → FFT → Channel Estimation → ZF/MMSE → Phase Tracking
                                            ↓
                         soft/hard demap → FEC decoder → BER/EVM/NMSE

Parallel research branches:
- 2×2 MIMO-OFDM spatial multiplexing
- 2×1 Alamouti diversity
- PA / DPD / PAPR / SLM
- high-Doppler and OTFS prototype
- water-filling / adaptive modulation
- narrowband interference detection and soft erasure
```

## Install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .[dev]
```

Optional dashboard:

```bash
pip install -e .[app]
streamlit run app/dashboard.py
```

The dashboard includes OFDM Link, Phase Noise, IQ Imbalance, Sampling Clock, Power Amplifier/DPD, High-Doppler ICI, 2x2 MIMO Detection, K-best MIMO, Limited-Feedback Beamforming, OFDMA Scheduling, **Queued OFDMA**, **Finite Blocklength**, and Water-Filling labs.

## Validate

```bash
pytest -q
```

Expected for v2.9:

```text
207 passed
```

## Run v2.9 experiments

```bash
python experiments/run_v29_suite.py
```

The v2.9 suite runs the five new state/control Monte Carlo studies in isolated subprocesses. Individual scripts can be run separately when iterating.

or individually:

```bash
python experiments/ici_aware_equalization.py
python experiments/memory_polynomial_dpd.py
python experiments/mimo_lmmse_estimation.py
python experiments/mimo_pilot_efficiency.py
python experiments/mimo_ml_detection.py
python experiments/otfs_iterative_detection.py
python experiments/ber_confidence_intervals.py
```

Results are exported to `results/data/` and `results/figures/`.

## Repository layout

```text
src/commlab/
├── modulation/          QAM + LLRs
├── ofdm/                OFDM transceiver
├── otfs/                small-grid OTFS / effective channel tools
├── channels/            AWGN / multipath / Rayleigh / Doppler
├── impairments/         CFO / phase noise / IQ / SCO / interference
├── estimation/          pilot LS / finite-CIR time-domain LS
├── equalization/        SISO ZF / MMSE / ICI-matrix LMMSE
├── synchronization/     preamble / CFO / CPE / affine phase tracking
├── coding/              convolutional + sparse accumulator LDPC
├── mimo/                MIMO channels / LS-LMMSE estimation / ML detection / STBC
├── rf/                  memoryless + memory PA / model-based + learned DPD
├── papr/                PAPR / clipping / SLM
├── computation/         analog over-the-air aggregation
├── resource_allocation/ water-filling
├── random_access/       grant-free access + IRSA graph/SIC random access
├── metrics/             BER / MSE / NMSE / EVM / Wilson confidence intervals
└── config.py

experiments/              reproducible studies
app/                      Streamlit dashboard
tests/                    automated validation
docs/                     architecture / report / inspirations
results/                  generated CSV and figures
```

## Scope discipline

The project does **not** claim:
- standards compliance;
- over-the-air RF validation;
- calibrated oscillator/RF hardware models;
- a standards LDPC implementation;
- an OTFS-vs-OFDM complexity-equivalent benchmark;
- production-grade adaptive DPD.

These boundaries are deliberate: every headline result should remain reproducible from code in the repository.
