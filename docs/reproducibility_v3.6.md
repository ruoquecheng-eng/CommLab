# CommLab v3.6 Reproducibility

## Paired logs

Same-seed estimators receive identical contexts, task classes, latent drift, logging propensities, actions, and potential-outcome uniforms. The two potential outcomes are used only to compute an oracle evaluation benchmark after logging; estimators receive only the observed action outcome.

## Commands

```bash
python -m pip install -e . --no-build-isolation
python tools/run_v36_suite.py
python -m pytest -q
python -m compileall -q src app experiments tools
python tools/build_manifest_v36.py
python tools/verify_release_v36.py
```

Full acceptance:

```bash
python tools/run_release_acceptance_v36.py
```

All reported errors are finite Monte Carlo summaries across explicit seeds. Non-monotone estimator and selector points are retained. The oracle is never an input to an estimator or policy decision.
