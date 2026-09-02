# CommLab-OFDM v0.4 Release Notes

v0.4 broadens the project from a synchronized SISO OFDM receiver into a multi-branch communication-system laboratory.

## New core modules
- rate-1/2, K=3 convolutional code with (7,5)_oct generators;
- hard-decision Viterbi decoder;
- finite-CIR time-domain LS channel estimator;
- sparse time-varying multipath channel with per-path normalized Doppler;
- time-domain 2x2 MIMO multipath OFDM chain with perfect-CSI ZF/MMSE detection;
- memoryless Rapp power-amplifier model and input-backoff control;
- distortionless selective mapping (SLM) PAPR reduction;
- water-filling power allocation and parallel-channel capacity utilities.

## New experiments
- coded vs uncoded QPSK-OFDM;
- 2x2 MIMO-OFDM over frequency-selective Rayleigh multipath;
- PA back-off vs BER/EVM/guard-bin spectral regrowth;
- Doppler/time-varying multipath: static CSI vs pilot interpolation vs finite-CIR LS vs genie per-symbol CSI;
- SLM candidate count vs PAPR CCDF and search complexity;
- water-filling vs equal-power OFDM resource allocation;
- model-based channel-estimation BER/NMSE comparison.

## Selected findings
- Rate-1/2 convolutional coding is worse than uncoded at 0 dB in the current hard-decision implementation, but becomes strongly beneficial by 2–6 dB; at 4 dB BER falls from about 3.80e-2 to 3.30e-3.
- In time-domain 2x2 MIMO-OFDM, MMSE beats ZF throughout the tested SNR range; at 12 dB BER is about 2.12e-2 vs 2.95e-2.
- Rapp PA back-off exposes a clean power-efficiency/distortion trade-off. At 0 dB IBO, 16-QAM OFDM EVM is about 20.1% with BER about 1.02e-2; at 6 dB IBO EVM falls to about 6.13% and BER is zero in the current noiseless-PA test.
- SLM lowers the 99th-percentile PAPR from about 9.17 dB (U=1) to 7.02 dB (U=4) and 6.45 dB (U=8) without waveform clipping distortion, at the cost of search complexity and side information.
- Finite-CIR time-domain LS removes the high-SNR interpolation floor when the assumed channel memory is correct: in the static 16-QAM test at 30 dB, BER is about 6.94e-6 versus 2.14e-2 for linear pilot interpolation.
- Water-filling is most useful at low SNR / strongly unequal subchannels. At 0 dB the current channel improves from 0.820 to 0.990 bit/s/Hz per data carrier; by 30 dB equal and water-filled allocations are effectively identical.
- Under per-path Doppler, a frame-static channel estimate collapses quickly. A finite-CIR pilot estimator tracks the time variation much better, but residual within-symbol ICI remains, motivating future ICI-aware equalization or an OTFS comparison branch.

## Validation
- 27/27 automated tests pass.
- dashboard syntax compiles.
- all v0.4 experiment scripts execute and export CSV/figures.
