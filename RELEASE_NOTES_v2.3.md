# CommLab v2.3 Release Notes

v2.3 focuses on **resilient and task-aware wireless edge intelligence**. It adds explicit model staleness, Byzantine-update robustness, privacy-noise/AirComp coupling, semantic packet scheduling, and confidence-triggered split inference.

## New capability groups

### Asynchronous federated learning
- Delayed model snapshots per client update.
- Naive stale-gradient application.
- Exponential staleness weighting.
- Exact local-Hessian stale-gradient transport for the quadratic ridge baseline.
- Metrics: final loss, parameter error, realized delay, stale/current gradient cosine.

### Byzantine-robust aggregation
- Sign-flip/scaling attack baseline with fixed malicious identities.
- Mean, coordinate median, and coordinate trimmed mean.
- Explicit breakdown-region sweeps rather than a single favorable attacker fraction.

### Private AirComp-FL baseline
- Per-client gradient clipping.
- Gaussian client perturbation before analog aggregation.
- Wireless AirComp noise and learning convergence in the same experiment.
- No formal DP guarantee is claimed; the noise multiplier is used only to study utility loss.

### Semantic resource scheduling
- Expiring task packets with heterogeneous importance and radio cost.
- Channel-first, importance-first, expected-value-per-resource, and urgency-aware schedulers.
- Metrics: task utility, expiry count, resource utilization, delivery age.

### Split inference
- Local early classification on a partial feature set.
- Confidence-triggered residual-feature offload.
- Wireless feature corruption, communication use, and end-to-end latency proxies.

## Selected findings

- Mean modeled staleness of eight updates reduces stale/current gradient cosine to roughly 0.67 in the tested convex problem; naive asynchronous FL worsens while staleness decay remains stable.
- Mean aggregation can catastrophically diverge at modest sign-flip/scaling attacker fractions. Coordinate median remains stable across the tested range; trimmed mean fails once attackers consume too much of its trimming budget.
- At high SNR, client perturbation becomes the dominant AirComp aggregation floor and increases final learning loss monotonically in the tested noise sweep.
- Task-value-aware scheduling dominates channel-first scheduling when resources are scarce, but the advantage disappears when enough radio resources exist to serve most urgent traffic.
- Confidence-adaptive split inference recovers most full-edge classification accuracy with substantially fewer residual-feature channel uses and lower average latency.

## Boundaries

This release is educational/research simulation. It is not a standards-compliant FL protocol, privacy system, adversarial-security product, learned semantic codec, or MEC deployment model.
