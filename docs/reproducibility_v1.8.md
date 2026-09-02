# Reproducibility — CommLab v1.8

## Environment

Recommended Python: 3.10–3.12.

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v18_suite.py
python tools/build_results_manifest_v18.py
python tools/verify_release_v18.py
```

Expected regression result:

```text
145 passed
```

## Determinism

All new v1.8 Monte Carlo experiments use fixed NumPy seeds. The release manifest stores SHA-256 hashes for every CSV and PNG in `results/data/` and `results/figures/`.

## New v1.8 experiment scripts

- `joint_csi_fronthaul_control.py`
- `deadline_harq_scheduling.py`
- `aoi_status_updates.py`
- `event_triggered_ris.py`
- `budget_constrained_isac.py`
- `grant_free_noma_random_access.py`

## Important reproducibility note

The first joint-CSI exploratory run exposed a duplicate-selection defect in the round-robin baseline at high refresh budgets. The defect was fixed, a regression test was added, and the exploratory result files were overwritten by a clean deterministic rerun. The final v1.8 manifest therefore contains only corrected results.

## Interpretation limits

- finite-blocklength results use the normal approximation rather than a code-specific standards decoder;
- AoI channels use a compact block reliability abstraction;
- event-triggered RIS uses current-rate probes and idealized phase updates;
- budgeted ISAC uses a transparent online token/dual heuristic;
- grant-free NOMA assumes perfect activity knowledge and perfect SIC cancellation after a successful layer.
