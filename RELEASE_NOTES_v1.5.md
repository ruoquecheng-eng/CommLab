# CommLab v1.5 Release Notes

v1.5 shifts the platform from adding isolated PHY algorithms toward coupling **distributed CSI overhead, uncertainty, finite blocklength, and sensing resource allocation**.

## New modules

- `commlab.mimo.fronthaul`
  - adaptive-range complex CSI scalar quantization;
  - quantization NMSE;
  - abstract CSI-fronthaul bit accounting;
  - proper-complex Gauss-Markov channel aging.
- `commlab.ris.robust`
  - channel uncertainty perturbation;
  - sample-average robust finite-bit Cell-Free RIS coordinate ascent.
- `commlab.information_theory.finite_blocklength`
  - inverse normal approximation for packet-error probability at fixed rate/blocklength.
- `commlab.scheduling.short_packet`
  - finite-blocklength-aware adaptive short-packet goodput model;
  - optional OLLA correction for biased SNR estimates.
- `commlab.sensing.resource_scheduling`
  - sensing-overhead-to-angle-uncertainty fusion;
  - joint sensing-fraction / active-aperture search.

## New v1.5 experiments

1. `cell_free_fronthaul_csi.py`
2. `cell_free_csi_aging.py`
3. `cellfree_ris_robust_imperfect_csi.py`
4. `short_packet_fbl_cross_layer.py`
5. `isac_sensing_resource_scheduling.py`

## Headline observations

- CSI quality improves sharply from 2/3-bit to 4/6-bit scalar feedback, but fronthaul grows linearly with the number of AP-user links and quantization bits.
- Slower CSI refresh is inexpensive under slowly varying channels but causes substantial cell-edge loss under faster channel aging.
- Sample-average RIS design becomes useful once CSI uncertainty is material; at low uncertainty it may lose slightly to the single-estimate optimizer, which is retained as a non-universal-result counterexample.
- Finite-blocklength-aware MCS selection pays an explicit spectral-efficiency cost and therefore does not receive "free reliability"; OLLA can correct persistent SNR-estimation bias and operate near a target NACK rate.
- Extra sensing is not always useful. With accurate angle prior the throughput optimum spends no extra resource on sensing; increasing uncertainty causes the optimum to allocate sensing time and reduce active aperture.

## Validation

- **116/116 tests passed**
- **94 CSV datasets**
- **160 figures**
- **254 result artifacts** in the v1.5 SHA-256 manifest
- package version **1.5.0**
