from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.mimo import zf_detect, mmse_detect, ml_detect_small, k_best_detect
from commlab.modulation import QAMModem
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(810); modem=QAMModem(16)
    labels=np.arange(16,dtype=np.uint8)[:,None]
    bits=((labels >> np.arange(3,-1,-1)) & 1).astype(np.uint8); const=modem.modulate(bits.reshape(-1))
    rows=[]
    for snr_db in (6,10,14,18,22):
        nv=10**(-snr_db/10); n=2600
        H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2)
        idx=rng.integers(0,16,size=(n,2)); x=const[idx]
        noise=np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2))); y=np.einsum('bij,bj->bi',H,x)+noise
        methods={'ZF':zf_detect(y,H),'MMSE':mmse_detect(y,H,nv),'K1':k_best_detect(y,H,const,1),'K4':k_best_detect(y,H,const,4),'K16':k_best_detect(y,H,const,16),'ML':ml_detect_small(y,H,const)}
        true=bits[idx].reshape(-1); vals={}
        for name,z in methods.items():
            nearest=np.argmin(abs(z[...,None]-const[None,None,:]),axis=-1); vals[name]=float(np.mean(bits[nearest].reshape(-1)!=true))
        # deterministic node expansion proxy for Nt=2, M=16
        exp1=16+16; exp4=16+4*16; exp16=16+16*16
        rows.append((snr_db,vals['ZF'],vals['MMSE'],vals['K1'],vals['K4'],vals['K16'],vals['ML'],exp1,exp4,exp16,256))
        print('SNR',snr_db,vals)
    with open(DATA/'mimo_kbest_detection.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','zf_ber','mmse_ber','k1_ber','k4_ber','k16_ber','ml_ber','k1_nodes','k4_nodes','k16_nodes','ml_vectors']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,5.0))
    for j,l,m in [(1,'ZF','o-'),(2,'MMSE','s-'),(3,'K-best K=1','d-'),(4,'K-best K=4','^-'),(5,'K-best K=16','v-'),(6,'Exhaustive ML','*-')]: plt.semilogy(a[:,0],np.maximum(a[:,j],1e-5),m,label=l)
    plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('2x2 16-QAM: K-best Complexity/Performance Ladder'); plt.grid(True,which='both',alpha=.3); plt.legend(ncol=2); plt.tight_layout(); plt.savefig(FIG/'mimo_kbest_detection_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.1,4.7)); plt.bar(['K=1','K=4','K=16','ML'],[32,80,272,256]); plt.ylabel('Search nodes / candidate vectors (proxy)'); plt.title('2x2 16-QAM Detection Search Effort'); plt.tight_layout(); plt.savefig(FIG/'mimo_kbest_complexity.png',dpi=180); plt.close()
if __name__=='__main__': main()
