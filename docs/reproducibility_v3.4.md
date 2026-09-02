# CommLab v3.4 Reproducibility

## Environment

Python >= 3.10 with NumPy, SciPy, Matplotlib, and pytest. Streamlit is optional for the Dashboard.

## Determinism and paired paths

Every formal experiment supplies explicit seeds. Same-seed policies regenerate the same class, drift, latent radio/edge, outcome-uniform, and latency-innovation paths. Actions can change service affinity, but no policy is given a favorable reseed. The current outcome becomes feedback only after the configured delay.

## Commands

```bash
python -m pip install -e . --no-build-isolation
python tools/run_v34_suite.py
python -m pytest -q
python -m compileall -q src app experiments tools
python tools/build_manifest_v34.py
python tools/verify_release_v34.py
```

Full release acceptance:

```bash
python tools/run_release_acceptance_v34.py
```

Percentages are finite Monte Carlo estimates, not analytical or conformal guarantees. Negative and non-monotone points are retained without seed replacement.
