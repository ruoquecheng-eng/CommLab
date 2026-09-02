from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_digital_twin_sync
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for interval in [2,4,8,12,16,24]:
    rr=[simulate_digital_twin_sync(policy='periodic',periodic_interval=interval,seed=s) for s in range(18)]
    rows.append(['periodic',interval,np.mean([x['position_rmse'] for x in rr]),np.mean([x['p95_position_error'] for x in rr]),np.mean([x['mean_aoii'] for x in rr]),np.mean([x['normalized_radio_load_per_slot'] for x in rr]),np.mean([x['update_attempt_fraction'] for x in rr]),np.mean([x['update_success_fraction'] for x in rr])])
for p in ['error_full','semantic_delta']:
    for th in [.5,1.0,1.5,2.5,4.0,6.0]:
        rr=[simulate_digital_twin_sync(policy=p,error_threshold=th,seed=s) for s in range(18)]
        rows.append([p,th,np.mean([x['position_rmse'] for x in rr]),np.mean([x['p95_position_error'] for x in rr]),np.mean([x['mean_aoii'] for x in rr]),np.mean([x['normalized_radio_load_per_slot'] for x in rr]),np.mean([x['update_attempt_fraction'] for x in rr]),np.mean([x['update_success_fraction'] for x in rr])])
with (DATA/'v28_digital_twin_sync.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['policy','control_parameter','position_rmse','p95_position_error','mean_aoii','normalized_radio_load_per_slot','update_attempt_fraction','update_success_fraction']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['periodic','error_full','semantic_delta']:
    r=[x for x in rows if x[0]==p]; plt.plot([x[5] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Normalized radio load / slot'); plt.ylabel('Position RMSE'); plt.title('Digital-twin synchronization: accuracy vs radio load'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_digital_twin_rmse_load.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['periodic','error_full','semantic_delta']:
    r=[x for x in rows if x[0]==p]; plt.plot([x[5] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Normalized radio load / slot'); plt.ylabel('Mean AoII proxy'); plt.title('Semantic state updates spend radio only when the twin is wrong'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_digital_twin_aoii_load.png',dpi=170); plt.close()
print('wrote v28 digital twin sync')
