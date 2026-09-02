from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.mimo import zf_detect, mmse_detect, mmse_sic_detect, k_best_detect
from commlab.modulation import QAMModem
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1101)
    modem=QAMModem(16); labels=np.arange(16,dtype=np.uint8)[:,None]; bits=((labels>>np.arange(3,-1,-1))&1).astype(np.uint8); const=modem.modulate(bits.reshape(-1))
    rows=[]
    for snr_db in (6,10,14,18,22):
        nv=10**(-snr_db/10); n=5000; H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2)
        idx=rng.integers(0,16,size=(n,2)); x=const[idx]; y=np.einsum('bij,bj->bi',H,x)+np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2)))
        methods={'ZF':zf_detect(y,H),'MMSE':mmse_detect(y,H,nv),'MMSE-SIC':mmse_sic_detect(y,H,const,nv,ordered=True),'K-best K=4':k_best_detect(y,H,const,4)}
        truth=bits[idx].reshape(-1); vals={}
        for name,z in methods.items():
            nearest=np.argmin(np.abs(z[...,None]-const[None,None,:]),axis=-1); vals[name]=float(np.mean(bits[nearest].reshape(-1)!=truth))
        rows.append((snr_db,vals['ZF'],vals['MMSE'],vals['MMSE-SIC'],vals['K-best K=4']))
        print(snr_db,vals)
    with open(DATA/'mimo_mmse_sic.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','zf_ber','mmse_ber','ordered_mmse_sic_ber','kbest4_ber']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,5.0))
    for j,l,m in [(1,'ZF','o-'),(2,'MMSE','s-'),(3,'Ordered MMSE-SIC','^-'),(4,'K-best K=4','d-')]: plt.semilogy(a[:,0],np.maximum(a[:,j],1e-5),m,label=l)
    plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('2x2 16-QAM: Linear, SIC and Tree-Search Detection'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_mmse_sic_ber.png',dpi=180); plt.close()
if __name__=='__main__': main()
