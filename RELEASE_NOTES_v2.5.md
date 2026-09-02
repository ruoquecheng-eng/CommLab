# CommLab v2.5 Release Notes

v2.5 extends the edge-intelligence branch toward resilience, hierarchical personalization, joint privacy/RF impairment analysis, energy-aware real-time inference, and heterogeneous downlink model distribution.

## New capabilities

- **Resilient asynchronous FL:** stale gradients and Byzantine sign-flip/scaling attacks coexist. Baselines include naive mean, coordinate median, and a transparent conflict-rejection + staleness-decay heuristic.
- **Clustered personalization:** compares one global model, two cluster models, and fully local models under structured heterogeneity and imperfect client clustering.
- **Private hardware AirComp:** evaluates clipped-gradient aggregation with client perturbation, PA clipping, AWGN, AGC and finite-resolution ADC in one chain.
- **Energy-aware split inference:** offload decisions jointly consider confidence, deadline feasibility, wireless energy and latency.
- **Layered model multicast:** introduces an edge-intelligence downlink baseline with a common base model and an enhancement layer for stronger clients.

## Selected findings

- At 13% Byzantine clients and mean staleness 4, naive averaging reaches median final loss about **2.10**, while coordinate median remains near **0.0208**. The more complicated stale/conflict heuristic is slightly worse than median, demonstrating that explicit complexity is not automatically beneficial.
- With clean clustering, the cluster model stays near test MSE **0.271** while the global model degrades from about **0.360** to **1.74** as cluster separation grows from 0.3 to 1.2. With 25% assignment error, the cluster model can become substantially worse than the local baseline.
- In private hardware AirComp, once the privacy-noise multiplier reaches 0.25, median MSE is about **4.7e-3 / 4.5e-3 / 4.4e-3 / 4.4e-3** for 3/4/6/8-bit ADC. Converter precision beyond roughly 4–6 bits is no longer the dominant error source.
- At 0 dB mean link SNR, the static split policy has raw accuracy about **81.8%** but only **45.4% on-time accuracy**. The energy-aware policy has about **74.8% on-time accuracy**, zero modeled deadline misses, and much lower mean device energy.
- As client SNR heterogeneity increases, common multicast becomes increasingly bottlenecked by the weakest receiver. At 7 dB SNR standard deviation, layered multicast needs roughly **3.49e5** normalized delivery-time units versus **7.08e5** for full common multicast, at a mean task-utility proxy of 0.85.

## Boundaries

These are educational/research baselines. The project does not claim a production FL security protocol, calibrated handset power model, formal DP accounting, neural model scalable coding, or standards-compliant multicast PHY.
