from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.sensing.resource_scheduling import joint_sensing_comm_resource_selection

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results/data'; FIG=ROOT/'results/figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
priors=[.5,1,2,4,6,10]; fracs=np.array([0,.01,.02,.04,.06,.1,.15,.2,.3]); elems=[8,16,32,64]; snr_per=.18
rows=[]; surfaces=[]
for p in priors:
    out=joint_sensing_comm_resource_selection(p,elems,fracs,snr_per,reference_std_deg=2.2)
    b=out['best']; rows.append(dict(prior_std_deg=p,optimal_sensing_fraction=b['sensing_fraction'],optimal_elements=b['elements'],posterior_std_deg=b['posterior_std_deg'],net_rate=b['net_rate']))
    for r in out['rows']: surfaces.append(dict(prior_std_deg=p,**r))
with open(DATA/'isac_sensing_resource_scheduling.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
with open(DATA/'isac_sensing_resource_surface.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=surfaces[0].keys()); w.writeheader(); w.writerows(surfaces)
fig,ax=plt.subplots(); ax.step([x['prior_std_deg'] for x in rows],[x['optimal_elements'] for x in rows],where='mid',marker='o',label='Active elements'); ax.set_xlabel('Prior angle std (deg)'); ax.set_ylabel('Optimal active ULA elements'); ax.set_title('ISAC uncertainty-aware aperture'); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(FIG/'isac_sensing_optimal_aperture.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(); ax.plot([x['prior_std_deg'] for x in rows],[100*x['optimal_sensing_fraction'] for x in rows],marker='o'); ax.set_xlabel('Prior angle std (deg)'); ax.set_ylabel('Optimal sensing overhead (%)'); ax.set_title('Sensing overhead adapts to tracking uncertainty'); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(FIG/'isac_sensing_optimal_overhead.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(); ax.plot([x['prior_std_deg'] for x in rows],[x['net_rate'] for x in rows],marker='o'); ax.set_xlabel('Prior angle std (deg)'); ax.set_ylabel('Optimized net communication rate'); ax.set_title('Joint sensing-time / beamwidth scheduling'); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(FIG/'isac_sensing_optimized_rate.png',dpi=180); plt.close(fig)
print(rows)
