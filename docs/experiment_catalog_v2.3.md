# v2.3 Experiment Catalog

| Experiment | Question | Main metrics | Important limitation |
|---|---|---|---|
| `v23_async_federated.py` | How does update staleness affect optimization direction and convergence? | final loss, parameter error, gradient cosine | quadratic convex model |
| `v23_byzantine_robust_fl.py` | When do robust coordinate aggregators resist or fail under malicious updates? | median final loss, parameter error | simple sign-flip/scaling attack |
| `v23_private_aircomp.py` | When does client Gaussian perturbation dominate wireless aggregation error? | learning loss, aggregation MSE | no formal DP accountant |
| `v23_semantic_scheduler.py` | When should task importance/urgency override channel-first scheduling? | task utility, expiry, age, utilization | synthetic semantic packets |
| `v23_split_inference.py` | How much communication/latency can confidence-triggered edge refinement save? | accuracy, channel uses, offload fraction, latency | Gaussian classification toy task |
