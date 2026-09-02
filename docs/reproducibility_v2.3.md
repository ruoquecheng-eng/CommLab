# v2.3 Reproducibility

## Environment

Install from the release root:

```bash
python -m pip install -e . --no-build-isolation
python -m pytest -q
```

The v2.3 experiment suite forces subprocesses to import this release's local `src/` tree so an older editable install cannot create a false-positive experiment run:

```bash
python experiments/run_v23_suite.py
```

## Determinism

All v2.3 Monte Carlo scripts use fixed explicit NumPy seeds. Comparisons within a sweep use controlled seed schedules so methods see matched problem families. CSV files are written before plots are generated.

## Release verification

`tools/verify_release_v23.py` recomputes SHA-256 for every CSV/PNG entry in `results/manifest_v2.3.json` and checks required release documentation.

## Known modeling limits

- Convex linear/ridge regression is used for transparent FL experiments.
- Attack models are deliberately simple and do not cover adaptive omniscient adversaries.
- Privacy noise is not converted into epsilon/delta.
- Semantic-task value and split-computing latency are normalized abstractions.
