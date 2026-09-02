from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RESULTS=ROOT/'results'
NEW={
 'v29_task_aware_repair.csv','v29_congested_model_refresh.csv','v29_battery_carbon_fair_fl.csv',
 'v29_twin_guided_prefetch.csv','v29_networked_control.csv'
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
 m={'release':'v2.9','csv':[csvmeta(p) for p in data],'figures':[filemeta(p) for p in figs]}
 out=RESULTS/'manifest_v2.9.json'; out.write_text(json.dumps(m,indent=2),encoding='utf-8')
 lines=['# Experiment Artifact Catalog — v2.9','',f'CSV datasets: **{len(data)}**  ',f'Figures: **{len(figs)}**','', '## New v2.9 datasets','']
 for item in m['csv']:
  if Path(item['path']).name in NEW: lines.append(f"- `{item['path']}` — {item['data_rows']} rows; columns: {', '.join(item['columns'])}")
 lines += ['', '## Validation','', '```bash','python -m pip install -e . --no-build-isolation','pytest -q','python experiments/run_v29_suite.py','python tools/build_results_manifest_v29.py','python tools/verify_release_v29.py','```','']
 (ROOT/'docs'/'experiment_catalog_v2.9.md').write_text('\n'.join(lines),encoding='utf-8')
 print(f'wrote {out} with {len(data)} CSVs and {len(figs)} figures')
if __name__=='__main__': main()
