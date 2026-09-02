from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_risk_sensitive_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for shock in [.3,.6,1.0,1.4,1.8,2.2]:
    for policy in ['mean_value','risk_value']:
        rr=[simulate_risk_sensitive_control(slots=3000,policy=policy,mean_snr_db=-3,shock_multiplier=shock,risk_weight=1.0,seed=s) for s in range(6)]
        rows.append([shock,policy,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['cvar95_control_cost'] for x in rr]),np.mean([x['mean_information_age'] for x in rr])])
with (DATA/'v30_risk_sensitive_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['shock_multiplier','policy','mean_control_cost','p95_control_cost','cvar95_control_cost','mean_information_age']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['mean_value','risk_value']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Rare-shock severity multiplier'); plt.ylabel('CVaR95 closed-loop cost'); plt.title('Risk-sensitive scheduling matters only in the tail-dominated regime'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_risk_cvar.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['mean_value','risk_value']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Rare-shock severity multiplier'); plt.ylabel('Mean closed-loop cost'); plt.title('Tail protection can cost average performance'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_risk_mean.png',dpi=170); plt.close()
print('wrote v30 risk-sensitive control')
