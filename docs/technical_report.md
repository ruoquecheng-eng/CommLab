# CommLab — Wireless Communication Systems Laboratory Technical Report

## v3.4 Addendum — Adaptive Risk-Control Orchestration

v3.4 turns the v3.3 resilience allocator into a delayed-feedback loop. A synthetic distribution shift makes deployed radio, edge, and deadline-tail point estimates stale. Global and class-local risk debts are updated only after task outcomes become observable, then modify how aggressively the shared migration/replica/duplication budget is spent.

The experiments separate post-drift task-weighted risk, critical-class risk, calibration gap, rolling risk, CVaR95 latency, physical resource proxies, and action switching. They show that adaptive feedback has an operating region: it helps under moderate drift and usable budgets, but can waste scarce credits, chase Bernoulli noise, hide rare critical classes when globally aggregated, and fail against infeasible targets or highly correlated radio paths.

The feedback structure is methodologically inspired by adaptive and localized risk control, but the finite synthetic action-dependent sequence does not meet the assumptions needed to claim conformal coverage. v3.4 is a research baseline for studying those gaps, not a theorem or production controller.

## 1. Objective
CommLab-OFDM is a Python link-level communication laboratory built to expose, rather than hide, the mechanisms behind OFDM waveform generation, multipath propagation, synchronization, channel estimation, equalization, coding, MIMO detection, RF nonlinearity, time variation, and parallel-channel resource allocation.

The project is intentionally modular and quantitative. Every major branch is expected to produce a reproducible experiment, a numerical metric, and a baseline comparison.

## 2. Baseline waveform
The baseline uses a 64-point FFT, 52 active subcarriers, a configurable pilot subset, and a 16-sample cyclic prefix. Gray QPSK, 16-QAM, and 64-QAM constellations are normalized to unit average symbol energy.

## 3. Receiver progression
### 3.1 Perfect timing and perfect CSI
The initial baseline verifies exact OFDM inversion, CP-based circularization, and one-tap frequency-domain equalization.

### 3.2 Pilot interpolation
Known comb pilots provide LS channel samples. Linear interpolation of real and imaginary components gives a simple practical baseline but develops a high-SNR error floor when the frequency response varies significantly between pilots.

### 3.3 Finite-CIR time-domain LS
v0.4 adds a structural channel estimator. The pilot observations satisfy a partial Fourier model of a finite impulse response. Solving this model for the CIR and transforming back to frequency removes much of the interpolation floor when the assumed channel memory is valid.

### 3.4 Timing, CFO, and residual phase
A repeated-half preamble provides frame timing and coarse normalized CFO estimation. Long frames show that a small residual CFO becomes a symbol-to-symbol common phase drift; pilot-based CPE tracking removes this residual rotation.

## 4. Forward error correction
A rate-1/2, constraint-length-3 convolutional code with (7,5)_oct generators and a hard-decision Viterbi decoder was implemented from first principles. The coded OFDM experiment deliberately reports both BER improvement and the information-rate penalty.

## 5. MIMO-OFDM
The earlier narrowband 2×2 MIMO detector has been extended into a time-domain OFDM chain:
- two independent QPSK-OFDM transmit waveforms;
- 2×2 frequency-selective Rayleigh FIR links;
- CP-protected convolution in the time domain;
- receiver FFT per antenna;
- perfect-CSI per-subcarrier ZF or linear-MMSE spatial detection.

This isolates MIMO detection from the still-future problem of MIMO pilot/channel estimation.

## 6. RF transmitter branch
### 6.1 PAPR and clipping
Existing experiments quantify OFDM PAPR and the distortion introduced by hard clipping.

### 6.2 Selective mapping
v0.4 implements SLM: multiple unit-magnitude phase-rotated OFDM candidates are generated and the lowest-PAPR waveform is selected. This reduces PAPR without clipping distortion, but requires more candidate transforms and side information.

### 6.3 Rapp power amplifier
A memoryless Rapp AM/AM model converts PAPR into a transmitter hardware trade-off. Input back-off controls how deeply the waveform drives saturation. The experiment measures BER/EVM and leakage from active OFDM carriers into nominal guard bins.

## 7. Time-varying channels and Doppler
Each sparse path can carry an independent Doppler shift. Three receiver baselines separate different failure mechanisms:
1. a channel estimate frozen at frame start;
2. per-symbol pilot-based channel tracking;
3. a genie per-symbol channel response evaluated near the OFDM symbol midpoint.

The large gap between frozen CSI and tracked CSI demonstrates channel aging. The residual gap to the genie and nonzero genie error at higher Doppler indicate within-symbol time variation / ICI, which cannot be removed by a purely diagonal one-tap equalizer.

## 8. Parallel-channel resource allocation
OFDM data subcarriers can be viewed as parallel Gaussian channels once diagonalized. A water-filling optimizer allocates a fixed total transmit power using channel power gains and noise level. It improves low-SNR spectral efficiency by turning off deep fades and converges toward equal power as SNR becomes high.

## 9. Selected quantitative results
### 9.1 Coding
At 4 dB sample SNR, uncoded BER is about 3.80e-2 while rate-1/2 convolutional coding + hard Viterbi gives about 3.30e-3. At 0 dB the coded link is slightly worse, illustrating that redundancy and hard-decision decoding do not guarantee gain in every regime.

### 9.2 MIMO-OFDM
At 12 dB in the current frequency-selective 2×2 experiment, ZF BER is about 2.95e-2 and MMSE BER about 2.12e-2.

### 9.3 PA back-off
At 0 dB IBO, EVM is about 20.1% and BER about 1.02e-2. At 6 dB IBO, EVM is about 6.13% and no bit errors are observed in the current noiseless-PA experiment.

### 9.4 SLM
The 99th-percentile PAPR drops from 9.17 dB (one baseline candidate) to 7.02 dB (4 candidates) and 6.45 dB (8 candidates).

### 9.5 Channel estimation
At 30 dB, pilot interpolation NMSE is about 5.65e-2 while finite-CIR time-domain LS NMSE is about 7.79e-4. Corresponding 16-QAM BERs are about 2.14e-2 and 6.94e-6.

### 9.6 Water-filling
At 0 dB nominal SNR, equal-power average capacity is 0.820 bit/s/Hz per data carrier and water-filling gives 0.990. At 30 dB both are approximately 9.105.

## 10. Reproducibility and software engineering
- deterministic RNG seeds;
- CSV result export;
- separate generated figures;
- 27 automated tests;
- modular Python package rather than notebook-only code;
- multi-mode Streamlit dashboard;
- explicit separation of implemented, genie, and future methods.

## 11. Interpretation limits
- SNR is currently sample-domain unless an experiment states otherwise; a unified Eb/N0 accounting layer is future work.
- The preamble and resource grid are educational, not standards waveforms.
- MIMO-OFDM currently assumes perfect CSI.
- The PA model is memoryless and does not yet include AM/PM, memory effects, or digital predistortion.
- Doppler experiments use simplified sparse per-path sinusoidal evolution rather than a full standardized tapped-delay-line model.
- The convolutional decoder is hard-decision only.

## 12. Next research extensions
The strongest next directions are:
- soft demapping and soft-input FEC;
- MIMO pilot design and channel estimation;
- ICI-aware equalization and an OFDM/OTFS high-mobility comparison;
- oscillator impairments (phase noise, IQ imbalance, sampling-clock offset);
- PA digital predistortion;
- packet-level PER/goodput metrics.

## 13. Methodological inspiration
The architecture follows established communication-system decomposition: separate carrier allocation, pilots/preambles, transforms, synchronization, channel estimation, equalization, FEC, and higher-level evaluation. `docs/methodological_inspirations.md` records external conceptual references while the implementation and experiment code in this repository remain project-specific.

# v0.5 Addendum

## 14. Soft information and coded modulation
The QAM modem now emits max-log per-bit LLRs using the actual constellation labelling. The convolutional decoder accepts these reliabilities through a soft-input Viterbi metric. This separates the value of the code itself from the information discarded by hard slicing. In the current QPSK-OFDM AWGN experiment at 2 dB, hard Viterbi BER is approximately 3.43e-2 while soft-input Viterbi reaches 4.40e-3.

## 15. Oscillator phase noise
A discrete Wiener phase process is applied sample-by-sample to the complex baseband waveform. Pilots estimate one common phase rotation per OFDM symbol. This sharply reduces CPE, but stronger phase noise still creates within-symbol ICI. The model is normalized by phase-increment standard deviation and is not presented as a calibrated oscillator PSD.

## 16. MIMO channel acquisition
The 2x2 MIMO-OFDM branch now includes explicit channel acquisition. Two training OFDM slots are time-orthogonal: only one transmitter is active in each slot and all configured active carriers carry a known training value. LS division estimates every receive/transmit channel on the active carrier set. This is intentionally simple and high-overhead, making it a clean baseline for future lower-overhead pilot design.

## 17. Diversity versus spatial multiplexing
A 2x1 Alamouti STBC baseline was added under equal total transmit power. It sacrifices the two-stream spatial-multiplexing objective and instead creates transmit diversity. At 16 dB in the current flat Rayleigh experiment, BER drops from roughly 1.21e-2 for SISO to 1.69e-3 for Alamouti.

## 18. Model-based DPD
The Rapp branch now has an analytic inverse predistorter. Because the Rapp output approaches the saturation amplitude asymptotically, desired peaks at or above saturation are unattainable; the inverse therefore clips its target below saturation. At useful back-off the cascade significantly improves EVM and guard leakage, while at very low back-off clipping limits the benefit. The method is a known-model baseline, not a hardware-trained DPD.

# v0.6 Addendum

## 19. Widely-linear IQ imbalance and training compensation
The receiver-front-end model is extended from purely multiplicative impairments to a conjugate-coupled model

\[
y[n]=\alpha x[n]+\beta x^*[n].
\]

A known complex training waveform estimates `(alpha,beta)` by least squares over the design matrix `[x, x*]`. Provided `|alpha|^2 != |beta|^2`, the 2x2 conjugate system has a closed-form inverse. The experiment demonstrates that severe constellation image distortion can be corrected in this idealized frequency-flat model. Frequency-selective IQ imbalance and DC/LO leakage remain outside scope.

## 20. Sampling-clock offset as time-axis distortion
SCO is modeled by fractional resampling, not by a phase-only surrogate. For receiver output sample index `n`, the model samples transmitter time approximately `n(1+epsilon)`. Two identical training bursts separated by a known transmit-sample distance estimate `epsilon` from their observed timing separation. A pilot affine-phase fit is also included as a weaker baseline; it compensates some per-symbol phase slope but cannot invert the sampling-time warp or all induced ICI.

## 21. Decoder-aware narrowband interference mitigation
A persistent complex tone creates a high-power outlier on one OFDM data carrier. Median carrier power plus MAD normalization detects the outlier without being dominated by the jammer. Instead of making a hard decision on that unreliable carrier, the receiver sets its coded-bit LLRs to zero before soft Viterbi decoding. This turns a confidently wrong observation into an erasure the code can bridge.

## 22. Sparse accumulator LDPC and normalized Min-Sum
A project-specific sparse parity-check matrix `H=[A|B]` is constructed with sparse randomized information columns and a lower-bidiagonal accumulator parity block. The structure permits exact sequential parity generation and sparse Tanner-graph decoding. Normalized Min-Sum message passing exposes both BER and iterative complexity. The construction is educational and deliberately separated from standards-defined LDPC profiles.

## 23. Data-fitted polynomial digital predistortion
The PA branch now supports indirect learning. Given PA input `x` and observed output `y`, an odd-order complex polynomial postdistorter is fitted:

\[
\hat x = \sum_p c_p y|y|^{2p}.
\]

The same coefficients are then reused as a predistorter on a new desired waveform. This creates a system-identification baseline that does not use the analytic Rapp inverse during fitting. Because both PA and DPD are memoryless, memory effects, AM/PM, temperature drift, and hardware calibration remain future work.

## 24. Small-grid OTFS prototype and high-Doppler structure
The OTFS branch implements a unitary ISFFT from delay-Doppler to time-frequency, OFDM modulation, and the inverse receiver transforms. A normalized deterministic channel applies integer sample delays and path-specific Doppler phases. For small grids, the code can explicitly build the effective symbol-domain channel matrix by basis probing. This enables two diagnostics:

1. OFDM off-diagonal energy, measuring loss of the diagonal one-tap assumption under Doppler;
2. delay-Doppler energy concentration, measuring how a small number of physical paths remain structurally concentrated after OTFS transforms.

The included BER comparison intentionally uses different receiver complexity (OFDM diagonal equalization versus OTFS full effective-channel LMMSE) and therefore must not be presented as a fair standards-level waveform ranking. Its purpose is to validate the transform/channel implementation and expose the structural motivation for more advanced sparse OTFS detection.

## 25. External methodological references for v0.6
The v0.6 directions were selected after reviewing mature communication-toolbox examples and documentation. In particular, current external examples emphasize IQ imbalance compensation for QAM/OFDM, explicit OFDM synchronization impairments, LDPC-based coded OFDM links, and OTFS as a delay-Doppler approach to high-Doppler ICI. The repository records these as conceptual references; code and measurements here remain project-specific and independently implemented.

# v0.7 Addendum

## 26. Explicit ICI matrix and banded high-Doppler equalization
Earlier Doppler experiments showed that per-symbol channel tracking cannot remove all errors because the channel changes *within* an OFDM symbol. v0.7 makes that mechanism explicit. For one CP-protected symbol, each FFT basis vector is transmitted through the time-varying multipath model to numerically form an effective frequency-domain matrix

\[
\mathbf Y = \mathbf H_{\mathrm{ICI}}\mathbf X + \mathbf N.
\]

A time-invariant channel produces an essentially diagonal matrix. Path-specific Doppler transfers energy into neighboring FFT bins, producing off-diagonal ICI. The receiver now compares diagonal, band-limited, and full LMMSE models. The experiment shows that much of the useful correction can be obtained from a narrow coupling band before paying the cost of a dense solve.

This is currently a **known effective-channel** study. A practical receiver must estimate the relevant diagonal/band entries from pilots or a parametric Doppler model.

## 27. Nonlinear PA memory and indirect-learning memory DPD
The RF branch is extended from memoryless AM/AM models to a memory polynomial

\[
y[n]=\sum_{m=0}^{M-1}\sum_{p\in\{1,3,5,\dots,P\}}
a_{m,p}x[n-m]|x[n-m]|^{p-1}.
\]

The same basis is used for least-squares model identification and an indirect-learning predistorter: a postdistorter is fitted from measured PA output back to PA input and then reused before the PA. This is still an offline normalized-baseband baseline, but it captures the central interaction between nonlinearity and finite memory. A deliberately retained low-back-off failure demonstrates that polynomial inverse learning has an operating region and can become unstable when the PA mapping is too distorted/ill-conditioned.

## 28. MIMO LMMSE estimation and pilot-overhead reduction
Two separate estimation studies were added.

First, noisy LS coefficients are passed through a zero-mean independent-channel LMMSE shrinkage prior. This deliberately simple Wiener baseline improves low-SNR MSE and converges to LS as noise vanishes.

Second, the high-overhead two-slot MIMO training scheme is replaced by a one-symbol frequency-orthogonal design. Active subcarriers are interleaved across transmit antennas so each pilot resource element contains only one transmitter. For each receive/transmit pair, pilot-frequency samples are fitted to a finite CIR of length `L`:

\[
H[k_p]=\sum_{\ell=0}^{L-1}h[\ell]e^{-j2\pi k_p\ell/N}.
\]

The recovered taps are FFT-transformed to the full active-carrier response. This trades a stronger finite-support model for lower training overhead and denoising.

## 29. Exhaustive small-MIMO maximum-likelihood detection
For low-order small MIMO, v0.7 adds a brute-force performance reference:

\[
\hat{\mathbf x}_{ML}=\arg\min_{\mathbf x\in\mathcal S^{N_t}}
\|\mathbf y-\mathbf H\mathbf x\|_2^2.
\]

For 2x2 QPSK only 16 candidates are evaluated per channel use. This exposes the gap between linear ZF/MMSE and joint detection while making the exponential complexity explicit. It is not proposed as a scalable massive-MIMO algorithm.

## 30. Sparse conjugate-gradient OTFS detection
The small-grid OTFS effective channel is often numerically concentrated: a few coefficients per observation row contain most of the energy. v0.7 keeps the strongest `K` coefficients per row and solves the regularized LMMSE normal equations by conjugate gradient rather than a direct dense inverse. The result creates three measurable axes:

- retained effective-channel energy;
- BER;
- CG iteration count.

This is a step toward sparse/message-passing detection while remaining easier to verify numerically against a direct LMMSE solution.

## 31. Confidence-aware Monte Carlo
BER measurements are Bernoulli estimates, so a finite simulation does not justify treating zero observed errors as zero probability. v0.7 adds Wilson score intervals and sequential simulation stopping. QPSK AWGN is used as a calibration experiment because its theoretical BER is known; the simulated confidence intervals track the theoretical curve through the tested range.

This statistical layer should eventually be propagated to every headline BER/PER study.

## 32. v0.7 methodological references
The v0.7 architecture was informed by mature external examples rather than copied implementation code. In particular:

- GNU Radio separates dynamic fading, CFO, sample-rate drift, and AWGN in its dynamic channel model and keeps synchronization/equalization modular.
- MathWorks documents memory-polynomial PA/DPD modeling and coefficient estimation from captured input/output waveforms.
- Current MIMO-OFDM examples use transmitter-dependent pilot indices and separate pilot-based channel estimation from MMSE/ZF equalization.
- High-Doppler OTFS examples explicitly demonstrate that OFDM single-tap equalization leaves residual ICI and that matrix-based equalization can remove inter-bin coupling.

The project-specific code here remains independently implemented and deliberately smaller than those production toolchains.

## 33. Frequency-selective widely-linear IQ compensation
The earlier IQ model used a single pair of complex coefficients. v0.7 extends it to finite-memory direct/image filters:

\[
y[n]=(h_d*x)[n]+(h_i*x^*)[n].
\]

Known training estimates both FIR paths by complex least squares. When filter memory is covered by the cyclic prefix, the useful OFDM symbol obeys a mirror-coupled frequency-domain relation. For non-DC subcarrier `k`,

\[
egin{bmatrix}Y[k]\Y^*[-k]\end{bmatrix}=
egin{bmatrix}H_d[k]&H_i[k]\H_i^*[-k]&H_d^*[-k]\end{bmatrix}
egin{bmatrix}X[k]\X^*[-k]\end{bmatrix}.
\]

The receiver inverts this 2x2 system per mirror pair. The experiment shows that a frequency-flat compensation baseline leaves an error floor that the FIR pairwise model removes in the tested regime. This remains a normalized baseband model; LO leakage, DC offsets, nonlinear mixers, and hardware calibration are outside scope.


# v0.8 Addendum

## 34. QR K-best MIMO tree search
The exhaustive ML detector gives a useful lower-complexity-system reference but scales as \(M^{N_t}\). v0.8 inserts a QR K-best detector between linear MMSE and exhaustive search. With \(\mathbf H=\mathbf Q\mathbf R\) and \(\bar{\mathbf y}=\mathbf Q^H\mathbf y\), the triangular metric is accumulated from the final transmit layer toward the first. Only the K lowest partial Euclidean metrics survive at each level. This exposes a continuous performance/search-cost ladder rather than a binary choice between MMSE and brute-force ML.

For 2x2 16-QAM, K=16 is sufficient to reproduce exhaustive ML in the current simulations; K=4 captures most of the gain at much smaller tree width. The implementation is intentionally pedagogical and does not include Schnorr-Euchner ordering, radius pruning, soft outputs, or hardware-oriented fixed-point optimizations.

## 35. Spatial correlation, conditioning, and MIMO capacity
The earlier MIMO channels were i.i.d. Rayleigh. v0.8 adds a Kronecker model

\[
\mathbf H=\mathbf R_r^{1/2}\mathbf W\mathbf R_t^{1/2},
\]

with exponential antenna correlation. Correlation makes channel columns less independent, increasing condition number, worsening ZF noise amplification, and reducing spatial multiplexing capacity. The experiment jointly reports BER, median/90th-percentile condition number, and

\[
C=\log_2\det\!\left(\mathbf I+\frac{\rho}{N_t}\mathbf H\mathbf H^H\right).
\]

This provides a direct bridge between numerical linear algebra and communication performance.

## 36. Limited-feedback MISO beamforming
A 4x1 MISO branch now compares single-antenna transmission, perfect-CSI maximum-ratio transmission, and finite codebook feedback. The receiver selects

\[
i^*=\arg\max_i |\mathbf h\mathbf w_i|^2
\]

from a shared unit-vector codebook and feeds back only its index. Increasing codebook size reduces the rate gap to perfect MRT while increasing feedback overhead. The current codebooks are random isotropic vectors and are not standardized WLAN/NR codebooks.

## 37. Conjugate-gradient high-Doppler ICI equalization
The known ICI matrix experiment previously used direct LMMSE solves. v0.8 solves

\[
(\mathbf A^H\mathbf A+\sigma_n^2\mathbf I)\hat{\mathbf x}=\mathbf A^H\mathbf y
\]

by conjugate gradient, using either the full matrix or a retained coupling band. This avoids explicit matrix inversion and makes iteration count a measurable complexity axis. In the current high-Doppler case, a +/-2 coupling band removes most of the one-tap error floor while requiring roughly a few tens of CG iterations.

## 38. Adaptive indirect-learning DPD under drift
A frozen inverse can become stale when PA coefficients change with operating condition. v0.8 introduces exponentially weighted block LS. For each new observation block, discounted sufficient statistics are updated,

\[
\mathbf R_t=\lambda\mathbf R_{t-1}+\Phi_t^H\Phi_t+\gamma\mathbf I,\qquad
\mathbf p_t=\lambda\mathbf p_{t-1}+\Phi_t^H\mathbf d_t,
\]

and the inverse model is \(\hat{\mathbf c}_t=\mathbf R_t^{-1}\mathbf p_t\). A sample-wise RLS implementation is retained as an experimental building block, but stronger-drift tests exposed occasional numerical coefficient explosions. The release therefore uses the more stable block-EWLS path for headline tracking results.

## 39. Generalized cross-memory polynomial
The ordinary memory polynomial couples each delayed complex sample only with its own envelope. v0.8 adds a causal generalized-memory branch containing lagging envelope cross terms of the form

\[
x[n-m]|x[n-m-\ell]|^{p-1}.
\]

A synthetic PA deliberately containing such cross-memory effects is used to test model mismatch. Standard MP and GMP are fitted with independent code paths and evaluated on held-out samples and indirect-learning DPD. The matched GMP gives much lower modeling error and lower EVM in its useful operating region, while both inverse models deteriorate under very aggressive drive.

## 40. Educational polar code and common rate-1/2 FEC benchmark
A self-contained polar encoder applies Arikan's transform \(F^{\otimes n}\). Frozen-bit reliability is generated by a BEC Bhattacharyya recursion, and decoding uses min-sum successive cancellation. The implementation is explicitly educational: it is not the 3GPP NR reliability sequence, CRC-aided list decoding, or NR rate matching.

A common BPSK/AWGN benchmark compares three roughly rate-1/2 families: soft Viterbi, the project-specific sparse LDPC with normalized Min-Sum, and N=128/K=64 polar SC. This exposes how waterfall position, block length, decoder structure, and iteration/recursion complexity differ without claiming universal ranking.

## 41. Multiuser proportional-fair OFDMA scheduling
v0.8 adds a system-level resource allocator. For user \(u\) and resource \(i\), the proportional-fair metric is

\[
\frac{\tilde R_t(u,i)}{T_{t-1}(u)},
\]

where current achievable rate is divided by exponentially averaged past throughput. Each OFDM resource is assigned to the largest metric. The experiment compares fixed round-robin, pure max-rate, and PF using aggregate rate, per-user throughput, and Jain's fairness index. This is a simplified perfect-CSI scheduler with no queueing, HARQ, interference coordination, or standardized MCS table.

## 42. v0.8 methodological references
The v0.8 design directions were informed by mature external communication workflows, while implementation remains project-specific. In particular:

- sphere/K-best style MIMO detection is naturally formulated after QR decomposition as a tree search over partial Euclidean distance;
- adaptive DPD workflows use memory-polynomial inverse learning and recursive/forgetting-factor coefficient updates;
- current system-level simulators use proportional-fair metrics based on achievable rate divided by historical throughput;
- practical CSI feedback/beamforming systems quantize or compress channel/precoder information rather than feeding back full continuous CSI.

These references motivated which trade-offs to expose; they are not copied code and do not make this repository standards-compliant.

# v0.9 Addendum — From Isolated Algorithms to Acquired/Coded/Queued Links

## Soft-output MIMO and coded detection

v0.9 adds bit-level max-log outputs to small-MIMO detection. For a received vector `y=Hs+n`, the exhaustive reference computes, for every stream/bit, the difference between the minimum Euclidean metrics over candidate vectors carrying bit 1 and bit 0, scaled by noise variance. QR K-best uses the retained final list as an approximation to these two hypothesis sets. Missing bit hypotheses are explicitly saturated rather than treated as mathematically infinite confidence.

The coded-MIMO experiment feeds these LLRs into the existing soft-input Viterbi decoder. This separates three effects: hard tree-search decisions, list quality, and soft reliability. The large gap between hard K=4 and exact max-log at 8--10 dB demonstrates that coded MIMO cannot be assessed from uncoded symbol decisions alone.

## CRC and Chase HARQ

Packets now carry a CRC-16-CCITT before convolutional encoding. Type-I HARQ discards failed soft observations, whereas Chase HARQ sums LLRs from repeated transmissions of the same codeword. ACK/NACK is generated from decoded CRC validity. The experiment reports final packet error, average transmissions, successful-packet latency, and delivered payload bits per transmitted QPSK symbol.

## Training-based ICI matrix acquisition

Instead of assuming the high-Doppler coupling matrix is known, v0.9 estimates a band-limited model from random full-band training. For output subcarrier `i`, only coefficients `H[i,j]` satisfying `|i-j|<=B` are fit by LS/ridge regression. This changes the receiver problem from a full N-parameter row estimate to `2B+1` parameters per row. The training-count experiment exposes the acquisition/performance trade-off and converges toward the corresponding genie-banded detector.

## Sparse delay-Doppler path acquisition

A known OTFS pilot grid generates a dictionary whose columns are the project-consistent received DD response to unit-gain candidate `(delay,doppler)` paths. OMP selects a prescribed number of paths and refits their complex gains by LS. Estimated physical paths are then used to reconstruct the full detector matrix. The current result is strongest for grid-aligned paths and intentionally does not claim off-grid super-resolution.

## Queue-aware OFDMA

The scheduler now contains explicit FIFO packets, Poisson arrivals, partial packet service, backlog, completed-packet delay, and per-user delivered bits. The delay-aware PF metric multiplies the conventional achievable-rate / historical-throughput metric by a normalized head-of-line delay boost. Results therefore expose throughput, fairness, backlog, and tail latency simultaneously rather than reducing the scheduler to average spectral efficiency.

## Finite-blocklength analysis

The information-theory branch adds the complex-AWGN normal approximation

`R ~= C - sqrt(V/n) Q^-1(epsilon) + log2(n)/(2n)`

with `C=log2(1+SNR)` and complex-AWGN dispersion `V=(1-(1+SNR)^-2)(log2 e)^2`. This is used only as a fundamental-limit approximation; code-specific BLER still requires the Monte Carlo coding branches.

# v1.0 Addendum — Reliability, Adaptation, Sensing, and Integrated Stress Tests

## 43. Incremental-redundancy HARQ

v1.0 adds a transparent puncturing/rate-matching baseline for the custom sparse LDPC mother code. Round 1 transmits all systematic bits plus one parity chunk; later redundancy versions reveal disjoint parity chunks. The decoder always sees the full mother-code LLR vector, with untransmitted bits represented by zero-LLR erasures. Repeated observations, if present, are accumulated in the same soft buffer.

This differs from Chase combining: Chase retransmits the same complete codeword and gains reliability through repeated observations, whereas IR spends later transmissions on previously unseen parity. The current schedule is deliberately simple and not a 3GPP/DVB redundancy-version map.

## 44. LDPC-coded soft-output MIMO

The soft MIMO chain is extended from convolutional/Viterbi coding to the project-specific sparse LDPC. One rate-1/2 codeword is QPSK-mapped and striped across two spatial streams. Both QR K-best list LLRs and exhaustive max-log LLRs feed the normalized Min-Sum decoder. This makes detector quality visible through two metrics simultaneously: information-bit BER/FER and average belief-propagation iteration count.

At intermediate SNR, higher-quality LLRs reduce both residual errors and iterative-decoder work. This is a useful precursor to future iterative detection/decoding, but no extrinsic information is fed back from the decoder to the MIMO detector in v1.0.

## 45. Off-grid OTFS Doppler refinement

The v0.9 OTFS OMP estimator is grid-based. v1.0 isolates the resulting model mismatch after a correct coarse support is available. Integer delays remain fixed, but each path's Doppler is locally searched on a fine continuous grid. After each coordinate update, all complex path gains are re-solved jointly by least squares.

This small refinement lowers pilot residual and Doppler error dramatically for fractional Doppler paths. It is not a fully gridless estimator: fractional delay, unknown path count, joint multidimensional Newton refinement, and Bayesian/sparse-prior estimation remain future work.

## 46. Outer-loop link adaptation

A small OLLA controller uses ACK/NACK feedback to adapt a conservative SNR backoff. If the estimated SNR is \(\hat\gamma\), MCS selection uses

\[
\gamma_{\rm eff}=\hat\gamma-\Delta.
\]

A NACK increases \(\Delta\); an ACK decreases it. For target BLER \(p_t\), the ACK step is chosen from

\[
\delta_{\rm ACK}=\delta_{\rm NACK}\frac{p_t}{1-p_t},
\]

so the expected offset drift is zero when observed BLER equals the target. The current experiment uses a synthetic MCS table and smooth BLER curves, so it demonstrates feedback calibration rather than any standardized link-adaptation table.

## 47. Communication-centric OFDM sensing

v1.0 opens a new sensing branch. Known QPSK communication symbols are reused as the probing waveform. For target range \(R\) and radial velocity \(v\), the normalized monostatic model applies two-way delay

\[
\tau=\frac{2R}{c}
\]

and Doppler

\[
f_D=\frac{2vf_c}{c}.
\]

After dividing the received grid by the known transmit symbols, an IFFT across subcarriers maps frequency-domain phase slope to delay/range and an FFT across OFDM symbols maps slow-time phase evolution to Doppler/velocity. This creates a range-Doppler map from the communication waveform itself.

The implementation also adds rectangular 2-D cell-averaging CFAR. Training cells estimate local noise power while guard cells protect a candidate target. A threshold scale based on the exponential-noise CA-CFAR approximation converts a requested false-alarm probability into a local detection threshold.

The present sensing model excludes array angle estimation, clutter models, target fluctuation statistics, range migration, calibrated radar cross section, hardware impairments, and waveform co-design.

## 48. Composite receiver impairment stress test

Many earlier experiments isolated one impairment at a time. v1.0 adds a composite frame containing timing uncertainty, CFO, IQ imbalance, Wiener phase noise, and AWGN. The receiver performs staged frame detection, repeated-half CFO estimation/correction, training-based widely-linear IQ inversion, and per-symbol pilot common-phase tracking.

The result exposes an important systems lesson: individually small residual synchronization errors can accumulate over a long OFDM frame. Coarse CFO alone leaves a severe error floor; pilot phase tracking is necessary to control residual phase drift in the tested configuration. This remains a normalized baseband stress test rather than a calibrated oscillator/RF model.

# v1.1 Addendum — Spatial Scaling, Array Sensing, Tracking, and Grid Refinement

## 49. Ordered MMSE-SIC
The MIMO detector now recomputes an MMSE front end after every sliced-stream cancellation. A reliability ordering derived from the diagonal MMSE error covariance determines the next stream. This exposes both the gain of interference cancellation and its potential error-propagation cost, while remaining far cheaper than exhaustive vector detection.

## 50. Massive/MU-MIMO precoding
A K-user downlink branch compares conjugate MRT and zero-forcing precoding as the base-station antenna count increases. Besides sum spectral efficiency, the experiment records normalized inter-user channel correlation and the coefficient of variation of normalized channel norms, providing direct numerical views of favorable propagation and channel hardening.

A separate reused-pilot model estimates the desired channel as the coherent sum of the desired and contaminating user's pilot responses. The resulting MRT beam leaks coherently toward the contaminating user, illustrating why pilot reuse can create an interference floor that additional antennas alone do not remove.

## 51. OFDM-ISAC angle processing
The sensing model now supports a receive ULA. Each target adds range phase, slow-time Doppler phase, and an array steering vector. Per-antenna range-Doppler FFT processing is followed by conventional Bartlett scanning. This creates a controlled range-Doppler-angle experiment and exposes the aperture/resolution trade-off.

## 52. Multi-frame sensing tracking
An alpha-beta constant-velocity filter predicts range and radial velocity across frames and updates on available range measurements. Missed detections are handled by prediction-only steps. The branch is intentionally a lightweight tracking baseline rather than a Kalman/PDA/JIPDA implementation.

## 53. Fractional OTFS delay/Doppler refinement
The OTFS branch now contains a compact fractional-delay waveform model and a local two-dimensional coordinate search around coarse support. Each coordinate update tests fractional delay/Doppler candidates, refits all path gains jointly by least squares, and minimizes pilot-domain residual. This extends v1.0's Doppler-only refinement while retaining explicit model limitations.

## 54. Circular redundancy versions
The HARQ rate-matching branch now includes a circular parity-buffer schedule. Each RV retransmits systematic bits but moves the parity window, so later rounds provide both repeated high-value evidence and different parity constraints. The mapping is deliberately transparent and non-standard.


## 55. Sparse-mmWave hybrid beamforming
A narrowband sparse geometric channel combines a small number of ULA steering-vector paths. The full-digital reference uses the dominant singular subspace. The hybrid baseline first selects transmit/receive beams from unitary DFT codebooks, then performs SVD in the reduced RF-chain channel. This produces a direct RF-chain-count versus rate-loss experiment without claiming a hardware-calibrated phase-shifter network.


## 56. MUSIC subspace angle estimation
Multiple spatial snapshots from the same range-Doppler cell form an array covariance matrix. After eigen-decomposition, the smallest-eigenvalue eigenvectors span an estimated noise subspace. The MUSIC pseudospectrum evaluates inverse projection energy of candidate steering vectors onto that noise subspace. In the current controlled two-source experiment, independent target amplitudes across snapshots make the covariance rank sufficient to distinguish two close directions that the conventional Bartlett spectrum merges. The source count is supplied to MUSIC; no AIC/MDL model-order selection is claimed.

---

# v1.2 extension: controllable propagation, model order, tracking and sparse precoding

## Reconfigurable intelligent surface baseline
v1.2 introduces a phase-only SISO RIS branch. The effective channel is

\[
h_{\rm eff}=h_d+\rho\sum_{n=1}^{N}h_{r,u,n}e^{j\theta_n}h_{b,r,n}.
\]

Continuous phase control co-phases every cascaded term with the direct path. Uniform finite-bit quantization then exposes phase-resolution loss. In the current normalized 10 dB Monte Carlo, 128 elements increase mean rate from about 1.05 bit/s/Hz with random phases to 6.24 with continuous control; 3-bit phase control reaches about 6.17.

## Semi-orthogonal MU-MIMO user selection
When candidate users outnumber simultaneously served spatial streams, selecting only the largest channel norms can produce mutually aligned channels. The new SUS branch greedily combines channel strength, a normalized-correlation threshold, and residual projection norm before ZF precoding. For 24 candidates, four scheduled users, and eight transmit antennas, SUS improves mean sum rate from 20.33 to 20.61 bit/s/Hz relative to strongest-norm selection while lowering median Gram condition number from 7.69 to 6.37.

## MDL model-order estimation before MUSIC
MUSIC requires a signal-subspace dimension. v1.2 estimates this dimension from covariance eigenvalues using an MDL score rather than assuming it is always known. For three synthetic sources at -5 dB, correct source-count probability increases from roughly 0.56 with 30 snapshots to 0.98 with 60 and 1.0 with 120 in the current setup. This branch makes a previously hidden assumption measurable.

## Multi-target range/velocity tracking
The sensing branch now includes constant-velocity Kalman tracks with joint range/velocity updates and greedy Mahalanobis nearest-neighbour association. In a two-target crossing experiment with roughly 14% missed detections and sparse clutter, raw range measurement RMSE is about 2.01 m while matched track-state RMSE is about 0.659 m. One target fragments once in the current run, illustrating the limitation of greedy association.

## OMP hybrid precoding
A new transmit-side hybrid beamforming branch approximates the dominant full-digital right-singular subspace with a sparse combination of DFT analog beams using orthogonal matching pursuit. On a 32x8 sparse geometric channel with two streams at 10 dB, OMP retains about 92.7% of full-digital mean rate with only two RF chains and about 97.4% with four, while consistently exceeding a one-shot DFT beam-selection baseline.

# v1.3 Extension: Distributed Access, Programmable Propagation, and Predictive Beam Management

## Cell-Free / user-centric distributed access
v1.3 adds a normalized distributed-access abstraction in which many single-antenna access points jointly serve a smaller user set. Geometry and log-normal-shadowed distance loss generate large-scale coefficients, while independent Rayleigh small-scale fading produces instantaneous channels. Each user can be served by its strongest `L` APs, from nearest-AP (`L=1`) through user-centric clusters to all-AP Cell-Free service.

The main experiment deliberately reports both user-rate statistics and the number of AP-user service links. For 24 APs and 8 users, mean 5%-tile user rate rises approximately `0.345 -> 0.936 -> 1.137 -> 1.278 bit/s/Hz` for nearest, UC-4, UC-8, and all-AP service, while service links rise `8 -> 32 -> 64 -> 192`. The point is the coordination trade-off, not a standards-level throughput prediction.

### Max-min power control
For fixed clustered MRT directions, v1.3 solves a max-min SINR power problem by bisection. For target SINR gamma, the coupled constraints have the standard form

\[
p \ge \gamma Fp + \gamma u,
\]

so the minimum required power is obtained from `(I-gamma F)^{-1}` when feasible. In the current UC-4 Monte Carlo, equal-power mean minimum-user rate is about `0.873 bit/s/Hz`; max-min power control raises it to `1.286` while reducing mean user rate from about `2.126` to `1.286`.

## Multi-user RIS coordinate optimization
The RIS branch now supports a K-user MISO effective channel

\[
H_{\rm eff}=H_d + H_{ru}\,\mathrm{diag}(e^{j\theta})G_{br}.
\]

A finite-bit coordinate-ascent baseline sweeps one RIS element at a time and recomputes the digital ZF or MRT precoder after each candidate phase. This is intentionally a local-search algorithm. In the current three-user 10 dB experiment, random phases produce mean sum rate about `1.84 bit/s/Hz`; 1/2/3-bit coordinate optimization reaches `4.52/5.10/5.32`.

## Predictive sensing-assisted beam tracking
The sensing branch now separates three beam-management policies under sparse angle measurements: reactive hold, constant-velocity Kalman prediction, and constant-acceleration Kalman prediction. A controlled accelerating target exposes model mismatch: the CV predictor is worse than reactive hold, while the matched CA model approaches the oracle beam. Mean rate is roughly `2.996`, `2.489`, `3.981`, and `4.075 bit/s/Hz` for reactive, CV, CA, and oracle policies respectively.

This is a useful negative result: prediction is not automatically beneficial. Its value depends on the motion model and sensing cadence.

## Uncertainty-aware aperture selection
A new robust beamwidth study treats angle error as Gaussian and evaluates expected communication rate for 8/16/32/64 active ULA elements. Larger arrays have more peak gain but narrower beams. The expected-rate-optimal aperture therefore decreases as angular uncertainty rises: 64 elements for sub-degree uncertainty, 32 around 1-2 degrees, 16 around 3-4 degrees, and 8 at roughly 6 degrees and above in the current normalized model.

# v1.4 Extension: Distributed CSI, Cross-Layer Feedback, and Joint Communication/Sensing Objectives

## Pilot-contamination-aware Cell-Free CSI acquisition
v1.4 explicitly models uplink pilot reuse in the distributed channel estimator. For pilot `p` at AP `m`,

\[
y_{p,m}=\sqrt{\rho_p}\sum_{j:p_j=p} h_{j,m}+n_{p,m}.
\]

Using independent Rayleigh priors with large-scale coefficient `beta`, the per-AP LMMSE estimate for user `k` is a scalar multiple of the shared pilot observation. Co-pilot users therefore contaminate one another coherently at the estimation stage. A transparent greedy assignment minimizes accumulated cosine overlap of the users' large-scale fading fingerprints across APs. The current 12-user experiment shows a large NMSE and cell-edge-rate benefit when pilot resources are scarce, while orthogonal assignment removes the modeled contamination when enough pilots are available.

## RIS-assisted Cell-Free access
The distributed AP channel is augmented by a single programmable surface,

\[
H_{\rm eff}=H_d+H_{ru}\,\mathrm{diag}(e^{j\theta})G_{ar}.
\]

A finite-bit coordinate optimizer recomputes distributed MRT after each candidate phase. Two utilities are exposed: total sum rate and minimum-user rate. The resulting experiment is intentionally a fairness-versus-throughput study rather than a claim of globally optimal RIS control.

## Event-driven OLLA/HARQ/queue loop
The new cross-layer abstraction keeps FIFO packet queues, correlated per-user SNR traces, biased/noisy SNR estimates, MCS thresholds, OLLA offsets, ACK/NACK feedback and Chase-style accumulated SNR evidence in one event loop. PF and delay-aware PF policies choose which queued user is served. This connects PHY-quality estimation errors to packet drops, retransmission cost and delay rather than studying each component independently.

## Joint communication/sensing beamforming
For one communication channel and one sensing direction, the beam is selected as the principal eigenvector of a weighted quadratic utility. Weight one produces communication MRT; weight zero produces the sensing steering vector. Sweeping the weight produces a compact Pareto frontier between communication rate and sensing beam gain, with a sharper conflict as the communication and sensing directions separate.

## AP activation and energy efficiency
A simple distributed-AP power model adds fixed transmit/fixed-site power and a per-active-AP circuit term. The experiment compares aggregate-strength AP selection against a coverage-aware greedy rule and reports mean rate, edge rate and rate per modeled watt. It demonstrates that all-AP operation can maximize rate while an intermediate active set maximizes energy efficiency under the chosen explicit power assumptions.

# v1.5 Addendum

## Distributed CSI fidelity, fronthaul, and aging
v1.5 introduces an explicit CSI transport abstraction for Cell-Free studies. Complex AP-user coefficients are scalar-quantized and the transport cost is counted as two real components per selected AP-user link. User-centric clustering therefore changes both spatial cooperation and CSI payload. A Gauss-Markov fading branch holds the quantized precoder between updates, exposing how channel aging makes long refresh intervals increasingly harmful under faster temporal decorrelation.

## Robust RIS under imperfect CSI
The Cell-Free RIS branch now distinguishes single-estimate optimization from sample-average robust optimization. Multiple perturbed channel realizations approximate a CSI uncertainty set; finite-resolution coordinate ascent maximizes mean utility across this ensemble. Held-out channel perturbations are used for evaluation so the robust method is not scored on its own training samples.

## Finite-blocklength link adaptation
The normal approximation is inverted to estimate packet-error probability for a chosen rate and blocklength. Successful blocks deliver `nR` information bits and failed blocks deliver zero, so conservative MCS selection has a real throughput cost. OLLA can then adapt a backoff from ACK/NACK feedback when the SNR estimator is systematically biased.

## ISAC sensing-resource scheduling
A lightweight uncertainty-fusion model converts sensing-time allocation into posterior angle variance. The expected communication rate then depends on both payload fraction and ULA aperture: larger arrays provide more peak gain but narrower beams. Exhaustive search over sensing fraction and active elements produces an interpretable sensing-overhead / beamwidth / throughput operating point.


# v1.6 Addendum: Coupled Uncertainty, Reliability, Sensing, and Deployment Cost

## Aged and quantized CSI for Cell-Free RIS
v1.6 distinguishes the age/precision of AP-RIS and RIS-user CSI from the finite-bit resolution of the RIS itself. Stale channel tensors are scalar-quantized for transport, while future/current channels follow a correlation abstraction. A naive finite-bit RIS controller optimizes the stale quantized snapshot; a sample-average controller optimizes expected utility over a predicted ensemble. The results intentionally retain cases where the robust controller trades mean performance for a better lower tail or loses under severe model mismatch.

## Finite-blocklength HARQ packet queues
The short-packet branch is now multi-user and queue driven. A scheduled packet chooses an MCS on its first attempt, each transmission consumes a fixed number of complex channel uses, Chase HARQ sums linear-SNR evidence, and packet error is evaluated by the finite-blocklength normal approximation. OLLA learns an ACK/NACK-dependent SNR offset, so reliability improvements carry explicit rate and retransmission costs.

## Predictive sensing-on-demand
The prior sensing-resource controller was myopic: it maximized only current-slot net rate. v1.6 adds a transparent two-step lookahead that values a lower posterior angle variance because it improves the next slot as well. This improves over the myopic controller on the maneuver trace but does not outperform an offline tuned fixed policy, demonstrating the remaining horizon/value-of-information limitation.

## Fronthaul-energy-aware Cell-Free control
A dynamic distributed link now combines AP activation, complex-CSI quantization, periodic updates, channel aging, AP circuit power and a per-bit fronthaul-energy abstraction. This produces an interior optimal CSI refresh interval whose location moves with channel correlation: high mobility increases the cost of stale precoder CSI and shifts the energy-efficiency optimum toward more frequent updates.

# v1.7 Addendum: Temporal CSI, Retransmission Structure, Slow Passive Control, and Queue-Aware ISAC

## 57. Fixed-budget asynchronous Cell-Free CSI refresh

v1.7 removes the assumption that every distributed AP can refresh CSI simultaneously. A per-slot AP-update budget is imposed. Three policies are compared: deterministic round-robin; expected stale-CSI MSE priority; and bounded-uncertainty priority with a maximum CSI age. The pure MSE policy reveals a useful failure mode: globally minimizing estimation error can starve low-power APs and damage cell-edge users. The age cap converts the problem into an explicit freshness-versus-fairness trade-off.

## 58. Predictive/differential CSI quantization

For Gauss-Markov channel evolution, the CPU predicts `rho * Hhat[t-1]` and the AP quantizes the innovation rather than the full channel. At fixed scalar bit depth, innovation power shrinks sharply as temporal correlation increases, producing a large NMSE advantage. No entropy coding or standards feedback framing is assumed; the experiment isolates source-prediction gain.

## 59. Finite-blocklength incremental-redundancy HARQ

For independent redundancy blocks with SNRs `gamma_i` and lengths `n_i`, v1.7 accumulates the normal-approximation information mean and dispersion across rounds. A packet's information bits remain fixed while IR increases effective code length; Chase combines repeated observations into a higher SNR at fixed first-round code length. This gives a transparent short-packet comparison without claiming a code-specific NR HARQ implementation.

## 60. Two-timescale RIS-assisted Cell-Free control

AP precoding is recomputed from the current effective channel every slot, while RIS phases may be updated only every `T_RIS` slots using sample-average optimization over recent snapshots. This intentionally isolates the cost of passive RIS control. A phase-noise perturbation is also applied at execution time. The experiment shows that moderate slow updates preserve most rate while reducing control bits, but very slow updates approach stale-phase performance.

## 61. Queue-aware sensing-on-demand

The ISAC controller now sees both target-angle uncertainty and packet queues. Candidate sensing fractions/apertures trade posterior angle precision against immediate payload service. Under congestion, queue-aware control reduces sensing and backlog while accepting worse tracking uncertainty. A two-slot model-predictive baseline recovers some future tracking value but remains a heuristic rather than an optimal POMDP.

# v1.8 Addendum: Budgeted Information, Deadlines, Freshness, Event-Triggered Control, and Random Access

## 62. Joint CSI refresh and bit allocation

v1.8 merges the previously separate asynchronous-refresh and predictive-compression branches. The CPU advances stale channel estimates with a Gauss-Markov conditional mean. A selected AP sends only the residual innovation, and a deterministic greedy controller chooses both the AP and the scalar quantizer depth under a single per-slot fronthaul-bit constraint. Candidate benefit approximates the stale-channel MSE removed by refreshing minus residual quantization distortion; the final link experiment uses the actual scalar quantizer rather than this proxy.

The study reveals two effects. First, joint refresh/precision control substantially lowers CSI NMSE at tight budgets. Second, a fixed bit depth can make some AP refreshes infeasible when one AP serves many users; variable precision allows those APs to remain refreshable. Forced refresh also need not be monotonic with budget because a low-value quantized update can inject more error than prediction alone.

## 63. Deadline-aware finite-blocklength HARQ

Each queued packet now carries an absolute expiry time. A scheduled packet keeps its first-round MCS and accumulates either incremental redundancy or Chase evidence. Three scheduling objectives are exposed: proportional-fair efficiency, earliest-deadline-first, and a reliability/urgency score based on estimated next-round finite-blocklength success. Expiry drops are separated from max-HARQ-round drops.

The resulting trade-off is explicit: EDF minimizes misses but is not necessarily the highest-goodput rule; reliability-aware urgency can move toward a middle operating point.

## 64. Age of Information

A new generate-at-will status-update simulator tracks receiver AoI rather than only packet throughput. Each user can be prioritized by current age, estimated SNR, or age multiplied by estimated success probability. Fresh attempts generate a new status sample at every scheduling opportunity, while Chase mode may retransmit an older failed sample. This exposes a classic freshness/reliability conflict: successful delivery of an old packet is not equivalent to delivery of a newly generated state.

## 65. Event-triggered RIS control

Passive phase control can now be refreshed on utility degradation rather than a fixed clock. A held RIS profile is probed on the current channel; if sum-rate falls sufficiently below the post-update reference, or if a maximum control age is reached, finite-bit coordinate optimization is rerun. Stable intervals therefore consume few control bits while fast-changing intervals trigger denser refreshes.

## 66. Long-term budget-constrained ISAC sensing

The sensing controller now faces a cumulative average sensing ceiling. A token-style feasibility rule ensures total sensing cannot exceed the available long-term budget, while a dual price biases online choices among sensing fractions and array apertures. The resulting schedule concentrates sensing around high process uncertainty instead of distributing it uniformly.

## 67. Grant-free random access with ideal SIC

A new access-layer branch models autonomous sparse device activity. Each active terminal independently selects one uplink resource. Collision-only decoding succeeds only on singleton resources above threshold. The NOMA baseline orders colliding users by received power and performs ideal strongest-first SIC. The experiment intentionally sweeps received-power dispersion: when users arrive at nearly equal power, SIC provides no gain; heterogeneous powers create a capture/SIC structure that can decode multiple colliders.


# v1.9 Extension — Random Access, AirComp, Slicing, and Energy-Constrained Freshness

## Graph-based coded random access

v1.9 adds a frame graph in which an active user repeats one packet over a random set of slots. Iterative SIC repeatedly decodes singleton slots and removes all replicas of newly decoded users. This exposes the classic threshold phenomenon: repetition is beneficial only while the random bipartite graph remains peelable. The experiment compares degree-one slotted ALOHA, repetition-3 without iterative cancellation, and an irregular `{2,3,8}` repetition distribution with SIC.

## Over-the-Air Computation

For device vectors $x_k$, the arithmetic target is $\bar x=K^{-1}\sum_k x_k$. Under ideal analog synchronization, channel inversion chooses a common receive gain so simultaneous transmissions superpose directly into a scaled sum. Full inversion is bottlenecked by the minimum channel magnitude. Truncated inversion suppresses devices below a channel threshold; this reduces inversion noise but changes the participant set. v1.9 reports both bandwidth cost and aggregation MSE, and uses median/p90 statistics because deep Rayleigh fades create heavy-tailed error.

## eMBB / URLLC mini-slot coexistence

The slicing abstraction assumes backlogged eMBB traffic and stochastic URLLC packet arrivals with short deadlines. Fixed reservation permanently removes PRBs from eMBB, adaptive reservation uses an EWMA traffic estimate, and preemption punctures eMBB only when URLLC is actually served. The purpose is not NR conformance but direct visibility of reservation waste, burst underprediction, deadline protection, and eMBB puncturing cost.

## Energy-harvesting Age of Information

Each sensor harvests one energy unit according to a Bernoulli process and has a finite battery. A status transmission consumes one unit. The scheduler chooses among energy-feasible users using age-only, SNR-only, age×reliability, or battery-aware freshness metrics. The main result is that transmission success count and information freshness can diverge dramatically: an SNR-greedy scheduler may update strong users almost every slot while weak users become arbitrarily stale.

# v2.0 — Wireless Edge Intelligence and Task-Oriented Communication

v2.0 connects the communication simulator to optimization and distributed-computation objectives. Rather than treating a received vector as the final product, these experiments ask how physical-layer aggregation error changes a downstream learning objective, how programmable propagation should be optimized for computation rather than sum power, and how task utility can diverge from source fidelity.

## Federated learning over AirComp

A deliberately small convex federated linear-regression problem is used so that aggregation error can be inspected without neural-network confounders. Each round computes local gradients and compares ideal aggregation, noisy orthogonal upload, full-inversion AirComp, and truncated inversion. Communication cost is recorded as modeled channel uses per aggregation round. A fixed initial gradient RMS scale is used for analog normalization so the channel noise does not artificially vanish near convergence.

## RIS-assisted AirComp

For effective device channel

\[h_k^{\rm eff}=h_{d,k}+\sum_n f_{k,n}g_n e^{j\theta_n},\]

full-inversion AirComp is controlled by \(\min_k |h_k^{\rm eff}|\). v2.0 therefore compares a conventional total-channel-power objective with a direct max-min objective. The latter is not globally optimized; it is a finite-bit coordinate-ascent baseline whose advantage is transparency.

## Cell-Free AirComp

Multiple AP observations are centrally combined with a unit-norm vector. Candidate search selects the combiner maximizing the weakest device projection. This exposes the benefit of distributed reception while explicitly assuming perfect CSI, phase coherence, and centralized sample availability.

## Task-oriented communication

The semantic/task-oriented branch uses a binary Gaussian classification problem with class means \(\pm\mu\). The scalar \(\mu^T x\) is a sufficient statistic for classification, allowing a controlled comparison between transmitting all source features and transmitting one task statistic. Classification accuracy and source-reconstruction MSE are reported separately to prevent task success from being misrepresented as source fidelity.

## Capture-aware IRSA

IRSA replica peeling is extended with a simple strongest-packet SINR capture condition. Perfect replica pointers and perfect cancellation after successful decoding remain assumed. The experiment isolates how received-power structure can create additional SIC opportunities and where graph overload still defeats the decoder.

# v2.1 Extension — Selection Bias, Access Uncertainty, and Multi-Task Semantics

## Communication-driven client selection under non-IID data

v2.1 introduces a two-group federated linear-regression problem in which the equal-client global objective requires both groups, while one group has systematically stronger long-term wireless channels. This creates a controlled cross-layer conflict: strongest-channel scheduling increases the minimum selected link amplitude but changes the effective data distribution seen by the optimizer. Random, strongest-channel, gradient×channel, and participation-age×channel policies are compared using global loss, group loss imbalance, selected-link strength, selection shares, and Jain participation fairness.

## Random-access federated participation

A federated round can now receive updates through degree-one slotted ALOHA or graph-based IRSA. Only decoded clients contribute gradients. The purpose is to expose how access-graph collapse creates empty learning rounds and how the same repetition law can be harmful under overload and useful under a lighter graph load. Decoded updates are assumed error-free after access resolution.

## Robust AirComp under CSI uncertainty

RIS-AirComp adds a sampled-uncertainty coordinate heuristic that maximizes a lower quantile of the weakest effective device channel across CSI perturbation scenarios. The experiment compares it against point-estimate max-min control on the same true channel realizations. The result is intentionally non-monotonic: moderate uncertainty can benefit from scenario averaging, while severe uncertainty/model mismatch can still defeat the heuristic.

For Cell-Free AirComp, APs can have heterogeneous CSI-error levels. A lower-confidence-bound candidate combiner penalizes projected links with high estimation variance. This branch focuses on upper-tail aggregation MSE rather than only median performance.

## Multi-task task-oriented representations

Two tasks are deterministic signs of different linear projections of an isotropic Gaussian source. Full raw transport, two task-specific sufficient statistics, a single shared rank-one semantic projection, and a rank-two shared subspace are compared. As the angle between task directions increases, the rank-one representation becomes an information bottleneck for at least one task, while the rank-two subspace retains both sufficient statistics. The experiment separates task-sharing efficiency from a claim of universal semantic compression.

## 64. v2.2 — Fixed-budget gradient communication

v2.2 adds a communication-budgeted federated optimizer. Each round has a fixed budget of transmitted real-valued gradient coordinates. Increasing the number of selected clients improves statistical coverage of non-IID data but reduces the top-k budget available to each client. Error-feedback residuals preserve dropped gradient mass across rounds, while an optional residual-aware allocator assigns more coordinates to clients with larger accumulated update energy. The experiment therefore separates three effects: participation diversity, instantaneous sparsification, and temporal error compensation.

## 65. v2.2 — AirComp RF/ADC impairment baseline

The analog aggregation path now includes memoryless transmit magnitude clipping, additive channel noise, optional receiver AGC, and finite-resolution uniform I/Q quantization. The purpose is not device-level RF accuracy; it is to demonstrate that AirComp's mathematical superposition property does not remove dynamic-range constraints. AGC reduces ADC overload/under-utilization, while transmitter clipping introduces a distortion floor that cannot be corrected by receiver gain control.

## 66. v2.2 — Progressive task-oriented communication

A two-task Gaussian source is projected onto the principal two-dimensional task subspace. A common rank-one semantic layer is transmitted first. If the noisy base representation yields insufficient task margin, an orthogonal enhancement layer is requested. This converts the prior fixed-rank multi-task semantic study into a variable-length representation whose average channel use grows with task conflict and confidence requirements.

## 67. v2.2 — Importance-aware random access for learning

The FL random-access branch now allows repetition degree to depend on gradient-norm rank. High-importance updates receive degree four, medium updates degree three, and low-importance updates degree two, keeping average repetition close to the uniform degree-three baseline. The key metric is not only decoded packet fraction but the fraction of total active gradient norm recovered after iterative singleton peeling. This exposes a MAC/learning utility trade-off and preserves the overload failure region.

## 68. v2.2 — Two-timescale RIS-AirComp federated learning

Direct, device-RIS, and RIS-receiver channels evolve using a Gauss-Markov process. Client-side AirComp inversion reacts to the current effective channel every learning round, while finite-bit RIS phases are recomputed only every T rounds using a weakest-device max-min objective. This creates an explicit passive-control overhead versus mobility/freshness trade-off and propagates it into federated optimization loss.

# v2.3 Extension — Resilient and Task-Aware Edge Intelligence

## 69. Asynchronous federated optimization

Clients now compute gradients on delayed server snapshots. The simulator records the cosine similarity between a stale gradient and the same client's gradient at the current model. Three baselines are compared: direct stale-gradient application, exponential staleness weighting, and a Hessian transport that is exact for the local quadratic ridge objective. The latter is intentionally labeled model-specific rather than a generic deep-learning correction.

## 70. Byzantine-robust coordinate aggregation

A fixed subset of clients applies sign-flip/scaling attacks to local gradients. The server compares arithmetic mean, coordinate median, and coordinate trimmed mean. Sweeping attacker fraction exposes both the extreme vulnerability of the mean and the finite breakdown region of robust coordinate estimators.

## 71. AirComp with client-side Gaussian perturbation

Local gradients are clipped to a norm bound and receive independent Gaussian perturbations before wireless superposition. The experiment separates wireless aggregation noise from client perturbation and propagates both into optimization loss. Because no privacy accountant or subsampling model is included, this is described only as a DP-style privacy-noise utility experiment.

## 72. Semantic-value resource scheduling

Radio queues contain synthetic semantic packets with importance, resource cost, expiry, and arrival time. Scheduling policies prioritize either channel reliability, importance, expected delivered value per resource, or value with urgency weighting. The experiment measures task utility rather than only packet throughput.

## 73. Confidence-triggered split inference

A Gaussian classification task is split between a local early classifier using a subset of source coordinates and an edge refinement that uses the residual coordinates. Adaptive operation offloads only when local confidence is low. The branch reports accuracy, offload fraction, modeled feature channel uses, mean latency, and p95 latency to expose local-compute versus communication/edge-refinement trade-offs.

# v2.4 Extension — Heterogeneous Models, Stragglers, Knowledge Transfer, and Real-Time Inference

## 74. Personalized federated bias-variance trade-off

Each client has a local linear optimum perturbed from a shared global direction. A pooled ridge estimator forms the global model, while a small local dataset produces a noisy client estimator. The personalized model

\[w_k^{(p)}=(1-\alpha)w_g+\alpha w_k^{(local)}\]

therefore exposes both non-IID bias and finite-sample local variance. Held-out client data are used for evaluation. As heterogeneity grows, the optimal alpha moves from global sharing toward stronger specialization; full local fitting is not automatically optimal at moderate heterogeneity because local sample size is deliberately small.

## 75. Straggler-resilient coded-compute abstraction

Synchronous distributed learning can be dominated by the slowest worker. v2.4 compares waiting for all K uncoded tasks, launching two copies of every task, and an MDS-style abstraction that launches K+r coded workers and permits recovery after any K responses. Worker time includes independent compute and communication components plus probabilistic heavy straggler slowdown. The experiment reports mean and upper-tail round latency together with redundant compute load so latency improvement is never presented as free.

## 76. Federated knowledge distillation over a constrained uplink

Instead of uploading each d-dimensional linear teacher, clients can evaluate a shared public probe matrix and upload only m teacher logits. The server averages noisy logits and fits a ridge student to the public probes. For data concentrated in a lower-dimensional latent subspace, a modest number of probes can preserve most task accuracy while reducing the transmitted scalar count. The abstraction assumes public probes are available to all clients and does not address domain shift or public-data privacy.

## 77. Deadline-aware channel-adaptive split inference

The prior confidence-triggered split baseline is extended with per-sample residual-link SNR and a hard end-to-end deadline. Offloading is permitted only when local confidence is low, the wireless refinement is predicted to be useful, and residual-feature transmission plus edge compute can complete before the deadline. Raw classification accuracy and on-time task accuracy are separated; this prevents late but correct predictions from being misreported as real-time successes.

## 78. One-bit over-the-air majority aggregation

Each client observes a noisy local gradient coordinate and transmits only its sign as a BPSK symbol. Synchronous wireless superposition creates a noisy analog vote and the server takes the sign of the received sum. Increasing the client population creates a majority-law gain when local gradients are unbiased, while sign-flipping clients reduce the vote margin and reveal an adversarial breakdown region. No channel coding or practical carrier/timing synchronization is included.

## v2.5 — Resilient and Real-Time Edge Intelligence

### Resilient asynchronous federated learning
v2.5 combines stale local gradients and Byzantine sign-flip/scaling attacks within the same convex FL trace. Coordinate median provides a strong baseline: under 13% Byzantine clients and mean delay four, naive mean aggregation has median final loss about 2.10 whereas coordinate median stays near 0.0208. A conflict-rejection plus exponential staleness-decay heuristic is slightly worse than median in this experiment, an intentional negative result showing that additional mechanism complexity need not improve robustness.

### Hierarchical personalization
Clients are generated around two latent model clusters. A global pooled ridge model, two cluster-specific pooled models and fully local models are evaluated on held-out client data. With accurate grouping, cluster models preserve low variance while tracking structured heterogeneity. As assignment error increases, cross-cluster contamination can remove this advantage and make local fitting preferable.

### Joint privacy and hardware AirComp
The analog aggregation chain now includes clipped gradients, client Gaussian perturbation, channel inversion, PA magnitude limiting, AWGN, receiver AGC and finite-resolution I/Q quantization. With privacy-noise multiplier 0.25, moving from 3 to 6 ADC bits improves median aggregation MSE only modestly, and 6 to 8 bits is essentially saturated because intentional perturbation dominates the error budget.

### Energy-aware split inference
Split inference now reports task accuracy, on-time task accuracy, mean device energy, channel uses and latency. At poor SNR, static confidence-only offloading may obtain higher raw accuracy while returning many predictions after the deadline. Deadline- and energy-aware policies reject such offloads, exposing the operational difference between offline accuracy and real-time task success.

### Layered downlink model multicast
v2.5 introduces a downlink edge-learning baseline. Full common multicast is limited by the weakest client spectral efficiency; serial unicast avoids the common-rate bottleneck but consumes large aggregate airtime. A scalable model abstraction sends a common base layer to all devices and an enhancement layer to the stronger half, trading average task utility for much lower delivery time as receiver SNR heterogeneity grows.

# v2.6 Extension — Downlink Synchronization and Learning-Aware Edge Control

## 79. AirComp user selection: analog quality versus statistical coverage
v2.6 separates two error sources that are often conflated in OTA-FL user selection. For a selected set S, the analog error is measured against the exact selected-client mean gradient, while the selection-bias term is measured between that selected mean and the all-client gradient. In the two-group non-IID problem, long-term channel strength is correlated with data group. Strongest-channel scheduling can therefore reduce analog AirComp error while increasing optimization bias. A greedy diversity baseline adds a gradient-direction novelty term to channel quality, producing a deliberate physical-layer versus learning-layer trade-off.

## 80. Progressive split inference
Residual source features are ordered by their contribution to a known linear task direction. The device starts from a local subset and can upload residual features in chunks. Confidence-only progressive transmission requests another chunk when the current margin is small; the adaptive policy additionally checks instantaneous link quality, modeled transmit energy and hard deadline feasibility. This extends one-shot split inference into a variable-length communication process whose output metric is on-time task accuracy rather than only offline classification accuracy.

## 81. Differential downlink model synchronization
The global-model downlink now distinguishes full broadcasts, deltas chained to the immediately preceding model, and keyframe-anchored differential packets. Chained deltas are efficient while every packet arrives, but a single loss can invalidate all later deltas until the next keyframe. Anchor-relative deltas grow mildly with keyframe age but can recover after isolated missed differentials if the receiver still owns the anchor. The model explicitly records normalized downlink payload, packet success, client model MSE and model-version age.

## 82. Energy-harvesting OTA federated participation
Each client has a finite battery and a heterogeneous Bernoulli energy-arrival process. Scheduling one analog update consumes one normalized energy unit. Under severe energy scarcity, scheduler differences are small because energy causality itself is the dominant constraint. As harvested energy becomes abundant, long-term channel/data correlation re-emerges and channel-greedy service can bias participation. An age-aware battery/channel score restores participation fairness at the cost of some weakest-link AirComp gain.

## 83. Importance-aware layered model multicast
The downlink layered-model abstraction now gives each client a task-importance weight. A common base layer is delivered to all devices; the enhancement layer uses a selected multicast code-rate threshold. Lowering the threshold includes weaker receivers and costs additional airtime. The importance-aware controller maximizes weighted task utility minus an explicit airtime penalty, showing that strongest-link receivers are not necessarily the most valuable recipients when application importance and SNR are negatively correlated.

# v2.7 Extension — Runtime Orchestration and State-Aware Edge Intelligence

## 84. Budget-constrained age-aware differential downlink

The v2.6 anchored-delta model is extended with a runtime keyframe controller. Rather than sending a full model every fixed number of rounds, the controller observes the 80th-percentile client model-version age and sends a keyframe only when age is high and a running normalized-downlink budget permits it; a hard maximum spacing prevents indefinite desynchronization. A common blockage episode makes periodic timing nontrivial. The main comparison deliberately matches average normalized downlink payload, so the adaptive scheme cannot win simply by transmitting more full models.

## 85. Carbon-aware federated client orchestration

Clients are assigned to three data groups and three electric-grid regions. Regional carbon-intensity proxies vary over time and are intentionally correlated with data-group identity. Carbon-only selection therefore creates a controlled counterexample: environmental cost can fall while statistical coverage and convergence degrade. A balanced score combines current gradient utility, carbon proxy and participation age. The carbon-weight sweep produces a loss-carbon-fairness Pareto rather than a single claimed optimum.

## 86. Edge AI model caching and inference routing

The edge server has finite model storage and serves a workload whose model popularity changes in three phases. Cached models execute with low edge latency; cache misses use a cloud/backhaul path. Loading a model into the cache is explicitly charged as backhaul traffic. Static, LRU, periodic popularity and periodic value-density policies are compared. Value-density weights expected request frequency by cloud-latency saving per cached MB, illustrating why maximum cache hit rate need not minimize inference latency or model-transfer traffic.

## 87. Queue-aware progressive split inference

Progressive inference requests now contend for one shared radio server. Each request starts from a local confidence state and can receive up to three wireless enhancement chunks. Requests have heterogeneous deadlines, task values and per-user SNR. Packet-style EDF, value and urgency policies are compared with FIFO and a completion-aware score that rewards partially served requests. The experiment exposes a completion-locality effect: aggressive preemption can leave many tasks partially refined but unusable before their deadlines.

## 88. Importance-aware multicast repair

A model is first broadcast at an aggressive multicast rate selected from a receiver-SNR quantile. Strong clients decode immediately while weaker clients miss the model. No-repair, repair-everyone and task-value-aware selective repair are compared. Selective repair ranks missed clients by importance per unicast airtime and stops at the conservative full-common airtime budget. This separates radio coverage from application utility and shows why guaranteeing every receiver through serial repair can be more expensive than a single weakest-user multicast.

# v2.8 Extension — State Recovery, Freshness, and Closed-Loop Runtime Control

## 89. Selective downlink repair under a matched resynchronization budget
v2.8 adds ACK-aware reconstruction-chain state to the differential model downlink. A periodic baseline spends one full common keyframe every ten rounds. Selective policies instead use a much rarer common keyframe and accumulate the remaining budget for client-specific state repair. Repairs are ranked by model-version age or task-importance-weighted age. At low SNR broad chain failure makes common keyframes more efficient; at high SNR failures become sparse and targeted repair reduces weighted model age and error at nearly identical downlink load.

## 90. Version-aware AI-model caching
A cache entry now contains both model identity and model version. Model versions evolve stochastically, and the utility of an edge-served inference decays with version gap. The version-aware policy allocates a hard refresh budget to new cache fills or differential refreshes according to expected task-value gain per transferred MB. This exposes the distinction between hit rate, task utility, model freshness and backhaul churn.

## 91. Virtual-debt carbon/fairness orchestration
A persistent deficit queue is maintained per FL client relative to a target long-run participation rate. Unserved clients accumulate debt and selected clients pay it down. The scheduling score combines current gradient utility, regional time-varying carbon cost and normalized debt. Increasing debt weight recovers participation fairness and convergence but consumes more carbon budget, yielding an explicit long-horizon Pareto.

## 92. Admission control for progressive split inference
Progressive enhancement requests no longer automatically enter the shared radio queue. The device can terminate locally if backlog is high or the expected task-value gain does not justify the congestion price. Accepted jobs are still served with completion-aware scheduling. At moderate/high loads admission prevents radio work from becoming stale before completion; at extreme overload a simple hard backlog gate can outperform the value-based heuristic.

## 93. Digital-twin semantic synchronization
The physical process evolves position and velocity, including two acceleration episodes. The edge twin propagates a constant-velocity prediction between updates. Periodic full-state updates are compared with state-error-triggered full updates and compact quantized state innovations. An Age-of-Incorrect-Information proxy is accumulated only while state error exceeds a tolerance. The experiment measures the accuracy/resource consequences of deciding *when* and *how much* state to transmit.

# v2.9 — State Value, Congestion, and Networked Control

## Task-conditioned model repair
v2.9 extends differential model repair from static importance to time-varying application demand. Every round broadcasts the same chained delta. Broken clients compete for a saved repair-credit budget. The task-aware score multiplies version-age/reliability-per-byte by static task importance and the currently realized request count. At burst strength 2.4, all policies use approximately 0.290 normalized downlink size per round, but task-aware repair raises realized/ideal task utility to about 0.792 versus 0.697 for age-only and reduces task-weighted model age to about 7.43 rounds. The experiment demonstrates that model freshness has value only through current downstream work.

## Refresh congestion as a source of model staleness
The versioned-cache branch now includes a FIFO model-refresh queue. A refresh request does not update the cached model until all requested bytes cross the backhaul. At 0.8 MB service per inference request, eager refresh accumulates roughly 579 MB P95 queue and serves models about 10.36 versions old. Congestion-aware refresh reduces these to about 416 MB and 7.75 versions. At 5 MB/request, periodic value-density refresh produces higher task utility than the congestion-aware heuristic, showing that congestion pricing is most useful when capacity is actually scarce.

## Battery-carbon-fair federated orchestration
Clients now have finite batteries, stochastic harvesting, and communication/compute energy costs. Carbon-only and virtual-debt policies are compared only among energy-feasible clients. Under harvest scale 0.12, approximately 89% of client-round states are infeasible and more than 93% of rounds cannot fill the requested six-client cohort; scheduling logic is therefore secondary to energy scarcity. Near harvest scale 0.50, carbon-only selection begins to reduce Jain participation fairness and increase excess loss, while debt/battery-aware orchestration restores learning performance at additional carbon cost.

## Digital-twin-guided edge-model prefetch
A mode-switching physical process selects the AI model required for inference. The digital twin sees noisy transition progress and direction. Blind predictive prefetch is useful at low uncertainty but becomes a model-transfer-churn mechanism as uncertainty rises. At uncertainty 0.8, blind prediction generates about 97,163 MB modeled transfer with 45.6% wrong prefetches. Uncertainty gating lowers these to about 12,082 MB and 15.4%, while mean inference latency remains about 11.82 ms versus 14.72 ms for purely reactive loading.

## Wireless networked control
Five mildly unstable scalar plants share one sensor transmission per slot. The remote controller predicts state between successful updates and applies fixed stabilizing feedback. At -4 dB mean sensor-link SNR, Max-Age keeps mean information age at roughly 18.8 slots but incurs mean closed-loop cost about 124.3. Control-value scheduling permits older information (about 22.2 slots) but lowers cost to about 14.3 by prioritizing plants according to link success, instability, state importance, and estimation mismatch. This provides a direct counterexample to treating minimum Age of Information as a universal system objective.

# v3.0 — Risk, Reliability, and Control-Aware Runtime Orchestration

## 99. Risk-sensitive wireless feedback scheduling
Rare plant-specific disturbances are added to multiple unstable feedback loops sharing one sensor channel. The mean-value scheduler prioritizes current expected estimation benefit; the risk-value scheduler adds an explicit plant-risk and staleness term. Empirical P95 and CVaR95 stage-cost metrics reveal a non-monotone operating region: tail protection is valuable when rare shocks materially dominate the objective, but extra conservatism can be wasteful outside that regime.

## 100. Variable-rate semantic state updates
The feedback branch now sends quantized innovations relative to the controller prediction rather than a full absolute state. Update precision is 3, 6, or 10 bits. Longer payloads improve reconstruction but reduce packet-success probability. A link-aware policy adapts precision from instantaneous SNR, estimation mismatch, plant importance, and information age, exposing a direct communication-precision/control trade-off.

## 101. Failure-aware edge task orchestration
Heterogeneous edge nodes have radio latency, service rate, energy proxy, queue state, and execution failure probability. Fast nodes are deliberately less reliable so latency and trust are not aligned. Latency-only, trust-aware, and risk-aware placement are compared using mean/P95 latency, deadline misses, failure rate, and energy proxy. The model is an orchestration abstraction rather than a deployed edge-service benchmark.

## 102. Joint model caching and inference offloading
Three edge servers maintain finite AI-model caches under drifting request popularity. Cache placement evolves on a slower epoch while every request is routed using radio delay, queue load, and model-miss cost. Cache-first routing can achieve excellent hit rate while concentrating work on a subset of edges and increasing latency; joint routing prices queueing and cache state together.

## 103. Cooperative multi-agent wireless control
A chain of coupled scalar agents shares one wireless feedback resource. Local-error scheduling refreshes the largest current estimation mismatch. System-value scheduling instead evaluates the immediate reduction in global state/formation estimation error if each candidate sensor were refreshed. The added coordination model helps under severe communication scarcity but can be unnecessary when reliable links make local-error scheduling sufficiently effective.

# v3.1 — Safety, Recovery, and Goal-Oriented Runtime Control

## 104. Safety-aware wireless feedback
Multiple mildly unstable plants share one feedback opportunity. Plants deliberately have different process-noise levels, instability, and safety-envelope widths so estimation-error priority and safety priority are not identical. The safety-value scheduler uses a compact sensor-side normalized proximity score plus link success and estimation mismatch. The experiment reports explicit state-bound violation probability in addition to mean/P95 control cost and information age. It is a heuristic safety-risk scheduler, not a certified control-barrier method.

## 105. Channel-adaptive feature precision and model depth
Each synthetic inference task observes a fading feature link and a task-difficulty variable. The runtime chooses 2/4/8 feature bits and analytic model depth 1–4 under a latency deadline. Low precision reduces transmission time but limits task fidelity; deeper computation improves the analytic task-accuracy proxy but adds latency. Fixed-light and fixed-deep baselines reveal when joint communication/computation adaptation is actually necessary.

## 106. Failure recovery by restart, checkpoint, or replication
Long-running edge tasks fail stochastically. Restart loses completed work, checkpoint migration periodically pays state-transfer/checkpoint overhead but bounds repeated work, and dual execution roughly doubles compute consumption while making recovery fast. P95 latency, deadline misses, recovery traffic and compute-load ratio expose a threshold: checkpointing is unnecessary when failure is very rare but increasingly valuable as failures become common.

## 107. Task-risk-aware AI-model replication
Seven synthetic AI models differ in size, request popularity and downstream criticality. Every model receives one base copy; additional copies consume a finite storage budget. Popularity placement minimizes frequent request exposure, whereas risk-aware placement weights popularity by criticality. Raw outage count and task-weighted outage can move in opposite directions, demonstrating why reliability objectives should reflect application consequence rather than event count alone.

## 108. Component-selective semantic control
A three-dimensional plant state has strongly unequal state-cost weights. One feedback slot can send one high-precision component or all components at lower precision. Round-robin, all-low and control-value component selection are compared under the same order of payload. The experiment shows that task/control relevance can dominate uniform source fidelity when communication is scarce.

## v3.2 — Reliability-Oriented Goal-Aware Runtime

### Reliability-oriented semantic HARQ
v3.2 adds a scalar task-statistic block-fading experiment in which retransmission can be driven either by channel SNR or by receiver task confidence. MRC combines repeated observations. The task-driven policy improves hard-sample and lower-tail reliability while naturally reducing retransmission demand as SNR rises. This is intentionally not a standards HARQ implementation.

### Mixed control and inference traffic
One wireless action per slot is shared by unstable-plant feedback and deadline-limited inference jobs. The experiment exposes why control-first, inference-first, and age-only scheduling are structurally incomplete when services have different downstream value functions. Task-value scheduling offers a controllable compromise but can still sacrifice physical-control quality under heavy inference load.

### Correlated failure domains
The model-replication experiment groups edge nodes into common failure domains. Placement based only on independent node reliability may place multiple copies behind the same site/rack/power failure. Domain-aware placement explicitly values failure diversity and sharply reduces task-weighted model outage under fixed storage.

### Stateful service migration
The migration experiment compares full cold state transfer, periodic neighbor checkpoints, and a deliberately simple predictive checkpoint policy. Periodic checkpointing is more robust in the current mobility model; predictive placement saves traffic only when speculation is accurate enough. The retained negative result prevents mobility prediction from being treated as free performance.

### Safety-value precision allocation
A three-component plant shares a hard state-communication bit budget. All components first receive coarse observability; remaining bits can refine high-risk components. Under poor channels, broad low-precision observability is more important than precision concentration. Once packet deliverability improves, risk-aware refinement becomes useful, creating a channel-dependent crossover.

## v3.2 Predictive-Resilience Main Line

### 109. Predictive failure migration under noisy degradation forecasts
Four synthetic edge nodes evolve through slowly varying latent degradation states and occasional shocks. Sticky execution, reactive post-failure migration, and predictive-risk migration share the same exogenous traces for a given seed. Predictive migration observes only a noisy one-step failure-risk estimate and pays an explicit state-transfer and latency cost whenever it moves. The key result is a forecast-quality crossover: low-noise prediction reduces failure exposure and mean latency, but noisy prediction creates false-positive migrations, increasing both traffic and P95 latency. This separates the value of failure prediction from the cost of acting on an unreliable forecast.

### 110. Failure-domain diversity under shared zone failures
The correlated-replication model is extended with a controllable shared zone-failure probability. Popularity and criticality placement may add several replicas while still concentrating them in too few failure domains. Diversity-risk placement explicitly values a new domain. At 10% zone-failure probability in the supplied 2.8 GB storage setting, it cuts task-weighted outage to about 3.55% versus roughly 8–9% for the non-diversity baselines, despite using a lower mean replication factor. The experiment is a direct counterexample to using replica count as a reliability metric.

### 111. Chance-constrained real-time inference admission
Synthetic inference tasks have a predicted mean edge latency and a jitter-dependent completion-time standard deviation. Mean-latency admission accepts an offload whenever expected latency fits the deadline. Chance-constrained admission requires the modeled probability of on-time completion to exceed 99%; rejected tasks execute a lower-utility local fallback. Raw utility, on-time utility, admission rate, and admitted deadline misses are reported simultaneously. As jitter grows, the chance policy preserves the deadline tail by becoming more selective, making the reliability/utility price explicit.

### 112. Unequal error protection for control-state components
A three-component unstable state is transmitted under a fixed budget of five repetitions per slot. Equal protection rotates two extra repetitions across components; critical UEP always assigns three repetitions to the most control-sensitive component. The controller predicts missing components. At low SNR, critical-component misses dominate downstream cost and UEP provides a large gain. At high SNR, one-shot delivery becomes reliable and both policies converge. The result therefore supports UEP only in a communication-limited operating region rather than as a universal control-coding rule.

### 113. Correlation-aware multi-connectivity reliability
Single-link, full dual-link duplication, and adaptive duplication share the same synthetic channel trace. A common-randomness mixture controls link-failure correlation. The adaptive policy uses pre-transmission link-quality estimates, not realized packet outcomes, and duplicates packets with the largest expected secondary-link rescue value. Full duplication gains strongly when failures are independent but loses diversity as correlation approaches one. Adaptive duplication uses about 1.73 transmissions/packet in the baseline stress regime and remains close to full duplication while saving radio resources.

### 114. Multi-connectivity coupled to safety-aware networked control
The dual-link abstraction is connected directly to the v3.1 safety-control branch. A sensor scheduler selects one plant per slot; single, full-duplicate, and adaptive-duplicate packet delivery then determines whether the remote controller receives the selected state. Adaptive duplication activates for weak predicted primary links or elevated normalized safety proximity. The experiment reports state-bound violation probability and control cost together with radio transmissions per slot. This converts a packet-level reliability technique into an end-to-end safety/resource trade-off and shows that correlation degrades the downstream safety benefit as well as packet diversity.

### v3.2 adaptive duplication frontier
The correlation-aware multi-connectivity baseline now exposes its pre-transmission duplication threshold as an experiment parameter. A separate sweep records packet outage, radio transmissions per packet, duplication rate, and P95 successful-packet latency at low, medium, and high path correlation. This turns the earlier single adaptive operating point into a reliability-resource frontier. The intended interpretation is not that one threshold is optimal globally: as correlation rises, an extra duplicate transmission provides less independent reliability and the frontier flattens. The policy still uses only predicted link-success probabilities before transmission and never inspects the realized packet outcome.

# v3.3 — Unified Resilience-Budget Orchestration

## 115. Cross-layer resilience-credit model
v3.3 places proactive service migration, cross-failure-domain replica execution, and dual-link packet duplication behind one normalized token-bucket budget. The normalization is a policy scarcity mechanism only; radio transmissions, replica executions, and migration traffic are still reported in their native proxy units. This avoids the stronger and unjustified claim that heterogeneous resources have a deployment-independent physical exchange rate.

The runtime observes noisy edge-risk forecasts, task criticality/deadline class, pre-transmission quality estimates for two radio paths, configured path correlation, and current credit state. It never sees realized packet or node failures before deciding. A common reactive recovery path remains available after a primary-edge failure and is accounted separately from proactive credit spending.

## 116. Budget sweep and diminishing returns
In the supplied mixed regime, increasing the proactive budget strongly reduces task-weighted deadline misses from roughly 22.2% with no proactive credits to about 12.3% at 0.6 credit/task and 9.6% at 1.0 credit/task. The resource mix changes as the cheap radio action saturates: replicas become common only after larger budgets are available. At still larger budgets, extra spending increasingly appears as replicas and speculative migration rather than proportional reliability gain.

## 117. Failure-mode-dependent mechanism selection
A deliberately separated regime sweep tests whether the same policy can recognize which layer is limiting reliability. In the radio-limited case the risk-budget controller spends almost entirely on duplication. When the radio is already strong but edge risk is amplified, duplication falls to only a few percent of tasks while cross-domain replica execution exceeds 60%. The experiment therefore turns three component mechanisms into a genuine allocation problem.

## 118. Forecast uncertainty and action confidence
The uncertainty-gated controller distinguishes evidence that the current edge is risky from evidence that another edge is credibly safer. Migration receives a stricter separation requirement than replication because a false migration changes future service affinity and transfers state. Under high forecast noise the gate nearly eliminates proactive migrations and materially reduces migration traffic. At low forecast noise the same caution can reject useful actions and slightly worsen deadline reliability, so confidence gating has a crossover rather than universal dominance.

## 119. Correlation-aware cross-layer reallocation
The radio duplication value calculation explicitly includes the configured common-randomness correlation model. As path correlation approaches one, the estimated rescue value of the secondary link decreases and the risk-budget policy redirects some credits toward edge replicas. Task-weighted deadline reliability still degrades because edge redundancy cannot replace missing radio diversity. This is an important negative systems result: an orchestrator can reallocate scarce resources, but it cannot create independence absent from the underlying failure process.

## 120. Excess-budget saturation
A dedicated high-budget sweep tests the common assumption that additional reliability budget should always be consumed. The ungated policy eventually spends large amounts on migration/replication and enters a saturation region where more budget yields little or no improvement. The uncertainty-gated policy instead plateaus below the available credit ceiling because low-confidence actions fail its value threshold. Leaving budget unused is therefore an explicit valid decision in v3.3.

## 121. Criticality weighting limitation
A task-criticality-weighted risk proxy is compared with the same greedy policy using unit task weights. Their ordering changes across budgets. The result demonstrates that task awareness cannot be reduced to multiplying an incomplete instantaneous failure proxy by a larger scalar. A stronger goal-oriented runtime would need a calibrated model of complete deadline/latency consequence, not merely criticality-weighted component outage reduction.

# v3.5 — Counterfactual Observability and Protected-Outcome Masking

## 122. Action-dependent resilience feedback
The v3.5 paired simulator generates primary and backup radio/edge potential failures before the policy acts. A successful duplicate or replica can convert a hidden base failure into a protected success. This makes the final label depend on the action and exposes why a closed-loop controller can become more confident while underlying components deteriorate.

## 123. Component telemetry and attribution
Delayed primary-component telemetry updates separate radio and edge debts. Under isolated radio drift, it correctly increases duplication and improves weighted reliability. Under isolated edge drift it also correctly shifts toward replicas, yet reliability does not improve in the supplied finite traces. Attribution is therefore evaluated separately from action effectiveness.

## 124. Routine-only safe audits
When component telemetry is unavailable, the hybrid controller may withhold protection from routine tasks and observe an unprotected label. Important and critical tasks are never audited. The audit sweep records the information/resource/class trade-off without claiming causal identification or safe-exploration guarantees.

## 125. Observability under delay and correlation
Component feedback usually crosses the synthetic drift-detection threshold earlier than outcome-only feedback, but task loss is not monotonically better. As radio correlation rises, duplication loses rescue value and the benefit of richer radio health feedback collapses. The limiting factor can be available diversity rather than visibility.

# v3.6 — Safe Offline Counterfactual Reliability Evaluation

## 126. Propensity-logged resilience decisions
Routine and important protection actions are randomized around a risk-based logging rule with a known exploration floor; critical tasks are always protected. Historical records expose only the selected action outcome. Paired potential outcomes are retained behind an evaluation boundary to quantify estimator error without creating online genie information.

## 127. Estimator and overlap diagnostics
DM, IPS, SNIPS, DR, and clipped DR share identical logs. Maximum importance weight, effective sample size, support-violation mass, signed error, empirical absolute error, and approximate intervals are reported together. Low exploration demonstrates that nominal task count can radically overstate effective information.

## 128. Critical-task identification boundary
An unsafe diagnostic target assigns nonzero probability to withholding protection from critical tasks. Since the safe logger never takes that action, the evaluator marks the value non-identifiable. DM and DR still output model extrapolations, which demonstrates why a finite number should not be mistaken for counterfactual evidence.

## 129. Nonstationary log reuse
Full-history evaluation is accurate for its own historical-mixture estimand but can badly underestimate the current final-window risk. Recency restriction reduces temporal bias until its smaller effective sample reintroduces variance. The result is an estimand/recency/variance trade-off, not a universal fixed window.

## 130. Offline policy selection limitation
Greedy selection makes occasional finite-sample mistakes. A deliberately strict conservative heuristic instead retains the baseline across the supplied range. The experiment records both selection regret and fallback frequency, showing that apparent safety can become permanent inaction when uncertainty bounds are weak or miscalibrated.

# v3.7 — Propensity Uncertainty and Confounding Stress Tests

## 131. Uncertain logging propensities
v3.7 separates six behavior-propensity sources: hidden synthetic truth, current nominal records, stale records, in-sample estimation, cross-fitted estimation, and a misspecified reduced model. Each source feeds the same IPS/SNIPS/DR family so evaluation changes can be attributed to the logging model rather than a new outcome generator.

## 132. Observable drift versus hidden confounding
A time-varying observed drift term changes the logging rule and can be learned from risk, uncertainty, class, and time features. A separate autocorrelated severity variable affects both action and outcome but is never observed by nuisance models. Updating the propensity model helps with the first mechanism and cannot identify the second.

## 133. Cross-fitting finite-sample limitation
Five-fold propensity prediction prevents a row from helping fit its own behavior score. In this low-dimensional synthetic setting, the price of using fewer nuisance-training samples often exceeds any reuse benefit: small-sample cross-fitted weights are larger and point error is not consistently lower. The result is retained to distinguish cross-fitting discipline from automatic improvement.

## 134. Odds-envelope sensitivity diagnostic
The evaluator perturbs each used propensity through a symmetric odds factor and recomputes pessimistic and optimistic empirical corrections. Larger gamma rapidly widens the interval. Aggregate paired-oracle coverage can occur at a gamma far below the maximum hidden row-wise true-versus-used odds gap, so both diagnostics are reported separately.

## 135. Robust-selection fallback
The sensitivity selector requires a candidate's pessimistic objective to beat the baseline's optimistic objective. Under the supplied envelope this rule avoids some confounded point-selection regret but never authorizes an update. Baseline fallback is an explicit cost, not proof of successful safe improvement.
