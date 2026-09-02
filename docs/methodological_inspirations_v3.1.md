# Methodological Inspirations — v3.1

CommLab v3.1 uses original transparent NumPy implementations. The following recent/public references influenced **problem structure and experimental questions**, not source code.

- Goal-oriented communications for cyber-physical systems (Nature Reviews Electrical Engineering, 2026): task/control utility should complement or replace uniform packet/bit metrics in constrained CPS communication. https://www.nature.com/articles/s44287-026-00303-9
- Channel-Adaptive Edge AI (2026 preprint): motivates joint adaptation of transmitted feature quality and edge model complexity under end-to-end inference constraints. https://arxiv.org/abs/2603.03146
- TrimMoE (2026 preprint): communication-aware adaptive depth and early exit motivate treating computation depth as an online communication-coupled action. https://arxiv.org/abs/2608.00573
- Component-based event-triggered networked control under hybrid attacks (Journal of the Franklin Institute, 2026): motivates component-wise rather than whole-state transmission as a control/network design variable. https://doi.org/10.1016/j.jfranklin.2026.108774
- FailLite (SoCC 2025 proceedings, published 2026): motivates resource-constrained failure-resilient model serving and selective/heterogeneous replication rather than assuming full model duplication is affordable. https://doi.org/10.1145/3772052.3772243
- Checkmate (NSDI 2026): motivates explicit accounting of checkpoint frequency, repeated work after failure, and recovery overhead in distributed learning/compute systems. https://www.usenix.org/conference/nsdi26/presentation/bhardwaj

No v3.1 branch claims reproduction of these systems or their reported performance.
