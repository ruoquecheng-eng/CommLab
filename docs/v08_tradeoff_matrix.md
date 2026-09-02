# v0.8 Trade-off Matrix

| Domain | Control variable | Benefit | Cost / failure mode | Headline observation |
|---|---|---|---|---|
| MIMO detection | K-best survivor count | Approaches joint ML performance | More tree expansions | 2x2 16-QAM at 18 dB: K=4 BER ~9.52e-3; K=16/ML ~7.69e-3 |
| MIMO propagation | Spatial correlation rho | None; it is a channel impairment | Rank loss / noise amplification | rho 0->0.95: median cond(H) 2.93->28.97, capacity 6.59->4.52 bit/s/Hz |
| Beamforming | CSI feedback bits | Better alignment to channel | Feedback/codebook overhead | 4x1 at 5 dB: 4 bits ~3.06, 8 bits ~3.42, perfect MRT ~3.61 bit/s/Hz |
| High-Doppler OFDM | ICI matrix bandwidth | Better ICI cancellation | More nonzeros / CG work | +/-2 band at 18 dB: BER ~2.48e-3 vs one-tap ~5.01e-2 |
| Adaptive DPD | Forgetting / block updates | Tracks changing PA inverse | Estimator variance / possible instability | Static final EVM ~4.04%; adaptive EWLS ~2.27% |
| RF model | Cross-memory GMP terms | Removes structural model mismatch | More coefficients and conditioning risk | At 8 dB IBO: MP-DPD ~1.29% EVM; GMP-DPD ~0.74% |
| FEC | Decoder/code family | Coding gain | Latency, block length, iterative complexity | At 3 dB: conv ~5.68e-3, custom LDPC ~3.98e-3, polar SC ~1.39e-3 BER |
| Multiuser scheduling | Opportunism vs history weighting | Higher aggregate rate | Fairness loss if too opportunistic | Max-rate ~248.2 / fairness .344; PF ~200.5 / .890 |

The table is intentionally phrased in terms of **trade-offs**, not winner labels. Results are specific to the documented simulation models and finite Monte Carlo runs.
