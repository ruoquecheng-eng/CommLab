from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import SparseAccumulatorLDPC, ldpc_incremental_redundancy_schedule, IncrementalRedundancyCombiner
from commlab.link import append_crc16, check_crc16, ChaseCombiner

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def bpsk_llr(bits, snr_db, rng):
    b=np.asarray(bits,dtype=np.uint8); x=1.0-2.0*b.astype(float)
    nv=1.0/(2*10**(snr_db/10)); y=x+np.sqrt(nv)*rng.normal(size=len(x))
    return 2*y/nv


def simulate(snr_db, packets=45, max_rounds=4, seed=10001):
    rng=np.random.default_rng(seed+int(10*snr_db)); code=SparseAccumulatorLDPC(k=48,seed=1701)
    schedule=ldpc_incremental_redundancy_schedule(code.k,code.n,max_rounds)
    stats={m:{'ok':0,'bits':0,'rounds':0} for m in ['Chase full-code','Incremental redundancy']}
    for _ in range(packets):
        payload=rng.integers(0,2,32,dtype=np.uint8); info=append_crc16(payload); cw=code.encode(info)
        # Chase: repeat the full mother code and sum LLRs.
        chase=ChaseCombiner(code.n)
        for r in range(max_rounds):
            L=chase.add(bpsk_llr(cw,snr_db,rng)); stats['Chase full-code']['bits']+=code.n
            dec,_,ok=code.decode_min_sum(L,max_iter=22)
            if ok and check_crc16(dec):
                stats['Chase full-code']['ok']+=1; stats['Chase full-code']['rounds']+=r+1; break
        else: stats['Chase full-code']['rounds']+=max_rounds
        # IR: reveal new parity on each round; unseen mother-code bits are erasures.
        ir=IncrementalRedundancyCombiner(code.n)
        for r,idx in enumerate(schedule):
            L=ir.add(idx,bpsk_llr(cw[idx],snr_db,rng)); stats['Incremental redundancy']['bits']+=len(idx)
            dec,_,ok=code.decode_min_sum(L,max_iter=22)
            if ok and check_crc16(dec):
                stats['Incremental redundancy']['ok']+=1; stats['Incremental redundancy']['rounds']+=r+1; break
        else: stats['Incremental redundancy']['rounds']+=len(schedule)
    rows=[]
    for m,s in stats.items():
        success=s['ok']/packets; goodput=(32*s['ok'])/max(s['bits'],1)
        rows.append((snr_db,m,success,s['bits']/packets,s['rounds']/packets,goodput))
    return rows


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rows=[]
    for s in [0,2,4,6,8]:
        q=simulate(s); rows.extend(q)
        print(f'{s:>2} dB  '+' | '.join(f'{r[1]} success={r[2]:.3f}, avg bits={r[3]:.1f}, goodput={r[5]:.3f}' for r in q))
    with open(DATA/'harq_incremental_redundancy.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','scheme','packet_success_rate','avg_transmitted_coded_bits','avg_rounds','payload_goodput_bit_per_tx_bit']); w.writerows(rows)
    plt.figure(figsize=(7.5,5))
    for m in ['Chase full-code','Incremental redundancy']:
        a=np.array([[r[0],r[2]] for r in rows if r[1]==m],float); plt.plot(a[:,0],a[:,1],'o-',label=m)
    plt.xlabel('BPSK Eb/N0-like SNR (dB)'); plt.ylabel('Packet success probability'); plt.title('HARQ Reliability: Chase vs Incremental Redundancy'); plt.grid(alpha=.3); plt.ylim(0,1.04); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'harq_ir_success.png',dpi=180); plt.close()
    plt.figure(figsize=(7.5,5))
    for m in ['Chase full-code','Incremental redundancy']:
        a=np.array([[r[0],r[5]] for r in rows if r[1]==m],float); plt.plot(a[:,0],a[:,1],'o-',label=m)
    plt.xlabel('BPSK Eb/N0-like SNR (dB)'); plt.ylabel('Delivered payload bits / transmitted coded bit'); plt.title('HARQ Efficiency: Soft Repetition vs New Redundancy'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'harq_ir_goodput.png',dpi=180); plt.close()

if __name__=='__main__': main()
