# Methodological Inspirations — v2.5

v2.5 borrows **research-question structure**, not source-code implementations.

- 2026 Byzantine-robust asynchronous FL work motivates evaluating malicious updates, staleness and non-IID effects jointly rather than in isolated experiments.
- Privacy-preserving / Byzantine-robust edge FL motivates treating privacy, robustness and dropout as coupled system constraints.
- Coherence-aware over-the-air distributed learning motivates explicit treatment of heterogeneous link impairments in wireless learning.
- Multi-stage semantic edge inference motivates progressive / conditional communication rather than unconditional full-feature offload.
- Task-oriented edge inference work motivates reporting task utility together with rate/latency rather than source reconstruction alone.

CommLab uses transparent NumPy baselines so assumptions and failure regions remain inspectable.
