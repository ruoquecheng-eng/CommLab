from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_selection_biased_fl
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
strategies=['random','channel','age_channel','gradient_channel']; disparities=[0,4,8,12]; rows=[]
for d in disparities:
    for s in strategies:
        vals=[]
        for rep in range(6):
            o=simulate_selection_biased_fl(s,rounds=120,n_select=4,channel_disparity_db=d,age_weight=2.0,heterogeneity=.7,seed=2100+rep)
            vals.append([o['final_global_loss'],o['parameter_error_to_global_optimum'],o['group_loss_gap'],o['participation_jain'],o['plus_selection_fraction'],o['mean_selected_weakest_gain']])
        m=np.mean(vals,axis=0); sd=np.std(vals,axis=0)
        rows.append((d,s,*m,*sd))
with (D/'v21_non_iid_client_selection.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['channel_disparity_db','strategy','final_loss','parameter_error','group_loss_gap','participation_jain','strong_group_selection_fraction','mean_selected_weakest_gain','sd_final_loss','sd_parameter_error','sd_group_loss_gap','sd_participation_jain','sd_strong_group_fraction','sd_weakest_gain']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for s in strategies:
    r=[x for x in rows if x[1]==s]; ax.plot([x[0] for x in r],[x[2] for x in r],'o-',label=s.replace('_',' '))
ax.set(xlabel='Long-term channel disparity between non-IID client groups (dB)',ylabel='Final global objective',title='Communication-Driven Client Selection Can Bias Non-IID FL'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_non_iid_selection_loss.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for s in strategies:
    r=[x for x in rows if x[1]==s]; ax.plot([x[0] for x in r],[x[5] for x in r],'o-',label=s.replace('_',' '))
ax.set(xlabel='Channel disparity (dB)',ylabel='Participation Jain fairness',ylim=(.45,1.02),title='Client Participation Fairness'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_non_iid_selection_fairness.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for s in strategies:
    r=[x for x in rows if x[1]==s]; ax.plot([x[0] for x in r],[x[7] for x in r],'o-',label=s.replace('_',' '))
ax.set(xlabel='Channel disparity (dB)',ylabel='Mean weakest selected link amplitude',title='Communication Quality Gained by Aggressive Selection'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_non_iid_selection_channel_gain.png',dpi=180); plt.close(fig)
print(rows)
