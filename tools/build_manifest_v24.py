from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''): h.update(c)
 return h.hexdigest()
def rows(pattern):
 return [{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(ROOT.glob(pattern))]
m={'release':'v2.4','package_version':'2.4.0','csv':rows('results/data/*.csv'),'figures':rows('results/figures/*.png')}
(ROOT/'results'/'manifest_v2.4.json').write_text(json.dumps(m,indent=2)+'\n')
print(len(m['csv']),len(m['figures']),len(m['csv'])+len(m['figures']))
