# CommLab v3.1 Release Notes

v3.1 extends the v3.0 risk/reliability milestone into **safety-aware control, communication-computation adaptive inference, explicit edge failure recovery, risk-aware AI-model replication, and component-selective goal-oriented state transmission**.

## New capability groups

1. **Safety-aware wireless feedback** — multiple plants have unequal safety envelopes. Scheduling compares age, estimation error, and normalized safety-boundary proximity.
2. **Channel-adaptive inference depth** — jointly selects feature precision (2/4/8 bits) and analytic edge-model depth (1–4) under an end-to-end latency budget.
3. **Edge failure recovery** — compares full restart, periodic checkpoint/migration, and dual execution under stochastic task failures.
4. **Risk-aware model replication** — places extra AI-model replicas according to either popularity or popularity × task criticality under finite edge storage.
5. **Component-selective semantic control** — a vector state shares a tiny feedback budget; policies compare round-robin high precision, all-component low precision, and control-value component selection.

## Key findings

- Safety-aware scheduling is regime dependent. Around -3 to +1 dB in the supplied trace it slightly reduces state-bound violations versus max-error scheduling, but under extreme -5 dB communication scarcity max-error can retain a small violation-rate advantage.
- At 0 dB, channel-adaptive depth obtains roughly 83.1% on-time task accuracy versus 67.9% for the fixed light configuration and 65.3% for fixed deep inference. By 10 dB, fixed deep inference catches up, showing that adaptation is most valuable in the constrained regime.
- Recovery policy has a clear failure-rate threshold. At only 1% task failure, checkpoint overhead makes its P95 latency worse than restart. At 12% failure, P95 latency falls from about 226.7 ms (restart) to 162.0 ms (checkpoint), while dual execution reaches about 132.7 ms at roughly 2x compute load.
- At a 3.2 GB replica-storage budget, risk-aware placement reduces task-weighted model outage from about 1.35% to 0.46%. At intermediate budgets it can accept a worse raw outage count in order to protect low-frequency high-criticality models.
- Component-selective control exposes a strong goal-oriented communication effect. At -3 dB, the value-component policy uses 7 bit/slot and obtains mean control cost about 0.61, versus about 9.88 for round robin and 3.59 for sending every component at low precision.

## Scientific boundaries

All v3.1 additions are transparent NumPy research abstractions. Safety violation is a simulated state-bound metric, not a formal control-barrier certificate. Adaptive-depth accuracy is an analytic toy task model, not a measured neural-network benchmark. Checkpoint/replication costs are synthetic system proxies. Model-replica criticality and node reliability are synthetic. Component-selective transmission uses a linear vector plant and does not claim semantic optimality.

## Release validation

- 218/218 automated regression tests.
- 184 CSV datasets and 319 PNG figures (503 hashed result artifacts).
- Single-command v3.1 experiment reproduction.
- Editable-install version/import verification without manual `PYTHONPATH`.
- Full source/experiment/Dashboard/tool compile check.
- ZIP CRC integrity check.
