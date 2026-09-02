# Portfolio Summary — CommLab-OFDM v0.9

## Recommended project title

**CommLab — Wireless Communication Systems Laboratory**  
*End-to-end simulation and evaluation of OFDM/MIMO links, receiver acquisition, coding/HARQ, RF impairments, high-mobility channels, and queue-aware multiuser scheduling.*

## Best v0.9 evidence to show

1. **Soft-output coded MIMO** — 2x2 QPSK, rate-1/2 convolutional code: at 8 dB, hard K=4/hard-Viterbi BER ~`1.07e-2`, soft K=4/soft-Viterbi ~`3.90e-3`, exact max-log/soft-Viterbi ~`2.44e-4`.
2. **HARQ** — at 0 dB block Rayleigh, Type-I packet success ~`59.2%`; Chase combining ~`91.7%`; payload goodput ~`0.186 -> 0.327 bit/QPSK-symbol`.
3. **Training-based high-Doppler ICI acquisition** — 12 random training OFDM symbols: matrix NMSE ~`2.81e-2`, BER ~`4.77e-3`; 32 symbols: BER ~`1.60e-3` vs genie-band ~`1.09e-3`.
4. **OTFS physical-path estimation** — one DD pilot + OMP: exact 3-path support recovery reaches `82.5% @20 dB` and `100% @25 dB` pilot SNR; 25 dB estimated-path BER ~`5.21e-5`.
5. **Queued OFDMA** — delay-aware PF improves P95 delay `155 -> 18 slots` versus ordinary PF in the current loaded trace while raising Jain fairness `0.987 -> 0.999` and reducing backlog `1.42 -> 0.124 Mbit`.
6. **Finite blocklength** — at 10 dB / target error `1e-3`, normal-approx rate is `3.05 bit/use` at n=100 versus Shannon `3.46`.

## Best figures for a portfolio page

- `coded_mimo_soft_output_ber.png`
- `harq_goodput.png`
- `ici_matrix_estimation_ber.png`
- `otfs_path_support_recovery.png`
- `queue_aware_p95_delay.png`
- `finite_blocklength_rate.png`

## Suggested CV bullet

Developed **CommLab**, a modular Python wireless-communications simulation platform spanning OFDM/MIMO, soft-output detection and FEC, CRC/HARQ, pilot-based channel/ICI acquisition, high-Doppler/OTFS experiments, RF impairment/DPD studies, and queue-aware OFDMA scheduling; built reproducible Monte Carlo experiments, automated tests, interactive labs, and quantitative BER/EVM/NMSE/latency/fairness evaluations.

## Scope discipline

Do not describe the project as a 5G/802.11 implementation, hardware SDR, or standards-compliant HARQ/LDPC/Polar stack. The strongest story is breadth plus transparent validation: each major result has code, a CSV, a generated figure, tests where applicable, and explicit limitations.
