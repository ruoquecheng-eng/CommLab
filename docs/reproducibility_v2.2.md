# Reproducibility — v2.2

## Environment-independent validation

```bash
python -m pip install -e . --no-build-isolation
python -c "import commlab; print(commlab.__version__, commlab.__file__)"
pytest -q
python -m compileall -q src app experiments tools
```

The installed package must report version `2.2.0` and resolve to this release tree rather than an older editable installation.

## v2.2 deterministic experiments

```bash
python experiments/run_v22_suite.py
```

The suite explicitly prepends the current release `src/` directory to child-process `PYTHONPATH`, preventing an older editable installation from silently satisfying experiment imports.

## Result manifest

```bash
python tools/build_results_manifest_v22.py
python tools/verify_release_v22.py
```

The manifest stores SHA-256 hashes for every CSV and PNG under `results/`.

## v2.2 experimental notes

- All fixed-budget gradient-compression strategies use the same nominal coordinate budget and matched Monte Carlo seeds.
- The residual-aware compressor reallocates coordinates from the same budget; it does not receive extra coordinates.
- ADC bit-depth comparisons reuse identical random seeds and PA settings. AGC changes only receiver scaling into the normalized ADC range.
- Layered semantic comparisons reuse the same task geometry/source samples for base/full/adaptive operation within each call.
- Importance-aware random access keeps mean repetition close to the degree-3 baseline; gains should be interpreted through decoded gradient mass as well as packet count.
- Two-timescale RIS-FL reports median final loss because rare deep-fade AirComp events can make mean learning loss heavy-tailed at long update intervals.

## Scope

These are deterministic seeded research simulations. They are not OTA measurements, standards conformance tests, or claims of global optimality.
