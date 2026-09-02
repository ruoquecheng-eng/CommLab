# CommLab v2.6 Release Notes

v2.6 extends the edge-intelligence branch into **downlink synchronization, progressive inference, learning-aware OTA user selection, energy-harvesting participation, and task-value-aware model distribution**.

## New capability groups

### AirComp user selection versus learning bias
- Strongest-channel selection, random/all-client baselines, and a greedy channel-aware gradient-diversity selector.
- Separates analog aggregation error relative to the selected-client mean from statistical selection bias relative to the all-client gradient.
- Demonstrates that a physically cleaner OTA sum can still train a worse global model under channel/data correlation.

### Progressive split inference
- Multi-stage residual feature upload in task-importance order.
- Local, full-offload, confidence-only, and channel/deadline/energy-aware progressive policies.
- Reports raw accuracy, on-time task accuracy, feature channel uses, latency and energy proxies.

### Differential downlink model broadcast
- Full-model every-round baseline.
- Chained delta coding with synchronization-chain failure after a missed delta.
- Periodic-keyframe anchor-relative differential baseline that can recover from isolated missed updates while the anchor remains valid.
- Explicit downlink-size versus client model-age/model-MSE trade-off.

### Energy-harvesting OTA-FL
- Finite client batteries, heterogeneous stochastic energy arrivals, and one-unit OTA update cost.
- Channel-only, battery/channel, and participation-age + battery/channel schedulers.
- Exposes the transition from energy-starved operation to selection-bias/fairness-limited operation.

### Importance-aware layered model multicast
- Common base layer plus enhancement multicast.
- Client task importance can be anti-correlated with radio quality.
- Enhancement-rate selection maximizes importance-weighted utility minus an explicit airtime penalty rather than assuming strongest clients are always most valuable.

## Selected v2.6 findings

- With 12 dB channel/data-group disparity, channel-only OTA selection achieves extremely low analog error but selects the strong-data group about 98.6% of the time and reaches global loss about 0.629; gradient-diversity selection lowers the bias and finishes near 0.460.
- At -2 dB mean residual-link SNR, full residual offload has about 85.1% raw accuracy but roughly 77.4% deadline misses and only 20.8% on-time accuracy. Progressive adaptive transmission uses about 1.17 residual feature channel uses on average, has zero modeled deadline misses, and reaches about 86.6% on-time accuracy.
- At keyframe interval 20, chained differential broadcast uses only about 0.21 normalized full-model size per round but reaches mean version age about 27.4 rounds. Anchor-relative differential coding uses about 0.32 and cuts age to about 20.0 rounds.
- Under abundant harvested energy, channel-only OTA-FL increasingly favors the statistically correlated strong-channel group. Participation-age-aware scheduling sacrifices weakest-link quality to restore fairness and improve final learning loss.
- When high-value clients are weak links, importance-aware layered multicast increases weighted task utility by roughly four to five percentage points in the current sweep for only a small airtime increase relative to a fixed stronger-half enhancement layer.

## Boundaries

- Differential model broadcast is a transparent keyframe/anchor abstraction, not a reproduction of the 2026 MTDC codec or a bit-exact downlink standard.
- Progressive split inference uses a Gaussian linear classification task and proxy compute/energy timing.
- Gradient diversity uses current exact gradients and is an educational scheduling baseline.
- Energy harvesting is Bernoulli and battery costs are normalized, not device-calibrated.
- Layered model utility is a task proxy, not a trained progressive neural-model codec.
