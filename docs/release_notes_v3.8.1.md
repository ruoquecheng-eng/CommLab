# CommLab v3.8.1

This desktop patch keeps the v3.8.0 workbench and numerical models unchanged. It improves troubleshooting for the Windows launcher:

- Each launch writes a separate timestamped log under `%LOCALAPPDATA%\CommLab\logs\`, so a failure report points to the current attempt instead of mixing in previous sessions.
- Startup diagnostics include the application version, runtime mode, Python executable, resource and dashboard paths, local address, process state, and recent log output.
- Launcher tests cover Unicode installation and user-data paths, and reading the tail of a large log.

Download the Windows installer (`CommLab-Setup-v3.8.1-Windows-x64.exe`) or portable ZIP (`CommLab-Windows-x64.zip`). The app serves its interface on localhost. All experiments produce synthetic simulation results; this release does not claim measured wireless data or hardware validation. The installer is not code-signed; Windows SmartScreen may show an unknown-publisher warning.
