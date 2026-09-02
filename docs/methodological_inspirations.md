# Methodological Inspirations and Scope

CommLab-OFDM is original educational/research-oriented project code. It does not copy a standards implementation. Several architectural choices deliberately mirror mature communication-system workflows so that the simulator remains technically recognizable and extensible.

## GNU Radio OFDM architecture
GNU Radio separates OFDM carrier allocation, pilots/preambles, IFFT/FFT, cyclic prefixing, frame synchronization, coarse frequency correction, channel estimation, equalization, serialization, and optional forward-error correction. CommLab-OFDM follows the same high-level separation of concerns while keeping each algorithm compact and inspectable.

- https://wiki.gnuradio.org/index.php/Basic_OFDM_Tutorial
- https://wiki.gnuradio.org/index.php/OFDM_Receiver
- https://wiki.gnuradio.org/index.php/OFDM_Transmitter

## High-Doppler channel studies
MathWorks examples emphasize that multipath fading and relative motion produce Doppler shifts, time variation, and degraded one-tap OFDM assumptions. This motivated CommLab-OFDM's Doppler branch and the comparison among frame-static CSI, pilot-updated CSI, finite-CIR time-domain LS, and a genie per-symbol channel baseline.

- https://www.mathworks.com/help/comm/ug/fading-channels.html
- https://www.mathworks.com/help/comm/ug/multipath-fading-channel.html
- https://www.mathworks.com/help/comm/ug/otfs-modulation.html

## Nonlinear transmitter studies
The power-amplifier branch was motivated by standard RF-system studies where OFDM's high PAPR interacts with PA saturation. CommLab-OFDM uses a memoryless Rapp AM/AM model and measures in-band EVM/BER plus spectral leakage into nominally unused OFDM guard bins.

- https://www.mathworks.com/help/comm/ug/digital-predistortion-to-compensate-for-power-amplifier-nonlinearities.html

## Scope discipline
The project intentionally distinguishes:
- implemented algorithms from future ideas;
- measured results from expected theory;
- simplified educational models from standards-compliant PHYs;
- perfect/genie baselines from practical estimators.

## v0.5 inspiration notes
- 5G NR uses phase-tracking reference signals to compensate oscillator-induced common phase error; this motivated treating pilot CPE tracking as a separate post-FFT loop rather than folding all oscillator error into CFO.
- Mature DPD workflows evaluate both in-band quality (EVM/MER) and out-of-band spectral regrowth. The v0.5 Rapp inverse uses this evaluation pattern while remaining an analytic educational baseline.
- MIMO receivers require channel acquisition before linear ZF/MMSE detection. v0.5 deliberately starts with high-overhead time-orthogonal training so that estimation error can be isolated before experimenting with more efficient pilot reuse.
- Transmit diversity and spatial multiplexing are distinct MIMO objectives. The Alamouti branch was added to make that design trade-off explicit rather than treating "MIMO" as one technique.

## v0.6 additions

- MathWorks, **Compensate I/Q Imbalance** and `comm.IQImbalanceCompensator`: motivated a separate front-end IQ impairment/compensation branch and the need to keep channel/constellation rotation distinct from IQ image compensation. https://www.mathworks.com/help/comm/ug/compensate-i-q-imbalance.html
- MathWorks, **OFDM Synchronization**: reinforces modeling frequency/phase/timing impairments explicitly rather than hiding them inside a generic noise block. https://www.mathworks.com/help/comm/ug/ofdm-synchronization.html
- MathWorks Communications Toolbox examples, including **DVB-S.2 Link, Including LDPC Coding**: motivated adding a genuinely iterative sparse-graph FEC family rather than only convolutional/Viterbi coding. The code here is a custom educational construction, not copied from DVB-S.2. https://www.mathworks.com/help/comm/examples.html
- MathWorks, **OTFS Modulation**: motivated the high-Doppler domain-structure experiment and, equally importantly, the explicit caveat that simple OFDM and OTFS receiver comparisons depend strongly on channel estimation and equalizer complexity. https://www.mathworks.com/help/comm/ug/otfs-modulation.html

# v0.7 references and design inspiration

The following external material informed *which problems to model and how to separate them architecturally*. CommLab-OFDM does not copy source code from these toolchains.

## Dynamic OFDM receiver structure
- GNU Radio, **Basic OFDM Tutorial**: https://wiki.gnuradio.org/index.php/Basic_OFDM_Tutorial
- GNU Radio, **Dynamic Channel Model**: https://wiki.gnuradio.org/index.php?title=Dynamic_Channel_Model

Useful architectural ideas: separate time/frequency synchronization, FFT-domain channel state, equalization, and downstream FEC; treat fading, CFO, sample-rate drift, and AWGN as independently configurable effects.

## PA memory and DPD
- MathWorks, **Power Amplifier — Model power amplifier with memory**: https://www.mathworks.com/help/simrf/ref/poweramplifier.html
- MathWorks, **comm.DPD — Digital predistorter**: https://www.mathworks.com/help/comm/ref/comm.dpd-system-object.html
- MathWorks, **Power Amplifier and DPD Modeling for Dynamic EVM Measurement**: https://www.mathworks.com/help/simrf/ug/power-amplifier-and-dpd-modeling-for-dynamic-evm-measurement-of-5g-waveforms.html

Useful idea: memory-polynomial bases are a compact transparent bridge between measured complex-baseband PA input/output data and offline DPD coefficient fitting.

## MIMO pilot/channel estimation
- MathWorks, **Apply OFDM in MIMO Simulation**: https://www.mathworks.com/help/comm/ug/ofdm-with-mimo-simulation.html
- MathWorks, **ofdmChannelEstimate**: https://www.mathworks.com/help/comm/ref/ofdmchannelestimate.html
- MathWorks, **ofdmEqualize**: https://www.mathworks.com/help/comm/ref/ofdmequalize.html

Useful ideas: give different transmit antennas distinguishable pilot resources; keep channel estimation and MIMO equalization as separate algorithmic layers; exploit time/frequency structure for denoising rather than relying only on raw pointwise LS.

## High-Doppler ICI and OTFS
- MathWorks, **OTFS Modulation**: https://www.mathworks.com/help/comm/ug/otfs-modulation.html

Useful idea: high Doppler violates the diagonal one-tap OFDM model by introducing ICI. A full channel matrix and LMMSE detector provide a clean reference for studying how much of that coupling must actually be modeled. CommLab's v0.7 banded ICI receiver and sparse CG OTFS detector are project-specific reduced-complexity experiments built around that structural observation.


## v0.8

- **MIMO search:** QR/sphere-decoder formulations motivated a K-best layer between linear MMSE and exhaustive ML.
- **Adaptive RF linearization:** memory-polynomial DPD literature and tool workflows motivated forgetting-factor adaptive inverse learning and explicit convergence/stability reporting.
- **Cross-memory PA models:** generalized/cross-term memory-polynomial structures motivated a controlled model-mismatch experiment.
- **System-level scheduling:** proportional-fair OFDMA examples motivated rate/history scheduling and Jain-fairness reporting.
- **CSI feedback:** practical beamforming feedback examples motivated a finite-codebook MISO study rather than assuming perfect CSI at the transmitter.

External conceptual references used during v0.8 planning include MathWorks sphere-decoder/DPD documentation and NVIDIA Sionna proportional-fair scheduling tutorials. The project implementation remains independent and deliberately smaller.

## v0.9 methodological inspirations

- Soft-output tree/sphere MIMO detection motivated the list-based max-log LLR branch: the important interface for coded MIMO is detector reliability, not only hard symbol decisions.
- Chase HARQ follows the classical idea of retransmitting the same coded packet and accumulating soft evidence; CommLab adds its own CRC, convolutional link, Rayleigh experiment, and goodput accounting.
- High-Doppler ICI acquisition uses a structured-system-identification viewpoint: fit only a local coupling band rather than estimating an unconstrained dense matrix.
- OTFS sparse acquisition follows the delay-Doppler sparsity principle: a pilot-generated path dictionary plus OMP is used as a transparent grid-based baseline before attempting off-grid/message-passing methods.
- Queue-aware PF extends the existing proportional-fair scheduler by exposing packet backlog and head-of-line delay, so throughput/fairness conclusions are not detached from latency.
- Finite-blocklength analysis is included to contrast asymptotic Shannon-rate scheduling with short-packet fundamental-limit penalties.

## v1.0 methodological inspirations

The v1.0 directions were selected after comparing the project against mature communication workflows:

- **Incremental-redundancy HARQ:** mature LTE/NR-style HARQ keeps a soft buffer and combines redundancy versions before channel decoding. CommLab implements only a transparent project-specific puncturing schedule so the principle can be studied without claiming standard rate matching.
- **System-level link adaptation:** current Sionna SYS examples combine physical-layer abstraction, link adaptation, proportional-fair scheduling, and user evolution. CommLab's OLLA branch adopts the feedback-control idea while keeping a small synthetic MCS/BLER model.
- **OTFS channel acquisition:** high-mobility OTFS examples estimate delay, Doppler, and complex gains from sparse delay-Doppler responses. CommLab extends its grid OMP baseline with a local off-grid Doppler refinement rather than copying a toolbox detector.
- **OFDM sensing / ISAC:** communication-centric OFDM sensing workflows remove known data modulation and process frequency/slow-time channel estimates into range-Doppler responses. CommLab implements a normalized monostatic model and its own 2-D FFT/CA-CFAR pipeline.

Useful external references:
- MathWorks, "DL-SCH HARQ Modeling" — https://www.mathworks.com/help/lte/ug/dl-sch-harq-modeling.html
- NVIDIA Sionna SYS system-level examples — https://nvlabs.github.io/sionna/sys/
- MathWorks, "OTFS Modulation" — https://www.mathworks.com/help/comm/ug/otfs-modulation.html
- MathWorks, "Integrated Sensing and Communication II: Communication-Centric Approach Using MIMO-OFDM" — https://www.mathworks.com/help/phased/ug/integrated-sensing-and-communication-2-communication-centric-approach-using-mimo-ofdm.html

## v1.3 distributed / predictive directions
- **Cell-Free / user-centric clustering:** the v1.3 branch borrows the architectural idea that distributed APs can jointly serve users and that user-centric association is itself an optimization problem. The implementation here is deliberately smaller: geometry + normalized pathloss/shadowing + Rayleigh fading + strongest-AP clusters + distributed MRT.
- **Predictive ISAC beam tracking:** recent networked ISAC work combines sensing-based target estimation, Kalman-style prediction, and next-slot beamforming. CommLab v1.3 adopts only the structural idea, with a transparent synthetic angle process and CA/CV Kalman baselines rather than SDR/SDR-based optimization.
- **System-level modularity:** Sionna SYS separates link adaptation, scheduling, physical-layer abstraction, and channel evolution. CommLab follows the same modular philosophy while keeping NumPy-scale implementations inspectable and CPU-friendly.

Reference starting points used for design inspiration (not source-code copying): NVIDIA Sionna SYS link-adaptation/system-level tutorials; recent cell-free user-centric clustering literature; and recent sensing-assisted predictive MIMO-OFDM beam-tracking literature.

## v1.4: distributed CSI, Cell-Free/RIS coupling, and cross-layer feedback

v1.4 was informed by current research themes rather than copied implementations:

- Cell-Free literature increasingly treats pilot assignment, AP/user association, pilot contamination and power control as coupled design variables. CommLab implements a deliberately simpler large-scale-overlap pilot heuristic and closed-form per-AP LMMSE estimator so every assumption is inspectable.
- RIS-assisted Cell-Free work motivates studying programmable propagation together with distributed access. CommLab uses finite-bit coordinate ascent with explicit sum-rate/min-rate objectives rather than opaque global-optimum claims.
- Modern system-level wireless simulators connect PHY abstraction, link adaptation/OLLA, scheduling and time-varying channels. CommLab's event-driven cross-layer loop mirrors that modular separation while retaining its own lightweight HARQ/queue model.
- Communication-centric ISAC research motivates joint spatial objectives. CommLab uses a principal-eigenvector quadratic baseline to expose the communication-rate versus sensing-gain Pareto frontier without claiming waveform-level or hardware-calibrated optimality.

## v1.5 — deployment and uncertainty coupling
- Fronthaul-aware user-centric Cell-Free architectures motivate treating AP-user association, CSI transport, and cooperation level as coupled design variables rather than free infrastructure. Example background: *Fronthaul-Aware User-Centric Generalized Cell-Free Massive MIMO Systems* (Mobini et al., arXiv:2506.14494).
- Ultra-dense Cell-Free roadmaps repeatedly identify scalable channel acquisition, fronthaul limitation, synchronization, and resource allocation as deployment bottlenecks; v1.5's quantization/aging models are intentionally small transparent baselines for those questions.
- The finite-blocklength branch uses the established normal-approximation viewpoint: fixed blocklength and target error probability reduce achievable rate relative to Shannon's infinite-blocklength limit. The implementation remains an analytical abstraction rather than a standard-specific decoder model.
