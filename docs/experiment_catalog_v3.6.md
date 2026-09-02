# CommLab v3.6 Experiment Catalog

| Script | Question | Outputs |
|---|---|---|
| `v36_exploration_overlap.py` | How do logging exploration, effective sample size, and OPE error interact? | one CSV, two PNGs |
| `v36_clipping_frontier.py` | Where is the clipping bias/variance frontier under weak overlap? | one CSV, two PNGs |
| `v36_model_misspecification.py` | When do propensity corrections help a stale direct outcome model? | one CSV, two PNGs |
| `v36_support_boundary.py` | Which target-policy regions are unsupported, especially for critical tasks? | one CSV, two PNGs |
| `v36_temporal_reuse.py` | How much old logged data should be reused under drift? | one CSV, two PNGs |
| `v36_policy_selection.py` | How do greedy selection error and conservative freezing change with log size? | one CSV, two PNGs |

Run all six with `python tools/run_v36_suite.py`.
