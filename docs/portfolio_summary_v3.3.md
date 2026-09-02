# CommLab v3.3 Portfolio Summary

**CommLab — Wireless Communication Systems Laboratory** is a pure-software wireless/edge-intelligence research platform spanning PHY simulation, MIMO, coding/HARQ, RF impairments, high mobility, MAC/scheduling, ISAC, federated/semantic communication, edge inference, model caching, Digital Twin synchronization, networked control, and reliability orchestration.

## v3.3 contribution

v3.3 introduces a **unified resilience-budget orchestrator** that forces three previously separate reliability mechanisms to compete for a finite resource budget:

- proactive service migration,
- cross-failure-domain edge replicas,
- correlation-aware dual-radio packet duplication.

The simulator explicitly studies where each mechanism fails. It shows that the useful redundancy mechanism changes with the dominant failure layer, that correlated radio paths can make duplication a poor use of reliability budget, and that noisy forecasts can convert extra budget into migration churn. An uncertainty-gated baseline can intentionally leave credits unused when the estimated benefit is not credible.

## Engineering/research emphasis

- transparent NumPy policy baselines rather than black-box RL;
- deterministic Monte Carlo scripts and regression tests;
- CSV + PNG output for every formal experiment family;
- Streamlit Dashboard for lightweight interactive exploration;
- explicit negative results and crossover regions;
- package/version/import validation and SHA-256 result manifests for releases;
- no claim of 3GPP bit-exact conformance, real hardware measurements, production edge orchestration, or safety certification.
