# CommLab v3.6 Release Acceptance

The canonical command is:

```bash
python tools/run_release_acceptance_v36.py
```

It performs an offline editable install, runs all six v3.6 experiments, executes the complete regression twice including one run with manual `PYTHONPATH` removed, validates distribution/runtime version and import location, compiles the source/application/experiments/tools trees, rebuilds the result manifest, and verifies every result hash and required release file.

## Accepted release record

- package/distribution/runtime: **3.6.0**;
- full pytest: **268 / 268 passed**;
- pytest with manual `PYTHONPATH` removed: **268 / 268 passed**;
- v3.6 experiment suite: **6 / 6**, about **23.8 seconds**;
- compileall: passed;
- result manifest: **220 CSV + 390 PNG = 610 artifacts**, all SHA-256 verified;
- total acceptance time: about **37.4 seconds** in the release environment.
