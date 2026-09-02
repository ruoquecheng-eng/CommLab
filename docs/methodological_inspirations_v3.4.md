# Methodological Inspirations — v3.4

v3.4 borrows problem structures, not code or formal guarantees.

- Gibbs and Candès, [Adaptive Conformal Inference Under Distribution Shift](https://proceedings.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html), motivates updating a calibration control variable from online error feedback under changing distributions.
- Gibbs and Candès, [Conformal Inference for Online Prediction with Arbitrary Distribution Shifts](https://jmlr.org/papers/v25/22-1218.html), motivates local-in-time diagnostics rather than only a full-horizon average.
- Angelopoulos et al., [Conformal Risk Control](https://openreview.net/forum?id=33XGfHLtZg), motivates expressing calibration in terms of a user-relevant loss rather than only interval coverage.
- Zecchin and Simeone, [Localized Adaptive Risk Control](https://openreview.net/forum?id=fogJgrozu1), motivates separating risk feedback across operating contexts instead of relying on one global average.
- Lobato et al., [Uncertainty-Aware Pooling of Vehicular Compute at the Edge](https://arxiv.org/abs/2607.17893), motivates comparing calibrated predictive risk, admission/resource cost, and an oracle-style diagnostic in an MEC setting.

CommLab's implementation is independently written. It does not implement the cited algorithms verbatim and does not inherit their assumptions or theorems.
