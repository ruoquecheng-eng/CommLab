# CommLab-OFDM v0.5 — Portfolio Selection

Do not show every experiment. The strongest application-facing story is a small number of comparisons that demonstrate engineering reasoning.

## Recommended seven figures
1. `channel_estimation_methods_ber.png` — model-driven finite-CIR LS versus naive interpolation.
2. `full_system_sync_ber.png` — coarse synchronization plus pilot phase tracking.
3. `soft_viterbi_gain.png` — value of soft reliability information in FEC.
4. `mimo_channel_estimation_ber.png` — perfect CSI versus acquired CSI in 2x2 MIMO-OFDM.
5. `alamouti_diversity.png` — diversity/reliability complement to spatial multiplexing.
6. `dpd_spectral_regrowth.png` — RF nonlinearity and model-based linearization.
7. `waterfilling_capacity.png` — physical-layer resource optimization.

## Recommended project description
**CommLab-OFDM — Modular Communication Systems Laboratory**  
Built a Python link-level simulation platform spanning QAM/OFDM waveform generation, synchronization, pilot- and model-based channel estimation, soft-decision FEC, 2x2 MIMO-OFDM, Alamouti diversity, Doppler and phase noise, PA nonlinearities/DPD, PAPR mitigation, and water-filling resource allocation. Designed reproducible experiments with BER, EVM, NMSE, PAPR and spectral-leakage metrics and maintained an automated validation suite.

## Two CV bullets
- Developed a modular OFDM link simulator with QPSK/16/64-QAM, synchronization, finite-CIR LS channel estimation, soft Viterbi FEC, and quantitative BER/EVM/NMSE evaluation under multipath, Doppler, CFO and oscillator phase noise.
- Extended the platform to 2x2 MIMO-OFDM channel acquisition/detection, Alamouti transmit diversity, nonlinear Rapp PA modeling with model-based DPD, SLM PAPR reduction, and water-filling resource allocation; maintained **33 automated tests** and reproducible experiment scripts.

## Claims to avoid
- Do not call the waveform 802.11/5G compliant.
- Do not call the phase-noise model a specific commercial oscillator model.
- Do not describe the analytic Rapp inverse as adaptive or learned DPD.
- Do not claim MIMO training is standards-optimal.
- Do not call the current high-Doppler branch OTFS; that comparison has not yet been implemented and validated.
