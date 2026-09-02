# v2.4 Reproducibility

## Install and test

```bash
python -m pip install -e . --no-build-isolation
python -m pytest -q
```

## New experiment suite

```bash
python experiments/run_v24_suite.py
```

The suite injects this release's local `src/` path into every experiment subprocess so an older editable installation cannot silently satisfy imports during development. Release validation separately installs package version 2.4.0 and reruns the complete test suite without a manually set `PYTHONPATH`.

## Determinism

All new experiments use explicit NumPy seed schedules. Within each comparison, policies are evaluated over matched problem families whenever the simulator permits it. CSV results are produced before figures.

## Release verification

`tools/build_manifest_v24.py` hashes every CSV and PNG under `results/`. `tools/verify_release_v24.py` recomputes those hashes and verifies required v2.4 documentation.

## Modeling limits

- Personalized learning uses ridge regression with finite local samples.
- MDS recovery is an order-statistics abstraction for coded computation.
- Distillation uses linear teachers/students and shared public probes.
- Split inference uses normalized communication and compute latency.
- OTA sign aggregation assumes synchronous sign symbols and ideal superposition apart from AWGN/sign flips.
