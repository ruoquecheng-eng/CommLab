# CommLab v3.7.1 Desktop Release Acceptance

The canonical source/package command is:

```bash
python tools/run_release_acceptance_v371.py
```

It performs an offline editable install, regenerates the six v3.7 numerical experiments, starts the desktop launcher and verifies the live Streamlit health endpoint, runs the complete regression twice with project-source `PYTHONPATH` removed for the second run, validates package/runtime/import identity, compiles application and desktop code, rebuilds the v3.7.1 result manifest, and verifies all hashes and required packaging files.

The PyInstaller specification is additionally built in the release environment and its frozen child-process health check is executed. Because PyInstaller does not cross-compile Windows executables, the distributable `.exe` and Inno Setup installer are built by `.github/workflows/desktop-windows.yml` on `windows-latest`.

## Accepted release record

- package/distribution/runtime: **3.7.1**;
- full pytest: **295 / 295 passed**;
- pytest with project-source `PYTHONPATH` removed: **295 / 295 passed**;
- desktop launcher focused tests: **8 / 8 passed**;
- source launcher live health check: passed;
- same-structure PyInstaller build and frozen-process health check: passed;
- v3.7 numerical experiment suite: **6 / 6**;
- compileall: passed;
- result manifest: **226 CSV + 402 PNG = 628 artifacts**, all SHA-256 verified;
- canonical acceptance completed in about **38.4 seconds** in the release environment.
