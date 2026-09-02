# CommLab v3.1 Reproducibility

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
```

The release is also validated after removing manual `PYTHONPATH` overrides so imports resolve through the installed editable distribution.

## Reproduce all v3.1 experiments

```bash
python experiments/run_v31_suite.py
```

The suite launches the five independent v3.1 experiment scripts concurrently. Each child process receives the current release `src/` path explicitly and an independent Matplotlib cache directory, preventing accidental import of an older editable installation and avoiding shared-cache races.

## Rebuild and verify result manifest

```bash
python tools/build_results_manifest_v31.py
python tools/verify_release_v31.py
```

The manifest hashes every CSV dataset and PNG figure in `results/`. Release verification re-hashes every artifact and checks the required v3.1 documentation files.

## Determinism and interpretation

Experiments use explicit NumPy seeds and report Monte Carlo averages where appropriate. Numerical values are properties of the supplied synthetic models, not measurements from production wireless, edge-computing, safety-control, or AI-serving hardware.
