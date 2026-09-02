"""Build a lightweight reproducibility manifest for generated experiment artifacts."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()


def csv_meta(path: Path):
    with path.open(newline='') as f:
        r=csv.reader(f); rows=list(r)
    return {
        'path':str(path.relative_to(ROOT)),
        'sha256':sha256(path),
        'columns':rows[0] if rows else [],
        'data_rows':max(0,len(rows)-1),
    }


def file_meta(path: Path):
    return {'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'bytes':path.stat().st_size}


def main():
    data=sorted((RESULTS/'data').glob('*.csv'))
    figs=sorted((RESULTS/'figures').glob('*.png'))
    manifest={
        'release':'v0.6',
        'csv':[csv_meta(p) for p in data],
        'figures':[file_meta(p) for p in figs],
    }
    out=RESULTS/'manifest_v0.6.json'; out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    lines=['# Experiment Artifact Catalog — v0.6','',f'CSV datasets: **{len(data)}**  ',f'Figures: **{len(figs)}**','',
           'The JSON manifest records SHA-256 hashes so generated artifacts can be checked for accidental changes.','', '## v0.6 datasets','']
    v06_names={'iq_imbalance_compensation.csv','sampling_clock_offset.csv','narrowband_interference.csv','ldpc_min_sum_ofdm.csv','learned_polynomial_dpd.csv','otfs_high_doppler.csv'}
    for item in manifest['csv']:
        if Path(item['path']).name in v06_names:
            lines.append(f"- `{item['path']}` — {item['data_rows']} rows; columns: {', '.join(item['columns'])}")
    lines += ['', '## Validation commands','', '```bash','pip install -e .[dev]','pytest -q','python experiments/run_v06_suite.py','python tools/build_results_manifest.py','```','']
    (ROOT/'docs'/'experiment_catalog_v0.6.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'wrote {out.relative_to(ROOT)} with {len(data)} CSVs and {len(figs)} figures')

if __name__=='__main__': main()
