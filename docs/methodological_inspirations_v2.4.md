# v2.4 Methodological Inspirations

The implementation is original to CommLab; these references motivated problem structure and experiment design rather than supplying copied code.

- **Personalizing Federated Learning with Over-the-Air Computations** — motivates treating personalization and wireless aggregation as a joint edge-learning problem rather than assuming one global model fits all clients. https://arxiv.org/abs/2302.12509
- **Personalized Over-the-Air Federated Learning with Personalized Reconfigurable Intelligent Surfaces** — motivates heterogeneity-aware personalized wireless FL and cross-layer personalization. https://arxiv.org/abs/2401.12149
- **Coded Computing for Low-Latency Federated Learning over Wireless Edge Networks** — motivates explicit straggler/redundancy/round-latency accounting. https://arxiv.org/abs/2011.06223
- **Straggler-Resilient Federated Learning over A Hybrid Conventional and Pinching Antenna Network** — recent example showing straggler mitigation remains an active wireless-FL systems problem. https://arxiv.org/abs/2508.15821
- **Broadband Digital Over-the-Air Computation for Wireless Federated Edge Learning** — reinforces that aggregation representation, synchronization, coding, and task learning are tightly coupled in practical wireless edge learning. https://arxiv.org/abs/2212.06596

CommLab v2.4 deliberately keeps the new branches small and interpretable: ridge personalization, MDS-style latency recovery, linear public-logit distillation, normalized deadline-aware split inference, and one-bit majority aggregation.
