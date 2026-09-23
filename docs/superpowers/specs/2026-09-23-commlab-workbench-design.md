# CommLab workbench design

## Goal

Make the existing local Streamlit application useful both for repeated research experiments and for showing a single experiment to another person. The numerical library, seed behavior, desktop launcher, and published historical results stay stable.

## User journey

The user finds a lab through a small set of subject groups or search, opens its controls, sets a seed, runs it, reads metrics and figures, and exports a compact record. Recent labs and pinned labs speed up return visits. A result record states the lab, input controls, seed, version, run time, and displayed metrics. Only metrics with the same name and unit are compared.

## Architecture

Keep Streamlit and the local desktop launch process. Extract an experiment catalog from the current single selectbox, with exact coverage of all existing mode names. Keep scientific calculations in `commlab`; the dashboard remains an adapter. Add small pure modules for catalog filtering and JSON-safe run records. The workbench shell manages navigation, preferences, status, and exports. It collects the controls and metrics actually shown by the selected lab, so records do not duplicate model inputs or invent results.

Move the dashboard toward a function that renders one selected lab. Retain the existing branch code initially. Changes that defer expensive computation must preserve each lab's parameters and test its output before enabling explicit execution. Avoid presenting a button as an execution control when computation still runs on every widget change.

## Validation and boundaries

All existing numerical and desktop launcher tests must pass. Add catalog coverage and run-record tests, then exercise representative modes with Streamlit's app test or a local browser. Check search, pins, recent list, stable seed, record export, compatible-metric comparison, and a frozen desktop launch smoke test. No real wireless measurements or hardware claims are introduced. Keep existing uncommitted launcher changes untouched.
