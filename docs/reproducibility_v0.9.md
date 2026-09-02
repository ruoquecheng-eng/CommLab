# Reproducibility — v0.9

## Deterministic structure

All headline v0.9 Monte Carlo scripts use explicit NumPy random seeds. They export machine-readable CSV files to `results/data/` and figures to `results/figures/`. The release manifest stores the SHA-256 and size of every CSV/PNG artifact.

## Unit tests

```bash
PYTHONPATH=src pytest -q
```

Expected release result:

```text
73 passed
```

The v0.9 tests specifically cover:

- exact soft-MIMO LLR hard-decision consistency;
- K-best full-list equivalence to clipped exact max-log LLRs for 2x2 QPSK;
- CRC-16 error detection and Chase LLR accumulation;
- packet/queue scheduler execution;
- noiseless sparse OTFS OMP path recovery;
- noiseless banded ICI-matrix LS recovery;
- finite-blocklength rate convergence toward Shannon capacity.

## Monte Carlo experiments

Run all new v0.9 experiments:

```bash
PYTHONPATH=src python experiments/run_v09_suite.py
```

The HARQ and OTFS studies are intentionally Monte-Carlo heavier than unit tests. For rapid iteration, run scripts individually.

## Manifest and release verification

```bash
python tools/build_results_manifest_v09.py
python tools/verify_release_v09.py
```

The verifier recomputes every result SHA-256 and checks the required release documents.

## Local editable installation

Normal online environment:

```bash
pip install -e .[dev]
```

When build isolation cannot download build requirements but compatible setuptools/wheel are already installed locally:

```bash
pip install -e . --no-build-isolation --no-deps
```

This changes packaging mechanics only; it does not alter simulation results.

## Statistical interpretation

Monte Carlo rows with `0 observed errors` are not interpreted as zero underlying error probability. When Wilson confidence intervals are available, they should be preferred. The newer packet experiments also report packet counts/transmission counts so finite-run uncertainty remains visible.
