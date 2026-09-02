# Reproducibility — v3.2

## Environment

- Python >= 3.10
- NumPy / SciPy / Matplotlib
- pytest for regression validation
- optional Streamlit + pandas for the interactive Dashboard

## Install and regression

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python -m compileall -q src app experiments tools
```

## Reproduce all v3.2 experiments

```bash
python tools/run_v32_suite.py
```

The suite preserves the five earlier v3.2 experiments and runs the six predictive-resilience/correlation experiments. Each experiment uses fixed NumPy seeds. Policy comparisons intentionally reuse the same seed so exogenous failure, channel, task, or control traces are matched wherever the simulator structure allows it.

## Release-path validation

A formal release additionally clears manually supplied `PYTHONPATH` and checks:

```bash
python - <<'PY'
import importlib.metadata, commlab
print(importlib.metadata.version('commlab-ofdm'))
print(commlab.__version__)
print(commlab.__file__)
PY
PYTHONPATH= pytest -q
```

Both version strings must be `3.2.0`, and `commlab.__file__` must resolve inside the v3.2 release tree.


## One-command release acceptance

```bash
python tools/run_release_acceptance_v32.py
```

This command performs the editable install, all v3.2 experiments, full pytest, version/import-path validation with `PYTHONPATH` removed, a second pytest with `PYTHONPATH` removed, compileall, manifest rebuild, and manifest/release verification. It intentionally runs the experiments in isolated child interpreters so long Matplotlib/NumPy state does not leak between Labs.

## Artifact integrity

```bash
python tools/build_manifest_v32.py
python tools/verify_release_v32.py
```

`results/manifest_v3.2.json` records SHA-256 hashes and file sizes for every CSV dataset and PNG figure. The verifier also checks the required v3.2 release documents.

## Statistical interpretation

These are finite deterministic-seed Monte Carlo experiments, not standards-conformance or safety-certification tests. Zero observed failures in a finite run mean only that no failure occurred in that trace. Crossover locations are empirical for the supplied synthetic parameterization and should not be interpreted as universal thresholds.
