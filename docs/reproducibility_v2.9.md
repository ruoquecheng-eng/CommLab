# Reproducibility — CommLab v2.9

## Environment
The release uses NumPy/Matplotlib/PyTest plus the existing optional Streamlit front end. All v2.9 experiments use explicit deterministic seeds and write only to unique v2.9 CSV/PNG paths.

## Install and regression
```bash
python -m pip install -e . --no-build-isolation
pytest -q
```
Expected: **207 passed**.

## Reproduce v2.9 experiments
```bash
python experiments/run_v29_suite.py
```
The suite runs the five v2.9 experiments in isolated subprocesses with independent Matplotlib cache directories. It is intentionally configured to complete as a single command in the release environment.

Individual scripts:
```bash
python experiments/v29_task_aware_repair.py
python experiments/v29_congested_model_refresh.py
python experiments/v29_battery_carbon_fair_fl.py
python experiments/v29_twin_guided_prefetch.py
python experiments/v29_networked_control.py
```

## Result integrity
```bash
python tools/build_results_manifest_v29.py
python tools/verify_release_v29.py
```
The manifest records SHA-256 for every CSV dataset and PNG figure in `results/`.

## Methodological controls added in v2.9
- All three task-repair policies use nearly the same long-run downlink load.
- Refresh jobs update a cached version only after queued bytes are actually served; enqueueing a refresh is not counted as freshness.
- FL client selection is restricted by battery energy causality before scores are ranked.
- Digital-twin uncertainty can change both the predicted transition direction and prefetch confidence; the predictor no longer has access to the true transition direction.
- Networked-control scheduling is evaluated by physical stage cost as well as information age, preventing a freshness-only conclusion.

## Known limitations
- Synthetic workloads and linear/quadratic learning/control models are used for interpretability.
- Model transfer sizes and carbon values are normalized engineering proxies.
- Digital-twin transition inference is not learned from a real physical asset.
- Networked control uses scalar linear plants, fixed feedback gains, and small sensor-side trigger metadata.
