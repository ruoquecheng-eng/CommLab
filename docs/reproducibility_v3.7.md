# v3.7 Reproducibility

## Run the focused suite

```bash
python tools/run_v37_suite.py
```

The command launches six isolated experiment subprocesses and writes six CSV datasets plus twelve PNG figures under `results/`.

## Run tests

```bash
python -m pytest -q
```

## Run formal acceptance

```bash
python tools/run_release_acceptance_v37.py
```

Acceptance performs an offline editable install, runs the v3.7 suite, runs the complete regression twice with the second run removing any project-source `PYTHONPATH`, validates distribution/runtime/import path, compiles code, rebuilds the result manifest, and verifies hashes and release files.

## Randomness and evaluation-only state

Every experiment passes explicit integer seeds. Within a seed, propensity modes share the same synthetic trace construction. The hidden severity, true behavior propensity, and paired potential outcomes are available only to scoring diagnostics. They are not included in observed-feature propensity or outcome models.

Matplotlib configuration is isolated per experiment by the suite. CSVs contain aggregated finite-run summaries; the source scripts define sample sizes, seed counts, and sweeps exactly.
