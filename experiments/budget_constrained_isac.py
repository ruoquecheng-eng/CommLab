from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.sensing.budget_control import simulate_budget_constrained_sensing

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
proc=np.r_[np.full(80,.05),np.linspace(.1,1.0,80),np.full(80,.8),np.linspace(.8,.05,80),np.full(80,.05)]
rows=[]; example=None
for budget in [.02,.05,.08,.12]:
    o=simulate_budget_constrained_sensing(proc,.5,[8,16,32,64],[0,.02,.05,.08,.12,.16,.22],.08,budget,
                                          information_weight=3.0,dual_step=.8)
    phase=[float(o['sensing_fraction'][i*80:(i+1)*80].mean()) for i in range(5)]
    rows.append({'budget':budget,'used_sensing_fraction':o['mean_sensing_fraction'],
                 'mean_posterior_std_deg':o['mean_posterior_std_deg'],'mean_payload_rate':o['mean_payload_rate'],
                 **{f'phase_{i+1}_sensing':v for i,v in enumerate(phase)}})
    if budget==.05: example=o
df=pd.DataFrame(rows); df.to_csv(OUT/'budget_constrained_isac.csv',index=False)
plt.figure(figsize=(6.5,4.2)); plt.plot(df.budget,df.used_sensing_fraction,marker='o',label='Actual use')
plt.plot(df.budget,df.budget,linestyle='--',label='Budget ceiling')
plt.xlabel('Long-Term Sensing Budget'); plt.ylabel('Mean Sensing Fraction'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'budget_isac_resource_use.png',dpi=180); plt.close()
fig,ax=plt.subplots(figsize=(7,4.2)); ax.plot(proc,label='Process uncertainty (deg/slot)')
ax.plot(4*example['sensing_fraction'],label='4× sensing fraction')
ax.set_xlabel('Slot'); ax.grid(alpha=.2); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/'budget_isac_adaptive_trace.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
