from __future__ import annotations
import csv, hashlib, importlib.metadata, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'results'/'manifest_v3.2.json'


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    failures=[]
    if not MANIFEST.exists():
        raise SystemExit('missing results/manifest_v3.2.json')
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if m.get('release')!='v3.2' or m.get('package_version')!='3.2.0':
        failures.append('manifest release/version mismatch')

    checked=0
    manifested=set()
    for group in ('csv','figures'):
        for item in m.get(group,[]):
            p=ROOT/item['path']; checked+=1; manifested.add(item['path'])
            if not p.exists(): failures.append(f'missing: {item["path"]}')
            elif sha256(p)!=item['sha256']: failures.append(f'hash mismatch: {item["path"]}')
    actual={str(p.relative_to(ROOT)) for p in (ROOT/'results'/'data').glob('*.csv')}
    actual|={str(p.relative_to(ROOT)) for p in (ROOT/'results'/'figures').glob('*.png')}
    for rel in sorted(actual-manifested): failures.append(f'unmanifested result artifact: {rel}')
    for rel in sorted(manifested-actual): failures.append(f'manifest entry missing on disk: {rel}')


    # v3.2-specific artifact sanity: the release must contain both the preserved
    # draft work and the predictive-resilience main line. Numeric cells that can
    # be parsed as floats must be finite; PNGs must carry the standard signature.
    required_csv = {
        'v32_semantic_harq.csv','v32_mixed_control_inference.csv',
        'v32_failure_domain_replication.csv','v32_service_migration.csv',
        'v32_safety_bit_allocation.csv','v32_predictive_failure_migration.csv',
        'v32_failure_domain_zone_risk.csv','v32_chance_constrained_inference.csv',
        'v32_control_uep.csv','v32_multi_connectivity.csv',
        'v32_multi_connectivity_frontier.csv','v32_multiconnectivity_safety_control.csv',
    }
    actual_csv_names={p.name for p in (ROOT/'results'/'data').glob('*.csv')}
    for name in sorted(required_csv-actual_csv_names):
        failures.append(f'missing v3.2 dataset: {name}')
    for name in sorted(required_csv & actual_csv_names):
        p=ROOT/'results'/'data'/name
        with p.open(newline='',encoding='utf-8') as f:
            rows=list(csv.reader(f))
        if len(rows) < 2 or not rows[0]:
            failures.append(f'empty v3.2 dataset: {name}')
            continue
        if len(rows[0]) != len(set(rows[0])):
            failures.append(f'duplicate CSV column in {name}')
        for ri,row in enumerate(rows[1:],start=2):
            if len(row) != len(rows[0]):
                failures.append(f'CSV width mismatch: {name}:{ri}')
                break
            for cell in row:
                try:
                    val=float(cell)
                except ValueError:
                    continue
                if not math.isfinite(val):
                    failures.append(f'non-finite numeric value: {name}:{ri}')
                    break
    for p in (ROOT/'results'/'figures').glob('v32_*.png'):
        if p.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
            failures.append(f'invalid PNG signature: {p.name}')

    summary=m.get('summary',{})
    if summary.get('csv_count') != len(list((ROOT/'results'/'data').glob('*.csv'))):
        failures.append('manifest csv_count mismatch')
    if summary.get('figure_count') != len(list((ROOT/'results'/'figures').glob('*.png'))):
        failures.append('manifest figure_count mismatch')

    req=[
        'README.md','PROJECT_STATUS.md','RELEASE_NOTES_v3.2.md','docs/technical_report.md',
        'docs/portfolio_summary_v3.2.md','docs/reproducibility_v3.2.md','docs/experiment_catalog_v3.2.md',
        'docs/v3.2_tradeoff_matrix.md','docs/methodological_inspirations_v3.2.md','docs/release_acceptance_v3.2.md',
        'docs/v3.2_reliability_orchestration_architecture.md','docs/v3.2_predictive_resilience_architecture.md',
        'tools/build_manifest_v32.py','tools/verify_release_v32.py','tools/run_v32_suite.py',
        'tools/run_release_acceptance_v32.py',
    ]
    for rel in req:
        if not (ROOT/rel).exists(): failures.append(f'missing release file: {rel}')

    try:
        dist=importlib.metadata.version('commlab-ofdm')
        import commlab
        if dist!='3.2.0': failures.append(f'distribution version is {dist}, expected 3.2.0')
        if commlab.__version__!='3.2.0': failures.append(f'runtime version is {commlab.__version__}, expected 3.2.0')
        try:
            Path(commlab.__file__).resolve().relative_to(ROOT.resolve())
        except ValueError:
            failures.append(f'commlab import path outside release tree: {commlab.__file__}')
    except Exception as exc:
        failures.append(f'package validation failed: {exc}')

    if failures:
        print('\n'.join(failures)); raise SystemExit(1)
    summary=m.get('summary',{})
    print(f"v3.2 release verification OK: {checked} hashed result artifacts; summary={summary}")

if __name__=='__main__':
    main()
