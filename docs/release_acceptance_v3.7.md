# CommLab v3.7 Release Acceptance

The canonical command is:

```bash
python tools/run_release_acceptance_v37.py
```

It performs an offline editable install, runs all six v3.7 experiments, executes the complete regression twice including one run with project-source `PYTHONPATH` removed, validates distribution/runtime version and import location, compiles the source/application/experiments/tools trees, rebuilds the result manifest, and verifies every result hash and required release file.

## Accepted release record

- package/distribution/runtime: **3.7.0**;
- full pytest: **287 / 287 passed**;
- pytest with project-source `PYTHONPATH` removed: **287 / 287 passed**;
- v3.7 experiment suite: **6 / 6**, about **17.5 seconds**;
- compileall: passed;
- result manifest: **226 CSV + 402 PNG = 628 artifacts**, all SHA-256 verified;
- total acceptance time: about **31.2 seconds** in the release environment;
- archive CRC and SHA-256 are checked after acceptance.
