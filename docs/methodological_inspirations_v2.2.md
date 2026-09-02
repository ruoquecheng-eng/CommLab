# Methodological Inspirations — v2.2

v2.2 borrows **problem structure**, not source code, from current research themes in wireless edge intelligence.

## Client selection + communication compression

Recent FL systems increasingly treat client participation, statistical heterogeneity, communication cost, and compression as coupled decisions rather than isolated knobs. Relevant 2026 examples include:

- MetaCS-FL — multi-objective client selection balancing training efficiency and fairness: https://doi.org/10.1016/j.future.2026.108707
- DCCF — dynamic co-optimization of client selection and gradient compression under non-IID data: https://doi.org/10.1016/j.eswa.2026.132239

CommLab v2.2 uses a much simpler transparent top-k/error-feedback model so the participation-versus-compression mechanism can be inspected directly.

## Progressive / multi-task semantic representations

Current task-oriented semantic communication work studies heterogeneous tasks, task-adaptive representations, and variable communication cost, including:

- Multitask Semantic Communications for Edge Intelligence Network: https://doi.org/10.1109/LWC.2026.3711560
- Scalable Semantic Communication for Multi-User Systems with Heterogeneous Tasks: https://doi.org/10.1109/IWCMC69287.2026.11580104

CommLab uses known Gaussian task directions and an analytic base/enhancement subspace instead of a learned encoder.

## Robust RIS-AirComp / edge intelligence

Recent 2026 work explicitly studies RIS-assisted over-the-air federated learning under imperfect cascaded CSI:

- Robust Design for RIS-Assisted Over-the-Air Federated Learning with Imperfect Cascaded CSI: https://doi.org/10.1109/TCCN.2026.3661518

v2.2 extends the prior CommLab RIS-AirComp branch in a different direction: slow finite-bit RIS control under channel evolution and learning dynamics.

## Hardware realism

The AirComp hardware branch is motivated by the general engineering fact that analog superposition is sensitive to amplitude linearity and converter dynamic range. The implementation is intentionally a normalized behavioral baseline (soft clipping, AGC, uniform I/Q quantization), not a transistor-level or measured RF model.
