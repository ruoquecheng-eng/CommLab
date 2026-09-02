from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.scheduling import jain_fairness_index
from commlab.scheduling.queue_aware import simulate_packet_scheduler

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(9031); slots,users,resources=1200,4,8
    avg_snr_db=np.array([0.,4.,8.,12.]); fading=rng.exponential(size=(slots,users,resources))
    snr=10**(avg_snr_db[None,:,None]/10)*fading
    capacity=1400*np.log2(1+snr)  # abstract payload bits per RB-slot
    arrivals=rng.poisson(.60,size=(slots,users)); packet_bits=10000
    policies=[('Round Robin','round_robin'),('Max Rate','max_rate'),('Proportional Fair','pf'),('Delay-aware PF','delay_pf')]
    rows=[]; traces={}
    for label,policy in policies:
        r=simulate_packet_scheduler(capacity,arrivals,packet_size_bits=packet_bits,policy=policy,beta=.98,delay_weight=3.0,target_delay_slots=15)
        fairness=jain_fairness_index(r['delivered_bits']); final_backlog=float(np.sum(r['backlog_bits'][-1]))
        rows.append((label,r['total_delivered_bits']/slots,fairness,r['mean_delay_slots'],r['p95_delay_slots'],r['completed_packets'],r['pending_packets'],final_backlog,*r['delivered_bits']))
        traces[label]=np.sum(r['backlog_bits'],axis=1)
        print(f'{label:20s} throughput={r["total_delivered_bits"]/slots:8.1f} fair={fairness:.3f} meanD={r["mean_delay_slots"]:6.2f} p95={r["p95_delay_slots"]:6.1f} pending={r["pending_packets"]:4d} backlog={final_backlog/1e6:.3f} Mbit')
    with open(DATA/'queue_aware_ofdma.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['scheduler','throughput_bits_per_slot','jain_fairness','mean_delay_slots','p95_delay_slots','completed_packets','pending_packets','final_backlog_bits','user0_bits','user1_bits','user2_bits','user3_bits']); w.writerows(rows)
    x=np.arange(len(rows)); throughput=[r[1] for r in rows]; fairness=[r[2] for r in rows]
    fig,ax=plt.subplots(figsize=(8.1,5.0)); ax.bar(x,throughput); ax.set_xticks(x,[r[0] for r in rows],rotation=15); ax.set_ylabel('Delivered bits / slot'); ax.set_title('Queued OFDMA: Throughput under Heterogeneous Channels'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'queue_aware_throughput.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.1,5.0)); ax.bar(x,[r[4] for r in rows]); ax.set_xticks(x,[r[0] for r in rows],rotation=15); ax.set_ylabel('95th-percentile packet delay (slots)'); ax.set_title('Queue-Aware Scheduling Tail Delay'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'queue_aware_p95_delay.png',dpi=180); plt.close(fig)
    plt.figure(figsize=(8.0,5.0))
    for label in traces: plt.plot(traces[label]/1e6,label=label,alpha=.9)
    plt.xlabel('Slot'); plt.ylabel('Total queued payload (Mbit)'); plt.title('Queue Backlog Evolution'); plt.grid(True,alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'queue_aware_backlog.png',dpi=180); plt.close()
    fig,ax=plt.subplots(figsize=(7.7,4.8)); ax.bar(x,fairness); ax.set_ylim(0,1.02); ax.set_xticks(x,[r[0] for r in rows],rotation=15); ax.set_ylabel('Jain fairness index'); ax.set_title('Long-Term User Fairness'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'queue_aware_fairness.png',dpi=180); plt.close(fig)

if __name__=='__main__': main()
