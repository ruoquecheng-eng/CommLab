# CommLab v3.3 Reproducibility

## Environment

- Python >= 3.10
- NumPy
- SciPy
- Matplotlib
- pytest
- Streamlit only for the optional Dashboard

## Determinism

Every v3.3 experiment calls the simulator with explicit integer seeds. Policies compared within the same `(seed, SNR, edge-risk, forecast-noise, correlation)` configuration regenerate the same exogenous degradation, task-class, radio, and failure distributions from the same root seed. Decisions then alter service affinity and resource usage, so later *policy state* can diverge, but the stochastic environment generator itself is not reseeded to favor a policy.

No seed was replaced because a curve looked unattractive. The high-budget saturation and task-weighting mixed result are intentionally retained.

## Reproduce v3.3 experiments

```bash
python -m pip install -e . --no-build-isolation
python tools/run_v33_suite.py
pytest -q
python -m compileall -q src app experiments tools
python tools/build_manifest_v33.py
python tools/verify_release_v33.py
```

## Interpretation

The v3.3 experiments are finite Monte Carlo studies. Reported percentages are empirical frequencies, not analytical guarantees. The resilience-credit scale is a synthetic scarcity/accounting mechanism and should not be interpreted as an energy unit.
