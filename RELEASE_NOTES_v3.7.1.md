# CommLab v3.7.1 Desktop Edition

v3.7.1 adds a Windows desktop distribution layer without changing the v3.7 numerical research results.

## Added

- double-click desktop launcher with no console window;
- localhost-only Streamlit child process with dynamic free-port selection;
- startup health check, reopen button, address copy, log path, and clean shutdown;
- source-mode smoke test;
- PyInstaller onedir specification;
- Inno Setup installer with Start Menu and optional Desktop shortcuts;
- Windows GitHub Actions artifact build;
- focused launcher unit tests and Chinese user documentation.

## Packaging boundary

The Windows executable must be built and smoke-tested on Windows. The source launcher and local Streamlit lifecycle can be tested on Linux, but PyInstaller does not cross-compile a Windows executable from Linux. The installer is unsigned until a code-signing certificate is supplied.

## Validation

- **295 / 295 tests passed** twice;
- **8 / 8 desktop-launcher tests passed**;
- source and frozen-process live health checks passed;
- same-structure PyInstaller onedir build passed;
- six numerical experiments completed;
- **628 / 628 result artifacts** passed SHA-256 verification;
- canonical v3.7.1 acceptance completed in about **38.4 seconds**.
