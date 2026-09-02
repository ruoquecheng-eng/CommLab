# CommLab v2.7 — Methodological Inspirations

These references motivated *problem structure and evaluation questions*. CommLab implements its own transparent educational baselines and does not reproduce the cited algorithms.

## Mixed-timescale FL downlink synchronization

- C.-H. Hu, Z. Chen, E. G. Larsson, **“Mixed-Timescale Differential Coding for Downlink Model Broadcast in Wireless Federated Learning,”** 2026. The paper motivates age-aware recovery from missed differential broadcasts and mixed reference timescales. CommLab v2.7 uses a simpler budgeted age-triggered keyframe controller.  
  https://arxiv.org/abs/2607.13119

## Multi-objective / carbon-aware client orchestration

- **FedCAMO: Federated Learning Carbon-Aware Multi-Objective Client Selection**, Computer Networks, 2026. It motivates treating carbon budget, accuracy, execution cost and fairness as simultaneous scheduling objectives. CommLab uses a small convex FL trace and a transparent weighted score rather than the paper's controller.  
  https://www.sciencedirect.com/science/article/pii/S1389128626004986

- **A Fairness Perspective on Client Selection and Aggregation Methods for Non-IID Mitigation in Federated Learning: A Survey**, Electronics, 2026. It motivates reporting participation fairness and not evaluating selection only by convergence speed.  
  https://www.mdpi.com/2079-9292/15/14/3178

## Edge AI model caching and inference offloading

- **Federated graph reinforcement learning for joint caching and inference offloading in edge intelligence**, Physical Communication, 2026. It motivates the slow cache-update / fast inference-routing decomposition and explicit model-storage constraints. CommLab implements greedy static/periodic/LRU baselines, not graph RL.  
  https://www.sciencedirect.com/science/article/pii/S1874490726002429

- **GNN-enhanced Multi-Agent Reinforcement Learning for joint model caching and task offloading in collaborative Mobile Edge Intelligence networks**, Future Generation Computer Systems, 2026. It reinforces the need to account for model storage, time-varying wireless demand, and inference latency jointly.  
  https://www.sciencedirect.com/science/article/pii/S0167739X26003754

## Runtime FL orchestration

- **FedJoint: A software architecture for adaptive orchestration in federated learning systems**, Information and Software Technology, 2026. It frames client selection and aggregation timing as coupled runtime-control problems under changing system conditions. CommLab v2.7 follows the same systems question while remaining a numerical simulator.  
  https://doi.org/10.1016/j.infsof.2026.108177
