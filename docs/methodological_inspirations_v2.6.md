# Methodological Inspirations — v2.6

These references motivated **problem structure and evaluation questions**, not copied implementation.

- Hu, Chen & Larsson, *Mixed-Timescale Differential Coding for Downlink Model Broadcast in Wireless Federated Learning* (2026). Motivates exploiting temporal correlation in global-model broadcasts while explicitly handling missed differential updates and periodic recovery. https://arxiv.org/abs/2607.13119
- Bagci et al., *Update Estimation and Scheduling for Over-the-Air Federated Learning with Energy Harvesting Devices*. Motivates coupling AirComp participation with battery/harvest state and data diversity rather than channel quality alone. https://arxiv.org/abs/2501.18298
- Tota Khel et al., *Analog Over-the-Air Federated Learning with Interference-Based Energy Harvesting* (published online 2026). Reinforces energy-aware OTA-FL scheduling as an active systems problem. https://uwe-repository.worktribe.com/output/16257369
- HKU work on *Inference at the wireless edge: capacity, progressive transmission, and multiple access*. Motivates progressive feature transmission, task-importance ordering and termination when marginal inference gain no longer justifies communication cost. https://hub.hku.hk/handle/10722/346404
- 2026 wireless-FL client-selection work continues to emphasize communication efficiency, data quality, fairness and dynamic link conditions, motivating the v2.6 separation between physical aggregation quality and statistical learning bias.
