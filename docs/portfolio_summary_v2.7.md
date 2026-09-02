# CommLab v2.7 — Portfolio Summary

**Recommended title:** CommLab — Wireless Communication, Edge Intelligence & Runtime Orchestration Laboratory

**One-line description:** A reproducible Python wireless-systems platform spanning PHY/MAC/network/edge intelligence; v2.7 adds state-aware downlink resynchronization, carbon-aware FL orchestration, AI-model caching, queue-aware progressive inference, and importance-aware multicast repair.

## Strong v2.7 evidence

- **Adaptive control under equalized communication cost:** an age/budget keyframe controller lowers client model age and synchronization MSE at essentially the same average downlink payload as a fixed schedule.
- **Environmental optimization can become statistical bias:** carbon-only FL scheduling heavily favors a low-carbon region whose clients carry a correlated data group, reducing carbon proxy but severely worsening the global objective.
- **Cache hit rate is not the only edge-serving metric:** popularity-only caching achieves a higher hit rate than value-density caching in the current trace, yet value-density lowers mean/p95 inference latency and model-loading backhaul by preferring models with larger latency savings per stored MB.
- **Progressive inference has completion locality:** packet-style EDF/value preemption can scatter chunks across many incomplete tasks; a completion-aware scheduler improves usable task utility in the moderate-load regime.
- **Downlink repair should follow application value:** selective repair of weak high-importance receivers recovers much of the task utility of full reliability without paying the enormous airtime of repairing every miss.

## Suggested portfolio figures

1. `results/figures/v27_adaptive_downlink_age.png`
2. `results/figures/v27_carbon_loss_pareto.png`
3. `results/figures/v27_edge_caching_latency.png`
4. `results/figures/v27_queued_split_utility.png`
5. `results/figures/v27_multicast_repair_utility.png`

## CV-safe bullet

Built and validated a modular Python wireless/edge-intelligence laboratory with 195 automated tests and 441 hashed experiment artifacts; designed runtime orchestration experiments showing how model synchronization, carbon-aware client selection, edge-model caching, progressive inference queues, and task-aware multicast repair create cross-layer performance trade-offs.

## Avoid overclaiming

Do not describe the carbon proxy as audited emissions, the adaptive keyframe controller as MTDC, the caching baseline as a production AI-serving scheduler, the split-inference task as a trained deep model, or selective multicast repair as a standard 5G/6G multicast protocol.
