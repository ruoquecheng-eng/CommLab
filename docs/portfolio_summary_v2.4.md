# CommLab v2.4 — Portfolio Summary

## Recommended title
**CommLab: Reproducible Wireless Systems and Edge-Intelligence Co-Design Laboratory**

## One-line description
A modular Python simulation platform connecting waveform/MIMO/RIS/ISAC and network control with federated learning, over-the-air computation, task-oriented communication, real-time edge inference, and distributed-compute reliability.

## Strongest v2.4 additions

- Built a held-out personalized-FL bias/variance experiment showing that the optimal global-to-local blend depends on non-IID client heterogeneity.
- Added a straggler-resilient coded-computing abstraction with mean/P95/P99 round latency and explicit redundant-compute cost.
- Implemented federated knowledge distillation where clients upload public-probe logits instead of full parameter vectors and evaluated accuracy versus wireless scalar budget.
- Extended split inference with per-sample channel quality and hard deadlines, separating raw classification accuracy from on-time task accuracy.
- Added one-bit OTA majority-sign aggregation with scaling and adversarial sign-flip sweeps.

## Safe CV bullets

- Developed and release-validated a Python wireless/edge-intelligence laboratory with 180 automated tests and 397 hashed experiment artifacts spanning PHY, MIMO, RIS, ISAC, HARQ/MAC, distributed learning, AirComp, semantic transport, and edge inference.
- Designed cross-layer experiments demonstrating that client heterogeneity, worker stragglers, communication representation, inference deadlines, and one-bit aggregation can change downstream task performance even when conventional link-level metrics appear favorable.
- Built deterministic Monte Carlo pipelines, interactive Streamlit labs, environment-independent package tests, release manifests, and explicit model/scope limitations for reproducible engineering analysis.

## Avoid claiming

- Production personalized-FL or gradient-coding performance.
- A standards-compliant federated-distillation, OTA-sign, or MEC protocol.
- Neural semantic models or large-scale benchmark training.
- Hardware latency, energy, or synchronization validation.
