# v0.3 Architecture

```text
                                 TRANSMITTER
Bits
 ↓
QPSK / 16-QAM / 64-QAM
 ↓
Data + Pilot Carrier Allocation
 ↓
64-point IFFT
 ↓
Cyclic Prefix
 ↓
Repeated-Half Training Preamble + Payload
 ↓
────────────────────────────────────────────────────────────
                         CHANNEL / IMPAIRMENTS
AWGN | Multipath | Rayleigh | Timing Offset | CFO | Phase Offset
 ↓
────────────────────────────────────────────────────────────
                                 RECEIVER
Known-Preamble Correlation ───────────────→ Frame Start
           │
Repeated-Half Phase Difference ──────────→ Coarse CFO Estimate
           │
CFO Correction
           ↓
Remove CP → FFT
   ├──────────────── Pilots ───────────────┐
   │                                       ├→ LS Channel Estimate / CPE Tracking
   └──────────────── Data ─────────────────┘
                           ↓
                       ZF / MMSE
                           ↓
                    Pilot CPE Correction
                           ↓
                       QAM Demap
                           ↓
BER / EVM / MSE / NMSE / PAPR / Goodput
```

## Design choices

- The repeated-half preamble is educational and deterministic; it is not an IEEE 802.11 preamble.
- Timing uses normalized known-sequence correlation for a clean, verifiable baseline.
- A Schmidl-Cox-style repeated-half metric is also implemented for experimentation.
- CFO is represented in subcarrier-spacing units, making epsilon=1 correspond to one OFDM-bin offset.
- The repeated halves provide a coarse CFO estimate.
- Four known pilots are reused for per-symbol common-phase tracking, which is required for long frames when coarse CFO estimation leaves a small residual.
- Channel estimation remains pilot-LS + complex linear interpolation in the baseline receiver, with pilot-density experiments making its limitations explicit.

## Current limitations

- No Doppler/time-selective channel in the baseline end-to-end receiver.
- No channel coding or soft information.
- No MIMO.
- No PA spectral-regrowth model; clipping experiments evaluate in-band distortion/PAPR only.
- Sample-domain SNR is used in experiments; it should not be silently interpreted as Eb/N0.
- The project is an educational/research simulator, not a standards-compliant WLAN PHY.

## v1.0 platform view

```text
                         CommLab
                           |
        +------------------+------------------+
        |                  |                  |
   PHY waveform       Reliability/MIMO     System layer
        |                  |                  |
  QAM / OFDM / OTFS   Soft detection      OLLA / MCS
  CP / pilots          FEC / HARQ          PF / queues
        |                  |                  |
        +----------- Receiver ---------------+
                    sync / CE / EQ
                    ICI / phase tracking
                           |
                RF + propagation models
             Doppler / IQ / SCO / PA / DPD
                           |
              +------------+------------+
              |                         |
        Communication link        OFDM sensing / ISAC
                                  range-Doppler / CFAR
```

The code intentionally keeps these blocks modular. A v1.0 experiment can therefore ask either a narrowly controlled algorithm question (for example, off-grid OTFS Doppler refinement) or an integrated systems question (for example, cumulative synchronization/RF compensation), without rewriting the core waveform machinery.
