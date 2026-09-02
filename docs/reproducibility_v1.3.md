# Reproducibility — v1.3

## Environment
- Python >= 3.10
- NumPy, SciPy, Matplotlib
- pytest for validation
- Streamlit/Pandas optional for the dashboard

## Validation commands
```bash
python -m pip install -e . --no-build-isolation
pytest -q
PYTHONPATH=src python experiments/run_v13_suite.py
python tools/build_results_manifest_v13.py
python tools/verify_release_v13.py
```

## Determinism
Every v1.3 Monte Carlo experiment uses an explicit NumPy random seed. The release manifest records SHA-256 hashes for every CSV and PNG artifact.

## Important modeling assumptions
- Cell-Free uses normalized geometry/pathloss + Rayleigh fading and perfect instantaneous CSI for beam construction.
- AP-user service-link count is a coordination/fronthaul *proxy*, not a byte-level network-load model.
- Max-min power control optimizes user powers for fixed MRT directions.
- RIS coordinate optimization is discrete local search and recomputes digital precoding after each candidate phase update.
- Predictive beam tracking uses synthetic angle measurements and ideal ULA response.
- Uncertainty-aware aperture selection assumes Gaussian pointing error and array peak SNR proportional to active element count.
