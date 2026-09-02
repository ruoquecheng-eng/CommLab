# Portfolio Summary — CommLab v1.0

## Recommended project title

**CommLab — Wireless Communication Systems Laboratory**

## One-line description

A modular Python research/engineering simulator spanning OFDM/OTFS waveforms, synchronization and estimation, MIMO, FEC/HARQ, RF impairments/DPD, link adaptation, packet scheduling, and communication-centric OFDM sensing.

## Strongest portfolio evidence

1. **High-Doppler ICI receiver** — one-tap failure, structured ICI estimation, banded/CG LMMSE recovery.
2. **Coded MIMO** — soft K-best/exact max-log LLRs coupled to Viterbi and sparse-LDPC iterative decoding.
3. **Incremental-redundancy HARQ** — punctured mother-code soft buffer, CRC/reliability and goodput accounting.
4. **RF impairment / DPD line** — phase noise, SCO, IQ imbalance, memory/cross-memory PA and learned/adaptive DPD.
5. **OTFS sparse acquisition** — pilot OMP, iterative LMMSE, plus v1.0 local off-grid Doppler refinement.
6. **System-level adaptation** — PF/queue-aware scheduling, finite-blocklength analysis, and ACK/NACK-driven OLLA.
7. **OFDM-ISAC** — communication data removal, range-Doppler processing, resolution trade-off, and 2-D CA-CFAR.

## Suggested figures for the website

- `results/figures/ici_aware_equalization_ber.png`
- `results/figures/coded_mimo_ldpc_ber.png`
- `results/figures/harq_ir_goodput.png`
- `results/figures/otfs_offgrid_doppler_mae.png`
- `results/figures/olla_bler_tracking.png`
- `results/figures/ofdm_isac_range_doppler_map.png`
- `results/figures/ofdm_isac_cfar_detection.png`
- `results/figures/full_receiver_stress_ber.png`

## CV bullets

- Developed **CommLab**, a modular Python wireless-communications laboratory covering OFDM/OTFS, synchronization, channel estimation, MIMO detection, FEC/HARQ, RF impairments/DPD, link adaptation, scheduling, and communication-centric sensing; maintained automated tests and deterministic experiment artifacts.
- Built structured high-mobility receivers using training-estimated ICI matrices, banded/iterative LMMSE detection, and sparse delay-Doppler path acquisition/refinement; quantified BER/NMSE/complexity trade-offs against genie references.
- Integrated soft-output K-best/exact MIMO detection with iterative FEC and implemented CRC-gated Chase and incremental-redundancy HARQ with retransmission/goodput accounting.
- Added an OFDM sensing branch using known communication symbols for range-Doppler estimation and CA-CFAR target detection, including coherent-processing resolution and weak-target detection studies.

## Interview-safe claims

Safe:
- "I implemented the algorithms and simulation/evaluation framework in Python and validated them with automated tests and reproducible Monte Carlo experiments."
- "The project intentionally uses educational/non-standard baselines when full standard implementations would require substantially more specification machinery."
- "I preserve negative/error-floor results and report 0 observed errors only as a finite-sample observation."

Do not claim:
- a 5G NR / Wi-Fi / DVB implementation;
- OTA/SDR or calibrated radar results;
- standards-compliant LDPC/polar/HARQ rate matching;
- production-grade DPD, radar, or scheduler performance;
- that OTFS universally outperforms OFDM under complexity-matched receivers.
