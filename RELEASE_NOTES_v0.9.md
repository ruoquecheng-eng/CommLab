# CommLab-OFDM v0.9 — Soft Links, HARQ, Channel Acquisition, and Queueing

v0.9 moves several branches from isolated physical-layer algorithms toward complete transmitter/receiver/system loops. The release adds soft-output MIMO detection connected to FEC, CRC-gated HARQ, structured acquisition of high-Doppler ICI matrices, sparse OTFS physical-path estimation, packet-queue scheduling, and finite-blocklength information-theoretic analysis.

## New capabilities

### Soft-output coded MIMO
- Exact small-system max-log bit LLR reference detector.
- QR K-best list detector with approximate max-log LLR output and explicit LLR saturation when a retained list lacks a bit hypothesis.
- End-to-end 2x2 QPSK + `(7,5)_oct` convolutional coding experiment comparing hard K-best/hard Viterbi, soft K-best/soft Viterbi, and exact max-log/soft Viterbi.
- At 8 dB in the current run: information BER is about `1.07e-2` (hard K=4), `3.90e-3` (soft K=4), and `2.44e-4` (exact max-log soft reference).

### CRC-gated Chase HARQ
- CRC-16-CCITT append/check helpers.
- Stateful LLR Chase combiner.
- Block-Rayleigh retransmission experiment with up to four transmissions.
- At 0 dB: final packet success rises from about `0.592` for Type-I HARQ to `0.917` with Chase combining; average transmissions are about `2.86` vs `2.52`.
- Goodput includes retransmission cost rather than reporting reliability alone.

### Training-based high-Doppler ICI acquisition
- Banded structured LS estimator for `y = H_ici x + n` from random full-band OFDM training symbols.
- The detector no longer needs a genie banded matrix in this branch.
- With ~23.6% off-diagonal channel energy at 18 dB, 12 training symbols give band-matrix NMSE about `2.81e-2` and BER about `4.77e-3`; 32 symbols give NMSE about `8.07e-3` and BER about `1.60e-3`, approaching the genie ±2-band result (~`1.1e-3`).

### Sparse OTFS path acquisition
- OTFS pilot dictionary generated from the project waveform/channel convention.
- OMP estimation of grid-aligned delay, Doppler, and complex path gains from one known DD-domain pilot.
- Estimated physical paths are used to reconstruct a detector matrix; this is no longer a known-path branch.
- In the current three-path 6x12 experiment, exact support recovery rises from `0.20` at 15 dB pilot SNR to `0.825` at 20 dB and `1.0` at 25 dB. At 25 dB, data BER is about `5.21e-5`, close to the genie-path run (`1.74e-5`).

### Packet queues and delay-aware scheduling
- FIFO packet queues, stochastic arrivals, per-resource service capacity, backlog traces, and packet-delay statistics.
- Round-robin, max-rate, PF, and delay-aware PF policies share the same arrival/channel realization.
- In the current loaded four-user experiment, delay-aware PF reaches ~`23.36 kbit/slot`, Jain fairness `0.999`, P95 delay `18` slots, and only `0.124 Mbit` residual backlog. Baseline PF reaches ~`22.28 kbit/slot`, fairness `0.987`, P95 delay `155` slots, and `1.42 Mbit` residual backlog.
- This is an abstract MAC/link scheduler, not a standards implementation.

### Finite-blocklength AWGN analysis
- Complex-AWGN capacity and dispersion helpers.
- Normal approximation `R ≈ C - sqrt(V/n)Q^-1(eps) + log2(n)/(2n)`.
- At 10 dB and target error probability `1e-3`, the approximation gives ~`3.05 bit/use` for `n=100`, `3.22` for `n=300`, `3.32` for `n=1000`, versus Shannon capacity `3.46 bit/use`.

## Validation

- `73/73` automated tests passing.
- v0.9 adds seven tests covering soft MIMO LLR signs/equivalence, CRC/Chase combining, packet scheduling, sparse OTFS OMP recovery, banded ICI LS recovery, and finite-blocklength monotonicity.
- New experiments export CSV and PNG artifacts under `results/`.

## Scope notes

- Soft-output exhaustive MIMO is a small-system reference; QR K-best is educational Python, not optimized sphere-decoder hardware.
- Chase HARQ retransmits the same coded packet; incremental redundancy and standards HARQ process timing are not implemented.
- ICI estimation assumes a chosen band width and training stationarity across the estimated OFDM channel matrix.
- OTFS OMP currently searches a discrete delay/Doppler grid and is strongest for grid-aligned paths; fractional off-grid estimation remains future work.
- Queue-aware scheduling uses abstract achievable-bit service values and does not model a 3GPP MAC/HARQ scheduler.
- Finite-blocklength normal approximation is a fundamental-limit approximation, not a code-specific BLER predictor.
