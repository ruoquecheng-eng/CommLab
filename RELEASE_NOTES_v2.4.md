# CommLab v2.4 Release Notes

v2.4 focuses on **heterogeneous edge intelligence, straggler resilience, knowledge transfer, deadline-aware inference, and one-bit over-the-air aggregation**. The release deliberately favors transparent system abstractions over heavyweight neural benchmarks so that communication/computation trade-offs remain inspectable.

## New capability groups

### Personalized federated learning
- Small-sample client-local ridge models and a pooled global model.
- Convex interpolation between global and local parameters.
- Held-out client test loss, p90 client loss, and personalization drift.
- Heterogeneity sweeps that expose a real bias-variance operating point rather than assuming full personalization is always best.

### Straggler-resilient coded computing
- Uncoded synchronous round baseline.
- Two-copy task replication.
- MDS-style recovery abstraction: launch K+r coded workers and finish after any K responses.
- Mean/P95/P99 latency and compute-load accounting.

### Federated knowledge distillation
- Clients fit local linear teachers.
- Full-model averaging uploads one model vector per client.
- Distillation uploads teacher logits on a shared public probe set and fits a server student.
- Task accuracy is reported against uploaded scalar count and wireless logit SNR.

### Deadline- and channel-aware split inference
- Per-sample residual-link SNR variation.
- Local confidence, expected edge reliability, and hard latency deadline in one offload rule.
- Raw accuracy and **on-time task accuracy** are reported separately so late inference is not counted as successful real-time service.

### One-bit OTA sign aggregation
- One BPSK gradient sign per client/coordinate.
- Wireless superposition implements a noisy majority vote.
- Client-count, SNR, local-gradient-noise, and sign-flipping-client sweeps.
- The branch is a signSGD-style analog abstraction, not a coded standards protocol.

## Selected findings

- Personalization strength should increase with data heterogeneity. In the tested small-client-data problem, homogeneous clients favor the global model; moderate heterogeneity produces an interior blend, while large heterogeneity moves the optimum toward local specialization.
- With 15% stragglers, uncoded P95 round latency is about 276 ms. An MDS-style K+4/K recovery abstraction lowers it to about 43.7 ms at 1.33x compute load; full two-copy replication costs 2x compute while retaining a heavier latency tail.
- At 10 dB, eight public logits per client use one third of the scalar uplink of a 24-D model vector and achieve about 92.6% task accuracy versus about 95.5% for model averaging. Twelve probes raise distilled accuracy to about 94.3% at half the model-upload scalar count.
- At a tight 1.8 ms deadline and 5 dB mean residual link, static confidence offload reaches high raw accuracy but misses the deadline for roughly 57.6% of samples. Its on-time task accuracy is about 36.9%, versus about 72.5% for the deadline-aware policy with zero modeled deadline misses.
- One-bit OTA majority aggregation gains substantially from more participating clients, but sign-flipping participants erode the vote margin: for 31 clients at 5 dB, sign error grows from about 5.7% with no attackers to about 12.7% at 30% sign flips and about 20.7% at 40%.

## Scope boundaries

- Personalized FL is a linear/ridge held-out generalization baseline, not a neural personalization benchmark.
- The MDS coded-compute branch models latency recoverability and redundant work; it does not implement a specific gradient code over real training tensors.
- Federated distillation assumes a shared public probe set and linear teachers/students.
- Split-inference latency and channel uses are normalized abstractions, not a calibrated MEC stack.
- OTA sign aggregation assumes synchronous sign symbols and does not include coding, carrier offsets, or practical multiple-access synchronization.
