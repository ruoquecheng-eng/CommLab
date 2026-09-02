# Reproducibility — v3.0

Recommended commands from the repository root:

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v30_suite.py
python tools/build_results_manifest_v30.py
python tools/verify_release_v30.py
python -m compileall -q src app experiments tools
```

The v3.0 experiment suite launches the five new experiments in independent subprocesses with separate Matplotlib cache directories. Seeds are fixed by each experiment; CSV and PNG outputs are hashed in `results/manifest_v3.0.json`.

Important interpretation rule: several v3.0 policies are intentionally regime dependent. Reproduction should preserve negative/crossover regions rather than tuning parameters until the newest policy dominates every baseline.
