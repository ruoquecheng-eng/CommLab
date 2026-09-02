# CommLab-OFDM v0.3 Release Notes

This release expands the v0.2 estimated-CSI OFDM receiver into a broader communication-system experimentation platform.

## Added
- 64-QAM
- EVM metrics
- repeated-half synchronization preamble
- frame timing offset model and normalized known-preamble detector
- Schmidl-Cox-style timing metric
- normalized CFO impairment, estimation, and correction
- pilot-based residual common-phase tracking
- CP-length robustness/overhead study
- pilot-density NMSE/overhead study
- PAPR CCDF and clipping-distortion study
- BER-constrained adaptive modulation study
- experimental 2x2 flat-Rayleigh MIMO ZF/MMSE branch
- optional Streamlit dashboard
- technical report draft
- v0.3 experiment-suite runner

## Validation
- 19/19 pytest checks pass.
- Python source, experiments, and dashboard compile successfully.

## Important engineering finding
A coarse CFO estimate can be numerically accurate and still be inadequate for a long OFDM frame: small residual CFO accumulates common phase rotation. The v0.3 receiver therefore uses pilots for per-symbol phase tracking after coarse CFO correction. This changes the 16-QAM 16-dB BER in the current CFO=0.12 experiment from ~0.414 (coarse CFO only) to ~0.00142, close to the ~0.000694 genie-sync baseline.
