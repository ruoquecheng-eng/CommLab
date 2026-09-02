# Reproducibility — v1.6

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v16_suite.py
python tools/build_results_manifest_v16.py
python tools/verify_release_v16.py
```

Expected regression status: **124 passed**.

## Determinism
The v1.6 experiment scripts use explicit NumPy RNG seeds. The RIS CSI-bit experiment reuses identical stale/current channel realizations and frozen random seeds across all bit depths; the first draft did not do this and was discarded because it confounded CSI precision with Monte Carlo sampling.

## Generated outputs
v1.6 brings the full release to **100 CSV files and 172 figures**. Every file under `results/data` and `results/figures` is hashed in `results/manifest_v1.6.json`.

## Modeling boundaries
- Delayed RIS CSI uses a Gauss-Markov correlation abstraction rather than a geometry/Jakes Doppler model.
- Sample-average robust RIS is a finite coordinate-search heuristic, not global stochastic optimization.
- FBL HARQ uses Chase SNR combining and the AWGN normal approximation, not standards rate matching or a particular decoder curve.
- Predictive sensing uses a two-step covariance/value-of-information heuristic; it is not a POMDP/RL optimum.
- Fronthaul power is an explicit energy-per-CSI-bit abstraction, not a measured optical/wireless fronthaul implementation.
