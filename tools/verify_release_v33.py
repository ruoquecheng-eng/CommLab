from __future__ import annotations
import csv, hashlib, importlib.metadata, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'results'/'manifest_v3.3.json'
REQ_CSV={
    'v33_resilience_budget.csv','v33_risk_regimes.csv','v33_forecast_uncertainty.csv',
    'v33_correlation_reallocation.csv','v33_budget_saturation.csv','v33_task_weighting.csv',
}
REQ_PNG={
    'v33_resilience_budget_reliability.png','v33_resilience_budget_actions.png',
    'v33_risk_regimes_action_mix.png','v33_risk_regimes_reliability.png',
    'v33_uncertainty_migration_churn.png','v33_uncertainty_reliability.png',
    'v33_correlation_budget_shift.png','v33_correlation_reliability.png',
    'v33_budget_saturation_reliability.png','v33_budget_saturation_spend.png',
    'v33_task_weighting_tradeoff.png',
}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def main():
    failures=[]
    if not MANIFEST.exists(): raise SystemExit('missing results/manifest_v3.3.json')
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if m.get('release')!='v3.3' or m.get('package_version')!='3.3.0': failures.append('manifest release/version mismatch')
    checked=0; manifested=set()
    for group in ('csv','figures'):
        for item in m.get(group,[]):
            p=ROOT/item['path']; checked+=1; manifested.add(item['path'])
            if not p.exists(): failures.append(f'missing: {item["path"]}')
            elif sha256(p)!=item['sha256']: failures.append(f'hash mismatch: {item["path"]}')
    actual={str(p.relative_to(ROOT)) for p in (ROOT/'results'/'data').glob('*.csv')}
    actual|={str(p.relative_to(ROOT)) for p in (ROOT/'results'/'figures').glob('*.png')}
    for rel in sorted(actual-manifested): failures.append(f'unmanifested result artifact: {rel}')
    for rel in sorted(manifested-actual): failures.append(f'manifest entry missing on disk: {rel}')

    actual_csv={p.name for p in (ROOT/'results'/'data').glob('*.csv')}
    actual_png={p.name for p in (ROOT/'results'/'figures').glob('*.png')}
    for name in sorted(REQ_CSV-actual_csv): failures.append(f'missing v3.3 dataset: {name}')
    for name in sorted(REQ_PNG-actual_png): failures.append(f'missing v3.3 figure: {name}')
    for name in sorted(REQ_CSV & actual_csv):
        p=ROOT/'results'/'data'/name
        with p.open(newline='',encoding='utf-8') as f: rows=list(csv.reader(f))
        if len(rows)<2 or not rows[0]: failures.append(f'empty v3.3 dataset: {name}'); continue
        if len(rows[0])!=len(set(rows[0])): failures.append(f'duplicate CSV column in {name}')
        for ri,row in enumerate(rows[1:],2):
            if len(row)!=len(rows[0]): failures.append(f'CSV width mismatch: {name}:{ri}'); break
            for cell in row:
                try: val=float(cell)
                except ValueError: continue
                if not math.isfinite(val): failures.append(f'non-finite numeric value: {name}:{ri}'); break
    for name in sorted(REQ_PNG & actual_png):
        if (ROOT/'results'/'figures'/name).read_bytes()[:8] != b'\x89PNG\r\n\x1a\n': failures.append(f'invalid PNG signature: {name}')

    summary=m.get('summary',{})
    if summary.get('csv_count')!=len(list((ROOT/'results'/'data').glob('*.csv'))): failures.append('manifest csv_count mismatch')
    if summary.get('figure_count')!=len(list((ROOT/'results'/'figures').glob('*.png'))): failures.append('manifest figure_count mismatch')

    req=[
        'README.md','PROJECT_STATUS.md','RELEASE_NOTES_v3.3.md','docs/technical_report.md',
        'docs/portfolio_summary_v3.3.md','docs/reproducibility_v3.3.md','docs/experiment_catalog_v3.3.md',
        'docs/v3.3_tradeoff_matrix.md','docs/methodological_inspirations_v3.3.md',
        'docs/v3.3_unified_resilience_architecture.md','docs/release_acceptance_v3.3.md',
        'tools/build_manifest_v33.py','tools/verify_release_v33.py','tools/run_v33_suite.py','tools/run_release_acceptance_v33.py',
    ]
    for rel in req:
        if not (ROOT/rel).exists(): failures.append(f'missing release file: {rel}')

    try:
        dist=importlib.metadata.version('commlab-ofdm'); import commlab
        if dist!='3.3.0': failures.append(f'distribution version is {dist}, expected 3.3.0')
        if commlab.__version__!='3.3.0': failures.append(f'runtime version is {commlab.__version__}, expected 3.3.0')
        try: Path(commlab.__file__).resolve().relative_to(ROOT.resolve())
        except ValueError: failures.append(f'commlab import path outside release tree: {commlab.__file__}')
    except Exception as exc: failures.append(f'package validation failed: {exc}')

    if failures:
        print('\n'.join(failures)); raise SystemExit(1)
    print(f"v3.3 release verification OK: {checked} hashed result artifacts; summary={summary}")

if __name__=='__main__': main()
