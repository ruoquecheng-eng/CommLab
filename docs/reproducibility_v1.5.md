# Reproducibility — v1.5

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v15_suite.py
python tools/build_results_manifest_v15.py
python tools/verify_release_v15.py
```

Expected regression status: **116 passed**.

## Determinism
The v1.5 experiment scripts use explicit NumPy RNG seeds. Cell-Free CSI quantization uses the same pre-generated channel realizations across feedback-bit settings so bit-resolution comparisons are paired rather than independent Monte Carlo samples.

## Generated outputs
v1.5 adds six CSV datasets and twelve figures. The full release contains **94 CSV files and 160 figures**. Every file in `results/data` and `results/figures` is hashed in `results/manifest_v1.5.json`.

## Modeling boundaries
- CSI-fronthaul bits are abstract coefficient payload counts; protocol headers, entropy coding and transport latency are not modeled.
- Gauss-Markov aging is a normalized fading process, not a standardized Doppler spectrum.
- Robust RIS uses a small sample-average uncertainty ensemble and finite coordinate search, not stochastic global optimization.
- Finite-blocklength BLER uses the normal approximation, not a particular LDPC/polar decoder curve.
- Sensing-resource scheduling uses a scalar angle-uncertainty fusion model and expected ULA rate, not a full radar resource grid.
