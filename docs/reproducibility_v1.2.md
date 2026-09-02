# Reproducibility — v1.2

## Environment
The repository is a pure-Python simulation project. The v1.2 validation sequence is:

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v12_suite.py
python tools/build_results_manifest_v12.py
python tools/verify_release_v12.py
```

The current v1.2 branch uses deterministic RNG seeds inside the new experiment scripts.

## New v1.2 experiment scripts
- `experiments/ris_phase_quantization.py`
- `experiments/mu_mimo_user_selection.py`
- `experiments/music_mdl_model_order.py`
- `experiments/isac_multitarget_kalman.py`
- `experiments/hybrid_omp_precoding.py`

## Interpretation boundaries
The RIS, mmWave, ISAC and MU-MIMO experiments are normalized synthetic models. They are intended to make algorithmic structure and trade-offs reproducible, not to substitute for calibrated RF/OTA measurements or standards-conformance simulation.
