# Reproducibility — v2.1

All v2.1 experiments use explicit seeds and export CSV plus PNG results.

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v21_suite.py
python tools/build_results_manifest_v21.py
python tools/verify_release_v21.py
```

Important modeling boundaries:

- the non-IID FL experiment intentionally correlates client data group and long-term channel quality;
- random-access FL assumes decoded updates are error-free once the access graph resolves them;
- robust RIS uses sampled CSI perturbations and finite-bit coordinate ascent;
- Cell-Free AirComp tail control uses candidate search and heterogeneous synthetic CSI-error variances;
- the multi-task semantic baseline uses known linear task directions and Gaussian sources.

The v2.1 suite explicitly prepends the current repository `src/` to subprocesses so a stale editable installation cannot cause an older release to be executed accidentally. Final validation should also install 2.1.0 and rerun tests without manual `PYTHONPATH`.
