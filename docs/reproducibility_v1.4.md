# Reproducibility — v1.4

## Local validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v14_suite.py
python tools/build_results_manifest_v14.py
python tools/verify_release_v14.py
```

The v1.4 scripts use fixed NumPy random seeds. CSV datasets and PNG figures are generated under `results/data` and `results/figures`. `results/manifest_v1.4.json` stores SHA-256 hashes so the release verifier can detect post-generation changes.

The simulations are normalized research/education models. Reproducibility means the repository regenerates the stated numerical experiments under its explicit assumptions; it does not imply real-RF calibration or standards conformance.
