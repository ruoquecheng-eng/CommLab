from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from commlab.scheduling.fbl_harq_queue import simulate_fbl_harq_queue

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1602); S=5000; U=4; means=np.array([-2.,1.,4.,7.]); true=np.zeros((S,U)); true[0]=means+rng.normal(size=U)
for t in range(1,S): true[t]=means+.95*(true[t-1]-means)+rng.normal(0,.8,U)
est=true+2.0+rng.normal(0,1.0,(S,U)); arr=(rng.random((S,U))<np.array([.035,.05,.065,.08])[None,:]).astype(int)
rows=[]; blocklengths=[80,120,240,480]
variants=[('Open-loop',False,False),('OLLA only',True,False),('HARQ only',False,True),('FBL+OLLA+HARQ',True,True)]
for n in blocklengths:
    for name,olla,harq in variants:
        r=simulate_fbl_harq_queue(true,est,arr,[-4,0,4,8,12],[.5,1,2,3,4],blocklength=n,target_bler=.03,use_olla=olla,use_harq=harq,policy='delay_pf',seed=1603)
        rows.append({'blocklength':n,'scheme':name,'goodput_bits_per_use':r['goodput_bits_per_use'],'nack_rate':r['nack_rate'],
                     'p95_delay_slots':r['p95_delay_slots'],'drops':r['drops'],'mean_attempts':r['mean_attempts_per_completed']})
df=pd.DataFrame(rows); df.to_csv(DATA/'fbl_harq_queue_coupled.csv',index=False)
for metric,ylabel,fn in [('goodput_bits_per_use','Goodput (information bit/channel use)','fbl_harq_queue_goodput.png'),('nack_rate','NACK rate','fbl_harq_queue_nack.png'),('p95_delay_slots','P95 packet delay (slots)','fbl_harq_queue_delay.png')]:
    fig,ax=plt.subplots()
    for name,_,_ in variants:
        s=df[df.scheme==name]; ax.plot(s.blocklength,s[metric],marker='o',label=name)
    ax.set_xlabel('Blocklength (complex channel uses)'); ax.set_ylabel(ylabel); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/fn,dpi=180); plt.close(fig)
print(df.to_string(index=False))
