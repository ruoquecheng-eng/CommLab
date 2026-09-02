from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo import semi_orthogonal_user_selection, strongest_norm_user_selection, mu_zf_precoder, downlink_sinr, sum_rate_from_sinr, favorable_propagation_metric
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1202); nt=8; kc=24; ks=4; snr=10**(10/10); trials=1000
stats={k:[] for k in ['random','strongest','SUS']}
for _ in range(trials):
    # Candidate users have mild unequal path gains to make norm-only selection tempting.
    gain_db=rng.normal(0,3,kc); H=((rng.normal(size=(kc,nt))+1j*rng.normal(size=(kc,nt)))/np.sqrt(2))*10**(gain_db[:,None]/20)
    idxs={
        'random':rng.choice(kc,ks,replace=False),
        'strongest':strongest_norm_user_selection(H,ks),
        'SUS':semi_orthogonal_user_selection(H,ks,alpha=.5),
    }
    for name,idx in idxs.items():
        S=H[idx]; W=mu_zf_precoder(S); sinr=downlink_sinr(S,W,snr)
        stats[name].append((sum_rate_from_sinr(sinr),np.linalg.cond(S@S.conj().T),favorable_propagation_metric(S)))
rows=[]
for name,v in stats.items():
    a=np.asarray(v); rows.append(dict(scheme=name,mean_sum_rate=a[:,0].mean(),p10_sum_rate=np.quantile(a[:,0],.1),median_gram_condition=np.median(a[:,1]),mean_user_correlation=a[:,2].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'mu_mimo_user_selection.csv',index=False)
fig,ax=plt.subplots(figsize=(6.5,4.5)); ax.bar(df.scheme,df.mean_sum_rate); ax.set_ylabel('Mean ZF sum rate (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'mu_mimo_user_selection_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,4.5)); ax.bar(df.scheme,df.median_gram_condition); ax.set_yscale('log'); ax.set_ylabel('Median cond(H Hᴴ)'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'mu_mimo_user_selection_condition.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
