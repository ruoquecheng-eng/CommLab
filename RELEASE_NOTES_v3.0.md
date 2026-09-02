# CommLab v3.0 Release Notes

v3.0 is a milestone release focused on **risk-sensitive, reliability-aware, and control-aware wireless runtime orchestration**. It preserves the full PHY/MAC/ISAC/edge-intelligence stack from v2.9 while adding five transparent cross-layer baselines.

## New capability groups

1. **Risk-sensitive networked control** — compares mean-value and tail-risk-aware sensor scheduling under rare process shocks; reports empirical P95/CVaR95 control cost.
2. **Variable-rate semantic/control updates** — transmits quantized state innovations using 3/6/10-bit payloads, exposing state precision versus wireless deliverability.
3. **Failure/trust-aware edge orchestration** — jointly exposes radio delay, queueing, energy proxy, state-dependent execution failure, recovery latency, and deadline misses.
4. **Joint AI-model caching and inference offloading** — couples slow cache placement to fast radio/queue/miss-aware request routing across multiple edge servers.
5. **Cooperative multi-agent networked control** — schedules feedback for a coupled chain by local freshness/error or predicted global formation-value reduction.

## Key findings

- Tail-risk-aware scheduling is **regime dependent**. With calibrated risk weight 1, it reduces CVaR in the intermediate/high-shock regime (around shock multipliers 1.4–1.8 in the supplied trace), but can be worse in mild or extreme regimes.
- Variable-rate predictive state updates are most useful when communication is constrained: at 0 dB the adaptive controller uses roughly half the high-precision payload while slightly reducing mean control cost; at high SNR fixed 10-bit updates regain the lead.
- A lowest-latency edge can be the least reliable edge. Risk-aware placement substantially reduces failure/deadline-miss probability at the cost of modest average-latency overhead.
- Cache hit rate is not an end-to-end objective. Cache-first routing can overload a small subset of edges; the joint cache/offload heuristic avoids this queue-concentration failure mode.
- Multi-agent system-value scheduling helps most in the severely communication-limited regime. Once links improve, a simpler local-error scheduler can be the better complexity/performance baseline.

## Scientific boundaries

All new branches are explicit NumPy simulation baselines. CVaR is empirical, edge reliability is synthetic, cache/offload policies are heuristics, and the coupled-control model is a scalar linear chain. No safety certification, production edge platform, or globally optimal stochastic controller is claimed.
