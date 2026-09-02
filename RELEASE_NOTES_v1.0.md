# CommLab v1.0 Release Notes

v1.0 is the first milestone that treats the repository as a **wireless communication systems laboratory** rather than only an OFDM receiver simulator. It adds new link-reliability, link-adaptation, delay-Doppler refinement, sensing, and cross-impairment integration experiments while preserving explicit non-standard / no-hardware boundaries.

## New capability groups

### Incremental-redundancy HARQ
- systematic-first puncturing/rate-matching schedule for the custom sparse LDPC mother code;
- full mother-code soft buffer with zero-LLR erasures for untransmitted positions;
- comparison against full-code Chase repetition using packet success, average coded bits, HARQ rounds, and payload goodput;
- educational mapping only: **not** 3GPP/DVB redundancy versions.

### LDPC-coded soft-output MIMO
- 2x2 QPSK Rayleigh MIMO carrying one custom LDPC codeword across both spatial streams;
- QR K-best list LLRs and exact max-log LLRs feed the normalized Min-Sum decoder;
- reports BER/FER and average LDPC iterations, showing that detector reliability changes both error rate and iterative-decoder cost.

### OTFS off-grid Doppler refinement
- local continuous-Doppler search around a correctly acquired coarse sparse support;
- joint least-squares gain update after coordinate refinement;
- explicitly isolates grid mismatch; integer delay and correct coarse support remain assumptions.

### ACK/NACK-driven OLLA
- outer-loop SNR backoff controlled by ACK/NACK feedback;
- asymmetric ACK/NACK step sizes chosen so expected drift is zero at the target BLER;
- simple MCS table and smooth synthetic BLER curves expose estimator-bias calibration and goodput/BLER trade-offs.

### Communication-centric OFDM sensing / ISAC
- known QPSK-OFDM data grid reused as a sensing waveform;
- normalized monostatic two-way range/Doppler target model;
- data removal followed by IFFT across subcarriers and FFT across OFDM symbols;
- range-Doppler heat maps, coherent-processing resolution study, and 2-D CA-CFAR target detection.

### Composite receiver stress test
- one frame simultaneously receives timing offset, CFO, IQ imbalance, Wiener phase noise, and AWGN;
- staged timing acquisition, coarse CFO correction, IQ estimation/inversion, and pilot CPE tracking;
- demonstrates that individually modest residual oscillator errors can dominate BER over a long OFDM frame.

## Headline v1.0 results

- **IR-HARQ, 4 dB:** packet success = 1.0 for both tested schemes; average transmitted coded bits `96.0 -> 76.5`, payload goodput `0.333 -> 0.418 bit/tx-bit` for Chase -> IR.
- **2x2 QPSK + custom LDPC, 4 dB:** K-best K=4 BER `6.37e-2`, exact max-log BER `4.45e-2`; average Min-Sum iterations `35.8 -> 26.4`.
- **2x2 QPSK + custom LDPC, 8 dB:** K-best K=4 BER `1.19e-3`; exact max-log gives `0 observed errors` in 6720 information bits, with Wilson 95% upper bound about `5.71e-4`.
- **OTFS off-grid refinement, 20 dB pilot SNR:** Doppler MAE `0.385 -> 0.011 bins`; relative pilot residual `0.612 -> 0.099`.
- **OLLA under +2.5 dB biased/noisy SNR estimates:** steady BLER `0.250 -> 0.0999` and goodput `2.102 -> 2.217 bit/use` relative to open-loop MCS selection.
- **OFDM sensing snapshot, 12 dB:** both on-grid targets are recovered at their exact range/velocity bins in the current synthetic scenario.
- **2-D CA-CFAR weak target:** detection probability rises from `0 @ -20 dB` to `0.857 @ -4 dB` and `1.0 @ 0 dB`; mean false alarms remain roughly 3 per processed map for the chosen training/guard/Pfa settings.
- **Composite 16-QAM receiver stress:** timing-only BER `0.424`; after staged CFO/IQ/pilot phase processing BER `9.70e-3`, EVM `140.9% -> 19.4%`.

## Validation

- `79/79` automated tests pass.
- v1.0 experiments export deterministic CSV/PNG artifacts.
- result artifacts are indexed by SHA-256 manifest and checked by the release verifier.

## Boundaries retained intentionally

- No standards-compliant IEEE 802.11/LTE/5G/DVB waveform or protocol stack.
- No over-the-air / calibrated RF or radar hardware measurements.
- IR-HARQ uses a project-specific sparse LDPC mother code and simple puncturing schedule.
- OLLA uses synthetic BLER curves rather than measured MCS curves.
- OTFS refinement assumes correct coarse integer-delay support and refines Doppler only.
- ISAC is a normalized monostatic narrowband model without angle estimation, clutter tracking, range migration, or array processing.
- `0 observed errors` is reported as a finite Monte Carlo observation, never as true BER = 0.
