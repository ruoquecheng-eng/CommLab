# CommLab v2.7 Release Notes

v2.7 extends CommLab from cross-layer wireless edge intelligence toward **runtime orchestration and state-aware control**. The new branch asks when the system should resynchronize, which clients should participate under environmental constraints, which AI models should be cached, how progressive inference requests should share a radio queue, and which weak downlink receivers are worth repairing.

## New capability groups

### Budget-constrained adaptive FL downlink
- Adds age-triggered full-model keyframes on top of anchor-relative differential updates.
- A running normalized-downlink budget prevents the adaptive controller from winning merely by transmitting more full models.
- Evaluates client model-version age, model MSE, packet success, keyframe count, and normalized downlink size under a common blockage episode.

### Carbon-aware federated orchestration
- Adds time-varying regional carbon-intensity proxies, heterogeneous device energy cost, client execution latency, non-IID data groups, and participation age.
- Compares random, gradient-utility, carbon-only, and balanced multi-objective client selection.
- Includes a carbon-weight Pareto sweep rather than claiming one universally optimal operating point.

### Edge AI model caching and inference routing
- Adds finite edge-model storage, heterogeneous model sizes, edge/cloud inference latencies, drifting request popularity, and model-load backhaul traffic.
- Compares static caching, LRU, periodic popularity caching, and periodic value-density caching.
- Recache interval exposes the slow-timescale cache-freshness versus model-churn/backhaul trade-off.

### Queue-aware progressive split inference
- Multiple progressive inference requests now share one radio server.
- Requests have heterogeneous deadlines, task values, local confidence, user SNRs, and up to three enhancement chunks.
- FIFO, EDF, value, urgency-value, and completion-aware scheduling expose the cost of fragmenting partially served inference jobs.

### Importance-aware multicast repair
- Aggressive multicast targets a stronger receiver quantile rather than the worst user.
- Missed clients can receive no repair, selective task-value-aware unicast repair under a full-common airtime budget, or repair for every miss.
- Separates radio coverage from importance-weighted task utility.

## Selected findings

- At 7 dB common blockage, fixed 5-round keyframes and budgeted-age control both use about 0.354 normalized full-model size per round. Budgeted-age lowers mean client model age from about 19.27 to 16.20 rounds and model MSE from about 1.55 to 1.27, while using roughly 24.6 rather than 31 full keyframes over the trace.
- Carbon-only client selection reduces the modeled total carbon proxy from about 324.7 (random) to 136.2 but raises final excess optimization loss from about 0.0167 to 0.499 and lowers participation fairness. A balanced controller around carbon weight 0.75-1.0 achieves about 288-301 carbon proxy with excess loss near 0.009.
- Periodic value-density model caching at a 160-request update interval achieves about 32.6 ms mean latency and 5.37 GB modeled backhaul traffic, versus 33.4 ms and 6.02 GB for popularity-only caching. LRU produces very high model-churn traffic (roughly 315 GB in the current trace).
- At inference arrival rate 0.65/slot, completion-aware progressive scheduling reaches about 0.50 on-time task-weighted utility versus about 0.47 for FIFO and 0.39-0.42 for the naive EDF/value/urgency policies. At extreme overload the advantage shrinks, exposing a load-dependent regime.
- With strong importance/SNR anticorrelation (0.8), aggressive multicast with no repair provides weighted utility about 0.465 at only 0.112x conservative full-common airtime. Selective importance repair raises utility to about 0.697 while remaining around 0.914x full-common airtime; repairing every missed receiver reaches full utility but costs about 3.87x.

## Boundaries

- Carbon values are system-level proxies based on modeled client energy and time-varying regional intensity; they are not lifecycle carbon accounting.
- Adaptive differential downlink is an educational age/budget controller, not the published 2026 mixed-timescale differential-coding algorithm.
- Edge caching uses synthetic model/request traces and transparent greedy policies, not an RL cache controller or production serving stack.
- Progressive split inference uses an analytic task proxy and one serial radio server; it is not a deployed neural early-exit system.
- Multicast repair uses Shannon-style spectral-efficiency timing proxies and perfect repair decoding once airtime is allocated.
