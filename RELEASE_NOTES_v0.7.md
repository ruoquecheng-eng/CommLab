# CommLab-OFDM v0.7 Release Notes

v0.7 is a receiver/RF-depth release. It adds explicit inter-carrier-interference models, nonlinear memory, lower-overhead MIMO channel acquisition, nonlinear MIMO detection baselines, iterative OTFS detection, and confidence-aware Monte Carlo reporting.

## Validation

- **54/54 automated tests passing**
- `python -m compileall` passes for `src/`, `experiments/`, and `app/`
- v0.7 experiment suite: `python experiments/run_v07_suite.py`

## 1. ICI-aware high-Doppler OFDM

New module: `src/commlab/equalization/ici.py`

The simulator can now explicitly probe one CP-protected OFDM symbol through a deterministic time-varying multipath channel and construct the full frequency-domain matrix

`Y = H_ici X + N`.

This makes Doppler-generated off-diagonal coupling measurable rather than hiding it inside a BER curve.

Receivers:
- diagonal / one-tap LMMSE (`bandwidth=0`);
- banded LMMSE retaining +/-1, +/-2, or +/-4 couplings;
- full known-matrix LMMSE.

At 18 dB and moving-path Doppler 1.5 subcarrier spacings:
- off-diagonal energy: ~23.6%;
- one-tap BER: ~4.21e-2;
- banded +/-2 BER: ~1.20e-3;
- full-matrix LMMSE: 0 observed errors in the current run.

This is a known-channel structural experiment, not a practical online ICI channel estimator.

## 2. Memory-polynomial PA and DPD

New module: `src/commlab/rf/memory_polynomial.py`

Implemented:
- memory-polynomial feature basis `x[n-m]|x[n-m]|^(p-1)`;
- arbitrary memory-polynomial application;
- least-squares PA identification;
- indirect-learning postdistorter fit reused as a predistorter;
- deterministic nonlinear 3-tap PA model.

At 8 dB input back-off:
- PA-only EVM: ~10.77%;
- memory-DPD EVM: ~0.85%;
- guard/occupied leakage: ~-29.9 dB -> ~-44.2 dB.

At 4 dB back-off the offline inverse fit becomes unstable. This failure is retained intentionally as an operating-range limitation rather than hidden.

## 3. MIMO LMMSE channel-estimation baseline

The existing orthogonal-training LS estimator now has a transparent scalar-prior LMMSE shrinkage baseline.

Channel NMSE:
- 0 dB: LS ~0.698, LMMSE ~0.410;
- 6 dB: LS ~0.176, LMMSE ~0.150;
- 24 dB: both ~0.0028.

As expected, the prior helps most when training observations are noisy and becomes irrelevant at high SNR.

## 4. One-symbol frequency-orthogonal MIMO training

New MIMO pilot design:
- all configured active carriers are interleaved across transmit antennas;
- both transmitters train simultaneously in one OFDM symbol;
- each receive/transmit link is reconstructed using finite-CIR LS and FFT.

Training overhead:
- old time-orthogonal full-active scheme: 2 OFDM symbols / 104 pilot resource elements;
- new frequency-orthogonal finite-CIR scheme: 1 OFDM symbol / 52 pilot resource elements.

At 12 dB in the current 2x2 sparse multipath family:
- two-slot full-active LS NMSE: ~0.144;
- one-slot finite-CIR LS NMSE: ~0.0508.

The gain comes from an explicit finite-channel-length model, not from fewer pilots alone.

## 5. 2x2 maximum-likelihood MIMO detector

New `ml_detect_small()` exhaustively searches all low-order transmit vectors.

For QPSK and 2 transmit antennas there are only 4^2 = 16 candidates per channel use, so exhaustive ML is practical as an educational bound.

At 12 dB:
- ZF BER: ~3.00e-2;
- MMSE BER: ~2.02e-2;
- exhaustive ML BER: ~4.29e-3.

This detector is deliberately labeled non-scalable because complexity grows exponentially with constellation order and transmit-stream count.

## 6. Sparse CG-LMMSE OTFS detection

The OTFS branch now supports:
- strongest-coefficient row sparsification of the effective channel;
- conjugate-gradient solution of the regularized LMMSE normal equations;
- direct full LMMSE as a numerical reference.

On the current 6x12 grid at 14 dB:
- 2 coefficients/row: 92.22% channel energy, BER ~5.51e-3, ~12 CG iterations;
- 3 coefficients/row: 96.69% energy, BER ~8.43e-4, ~24 iterations;
- 5 coefficients/row: 99.06% energy, BER ~4.96e-5, ~27 iterations;
- 8 coefficients/row: effectively all modeled energy, 0 observed errors, ~29.5 iterations.

This creates an explicit sparsity / performance / iterative-complexity trade-off.

## 7. Confidence-aware BER simulation

New module: `src/commlab/metrics/confidence.py`

Implemented:
- Wilson score intervals;
- BER + 95% confidence bounds;
- sequential Monte Carlo stopping by target error count or bit budget.

QPSK AWGN validation tracks theory across 0-10 dB Eb/N0. At 10 dB:
- 10 errors / 4,000,000 bits;
- measured BER: 2.50e-6;
- 95% Wilson interval: approximately [1.36e-6, 4.60e-6];
- theoretical BER: 3.87e-6.

This replaces misleading literal `BER=0` claims with statistically meaningful bounds where appropriate.


## 8. Frequency-selective IQ imbalance

New module: `src/commlab/impairments/frequency_iq.py`

The previous flat model `y=alpha*x+beta*x*` is generalized to

`y = h_d * x + h_i * conj(x)`.

Known complex training jointly identifies the direct and image FIR filters. For CP-protected OFDM, each mirror-subcarrier pair `(k,-k)` is then corrected by solving the corresponding 2x2 widely-linear frequency-domain system.

At 26 dB for the current 64-QAM impairment:
- raw BER: ~2.55e-2;
- flat IQ compensation BER: ~1.03e-3;
- FIR mirror-pair compensation: 0 observed errors;
- EVM: ~12.98% -> 8.38% -> 4.66%.

This directly closes one limitation noted in v0.6: frequency-selective image coupling cannot generally be represented by one global `(alpha,beta)` pair.

## 9. Dashboard

New interactive labs:
- **High-Doppler ICI**: visualize the effective OFDM channel matrix and compare one-tap, banded, and full ICI-aware detection;
- **2x2 MIMO Detection**: live ZF/MMSE/ML comparison for QPSK.

Existing labs remain available for OFDM/CFO, phase noise, IQ imbalance, SCO, PA/DPD, and water-filling.

## Scope boundaries retained

v0.7 still does not claim:
- standards compliance;
- over-the-air RF validation;
- online/adaptive memory DPD;
- online ICI-channel estimation;
- standards MIMO pilot patterns;
- scalable ML MIMO detection;
- standards OTFS detector equivalence.
