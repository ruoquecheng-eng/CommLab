# CommLab v3.5 Release Acceptance

The canonical acceptance command is:

```bash
python tools/run_release_acceptance_v35.py
```

It performs an offline editable install, runs all six v3.5 experiments, executes the full regression twice (including one run with manual `PYTHONPATH` removed), validates distribution/runtime version and import location, compiles source/application/experiments/tools, rebuilds the result manifest, and verifies every result hash and required v3.5 release file.

## Accepted release record

- package/distribution/runtime: **3.5.0**;
- full pytest: **252 / 252 passed**;
- pytest with manual `PYTHONPATH` removed: **252 / 252 passed**;
- v3.5 experiment suite: **6 / 6**, about **14.5 seconds**;
- compileall: passed;
- result manifest: **214 CSV + 378 PNG = 592 artifacts**, all SHA-256 verified;
- total acceptance time: about **27.6 seconds** in the release environment.
