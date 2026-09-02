from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; RESULTS=ROOT/"results"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def csvmeta(path):
    with path.open(newline="",encoding="utf-8") as f:
        r=csv.reader(f); header=next(r,[]); rows=sum(1 for _ in r)
    return {"path":str(path.relative_to(ROOT)),"sha256":sha256(path),"columns":header,
            "data_rows":rows,"bytes":path.stat().st_size}

def filemeta(path):
    return {"path":str(path.relative_to(ROOT)),"sha256":sha256(path),"bytes":path.stat().st_size}

def main():
    data=sorted((RESULTS/"data").glob("*.csv")); figs=sorted((RESULTS/"figures").glob("*.png"))
    manifest={"release":"v3.6","package_version":"3.6.0","summary":{
        "csv_count":len(data),"figure_count":len(figs),"result_artifact_count":len(data)+len(figs)},
        "csv":[csvmeta(p) for p in data],"figures":[filemeta(p) for p in figs]}
    out=RESULTS/"manifest_v3.6.json"; out.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(f"wrote {out} with {len(data)} CSVs + {len(figs)} figures = {len(data)+len(figs)} artifacts")

if __name__=="__main__": main()
