# Reproducibility — v0.8

## Environment

- Python >= 3.10
- NumPy, SciPy, Matplotlib
- pytest for automated validation
- Streamlit/Pandas only for the optional interactive dashboard

## Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e .[dev]
```

In an offline environment where build dependencies are already installed, use:

```bash
pip install -e . --no-build-isolation --no-deps
```

## Validate source

```bash
python -m compileall -q src app experiments tools
pytest -q
```

Expected v0.8 result:

```text
66 passed
```

## Reproduce v0.8 experiments

```bash
python experiments/run_v08_suite.py
```

The v0.8 suite contains eight experiment families. On constrained execution environments it can be run one script at a time; the suite itself is simply a checked sequential launcher.

## Artifact integrity

```bash
python tools/build_results_manifest_v08.py
```

The generated `results/manifest_v0.8.json` records SHA-256 hashes for every CSV and PNG result. Current release inventory:

- 45 CSV datasets
- 81 figures

## Randomness

Headline experiments use fixed NumPy random seeds. The seeds are visible in each experiment script. Fixed seeds make regression comparison easier; they do not substitute for larger Monte Carlo studies when estimating very low BER.

## Statistical interpretation

- `0 observed errors` means no errors were seen in that finite sample, not zero underlying probability.
- The dedicated BER confidence experiment uses Wilson intervals and sequential stopping.
- Not every historical experiment has yet been converted to confidence-aware stopping; headline low-BER claims should retain their sample-size context.

## Model-scope warnings

- WLAN-like carrier layout is educational, not standards-compliant Wi-Fi.
- Polar, LDPC, pilot, beamforming-codebook, PF-scheduler, PA, and OTFS branches are project-specific research/teaching baselines unless explicitly stated otherwise.
- Many receiver studies assume known channel/impairment parameters to isolate one algorithmic question; those assumptions are recorded in the corresponding experiment and report section.
