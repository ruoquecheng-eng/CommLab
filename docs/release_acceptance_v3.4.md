# CommLab v3.4 Release Acceptance

The authoritative acceptance command is:

```bash
python tools/run_release_acceptance_v34.py
```

It performs an offline editable install, the six v3.4 experiments, full pytest, version/import-path checks with manual `PYTHONPATH` removed, a second full pytest, compileall, result-manifest build, and release verification.

## Accepted result

- package/distribution/runtime: `3.4.0`;
- v3.4 suite: 6/6;
- pytest: 243/243;
- pytest without manual `PYTHONPATH`: 243/243;
- compileall: passed;
- manifest: 208 CSV + 366 PNG = 574 verified artifacts;
- total acceptance time: approximately 30.6 seconds.
