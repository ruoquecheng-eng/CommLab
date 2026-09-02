# CommLab v1.2 Release Notes

v1.2 expands CommLab in five directions that are deliberately different from the v1.1 additions: reconfigurable propagation, overloaded MU-MIMO user selection, source-count-aware subspace sensing, clutter/missed-detection multi-target tracking, and sparse hybrid-precoder approximation.

## New capability groups

### Reconfigurable intelligent surface (RIS) link baseline
- SISO cascaded BS–RIS–UE channel with phase-only reflection.
- Continuous co-phasing of cascaded terms and finite-bit phase quantization.
- Rate/array-size studies compare random, 1/2/3-bit, and continuous phase control.
- Explicitly normalized and geometry-free: no 3GPP path loss, mutual coupling, insertion loss, or hardware calibration is claimed.

### Semi-orthogonal MU-MIMO user selection
- Greedy SUS first rewards channel strength, then favors users with low normalized cross-correlation and large orthogonal-projection norm.
- Creates an overloaded candidate-user study before ZF downlink precoding.
- Compares random, strongest-norm, and SUS scheduling using sum rate, Gram conditioning, and user correlation.

### MUSIC model-order estimation with MDL
- Adds covariance-eigenvalue MDL source-count estimation before MUSIC.
- Exposes source-count reliability versus SNR and snapshot count instead of assuming the number of emitters is always known.
- Keeps the spatially-white-noise / narrowband-array assumptions visible.

### Multi-target range/velocity Kalman tracking
- Constant-velocity 2-state Kalman tracks using joint range/velocity detections.
- Greedy Mahalanobis nearest-neighbour association, missed-detection survival, tentative-track spawning, and stale-track deletion.
- Synthetic crossing-target study includes missed detections and sparse clutter.

### OMP hybrid precoding
- Orthogonal matching pursuit approximates the dominant right-singular transmit subspace with phase-only DFT atoms.
- Compares OMP hybrid, one-shot DFT beam selection, and full-digital SVD as RF-chain count varies.
- Receive processing is fully digital in this new OMP branch, so the experiment isolates transmit-side RF-chain constraints.

## Headline results

- RIS @ 10 dB normalized SNR, 128 elements: random phases `1.05`, 1-bit `5.10`, 2-bit `5.97`, 3-bit `6.17`, continuous phase `6.24 bit/s/Hz` mean spectral efficiency.
- 24 candidate / 4 scheduled users, 8-Tx ZF: random mean sum rate `13.33`, strongest-norm `20.33`, SUS `20.61 bit/s/Hz`; median cond(HH^H) improves `7.69 -> 6.37` from strongest-only to SUS.
- MDL source count for three sources at -5 dB: correct-count probability rises from `0.558` with 30 snapshots to `0.983` with 60 and `1.0` with 120 snapshots in the current Monte Carlo.
- Two-target tracker with 14% per-target missed detections plus sparse clutter: range RMSE `2.01 m` raw -> `0.659 m` tracked. The current run retains two confirmed tracks but shows one target-track fragmentation event, preserving the nearest-neighbour limitation.
- 32x8 sparse MIMO, 2 streams, 10 dB: OMP hybrid retains about `92.7%` of full-digital mean rate with 2 RF chains, `97.4%` with 4, and `99.0%` with 8; it also outperforms the one-shot DFT-selection baseline at every tested RF-chain count.

## Boundaries

- RIS is a normalized phase-control baseline, not a geometry-calibrated or standards channel model.
- SUS is a flat-fading user-selection study; no scheduler queues, CQI delays, or 3GPP control signaling are included.
- MDL/MUSIC assumes a ULA, narrowband signals, adequate covariance snapshots, and spatially white noise.
- Multi-target association is greedy nearest neighbour, not JPDA/MHT/PHD filtering; clutter can create tentative tracks and long miss streaks can fragment an identity.
- OMP hybrid precoding uses a DFT analog dictionary and ideal phase-only weights; quantized phase shifters, RF insertion loss, and receiver hybrid constraints are not included in the headline OMP experiment.
