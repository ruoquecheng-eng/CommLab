# CommLab v2.7 — Reproducibility

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v27_suite.py
python tools/build_results_manifest_v27.py
python tools/verify_release_v27.py
```

All v2.7 experiments use deterministic NumPy seeds and write numerical data to `results/data/` and figures to `results/figures/`. The release manifest stores SHA-256 hashes for every CSV and PNG result artifact.

## v2.7 experiment scripts

- `experiments/v27_adaptive_downlink.py`
- `experiments/v27_carbon_federated.py`
- `experiments/v27_edge_caching.py`
- `experiments/v27_queued_split.py`
- `experiments/v27_multicast_repair.py`

## Methodological notes

- Fixed and budgeted-age downlink controllers are compared at nearly identical average normalized payload in the main sweep; the adaptive result is not attributed to extra airtime.
- Carbon-aware FL deliberately correlates regional carbon intensity with data-group identity so carbon-only client selection can expose selection bias rather than receiving a free environmental win.
- Edge caching charges newly loaded models to backhaul traffic; LRU therefore cannot hide cache churn behind hit-rate metrics.
- Queue inference treats deadline-expired predictions as unusable for on-time task utility even if they would be correct offline.
- Multicast repair reports both task utility and airtime ratio; selective-repair utility gains are never presented as free.
