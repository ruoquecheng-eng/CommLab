# Reproducibility — v2.5

From the repository root:

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v25_suite.py
python tools/build_results_manifest_v25.py
python tools/verify_release_v25.py
python -m compileall -q src app experiments tools
```

The v2.5 experiment suite explicitly inserts the current release `src/` directory into child-process `PYTHONPATH` so that a stale editable install cannot silently run an older package. Final release validation separately installs package version 2.5.0 and reruns the full tests without a manually supplied source path.

All Monte Carlo scripts use fixed seeds. Numerical results are simulation outcomes for the documented normalized models, not measurements from calibrated radios or production edge devices.
