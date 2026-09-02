# CommLab v3.2 Release Acceptance

Formal package/runtime version: **3.2.0**.

## Acceptance result

`python tools/run_release_acceptance_v32.py` completed successfully. The command performed the editable installation, full v3.2 experiment suite, full regression tests, import/version validation with `PYTHONPATH` removed, a second no-`PYTHONPATH` regression, compileall, manifest rebuild, and manifest verification.

- v3.2 experiments: **12 / 12 passed**
- full pytest: **230 / 230 passed**
- no-`PYTHONPATH` pytest: **230 / 230 passed**
- distribution version: **3.2.0**
- runtime version: **3.2.0**
- result artifacts: **196 CSV + 343 PNG = 539**
- result hashes: **539 / 539 verified**
- total one-command acceptance time in this environment: **191.8 s**

## Import-path check

```text
distribution 3.2.0
runtime 3.2.0
/mnt/data/CommLab-v3.2/src/commlab/__init__.py
```

## Suite timing observation

The full 12-experiment suite completed in about 144–147 s across repeated release runs. The preserved Mixed Control-Inference and Safety Bit Allocation studies remain the slowest experiments; they are intentionally retained rather than removed for release convenience. Experiments run in isolated child interpreters to avoid cross-Lab Matplotlib/NumPy state leakage.

## Release boundary

These checks validate software reproducibility and artifact integrity. They are not wireless-standards conformance, hardware validation, production edge-cluster qualification, or control-safety certification.
