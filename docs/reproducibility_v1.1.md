# Reproducibility — v1.1

```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v11_suite.py
python tools/build_results_manifest_v11.py
python tools/verify_release_v11.py
```

The v1.1 suite contains only the new v1.1 experiments so it stays below typical single-command execution limits. Earlier release datasets remain in the repository and are included in the result manifest.
