# Reproducibility — v0.7

## Validation commands

```bash
python -m compileall -q src experiments app tools
pytest -q
python experiments/run_v07_suite.py
```

Current validated result:

```text
54 passed
```

The complete v0.7 suite was rerun after the final source changes.

## Generated experiment artifacts

The release currently contains:

- **37 CSV/data files** under `results/data/`;
- **66 figures** under `results/figures/`;
- **103 hashed result artifacts** in `results/manifest_v0.7.json`.

The manifest stores file sizes and SHA-256 hashes so result changes can be detected.

## Randomness

Headline experiments use explicit NumPy RNG seeds. They are intended to be deterministic for a fixed NumPy/SciPy numerical environment. Very small floating-point changes across BLAS/platform versions may alter final least-significant digits or rare Monte Carlo decisions.

## BER language

`0 observed errors` means no errors occurred in the finite simulated bit count. It does **not** mean the underlying BER is mathematically zero. v0.7 adds Wilson confidence intervals and a QPSK theory calibration experiment to make that distinction explicit.

## Packaging smoke test

In the offline execution environment, normal isolated editable installation attempted to fetch build requirements and therefore could not access the network. The project was successfully installed and imported with the locally available build backend using:

```bash
pip install -e . --no-deps --no-build-isolation
```

The installed package then passed all 54 tests.
