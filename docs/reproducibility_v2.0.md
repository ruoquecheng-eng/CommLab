# Reproducibility — v2.0

All new v2.0 experiments use explicit random seeds and export CSV plus PNG results.

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v20_suite.py
python tools/build_results_manifest_v20.py
python tools/verify_release_v20.py
```

The v2.0 algorithms are intentionally transparent baselines. Monte Carlo values are not hardware measurements. Analog AirComp assumes timing/frequency alignment; Cell-Free AirComp assumes coherent centralized reception; RIS channels are normalized synthetic channels; the task-oriented experiment uses a known sufficient statistic rather than a learned semantic encoder.
