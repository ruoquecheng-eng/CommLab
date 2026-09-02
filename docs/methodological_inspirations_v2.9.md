# Methodological Inspirations — v2.9

These sources motivate **problem structure only**; CommLab implements independent transparent baselines and does not reproduce the cited algorithms.

## Long-horizon federated client orchestration
- **FedCAMO (Computer Networks, 2026)** — carbon-budgeted multi-objective FL client selection with online control, fairness, and compute/communication energy accounting. CommLab uses this only as inspiration for jointly exposing carbon, fairness, and system-state constraints; v2.9 adds explicit battery energy causality and a simple virtual-debt baseline.
- **MetaCS-FL (Future Generation Computer Systems, 2026)** — event-driven client selection using historical/current client state and multiple objectives including time, energy, accuracy, and fairness. CommLab deliberately uses a transparent score rather than the paper's metaheuristic optimization.
- **FedCure (AAAI 2026)** — participation-aware scheduling with virtual queues in semi-asynchronous non-IID FL. This supports the broader design principle that participation imbalance should be persistent system state rather than a one-round penalty.

## Networked estimation and control
- **The Many Facets of Information in Networked Estimation and Control (Annual Review of Control, Robotics, and Autonomous Systems)** — review of event-triggered communication, estimation under communication constraints, and the fact that timing/freshness value depends on the physical control task. v2.9 uses a small multi-loop scalar control baseline to demonstrate this metric dependence.

## Digital twin / edge state synchronization
- 2026 digital-twin and semantic-edge literature increasingly treats synchronization error, communication load, and edge inference jointly. CommLab keeps this idea at the level of a transparent mode-switching predictor and explicit wrong-prefetch cost rather than using an opaque AI twin.
