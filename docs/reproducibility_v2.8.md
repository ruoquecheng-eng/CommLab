# Reproducibility — v2.8

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
```

The release must also pass pytest after clearing `PYTHONPATH`, so successful validation cannot rely on an older source tree being imported accidentally.

## New v2.8 experiments

```bash
python experiments/run_v28_suite.py
```

The suite runs independent experiment scripts in parallel with separate Matplotlib cache directories:
- `v28_selective_downlink_repair.py`
- `v28_versioned_caching.py`
- `v28_fair_carbon_orchestration.py`
- `v28_split_admission.py`
- `v28_digital_twin_sync.py`

All random experiments use explicit NumPy seeds and aggregate multiple independent seeds in the published CSVs.

## Artifact verification

```bash
python tools/build_results_manifest_v28.py
python tools/verify_release_v28.py
```

The manifest hashes every CSV dataset and PNG result figure using SHA-256. Release verification checks both hashes and required v2.8 documentation files.

## Interpretation constraints
- Digital-twin dynamics are a 1-D linear state model with synthetic maneuvers.
- Carbon is a modeled operational proxy, not audited emissions accounting.
- Model versions, task utilities, and cache refresh traffic are synthetic edge-inference abstractions.
- Selective repair and admission controllers are transparent heuristics, not globally optimal policies.
