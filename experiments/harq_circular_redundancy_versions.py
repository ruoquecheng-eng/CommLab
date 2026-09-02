from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.coding import SparseAccumulatorLDPC, IncrementalRedundancyCombiner, systematic_circular_rv_indices
from commlab.link import append_crc16, check_crc16
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'
def llr(bits,snr_db,rng):
    x=1-2*np.asarray(bits).astype(float); nv=1/(2*10**(snr_db/10)); y=x+np.sqrt(nv)*rng.normal(size=len(x)); return 2*y/nv

def sim(snr_db,packets=35):
    rng=np.random.default_rng(1200+snr_db); code=SparseAccumulatorLDPC(k=48,seed=1701); schemes={'RV0 repetition':False,'Circular RV 0-3':True}; out=[]
    for name,vary in schemes.items():
        okc=bits_tx=rounds=0
        for _ in range(packets):
            p=rng.integers(0,2,32,dtype=np.uint8); cw=code.encode(append_crc16(p)); buf=IncrementalRedundancyCombiner(code.n)
            for r in range(4):
                idx=systematic_circular_rv_indices(code.k,code.n,72,r if vary else 0,4); L=buf.add(idx,llr(cw[idx],snr_db,rng)); bits_tx+=len(idx)
                dec,_,ok=code.decode_min_sum(L,max_iter=20)
                if ok and check_crc16(dec): okc+=1; rounds+=r+1; break
            else: rounds+=4
        out.append((snr_db,name,okc/packets,bits_tx/packets,rounds/packets,32*okc/max(bits_tx,1)))
    return out

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rows=[]
    for s in (0,2,4,6): rows.extend(sim(s)); print(s,rows[-2:])
    with open(DATA/'harq_circular_redundancy_versions.csv','w',newline='') as f: csv.writer(f).writerows([['snr_db','scheme','success','avg_tx_bits','avg_rounds','goodput'],*rows])
    plt.figure(figsize=(7.3,4.8))
    for name in ('RV0 repetition','Circular RV 0-3'):
        a=np.array([[r[0],r[5]] for r in rows if r[1]==name],float); plt.plot(a[:,0],a[:,1],'o-',label=name)
    plt.xlabel('SNR (dB)'); plt.ylabel('Payload goodput (bit/tx-bit)'); plt.title('Project-specific HARQ Circular Redundancy Versions'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'harq_circular_rv_goodput.png',dpi=180); plt.close()
if __name__=='__main__': main()
