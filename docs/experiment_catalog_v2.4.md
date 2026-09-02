# v2.4 Experiment Catalog

## `v24_personalized_fl.py`
Sweeps client heterogeneity and global/local personalization weight. Produces mean/p90 held-out client MSE and optimum personalization trend.

## `v24_straggler_coding.py`
Sweeps straggler probability for uncoded synchronization, MDS-style K-of-N recovery, and two-copy replication. Reports mean/P95/P99 round latency and compute load.

## `v24_federated_distillation.py`
Sweeps public-probe count and noisy logit-upload SNR. Compares full-model averaging accuracy with server-side student distillation and scalar communication cost.

## `v24_channel_aware_split.py`
Sweeps mean residual-link SNR and inference deadline for static-confidence and channel/deadline-aware offloading. Reports raw accuracy, on-time accuracy, channel uses, latency, and deadline misses.

## `v24_sign_aircomp.py`
Sweeps client count and SNR for one-bit OTA majority aggregation, then sign-flipping-client fraction for a fixed 31-client system.
