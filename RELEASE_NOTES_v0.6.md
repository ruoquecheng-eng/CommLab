# CommLab-OFDM v0.6 Release Notes

v0.6 focuses on **realistic baseband front-end impairments, decoder-aware interference handling, iterative sparse coding, learned RF linearization, and a carefully bounded OTFS prototype**.

## Added

### IQ imbalance
- widely-linear impairment `y = alpha*x + beta*conj(x)`;
- gain/phase parameterization;
- LS estimation from known training;
- analytic inverse compensation;
- image rejection ratio metric;
- 64-QAM OFDM BER/EVM experiment.

### Sampling-clock offset
- fractional-time waveform resampling;
- cubic complex interpolation;
- two-separated-training-burst ppm estimator;
- inverse resampling baseline;
- pilot affine phase-vs-subcarrier estimator for comparison.

### Narrowband interference
- controlled complex-tone jammer with explicit SIR;
- robust median/MAD carrier outlier detector;
- decoder-aware soft erasure for flagged QPSK carriers before Viterbi.

### Sparse iterative FEC
- custom rate-1/2 sparse accumulator-LDPC code;
- deterministic parity-check generation;
- exact sparse encoder;
- normalized Min-Sum iterative decoder;
- convergence/iteration instrumentation.

### Data-fitted DPD
- odd-order complex memoryless polynomial basis;
- indirect-learning LS fit from PA input/output samples;
- learned predistorter experiment against PA-only and known-Rapp-inverse baselines.

### OTFS prototype
- unitary ISFFT/SFFT transforms;
- OFDM Heisenberg/Wigner modulation chain;
- normalized delay-Doppler path model;
- numerical effective channel matrix builder for small grids;
- linear LMMSE detector;
- OFDM diagonal-energy and DD concentration diagnostics.

### Dashboard
New interactive labs:
- IQ Imbalance;
- Sampling Clock;
- data-fitted polynomial DPD option in the PA lab.

## Validation

- **43/43 tests passing**.
- no-channel OFDM-grid and OTFS roundtrips validated to machine precision;
- IQ LS inversion validated noiselessly;
- SCO zero-offset identity and inverse-resampling sanity test;
- LDPC syndrome and noiseless Min-Sum decode test;
- polynomial DPD identity-fit test.

## Important interpretation limits

- The custom sparse code is not a 3GPP/DVB LDPC implementation.
- The SCO model is normalized baseband resampling; it does not include ADC jitter or a hardware clock loop.
- IQ compensation is training-based and does not model frequency-dependent IQ imbalance.
- The polynomial DPD is memoryless; the Rapp PA also has no memory.
- The OTFS BER comparison is **illustrative and receiver-asymmetric**: OFDM uses a conventional diagonal one-tap receiver while OTFS uses a known effective-channel full LMMSE detector on a small grid.

These limits are intentionally documented rather than hidden.
