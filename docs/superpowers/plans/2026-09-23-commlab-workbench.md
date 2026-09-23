# CommLab Workbench Implementation Plan

> **For agentic workers:** Use the current approved CommLab design and implement each task with focused verification.

**Goal:** Improve discovery, repeatability, and presentation across all existing CommLab labs.

**Architecture:** Keep the numerical package and Streamlit dashboard. Add a catalog and run-record layer, then refactor only the shared dashboard shell and the selected lab path as needed. Avoid edits to desktop launcher files with pre-existing local changes.

**Tech Stack:** Python 3.10+, Streamlit 1.63 locally, NumPy, pytest.

**Spec:** `docs/superpowers/specs/2026-09-23-commlab-workbench-design.md`

## Global constraints

- Preserve every current mode name and its numerical model behavior.
- Keep all computations local and the existing `127.0.0.1` desktop launch path.
- State that all experiments are simulated where result context is shown.
- Never describe one lab's metric as directly comparable to an incompatible lab.
- Preserve the four pre-existing dirty launcher, test, doc, and ignore-file changes.

## Review focus

- Search with mixed case, spaces, and no matches keeps a usable lab picker.
- An unknown or removed saved favorite is ignored safely.
- A run record with NumPy values becomes valid JSON without changing units.
- Changing a seed changes only the selected lab's simulated sample, not the scientific model.
- A desktop build still resolves `app/dashboard.py` and bundled helper modules.

### Task 1: Catalog and navigation

**Files:** `app/lab_catalog.py`, `app/dashboard.py`, `tests/test_lab_catalog.py`

- [x] Record the existing mode list once in a pure module and classify all names.
- [x] Test that catalog names match every dashboard branch plus the fallback lab.
- [x] Add topic search, categories, recent and pinned labs to the Streamlit sidebar.
- [x] Check representative selections in the local app.

### Task 2: Run record and export

**Files:** `app/run_record.py`, `app/dashboard.py`, `tests/test_run_record.py`

- [x] Implement JSON-safe capture of selected lab, seed, controls, metrics, version and elapsed time.
- [x] Test arrays, NumPy scalars, nonfinite values and metric compatibility.
- [x] Add a visible record/download area and comparisons only for compatible metrics.
- [x] Check deterministic replay for a representative lab.

### Task 3: Shared layout and execution behavior

**Files:** `app/dashboard.py`, dashboard helper modules, `tests/test_dashboard_workbench.py`

- [x] Organize heading, controls, status, outputs and limitations consistently.
- [x] Make parameter submission explicit for all labs, with last-submitted state and reset.
- [x] Verify controls and results for representative old and new modes.

### Task 4: Packaging and full regression

**Files:** `README.md`, `docs/windows_desktop_v3.7.1.md` only if needed, desktop spec only if bundle imports require it.

- [x] Run focused catalog, record and dashboard tests using a writable `--basetemp`.
- [x] Run the full pytest suite and syntax check (315 passed on 2026-09-23).
- [x] Run source and frozen desktop smoke and inspect UI at laptop and narrow widths.
- [x] Record remaining limits without overstating a fully migrated interface.

The numerical lab branches remain in the original large dashboard module; the catalog, local state, widget capture, and record/export logic are separate. The shell is Chinese-first, while established lab names and many scientific controls remain in English. The tested build is a local frozen build, not a published installer or release.
