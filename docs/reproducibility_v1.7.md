# CommLab v1.7 Reproducibility

## Environment

- Python >= 3.10
- NumPy / SciPy / Matplotlib
- pytest for regression validation
- pandas is used by experiment scripts and the optional Streamlit dashboard environment

## Install and validate

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v17_suite.py
python tools/build_results_manifest_v17.py
python tools/verify_release_v17.py
```

## Determinism

The v1.7 experiments use explicit NumPy random seeds. Policy comparisons that are intended to isolate an algorithmic choice reuse the same geometry/channel/arrival traces wherever practical:

- asynchronous CSI policies reuse the same geometry and channel seed for each update budget;
- IR and Chase HARQ use the same SNR and packet-arrival traces;
- predictive CSI coding compares absolute and innovation quantization on the same evolving channel;
- queue-aware ISAC policies reuse the same arrival, process-noise, and user-rate traces.

## Statistical interpretation

The experiments are finite Monte Carlo studies, not standards conformance tests. Headline zero-drop or zero-error observations mean no event was observed in the finite run; they are not mathematical zero probabilities.

## Result integrity

`results/manifest_v1.7.json` records SHA-256 hashes for every CSV dataset and PNG figure in the release. `tools/verify_release_v17.py` recomputes those hashes and checks required release documents.
