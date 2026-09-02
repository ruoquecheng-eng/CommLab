# CommLab v2.0 Release Notes

v2.0 is a milestone release that adds a **Wireless Edge Intelligence / Task-Oriented Communications** layer to the existing wireless-systems laboratory.

## Added

- Federated linear-regression training with noisy analog AirComp gradient aggregation and explicit modeled channel-use accounting.
- Full-inversion versus truncated-inversion FL, including threshold/participation studies.
- RIS-assisted AirComp with finite-bit coordinate optimization for total channel power versus weakest-device gain.
- FL convergence under fixed RIS-shaped AirComp channels.
- Cell-Free AirComp with centralized candidate-search receive combining.
- A controlled task-oriented classification baseline that uses one analytically sufficient scalar instead of a full source vector.
- Capture-aware IRSA with power-domain SINR decoding and iterative replica cancellation.
- Five corresponding Streamlit labs and a deterministic v2.0 experiment suite.

## Representative results

- 12-client FL, 80 rounds, 10 dB: orthogonal upload uses 960 modeled channel uses and finishes near global loss 0.0476; full-inversion AirComp uses 80 and finishes near 0.0205; ideal aggregation is near 0.0201.
- 2-bit RIS on the fixed AirComp channel: max-min weakest gain ~0.226 versus sum-gain ~0.146, with lower aggregation MSE and better FL convergence.
- 8-AP Cell-Free AirComp: median aggregation MSE ~4.65e-4 versus ~1.05e-3 for best-single-AP reception.
- 20 dB task-oriented toy problem: one scalar channel use gives ~97.6% classification accuracy versus ~97.8% for 16 transmitted source dimensions, while source reconstruction remains much worse.
- Capture-aware IRSA reaches ~0.762 packet/slot in the tested 9 dB received-power-spread regime before overloading causes collapse.

## Validation

Run:

```bash
python -m pip install -e . --no-build-isolation
pytest -q
python experiments/run_v20_suite.py
python tools/build_results_manifest_v20.py
python tools/verify_release_v20.py
```

## Release inventory

- 154/154 automated tests passing.
- 122 CSV datasets.
- 213 figures.
- 335 result artifacts verified by SHA-256 manifest.
