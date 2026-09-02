# CommLab v3.3 Release Acceptance

Formal acceptance command:

```bash
python tools/run_release_acceptance_v33.py
```

## Result

**PASSED**

- editable install: **12.5 s**
- six-experiment v3.3 suite: **60.8 s**
- v3.3 suite internal runtime: **57.0 s**
- full pytest: **236 / 236 passed**
- full pytest step: **18.1 s**
- distribution version: **3.3.0**
- runtime `commlab.__version__`: **3.3.0**
- import path: `/mnt/data/CommLab-v3.3/src/commlab/__init__.py`
- pytest with `PYTHONPATH` removed: **236 / 236 passed**
- no-`PYTHONPATH` pytest step: **16.2 s**
- `compileall -q src app experiments tools`: **passed**
- result manifest: **202 CSV + 354 PNG = 556 SHA-256 verified result artifacts**
- manifest/release verification: **passed**
- complete acceptance wall time: **113.9 s**

The suite runs each experiment in its own Python process. This avoids retaining Matplotlib/NumPy state between long Monte Carlo scripts and makes individual experiment timing/failure visible.

## Final packaging checks

After the acceptance command, the release packaging procedure additionally performs cache cleanup, ZIP creation, ZIP CRC verification, and ZIP SHA-256 generation. These steps are recorded in the final project status and checksum file.
