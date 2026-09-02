# CommLab v3.5 Reproducibility

## Deterministic paired paths

Every formal sweep uses explicit seeds. Same-seed policies receive the same task classes, drifting latent radio/edge states, primary/backup outcome uniforms, telemetry availability, audit draws, and tail failures. Decisions never read the realized current outcome.

## Commands

```bash
python -m pip install -e . --no-build-isolation
python tools/run_v35_suite.py
python -m pytest -q
python -m compileall -q src app experiments tools
python tools/build_manifest_v35.py
python tools/verify_release_v35.py
```

Full acceptance:

```bash
python tools/run_release_acceptance_v35.py
```

Percentages are finite Monte Carlo estimates. Negative and non-monotone points are retained without seed replacement. Hidden unprotected outcomes are evaluation-only unless an explicit audit reveals them.
