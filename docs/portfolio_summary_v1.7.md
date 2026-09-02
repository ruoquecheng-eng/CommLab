# CommLab v1.7 — Portfolio Summary

## Positioning

**CommLab — Wireless Communication Systems Laboratory** is a reproducible Python research platform spanning PHY waveform/receiver design, coding/HARQ, MIMO/Cell-Free/RIS, RF impairment/DPD, high mobility/OTFS, system scheduling, and communication-centric sensing. v1.7 emphasizes **temporal information management**: what to update, what to compress, when to retransmit, when passive control should change, and when sensing should yield resources to packet queues.

## Strongest v1.7 stories

### 1. Fixed-budget asynchronous CSI refresh
A 20-AP / 8-user Cell-Free experiment allows only 1–8 AP CSI refreshes per slot. Pure uncertainty scheduling minimizes average channel-estimation error but can starve low-power APs for hundreds of slots, causing very poor edge rate. A bounded-uncertainty policy enforces a maximum CSI age before reverting to uncertainty priority. At four updates/slot, its mean CSI NMSE is about `0.076` versus round-robin `0.245`, while edge rate remains `0.721` versus round-robin `0.777 bit/s/Hz` rather than collapsing to the pure-uncertainty value `0.319`.

### 2. Predictive/differential CSI compression
Instead of scalar-quantizing the full channel each update, the AP transmits the innovation relative to the CPU's Gauss-Markov predictor. With identical 3-bit/component quantizers, mean NMSE gain grows from roughly `4.2 dB` at correlation `.8` to `19.1 dB` at `.995`. The result demonstrates why highly correlated CSI is better treated as a temporal source rather than independent snapshots.

### 3. Finite-blocklength incremental-redundancy HARQ
A queue-level normal-approximation model accumulates capacity and dispersion across independent redundancy blocks rather than simply repeating a codeword. At `-2 dB`, IR improves payload goodput `0.452 -> 0.581 bit/channel-use`, removes 10 observed drops, and reduces mean rounds `3.32 -> 2.58` relative to Chase. Above about 2–4 dB the curves merge because most packets complete in one round.

### 4. Two-timescale RIS control
RIS phase updates are separated from fast AP precoding. In the current correlated Cell-Free trace, a 4-slot RIS update interval requires only `3 control bit/slot` versus `12 bit/slot` for per-slot 2-bit control, while mean sum-rate is `4.56` versus `4.67 bit/s/Hz`. Longer intervals save more control traffic but eventually approach stale-control performance.

### 5. Queue-aware ISAC sensing
The sensing controller now competes directly with packet service. In the overloaded trace, a tracking-only policy spends `15%` of slots on sensing and leaves about `4.42k` final backlog bits. Queue-aware control reduces sensing to about `9.2%`, raises delivered payload, and cuts backlog to about `3.76k` bits while accepting larger angle uncertainty. A two-step predictive version restores some tracking quality without fully surrendering the payload gain.

## Suggested CV bullet

> Developed CommLab, a modular Python wireless-systems laboratory with 134 automated tests and over 100 reproducible experiment datasets; implemented fixed-budget asynchronous Cell-Free CSI scheduling, predictive CSI compression, finite-blocklength IR-HARQ, two-timescale RIS control, and queue-aware ISAC resource allocation.

## Best v1.7 figures

- `async_csi_edge_rate.png`
- `async_csi_nmse.png`
- `predictive_csi_nmse_gain.png`
- `fbl_ir_harq_goodput.png`
- `two_timescale_ris_overhead.png`
- `queue_aware_isac_sensing_trace.png`

## Scope boundaries

Do not claim an optimal CSI scheduler, entropy-coded CSI feedback, 3GPP NR HARQ, hardware RIS control timing, or an optimal ISAC POMDP. The v1.7 methods are transparent research baselines designed to expose temporal/fronthaul/retransmission/resource trade-offs.
