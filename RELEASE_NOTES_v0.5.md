# CommLab-OFDM v0.5 Release Notes

v0.5 extends the platform in five deliberately different directions: soft-information coding, oscillator phase noise, MIMO channel acquisition, transmit diversity, and model-based PA linearization.

## Added

### Soft-information FEC
- generic max-log QAM bit LLRs for QPSK / 16-QAM / 64-QAM;
- soft-input Viterbi decoding for the existing rate-1/2 `(7,5)_oct` convolutional code;
- hard-vs-soft coded OFDM experiment.

Representative result at 2 dB sample-domain SNR:
- uncoded BER: `8.04e-2`;
- hard Viterbi: `3.43e-2`;
- soft-input Viterbi: `4.40e-3`.

At 4 dB, soft decoding reaches `8.0e-5` in the current run versus `3.32e-3` for hard Viterbi.

### Oscillator phase noise
- normalized discrete-time Wiener phase-noise model;
- 64-QAM OFDM phase-noise experiment;
- pilot-based per-symbol CPE tracking reused as a PT-RS-like educational baseline.

At phase-increment std `0.01 rad/sample` and 28 dB SNR:
- raw BER: `0.305`;
- pilot-CPE-tracked BER: `1.67e-4`;
- raw EVM: `70.5%`;
- tracked EVM: `5.07%`.

At stronger phase noise the tracked link still degrades, exposing residual within-symbol ICI rather than pretending CPE tracking solves all oscillator noise.

### 2x2 MIMO channel acquisition
- time-orthogonal full-active-carrier training symbols;
- LS MIMO channel estimation on all active carriers;
- estimated-frequency-response MIMO-OFDM detector path;
- perfect-CSI vs estimated-CSI BER and channel-NMSE experiment.

At 12 dB:
- perfect-CSI MMSE BER: `3.06e-2`;
- training-LS + MMSE BER: `5.29e-2`;
- channel NMSE: `4.41e-2`.

### Alamouti transmit diversity
- 2x1 Alamouti STBC encoder/decoder with equal total transmit power;
- SISO Rayleigh vs Alamouti diversity experiment.

At 16 dB:
- SISO BER: `1.21e-2`;
- 2x1 Alamouti BER: `1.69e-3`.

This complements the existing 2x2 spatial-multiplexing branch: one branch explores multiplexing, the other diversity.

### Model-based digital predistortion
- analytic inverse of the memoryless Rapp AM/AM model;
- explicit clipping below asymptotic saturation;
- PA-only vs inverse-DPD+PA EVM and guard-leakage study.

At 8 dB waveform back-off:
- PA-only EVM: `3.36%`;
- inverse-DPD EVM: `1.23%`;
- guard leakage improves from `-31.7 dB` to `-39.1 dB`.

At very low back-off the inverse must clip unattainable desired peaks and therefore provides little or no spectral benefit. This limitation is retained in the results.

## Engineering
- test count: **33/33 passing**;
- Streamlit adds a Phase Noise lab and optional known-model DPD;
- `run_v05_suite.py` reproduces all v0.5 experiments;
- new CSV data and portfolio-quality figures are exported automatically.

## New figures
- `soft_viterbi_gain.png`
- `phase_noise_ber.png`
- `phase_noise_evm.png`
- `dpd_evm.png`
- `dpd_spectral_regrowth.png`
- `mimo_channel_estimation_ber.png`
- `mimo_channel_estimation_nmse.png`
- `alamouti_diversity.png`

## Interpretation limits
- soft LLRs currently use max-log AWGN metrics and do not yet propagate per-subcarrier post-equalization covariance in arbitrary channels;
- the phase-noise model is normalized and is not calibrated to a specific oscillator PSD mask;
- MIMO training is intentionally simple time-orthogonal training, not a 3GPP/WLAN pilot design;
- DPD is an idealized inverse of a known memoryless PA model, not an adaptive memory-polynomial or measured-hardware DPD;
- Alamouti currently uses flat block fading with perfect receiver CSI.
