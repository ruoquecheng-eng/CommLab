from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.link import OuterLoopLinkAdaptation, select_mcs, logistic_bler

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def simulate(use_olla, seed=10004, slots=8000):
    rng=np.random.default_rng(seed); thresholds=np.array([-3,1,5,9,13],float); eff=np.array([.5,1.,2.,3.,4.5])
    olla=OuterLoopLinkAdaptation(target_bler=.1,nack_step_db=.22) if use_olla else None
    offset=[]; good=[]; nack=[]; mcs=[]; true_snr=[]
    state=8.0
    for t in range(slots):
        state=.96*state+.04*8.0+rng.normal(scale=.7); s=float(np.clip(state,-5,20)); est=s+2.5+rng.normal(scale=1.2)
        eff_snr=olla.effective_snr_db(est) if olla else est
        idx,se=select_mcs(eff_snr,thresholds,eff); p=logistic_bler(s,thresholds[idx],width_db=.9,midpoint_bler=.1)
        fail=bool(rng.random()<p); ack=not fail
        if olla: olla.update(ack); off=olla.offset_db
        else: off=0.0
        offset.append(off); good.append(0.0 if fail else se); nack.append(float(fail)); mcs.append(idx); true_snr.append(s)
    return np.array(offset),np.array(good),np.array(nack),np.array(mcs),np.array(true_snr)


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rows=[]; traces={}
    for name,use in [('Biased open-loop',False),('OLLA target BLER=10%',True)]:
        off,g,n,m,s=simulate(use); traces[name]=(off,g,n,m,s); tail=slice(1000,None)
        rows.append((name,np.mean(n[tail]),np.mean(g[tail]),np.mean(m[tail]),np.mean(off[tail])))
        print(name, 'BLER=',rows[-1][1],'goodput=',rows[-1][2],'avg MCS=',rows[-1][3],'offset=',rows[-1][4])
    with open(DATA/'olla_link_adaptation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['scheme','steady_bler','steady_goodput_bit_per_use','mean_mcs_index','mean_snr_backoff_db']); w.writerows(rows)
    plt.figure(figsize=(8,5))
    off,g,n,m,s=traces['OLLA target BLER=10%']; win=250; roll=np.convolve(n,np.ones(win)/win,mode='valid')
    plt.plot(roll,label=f'{win}-slot BLER'); plt.axhline(.1,linestyle='--',label='10% target'); plt.xlabel('Slot'); plt.ylabel('BLER'); plt.title('Outer-Loop Link Adaptation Tracks Target BLER'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'olla_bler_tracking.png',dpi=180); plt.close()
    plt.figure(figsize=(8,5)); plt.plot(off,label='OLLA SNR backoff'); plt.axhline(2.5,linestyle='--',label='Mean estimator bias'); plt.xlabel('Slot'); plt.ylabel('Backoff (dB)'); plt.title('OLLA Learns a Conservative Offset from ACK/NACK'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'olla_offset_tracking.png',dpi=180); plt.close()

if __name__=='__main__': main()
