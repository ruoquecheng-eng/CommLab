# Portfolio-Facing Summary

## Project title
**CommLab-OFDM — Link-Level Communication System Simulation and Receiver Evaluation Platform**

## One-line description
A modular Python communication-system laboratory implementing OFDM, synchronization, channel estimation, MIMO detection, convolutional coding, RF nonlinearity, Doppler channels, PAPR reduction, and power allocation with reproducible link-level experiments.

## Strongest technical points to show on a portfolio page
1. **Receiver synchronization:** frame timing, CFO estimation/correction, and pilot common-phase tracking.
2. **Model-based channel estimation:** finite-CIR time-domain LS strongly reduces the high-SNR floor of naive pilot interpolation.
3. **2×2 MIMO-OFDM:** time-domain frequency-selective multipath + per-subcarrier ZF/MMSE spatial detection.
4. **RF nonlinearity:** Rapp PA back-off vs EVM, BER, and guard-bin spectral regrowth.
5. **PAPR reduction:** clipping trade-off plus distortionless SLM candidate search.
6. **Forward error correction:** from-scratch convolutional encoder and Viterbi decoder.
7. **High mobility:** per-path Doppler study separating channel-aging error from within-symbol ICI.
8. **Resource optimization:** equal-power vs water-filling capacity on OFDM subchannels.

## Best figures for an application-facing page
- `full_system_sync_ber.png`
- `channel_estimation_methods_nmse.png`
- `mimo_ofdm_multipath_ber.png`
- `pa_ibo_evm.png`
- `papr_slm_ccdf.png`
- `doppler_ici_ber.png`
- `waterfilling_capacity.png`

Do not show all figures on the first page. Use 4–5 as headline evidence and leave the rest behind an “Experiments” section.

## Suggested CV bullet
Developed **CommLab-OFDM**, a modular Python link-level communication simulator implementing QAM/OFDM, multipath and Doppler channels, synchronization, pilot-based and finite-CIR channel estimation, ZF/MMSE equalization, convolutional/Viterbi FEC, 2×2 MIMO-OFDM, nonlinear PA modeling, PAPR reduction, and water-filling; validated the platform with 27 automated tests and reproducible BER/EVM/NMSE/capacity experiments.

## Shorter CV bullet
Built a Python OFDM/MIMO link simulator with synchronization, channel estimation, FEC, Doppler/RF impairments, and quantitative BER/EVM/NMSE evaluation; 27 automated tests and reproducible experiment suite.

## What not to claim
- Do not call this an IEEE 802.11/5G standards implementation.
- Do not describe the Rapp model as a measured hardware PA.
- Do not describe MIMO-OFDM as practical-CSI yet; current branch uses perfect MIMO CSI.
- Do not call the convolutional decoder soft-decision; it is currently hard-decision.
- Do not call the Doppler model a full standardized TDL/CDL channel model.
- Do not claim OTFS is implemented yet.

## Interview-ready narrative
The project started from a basic SISO OFDM chain and was expanded by using each observed failure mode to motivate the next receiver or system component: multipath motivated CP/equalization; imperfect CSI motivated pilots and model-based channel estimation; residual CFO motivated pilot phase tracking; high PAPR motivated clipping, SLM, and PA modeling; channel diversity motivated MIMO; mobility motivated Doppler/ICI studies; and unequal subcarrier quality motivated water-filling. This creates a coherent engineering progression rather than a collection of unrelated demos.
