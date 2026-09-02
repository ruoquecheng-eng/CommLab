from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/"results"/"manifest_v3.5.json"
REQ_CSV={"v35_masking_budget.csv","v35_regime_attribution.csv","v35_telemetry_dropout.csv",
         "v35_audit_frontier.csv","v35_feedback_delay.csv","v35_correlation_observability.csv"}
REQ_PNG={"v35_masking_budget_fraction.png","v35_masking_budget_debt.png",
         "v35_regime_attribution_reliability.png","v35_regime_attribution_actions.png",
         "v35_telemetry_dropout_reliability.png","v35_telemetry_dropout_audits.png",
         "v35_audit_frontier_class_tradeoff.png","v35_audit_frontier_resource.png",
         "v35_feedback_delay_detection.png","v35_feedback_delay_reliability.png",
         "v35_correlation_observability_reliability.png","v35_correlation_observability_masking.png"}

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def main():
    failures=[]
    if not MANIFEST.exists(): raise SystemExit("missing results/manifest_v3.5.json")
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("release")!="v3.5" or m.get("package_version")!="3.5.0": failures.append("manifest release/version mismatch")
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
    failures += [f"missing v3.5 dataset: {x}" for x in sorted(REQ_CSV-actual_csv)]
    failures += [f"missing v3.5 figure: {x}" for x in sorted(REQ_PNG-actual_png)]
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
    required=["README.md","PROJECT_STATUS.md","RELEASE_NOTES_v3.5.md","docs/technical_report.md",
        "docs/portfolio_summary_v3.5.md","docs/reproducibility_v3.5.md","docs/experiment_catalog_v3.5.md",
        "docs/v3.5_tradeoff_matrix.md","docs/methodological_inspirations_v3.5.md",
        "docs/v3.5_observability_architecture.md","docs/release_acceptance_v3.5.md",
        "tools/build_manifest_v35.py","tools/verify_release_v35.py","tools/run_v35_suite.py",
        "tools/run_release_acceptance_v35.py"]
    failures += [f"missing release file: {x}" for x in required if not (ROOT/x).exists()]
    try:
        import commlab
        dist=importlib.metadata.version("commlab-ofdm")
        if dist!="3.5.0": failures.append(f"distribution version is {dist}")
        if commlab.__version__!="3.5.0": failures.append(f"runtime version is {commlab.__version__}")
        try: Path(commlab.__file__).resolve().relative_to(ROOT.resolve())
        except ValueError: failures.append(f"import outside release tree: {commlab.__file__}")
    except Exception as exc: failures.append(f"package validation failed: {exc}")
    if failures:
        print("\n".join(failures)); raise SystemExit(1)
    print(f"v3.5 release verification OK: {checked} hashed result artifacts; summary={summary}")

if __name__=="__main__": main()
