# CommLab v2.3 — Portfolio Summary

## Recommended title
**CommLab: A Reproducible Wireless Systems and Edge-Intelligence Simulation Laboratory**

## One-line description
A modular Python research simulator connecting PHY/MAC/network effects to downstream learning, sensing, distributed computation, task-oriented communication, robustness, and resource-control objectives.

## Strongest v2.3 additions

- Built an asynchronous FL simulator that measures both optimization loss and the angular conflict between stale and current gradients.
- Implemented Byzantine sign-flip/scaling attacks with mean, coordinate-median, and trimmed-mean aggregation to expose empirical robustness breakdown regions.
- Coupled client-side clipping/Gaussian perturbation with AirComp aggregation to quantify privacy-noise versus wireless-noise learning degradation without overstating formal DP guarantees.
- Added semantic packet scheduling where radio resources are allocated by channel quality, task importance, expected task value per resource, or urgency.
- Added confidence-triggered split inference to quantify classification accuracy, residual-feature communication use, offload rate, and latency.

## Safe CV bullets

- Developed a Python wireless-systems laboratory with 175 automated tests and 382 hashed result artifacts spanning OFDM/MIMO, Cell-Free/RIS/ISAC, coding/HARQ, random access, AirComp, federated learning, semantic communication, and cross-layer control.
- Designed reproducible communication-learning experiments showing that stale gradients, communication-driven client bias, adversarial updates, privacy perturbations, and radio-resource scarcity can change downstream optimization/task utility even when conventional link metrics appear favorable.
- Implemented interactive Streamlit experiments and release-verification tooling with deterministic Monte Carlo datasets, figures, manifests, package-install tests, and explicit scope limitations.

## Avoid claiming

- Formal differential privacy guarantees.
- Production Byzantine-security guarantees.
- A standards-compliant FL/MEC/semantic-communication stack.
- Neural semantic coding or large-scale deep-learning benchmarks.
- Hardware validation.
