# CommLab-OFDM v0.8 Release Notes

v0.8 shifts emphasis from adding isolated blocks to studying **performance/complexity, CSI overhead, adaptation, model mismatch, and system-level fairness**.

## New modules

- QR-based `k_best_detect` for tunable MIMO tree search.
- Kronecker-style spatially correlated Rayleigh MIMO generation and equal-power capacity evaluation.
- 4x1 limited-feedback MISO beamforming with finite unit-vector codebooks.
- Conjugate-gradient LMMSE detector for full or band-limited OFDM ICI matrices.
- Stateful complex RLS plus a more stable block exponentially-weighted LS memory-polynomial estimator.
- Causal generalized-memory-polynomial basis with lagging envelope cross terms.
- Self-contained polar transform, BEC-derived reliability ordering, and min-sum successive-cancellation decoder.
- Proportional-fair OFDMA resource scheduler and Jain fairness metric.

## Headline results

- **2x2 16-QAM K-best:** at 18 dB, MMSE BER ~= 2.41e-2, K=4 ~= 9.52e-3, and K=16 = exhaustive ML ~= 7.69e-3.
- **MIMO correlation:** rho 0 -> 0.95 increases median cond(H) 2.93 -> 28.97; ZF BER 2.87e-2 -> 3.46e-1 at 12 dB.
- **4x1 limited feedback:** at 5 dB, perfect MRT rate ~= 3.61 bit/s/Hz; 4, 6, 8 feedback bits yield ~= 3.06, 3.28, 3.42.
- **CG ICI:** with 25.3% off-diagonal channel energy at 18 dB, one-tap BER ~= 5.01e-2; CG-LMMSE band +/-2 ~= 2.48e-3 in about 27 iterations.
- **Adaptive DPD:** a frozen DPD drifts from 0.85% to 4.04% EVM; block-EWLS adaptation finishes near 2.27%.
- **Cross-memory GMP:** at 8 dB back-off, standard MP-DPD ~= 1.29% EVM and GMP-DPD ~= 0.74%; both deteriorate at aggressive 6 dB back-off.
- **Rate-1/2 FEC:** at 3 dB Eb/N0, soft convolutional ~= 5.68e-3, custom LDPC ~= 3.98e-3, educational polar-SC ~= 1.39e-3 BER.
- **OFDMA PF scheduling:** max-rate sum ~= 248.2 / fairness 0.344; PF ~= 200.5 / fairness 0.890; round-robin ~= 157.0 / fairness 0.865.

## Important limitations

- The K-best and ML studies are small-MIMO educational baselines, not optimized hardware detectors.
- Beamforming codebooks are random isotropic codebooks, not IEEE 802.11/3GPP standardized CSI codebooks.
- The polar code is an educational BEC-designed construction, not 5G NR control-channel coding.
- Adaptive DPD remains offline/baseband simulation. The stable headline uses block EWLS; an unconstrained sample-wise RLS version exhibited coefficient-instability spikes under stronger drift.
- The GMP experiment uses a synthetic PA generated from the same broad model family, so its near-perfect forward identification demonstrates structural model match, not real-hardware generalization.
- The PF scheduler assumes perfect instantaneous achievable-rate knowledge and no inter-user interference.

## Validation

- **66/66 automated tests pass.**
- `python -m compileall src app experiments tools` passes.
- v0.8 has **45 CSV datasets** and **81 generated figures** after the current experiment suite.
