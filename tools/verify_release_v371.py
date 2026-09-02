from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/"results"/"manifest_v3.7.1.json"
REQ_CSV={"v37_propensity_modes.csv","v37_hidden_confounding.csv","v37_logging_drift.csv",
         "v37_sensitivity_frontier.csv","v37_crossfit_sample_size.csv","v37_robust_policy_selection.csv"}
REQ_PNG={"v37_propensity_modes_error.png","v37_propensity_modes_calibration.png",
         "v37_hidden_confounding_error.png","v37_hidden_confounding_gamma.png",
         "v37_logging_drift_error.png","v37_logging_drift_calibration.png",
         "v37_sensitivity_frontier_width.png","v37_sensitivity_frontier_coverage.png",
         "v37_crossfit_sample_size_error.png","v37_crossfit_sample_size_weights.png",
         "v37_robust_policy_selection_regret.png","v37_robust_policy_selection_fallback.png"}

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def main():
    failures=[]
    if not MANIFEST.exists(): raise SystemExit("missing results/manifest_v3.7.1.json")
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("release")!="v3.7.1" or m.get("package_version")!="3.7.1": failures.append("manifest release/version mismatch")
    checked=0; manifested=set()
    for group in ("csv","figures"):
        for item in m.get(group,[]):
            p=ROOT/item["path"]; checked+=1; manifested.add(item["path"])
            if not p.exists(): failures.append(f"missing: {item['path']}")
            elif sha256(p)!=item["sha256"]: failures.append(f"hash mismatch: {item['path']}")
    actual={str(p.relative_to(ROOT)) for p in (ROOT/"results"/"data").glob("*.csv")}
    actual|={str(p.relative_to(ROOT)) for p in (ROOT/"results"/"figures").glob("*.png")}
    failures += [f"unmanifested result artifact: {x}" for x in sorted(actual-manifested)]
    failures += [f"manifest entry missing on disk: {x}" for x in sorted(manifested-actual)]
    actual_csv={p.name for p in (ROOT/"results"/"data").glob("*.csv")}; actual_png={p.name for p in (ROOT/"results"/"figures").glob("*.png")}
    failures += [f"missing v3.7 dataset: {x}" for x in sorted(REQ_CSV-actual_csv)]
    failures += [f"missing v3.7 figure: {x}" for x in sorted(REQ_PNG-actual_png)]
    for name in sorted(REQ_CSV & actual_csv):
        with (ROOT/"results"/"data"/name).open(newline="",encoding="utf-8") as f: rows=list(csv.reader(f))
        if len(rows)<2 or not rows[0]: failures.append(f"empty dataset: {name}"); continue
        if len(rows[0])!=len(set(rows[0])): failures.append(f"duplicate CSV column: {name}")
        for i,row in enumerate(rows[1:],2):
            if len(row)!=len(rows[0]): failures.append(f"CSV width mismatch: {name}:{i}"); break
            for cell in row:
                try: value=float(cell)
                except ValueError: continue
                if not math.isfinite(value): failures.append(f"non-finite value: {name}:{i}"); break
    for name in sorted(REQ_PNG & actual_png):
        if (ROOT/"results"/"figures"/name).read_bytes()[:8]!=b"\x89PNG\r\n\x1a\n": failures.append(f"invalid PNG: {name}")
    summary=m.get("summary",{})
    if summary.get("csv_count")!=len(actual_csv): failures.append("manifest csv_count mismatch")
    if summary.get("figure_count")!=len(actual_png): failures.append("manifest figure_count mismatch")
    required=["README.md","PROJECT_STATUS.md","RELEASE_NOTES_v3.7.md","docs/technical_report.md",
        "docs/portfolio_summary_v3.7.md","docs/reproducibility_v3.7.md","docs/experiment_catalog_v3.7.md",
        "docs/v3.7_tradeoff_matrix.md","docs/methodological_inspirations_v3.7.md",
        "docs/v3.7_propensity_robust_architecture.md","docs/release_acceptance_v3.7.md",
        "tools/build_manifest_v37.py","tools/verify_release_v37.py","tools/run_v37_suite.py",
        "tools/run_release_acceptance_v37.py",
        "RELEASE_NOTES_v3.7.1.md","docs/windows_desktop_v3.7.1.md","docs/release_acceptance_v3.7.1.md",
        "desktop/launcher.py","desktop/CommLabDesktop.spec","desktop/build_windows.ps1",
        "desktop/installer.iss",".github/workflows/desktop-windows.yml",
        "tools/build_manifest_v371.py","tools/verify_release_v371.py","tools/run_release_acceptance_v371.py"]
    failures += [f"missing release file: {x}" for x in required if not (ROOT/x).exists()]
    try:
        import commlab
        dist=importlib.metadata.version("commlab-ofdm")
        if dist!="3.7.1": failures.append(f"distribution version is {dist}")
        if commlab.__version__!="3.7.1": failures.append(f"runtime version is {commlab.__version__}")
        try: Path(commlab.__file__).resolve().relative_to(ROOT.resolve())
        except ValueError: failures.append(f"import outside release tree: {commlab.__file__}")
    except Exception as exc: failures.append(f"package validation failed: {exc}")
    if failures:
        print("\n".join(failures)); raise SystemExit(1)
    print(f"v3.7.1 release verification OK: {checked} hashed result artifacts; summary={summary}")

if __name__=="__main__": main()
