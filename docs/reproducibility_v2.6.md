# CommLab v2.6 — Reproducibility

## Environment

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v26_suite.py
python tools/build_results_manifest_v26.py
python tools/verify_release_v26.py
```

The v2.6 experiments use deterministic NumPy seeds, write their numerical outputs to `results/data/`, and write figures to `results/figures/`. The release manifest records SHA-256 hashes for every CSV and PNG result artifact.

## v2.6 experiment scripts

- `experiments/v26_aircomp_selection.py`
- `experiments/v26_progressive_split.py`
- `experiments/v26_downlink_differential.py`
- `experiments/v26_eh_aircomp_fl.py`
- `experiments/v26_importance_multicast.py`

## Methodological notes

- The AirComp selection experiment separately records analog distortion relative to the selected-client mean and statistical bias relative to the all-client mean.
- The split-inference experiment counts correct results that exceed the deadline as late, not as on-time task successes.
- Differential downlink schemes are evaluated on the same server-model trajectory and client SNR realizations within a fixed seed.
- Importance-aware multicast reports both utility and airtime; utility improvement is never described as free.
- All energy, model-bit and latency quantities in these new system-level abstractions are normalized/educational unless explicitly labeled otherwise.
