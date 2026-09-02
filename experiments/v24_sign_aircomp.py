from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_sign_aircomp
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-5,0,5,10]:
    for k in [3,5,9,15,31,63]:
        o=simulate_sign_aircomp(n_clients=k,snr_db=snr,client_gradient_noise=.7,trials=1000,seed=2440)
        rows.append({'snr_db':snr,'n_clients':k,'byzantine_fraction':0,'sign_error_rate':o['sign_error_rate'],'vote_margin':o['mean_vote_margin']})
for b in [0,.05,.1,.2,.3,.4]:
    o=simulate_sign_aircomp(n_clients=31,snr_db=5,client_gradient_noise=.7,byzantine_fraction=b,trials=1200,seed=2441)
    rows.append({'snr_db':5,'n_clients':31,'byzantine_fraction':b,'sign_error_rate':o['sign_error_rate'],'vote_margin':o['mean_vote_margin']})
with open(OUT/'v24_sign_aircomp.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
plt.figure()
for snr in [-5,0,5,10]:
    rr=[r for r in rows if r['snr_db']==snr and r['byzantine_fraction']==0]; plt.plot([r['n_clients'] for r in rr],[r['sign_error_rate'] for r in rr],marker='o',label=f'{snr} dB')
plt.xlabel('Clients'); plt.ylabel('Majority-sign error rate'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_sign_aircomp_scaling.png',dpi=180); plt.close()
rr=[r for r in rows if r['n_clients']==31 and r['snr_db']==5 and r['byzantine_fraction']>=0]
# Deduplicate zero baseline for plot
seen={}; [seen.setdefault(r['byzantine_fraction'],r) for r in rr]; rr=list(seen.values())
plt.figure(); plt.plot([100*r['byzantine_fraction'] for r in rr],[r['sign_error_rate'] for r in rr],marker='o'); plt.xlabel('Sign-flipping clients (%)'); plt.ylabel('Majority-sign error rate'); plt.tight_layout(); plt.savefig(FIG/'v24_sign_aircomp_adversaries.png',dpi=180); plt.close()
print(rr)
