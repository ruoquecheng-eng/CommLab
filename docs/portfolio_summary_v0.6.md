# Portfolio Summary — CommLab-OFDM v0.6

## Suggested title

**CommLab-OFDM — Link-Level Wireless Communication and Receiver Evaluation Laboratory**

## One-line description

Built a modular Python communications laboratory covering OFDM synchronization/channel estimation, soft and iterative FEC, MIMO, RF impairments/DPD, high-mobility channels, and quantitative link-level evaluation.

## Strongest CV bullet

> Developed a modular OFDM/wireless link simulator in Python with QAM, multipath/Doppler, synchronization, pilot- and model-based channel estimation, soft/iterative FEC, MIMO, oscillator/RF impairments, digital predistortion, and reproducible BER/EVM/NMSE experiments; validated 43 automated tests and documented limitations of each receiver/model.

## Optional second bullet for an EEE/communications application

> Implemented receiver-oriented studies including widely-linear IQ compensation, sampling-clock-offset estimation/resampling, decoder-aware narrowband-interference erasures, time-domain LS channel estimation, 2x2 MIMO-OFDM, and a small high-Doppler OTFS prototype.

## Figures to show first

1. `full_system_sync_ber.png` — residual CFO problem and pilot tracking solution.
2. `channel_estimation_method_ber.png` or equivalent v0.4 finite-CIR LS comparison.
3. `soft_viterbi_gain.png` — value of soft reliability information.
4. `iq_imbalance_ber.png` — front-end impairment and compensation.
5. `sampling_clock_ber.png` — timing-axis impairment and resampling correction.
6. `learned_dpd_evm.png` — data-fitted RF linearization.
7. `otfs_channel_structure.png` — high-Doppler domain structure.

If page space is limited, show only four: synchronization, channel estimation, IQ/SCO, learned DPD.

## Results worth quoting

- 64-QAM IQ imbalance: 4 dB/15° impairment gives BER ~0.134; training-LS widely-linear compensation gives 0 observed errors in the current run.
- 500 ppm SCO: BER ~0.470 -> ~0.0286 after two-burst ppm estimation and cubic inverse resampling.
- Narrowband jammer at -5 dB SIR: coded BER ~0.0209 -> 0 observed errors after detected-carrier LLR erasure in the current 20k-bit run.
- Custom sparse Min-Sum code at 2 dB: BER ~0.00344; average 7.16 iterations.
- Data-fitted polynomial DPD at 8 dB back-off: EVM ~3.40% -> ~1.23%; leakage ~-31.6 -> ~-39.1 dB.
- High-Doppler prototype: OFDM effective off-diagonal energy grows to ~15.1%, directly exposing the failure of the one-tap diagonal model.

## Claims to avoid

Do **not** write:
- "5G NR simulator";
- "IEEE 802.11 implementation";
- "hardware-validated RF system";
- "5G LDPC";
- "OTFS outperforms OFDM" without the receiver-complexity caveat;
- "adaptive DPD" for the current memoryless indirect-learning fit;
- "real-time" unless later measured on an actual real-time implementation.

The strongest presentation style is **problem -> diagnostic experiment -> receiver/algorithm modification -> quantitative result -> limitation**.
