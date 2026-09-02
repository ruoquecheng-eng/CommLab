from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/'results'/'manifest_v1.0.json'
def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()
def main():
    m=json.loads(MANIFEST.read_text()); failures=[]; checked=0
    for group in ('csv','figures'):
        for item in m[group]:
            p=ROOT/item['path']; checked+=1
            if not p.exists(): failures.append(f'missing: {item["path"]}')
            elif sha256(p)!=item['sha256']: failures.append(f'hash mismatch: {item["path"]}')
    required=['README.md','PROJECT_STATUS.md','RELEASE_NOTES_v1.0.md','docs/technical_report.md','docs/portfolio_summary_v1.0.md','docs/reproducibility_v1.0.md','docs/experiment_catalog_v1.0.md','docs/methodological_inspirations.md']
    for rel in required:
        if not (ROOT/rel).exists(): failures.append(f'missing release file: {rel}')
    if failures:
        print('\n'.join(failures)); raise SystemExit(1)
    print(f'v1.0 release verification OK: {checked} hashed result artifacts + {len(required)} required release files')
if __name__=='__main__': main()
