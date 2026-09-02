from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.scheduling import proportional_fair_schedule, jain_fairness_index
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(812); slots=500; users=4; carriers=48
    # Deliberately unequal average SNRs; AR(1) log-SNR variation creates local peaks.
    means_db=np.array([3.,7.,11.,15.]); rho=.92; z=np.zeros((slots,users,carriers)); z[0]=rng.normal(size=(users,carriers))
    for t in range(1,slots): z[t]=rho*z[t-1]+np.sqrt(1-rho**2)*rng.normal(size=(users,carriers))
    snr_db=means_db[None,:,None]+3.0*z; rate=np.log2(1+10**(snr_db/10))
    # Max-rate scheduler.
    max_alloc=np.argmax(rate,axis=1); max_slot=np.zeros((slots,users))
    for t in range(slots):
        for u in range(users):
            m=max_alloc[t]==u; max_slot[t,u]=rate[t,u,m].sum()
    # Frequency round-robin fixed partition.
    rr_slot=np.zeros((slots,users));
    for u in range(users): rr_slot[:,u]=rate[:,u,u::users].sum(axis=1)
    pf_alloc,pf_slot,pf_state=proportional_fair_schedule(rate,beta=.98)
    schemes={'Round-robin':rr_slot,'Max-rate':max_slot,'Proportional fair':pf_slot}; rows=[]
    for name,arr in schemes.items():
        thr=arr.mean(axis=0); rows.append((name,float(thr.sum()),jain_fairness_index(thr),*thr.tolist())); print(name,'sum',thr.sum(),'fair',jain_fairness_index(thr),'users',thr)
    with open(DATA/'proportional_fair_ofdma.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['scheme','sum_rate','jain_fairness','user0','user1','user2','user3']); w.writerows(rows)
    names=[r[0] for r in rows]; sums=[r[1] for r in rows]; fairs=[r[2] for r in rows]
    plt.figure(figsize=(7.2,4.8)); x=np.arange(3); plt.bar(x,sums); plt.xticks(x,names,rotation=10); plt.ylabel('Mean sum spectral efficiency / slot'); plt.title('OFDMA Scheduling: Throughput Trade-off'); plt.tight_layout(); plt.savefig(FIG/'proportional_fair_sum_rate.png',dpi=180); plt.close()
    plt.figure(figsize=(7.2,4.8)); plt.bar(x,fairs); plt.xticks(x,names,rotation=10); plt.ylim(0,1.05); plt.ylabel("Jain's fairness index"); plt.title('OFDMA Scheduling: Fairness Trade-off'); plt.tight_layout(); plt.savefig(FIG/'proportional_fair_fairness.png',dpi=180); plt.close()
    plt.figure(figsize=(9,3.8)); plt.imshow(pf_alloc[:100].T,aspect='auto',interpolation='nearest'); plt.xlabel('Slot'); plt.ylabel('Subcarrier'); plt.title('Proportional-Fair User Allocation (first 100 slots)'); plt.colorbar(label='User index'); plt.tight_layout(); plt.savefig(FIG/'proportional_fair_allocation.png',dpi=180); plt.close()
if __name__=='__main__': main()
