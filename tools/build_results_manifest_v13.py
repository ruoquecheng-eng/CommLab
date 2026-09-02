from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RESULTS=ROOT/'results'
NEW={
'cell_free_user_centric.csv','cell_free_power_control.csv','ris_multiuser_coordinate.csv','ris_coordinate_convergence.csv',
'isac_predictive_beam_tracking.csv','isac_predictive_beam_trace.csv','isac_uncertainty_aware_beamwidth.csv'
}
def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def csvmeta(p):
    with p.open(newline='') as f: rows=list(csv.reader(f))
    return {'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'columns':rows[0] if rows else [],'data_rows':max(0,len(rows)-1),'bytes':p.stat().st_size}
def filemeta(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'bytes':p.stat().st_size}
def main():
    data=sorted((RESULTS/'data').glob('*.csv')); figs=sorted((RESULTS/'figures').glob('*.png'))
    m={'release':'v1.3','csv':[csvmeta(p) for p in data],'figures':[filemeta(p) for p in figs]}
    out=RESULTS/'manifest_v1.3.json'; out.write_text(json.dumps(m,indent=2),encoding='utf-8')
    lines=['# Experiment Artifact Catalog — v1.3','',f'CSV datasets: **{len(data)}**  ',f'Figures: **{len(figs)}**','', '## New v1.3 datasets','']
    for item in m['csv']:
        if Path(item['path']).name in NEW: lines.append(f"- `{item['path']}` — {item['data_rows']} rows; columns: {', '.join(item['columns'])}")
    lines += ['', '## Validation','', '```bash','python -m pip install -e . --no-build-isolation','pytest -q','PYTHONPATH=src python experiments/run_v13_suite.py','python tools/build_results_manifest_v13.py','python tools/verify_release_v13.py','```','']
    (ROOT/'docs'/'experiment_catalog_v1.3.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'wrote {out} with {len(data)} CSVs and {len(figs)} figures')
if __name__=='__main__': main()
