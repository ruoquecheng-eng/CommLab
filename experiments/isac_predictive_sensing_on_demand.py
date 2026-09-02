from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing.closed_loop import simulate_sensing_on_demand, simulate_predictive_sensing_on_demand

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
q=np.r_[np.full(80,.08),np.linspace(.2,1.4,80),np.full(80,.12)]
common=(q,.5,[8,16,32,64],[0,.01,.02,.04,.06,.1,.15,.2,.3],.16,2.2)
res={
    'No sensing':simulate_sensing_on_demand(q,.5,[8,16,32,64],[0],.16,2.2,fixed_sensing_fraction=0),
    'Fixed 5%':simulate_sensing_on_demand(q,.5,[8,16,32,64],[0],.16,2.2,fixed_sensing_fraction=.05),
    'Myopic adaptive':simulate_sensing_on_demand(*common),
    '2-step predictive':simulate_predictive_sensing_on_demand(*common,lookahead_weight=.9),
}
summary=[]; trace=[]
for name,r in res.items():
    summary.append({'scheme':name,'mean_net_rate':r['mean_net_rate'],'mean_sensing_fraction':r['mean_sensing_fraction'],'mean_posterior_std_deg':r['mean_posterior_std_deg']})
    for x in r['rows']: trace.append({'scheme':name,**x})
pd.DataFrame(summary).to_csv(DATA/'isac_predictive_sensing_summary.csv',index=False); td=pd.DataFrame(trace); td.to_csv(DATA/'isac_predictive_sensing_trace.csv',index=False)
fig,ax=plt.subplots()
for name in ['Myopic adaptive','2-step predictive','Fixed 5%']:
    s=td[td.scheme==name]; ax.plot(s.slot,100*s.sensing_fraction,label=name)
ax.axvline(80,linestyle='--',linewidth=1); ax.axvline(160,linestyle='--',linewidth=1); ax.set_xlabel('Slot'); ax.set_ylabel('Sensing overhead (%)'); ax.set_title('Sensing-on-demand around a maneuver interval'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'isac_predictive_sensing_fraction.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for name in res:
    s=td[td.scheme==name]; ax.plot(s.slot,s.posterior_std_deg,label=name)
ax.set_xlabel('Slot'); ax.set_ylabel('Posterior angle std (deg)'); ax.set_title('Tracking uncertainty under resource-control policies'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'isac_predictive_sensing_uncertainty.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(); sd=pd.DataFrame(summary).sort_values('mean_net_rate'); ax.bar(sd.scheme,sd.mean_net_rate); ax.set_ylabel('Mean net communication rate'); ax.tick_params(axis='x',rotation=20); ax.set_title('Myopic vs predictive vs oracle-tuned fixed sensing'); fig.tight_layout(); fig.savefig(FIG/'isac_predictive_sensing_net_rate.png',dpi=180); plt.close(fig)
print(pd.DataFrame(summary).to_string(index=False))
