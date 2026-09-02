# Reproducibility — CommLab v1.9

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
```

The project targets Python 3.10+ with NumPy, SciPy and Matplotlib. Streamlit/Pandas are optional dashboard dependencies.

## New experiment suite

```bash
python experiments/run_v19_suite.py
```

This executes:

1. `irsa_coded_random_access.py`
2. `aircomp_aggregation.py`
3. `embb_urllc_slicing.py`
4. `energy_harvesting_aoi.py`

Every new Monte Carlo script uses explicit NumPy random seeds. CSV data are written under `results/data/` and figures under `results/figures/`.

## AirComp heavy tails

Full channel inversion and orthogonal ZF over Rayleigh fading are sensitive to rare near-zero channel magnitudes. v1.9 therefore stores mean MSE but uses **median MSE** for the main SNR plot and also records the full-inversion p90 MSE. This is intentional and should not be replaced by a cherry-picked seed merely to force a monotonic sample mean.

## Release validation

The v1.9 manifest hashes every CSV and PNG result. `tools/verify_release_v19.py` recomputes those SHA-256 values and checks required release documents.
