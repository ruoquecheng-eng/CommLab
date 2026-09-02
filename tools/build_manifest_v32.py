from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
CORE_NEW={
    'v32_predictive_failure_migration.csv',
    'v32_failure_domain_zone_risk.csv',
    'v32_chance_constrained_inference.csv',
    'v32_control_uep.csv',
    'v32_multi_connectivity.csv',
    'v32_multi_connectivity_frontier.csv',
    'v32_multiconnectivity_safety_control.csv',
}
PRESERVED={
    'v32_semantic_harq.csv','v32_mixed_control_inference.csv',
    'v32_failure_domain_replication.csv','v32_service_migration.csv',
    'v32_safety_bit_allocation.csv',
}


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def csvmeta(path: Path):
    with path.open(newline='',encoding='utf-8') as f:
        r=csv.reader(f); header=next(r,[]); rows=sum(1 for _ in r)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'columns':header,'data_rows':rows,'bytes':path.stat().st_size}


def filemeta(path: Path):
    return {'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'bytes':path.stat().st_size}


def main():
    data=sorted((RESULTS/'data').glob('*.csv'))
    figs=sorted((RESULTS/'figures').glob('*.png'))
    manifest={
        'release':'v3.2','package_version':'3.2.0',
        'summary':{'csv_count':len(data),'figure_count':len(figs),'result_artifact_count':len(data)+len(figs)},
        'csv':[csvmeta(p) for p in data],
        'figures':[filemeta(p) for p in figs],
    }
    out=RESULTS/'manifest_v3.2.json'
    out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')

    lines=[
        '# Experiment Artifact Catalog — v3.2','',
        f'CSV datasets: **{len(data)}**  ',f'Figures: **{len(figs)}**  ',
        f'Verified result artifacts: **{len(data)+len(figs)}**','',
        '## Predictive-resilience main line',''
    ]
    byname={Path(item['path']).name:item for item in manifest['csv']}
    for name in sorted(CORE_NEW):
        item=byname.get(name)
        if item:
            lines.append(f"- `{item['path']}` — {item['data_rows']} rows; columns: {', '.join(item['columns'])}")
    lines += ['','## Preserved earlier v3.2 datasets','']
    for name in sorted(PRESERVED):
        item=byname.get(name)
        if item:
            lines.append(f"- `{item['path']}` — {item['data_rows']} rows; columns: {', '.join(item['columns'])}")
    lines += [
        '', '## Reproduction and validation','', '```bash',
        'python -m pip install -e . --no-build-isolation',
        'python tools/run_v32_suite.py',
        'pytest -q',
        'python -m compileall -q src app experiments tools',
        'python tools/build_manifest_v32.py',
        'python tools/verify_release_v32.py',
        '```',''
    ]
    (ROOT/'docs'/'experiment_catalog_v3.2.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'wrote {out} with {len(data)} CSVs + {len(figs)} figures = {len(data)+len(figs)} artifacts')

if __name__=='__main__':
    main()
