# CommLab Project Status

## Current formal release: v3.7.1 Desktop

- Working/release tree: `CommLab-v3.7`
- Package/runtime: **3.7.1**
- Desktop launcher: source and frozen-process smoke tests passed
- Windows packaging: PyInstaller + Inno Setup + GitHub Actions workflow
- Full regression: **287 / 287 passed**
- Regression with project-source `PYTHONPATH` removed: **287 / 287 passed**
- v3.7 experiment suite: **6 / 6 completed**
- Result inventory: **226 CSV + 402 PNG = 628 SHA-256-verified artifacts**
- `compileall src app experiments tools`: passed
- editable install / distribution / runtime / import-path checks: passed
- v3.7 numerical results and all earlier modules/results retained

## v3.7 research line

1. uncertain, stale, and learned logging propensities;
2. observable propensity drift versus hidden common causes;
3. in-sample and cross-fitted nuisance estimation;
4. empirical propensity calibration and weight diagnostics;
5. odds-envelope sensitivity width and aggregate coverage;
6. point selection versus conservative baseline fallback.

## Scientific boundary

v3.7 is a synthetic NumPy contextual-bandit stress test. Hidden truth and paired outcomes score the method only. The sensitivity envelope is not a sharp partial-identification bound, the selector is not a safe-policy-improvement certificate, and no production telemetry, valid instrument, or safety certification is claimed.
