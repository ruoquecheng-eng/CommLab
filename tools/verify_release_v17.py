from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/'results'/'manifest_v1.7.json'
def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def main():
    m=json.loads(MANIFEST.read_text()); failures=[]; checked=0
    for group in ('csv','figures'):
        for item in m[group]:
            p=ROOT/item['path']; checked+=1
            if not p.exists(): failures.append(f'missing: {item["path"]}')
            elif sha256(p)!=item['sha256']: failures.append(f'hash mismatch: {item["path"]}')
    req=['README.md','PROJECT_STATUS.md','RELEASE_NOTES_v1.7.md','docs/technical_report.md','docs/portfolio_summary_v1.7.md','docs/reproducibility_v1.7.md','docs/experiment_catalog_v1.7.md','docs/v1.7_tradeoff_matrix.md','docs/methodological_inspirations_v1.7.md']
    for rel in req:
        if not (ROOT/rel).exists(): failures.append(f'missing release file: {rel}')
    if failures: print('\n'.join(failures)); raise SystemExit(1)
    print(f'v1.7 release verification OK: {checked} hashed result artifacts + {len(req)} required release files')
if __name__=='__main__': main()
