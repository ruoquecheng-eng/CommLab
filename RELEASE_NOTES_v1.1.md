# CommLab v1.1 Release Notes

v1.1 expands CommLab in four directions that were intentionally thin in v1.0: scalable spatial processing, sensing angle/tracking, retransmission redundancy-version structure, and joint fractional delay-Doppler refinement.

## New capability groups

### Ordered MMSE-SIC
- Recomputes the MMSE filter after every cancellation stage.
- Orders streams using the diagonal MMSE error covariance proxy.
- Creates a complexity/performance bridge between linear MMSE and QR K-best.

### Massive / multi-user MIMO
- Four-user downlink MRT and ZF precoding for 4–64 base-station antennas.
- Measures sum spectral efficiency, Jain fairness, inter-user normalized correlation, and channel-norm hardening.
- Adds a compact reused-pilot contamination model to demonstrate coherent leakage.

### Sparse-mmWave hybrid beamforming
- Geometric ULA channel with random AoA/AoD paths.
- DFT analog beam selection plus low-dimensional digital SVD.
- RF-chain count exposes hardware-complexity versus spectral-efficiency loss relative to full-digital SVD.

### ISAC receive-array processing and tracking
- Uniform linear receive array with half-wavelength spacing.
- Per-antenna range-Doppler processing followed by Bartlett angle scanning.
- Alpha-beta constant-velocity range tracker handles noisy and missed detections across frames.
- Multi-snapshot MUSIC pseudospectrum adds a source-count-known subspace super-resolution baseline alongside Bartlett scanning.

### Fractional OTFS delay/Doppler refinement
- Adds a controlled fractional-delay channel based on complex interpolation.
- Performs local 2-D coordinate refinement of delay and Doppler, followed by joint LS gain fitting.
- Explicitly remains an educational local refinement rather than a super-resolution/gridless estimator.

### Circular redundancy-version HARQ
- Every RV repeats systematic bits and rotates through a circular parity buffer.
- Soft observations accumulate in the existing mother-code LLR buffer.
- This remains project-specific and does not claim 3GPP/DVB rate matching.

## Headline results

- 2x2 16-QAM, 18 dB: ZF `2.76e-2`, MMSE `2.48e-2`, ordered MMSE-SIC `1.53e-2`, K-best K=4 `1.00e-2` BER.
- 4-user MU-MIMO, 10 dB: ZF mean sum rate rises from `5.08` to `28.96 bit/s/Hz` as the array grows from 4 to 64 antennas; mean normalized user-channel correlation falls `0.453 -> 0.111`.
- Reused-pilot contamination: median desired/leakage ratio remains near `6 dB` even at 128 antennas, while an orthogonal-pilot-like estimate improves with aperture.
- 32x8 sparse channel, 2 streams, 10 dB: DFT-hybrid mean rate `14.77 -> 17.30 bit/s/Hz` as RF chains increase `2 -> 8`, versus roughly `17.5 bit/s/Hz` full-digital SVD.
- ISAC ULA: 4 antennas fail to separate the two same-range/same-Doppler targets in the current Bartlett test; 8 and 16 antennas recover approximately `(-17.75°, 21.5°)` and `(-18°, 22°)`.
- Alpha-beta tracking: range RMSE improves `3.11 m -> 1.80 m` with 19 missed measurements in 220 frames.
- Close-angle ISAC: Bartlett peaks at about `-6.1°/-3.1°` for true `-6°/+6°`, while MUSIC recovers `-6°/+6°` in the current 80-snapshot test.
- Fractional OTFS refinement: local-search delay error about `0.04` bins and Doppler error `0` on the controlled `(2.35, 1.42)` path, versus coarse `(0.35, 0.42)` errors.
- Circular RV HARQ: unlike repeated transmission of the same punctured subset, rotating parity observations eventually expose the full mother-code structure and greatly improve decoding in the current small Monte Carlo.

## Boundaries

- Massive-MIMO studies use i.i.d. flat Rayleigh channels and all-digital precoders; no 3GPP channel geometry or hybrid RF network is claimed.
- Pilot contamination is a deliberately minimal two-user reused-pilot model.
- ISAC angle processing uses conventional Bartlett beamforming, not MUSIC/ESPRIT or calibrated arrays.
- Tracking is a single-target alpha-beta baseline without probabilistic data association.
- Fractional OTFS delay uses interpolation and local coordinate search; it is not a standards-grade fractional-delay model.
- Circular RV mapping is transparent project-specific logic, not a standards rate matcher.
