from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.mimo import correlated_rayleigh_mimo_channel, mimo_capacity_bits_per_hz, zf_detect, mmse_detect
from commlab.modulation import QAMModem
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(811); modem=QAMModem(4); labels=np.arange(4,dtype=np.uint8)[:,None]; bits=((labels>>np.array([1,0]))&1).astype(np.uint8); const=modem.modulate(bits.reshape(-1))
    snr_db=12; nv=10**(-snr_db/10); n=30000; rows=[]
    for rho in (0,.3,.6,.8,.9,.95):
        H=correlated_rayleigh_mimo_channel(n,2,2,rho,rho,rng); idx=rng.integers(0,4,size=(n,2)); x=const[idx]; noise=np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2))); y=np.einsum('bij,bj->bi',H,x)+noise
        true=bits[idx].reshape(-1); vals=[]
        for z in (zf_detect(y,H),mmse_detect(y,H,nv)):
            near=np.argmin(abs(z[...,None]-const[None,None,:]),axis=-1); vals.append(float(np.mean(bits[near].reshape(-1)!=true)))
        cap=mimo_capacity_bits_per_hz(H,10**(snr_db/10)); cond=np.linalg.cond(H)
        rows.append((rho,vals[0],vals[1],float(np.mean(cap)),float(np.median(cond)),float(np.percentile(cond,90))))
        print(f'rho={rho:.2f} ZF={vals[0]:.4g} MMSE={vals[1]:.4g} C={np.mean(cap):.3f} median-cond={np.median(cond):.2f}')
    with open(DATA/'mimo_spatial_correlation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['rho','zf_ber','mmse_ber','mean_capacity_bphz','median_condition_number','p90_condition_number']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.3,4.8)); plt.semilogy(a[:,0],a[:,1],'o-',label='ZF'); plt.semilogy(a[:,0],a[:,2],'s-',label='MMSE'); plt.xlabel('Tx/Rx correlation coefficient ρ'); plt.ylabel('BER at 12 dB'); plt.title('Spatial Correlation Degrades 2x2 MIMO Detection'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_spatial_correlation_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.8)); plt.plot(a[:,0],a[:,3],'o-',label='Mean capacity'); ax=plt.gca(); ax.set_xlabel('Correlation coefficient ρ'); ax.set_ylabel('Capacity (bit/s/Hz)'); ax2=ax.twinx(); ax2.plot(a[:,0],a[:,4],'s--',label='Median cond(H)'); ax2.set_ylabel('Median condition number'); plt.title('MIMO Rank/Conditioning Loss under Spatial Correlation'); plt.tight_layout(); plt.savefig(FIG/'mimo_spatial_correlation_capacity.png',dpi=180); plt.close()
if __name__=='__main__': main()
