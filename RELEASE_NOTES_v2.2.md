# CommLab v2.2 Release Notes

v2.2 extends the Wireless Edge Intelligence branch from selection/task conflict into **communication-budget allocation, hardware-realistic analog aggregation, progressive task representations, MAC-level update importance, and slow/fast control coupling**.

## New modules

- `computation/gradient_compression.py`
  - deterministic top-k gradient sparsification;
  - error-feedback residual accumulation;
  - fixed coordinate-budget FL with client-count/compression trade-offs;
  - residual-aware integer coordinate allocation across selected clients.
- `computation/aircomp_hardware.py`
  - full-inversion AirComp with transmit magnitude clipping;
  - finite-resolution I/Q ADC;
  - per-vector receiver AGC and overload accounting.
- `computation/layered_semantic.py`
  - two-task Gaussian task-oriented representation;
  - rank-one base layer plus orthogonal enhancement layer;
  - confidence-triggered variable-length transmission.
- `computation/importance_random_access.py`
  - IRSA-style iterative singleton peeling;
  - uniform versus gradient-importance repetition degrees;
  - decoded gradient-mass metric in addition to decoded-client fraction.
- `computation/timescale_ris_fl.py`
  - Gauss-Markov direct/RIS channel evolution;
  - finite-bit max-min RIS updates on a slower timescale than FL rounds;
  - AirComp learning loss, weakest-device gain, and RIS control-bit accounting.

## New experiments

- `v22_budgeted_gradient_compression.py`
- `v22_aircomp_hardware.py`
- `v22_layered_semantic.py`
- `v22_importance_random_access_fl.py`
- `v22_two_timescale_ris_fl.py`

## Selected results

### Fixed communication budget: participation versus compression

With 12 non-IID clients, 32 model coordinates, and a nominal budget of 32 transmitted coordinates per round:

- selecting one client permits a dense 32-coordinate update but gives mean parameter error about **0.249**;
- with error feedback, selecting 3-4 clients and sending roughly 8-10 coordinates/client reduces error to about **0.081-0.083**;
- selecting all 12 clients with equal 2-coordinate top-k updates raises error to about **0.116**;
- residual-aware allocation reduces the 12-client point to about **0.083**, showing that communication budget should not necessarily be split uniformly.

Without error feedback, aggressive sparsification degrades rapidly: the 12-client point reaches about **0.654** parameter error. The result exposes an interior client-diversity/compression operating region rather than monotonic benefit from more participants.

### AirComp hardware dynamic range

For 16-device AirComp at 24 dB with mild PA clipping:

- 3-bit ADC without AGC: median aggregation MSE about **8.54e-3**;
- 3-bit ADC with AGC: about **3.54e-3**;
- 6-bit with AGC: about **2.48e-4**;
- 8-bit with AGC: about **1.96e-4**.

The no-AGC runs overload roughly **24%** of I/Q samples in this normalized model, while AGC reduces overload to about **0.1%**. Beyond roughly 6 bits, the curve approaches the analog/noise floor rather than continuing to improve at the same rate.

Transmit clipping produces an independent floor: reducing normalized PA saturation from 3.0 to 0.7 raises median MSE from about **5.5e-5** to **2.50e-3**.

### Progressive task-oriented representation

At 10 dB and 60-degree task separation:

- one base semantic layer: about **81.1%** mean two-task accuracy at 1 channel use;
- confidence-adaptive enhancement: about **88.9%** using **1.42** uses/sample on average;
- always transmitting both layers: about **90.3%** at 2 uses.

When the task directions become orthogonal, the adaptive controller requests the second layer for all samples and becomes the full two-layer scheme. The model therefore exposes a progressive semantic-rate trade-off without a learned codec.

### Importance-aware random access for FL

The importance policy maps gradient-norm ranks to repetition degrees 2/3/4 while preserving an average repetition degree near 3. At 18 shared slots/round:

- uniform repetition decodes about **51.9%** of active clients and **51.9%** of gradient-norm mass;
- importance-aware repetition decodes about **60.7%** of clients and **61.4%** of gradient mass.

At severe overload (10 slots), both policies remain poor; priority repetition does not remove the random-access threshold. The experiment therefore studies which updates survive contention, not only packet count.

### Two-timescale RIS-AirComp-FL

For slowly varying channels (`rho=.995`), updating a 10-element 2-bit RIS every 4 FL rounds reduces control load from **20** to about **5.14 bit/round** while median final learning loss remains essentially unchanged (`0.02068 -> 0.02074`).

As temporal correlation falls, stale passive control becomes more costly. At `rho=.95`, the weakest-device gain drops from about **0.272** with per-round RIS updates to about **0.189** at a 4-round interval, and longer update intervals further degrade the AirComp bottleneck and learning robustness.

## Dashboard

New interactive labs:

- Budgeted Gradient FL
- AirComp Hardware
- Layered Semantic
- Importance Random-Access FL
- Two-timescale RIS FL

## Validation

v2.2 is validated with the full historical regression suite plus deterministic v2.2 experiments, environment-independent editable installation, source/Dashboard compilation, result-manifest verification, and ZIP integrity checks. See `docs/reproducibility_v2.2.md`.
