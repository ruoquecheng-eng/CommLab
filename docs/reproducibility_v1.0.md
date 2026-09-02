# Reproducibility — v1.0

## Environment

- Python >= 3.10
- NumPy, SciPy, Matplotlib
- pytest for validation
- optional Streamlit/Pandas for the dashboard

## Validation

```bash
python -m pip install -e . --no-build-isolation
pytest -q
```

Expected v1.0 regression status: **79 passed**.

## New v1.0 experiment suite

```bash
PYTHONPATH=src python experiments/run_v10_suite.py
```

The suite is intentionally computationally heavier than unit tests. In execution environments with per-command time limits, individual experiment scripts can be run separately; their deterministic seeds preserve the same results.

## New v1.0 scripts

- `harq_incremental_redundancy.py`
- `coded_mimo_ldpc.py`
- `otfs_offgrid_refinement.py`
- `olla_link_adaptation.py`
- `ofdm_isac_range_doppler.py`
- `ofdm_isac_cfar.py`
- `full_receiver_impairment_stress.py`

## Artifact verification

```bash
python tools/build_results_manifest_v10.py
python tools/verify_release_v10.py
```

The manifest stores relative paths, byte sizes, CSV schemas/row counts, and SHA-256 hashes for result CSV/PNG artifacts. The verifier recomputes every hash and checks required release documentation.

## Monte Carlo interpretation

- Random seeds are fixed per experiment for deterministic reproduction.
- `0 observed errors` is not treated as a mathematical BER of zero.
- BER experiments use Wilson intervals where implemented.
- Small-sample pedagogical sweeps should be interpreted as controlled demonstrations, not compliance/conformance tests.
