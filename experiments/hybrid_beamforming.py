from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.mimo import sparse_geometric_mimo_channel, full_digital_svd_rate, hybrid_dft_svd_rate
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'
def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1107); rows=[]; snr=10
    for rf in (2,3,4,6,8):
        h=[]; f=[]
        for _ in range(1800):
            H,_,_=sparse_geometric_mimo_channel(8,32,4,rng); f.append(full_digital_svd_rate(H,snr,2)); h.append(hybrid_dft_svd_rate(H,snr,2,rf))
        rows.append((rf,np.mean(h),np.mean(f),np.mean(np.array(h)/np.array(f)),np.percentile(h,10)))
        print(rf,rows[-1])
    with open(DATA/'hybrid_beamforming.csv','w',newline='') as g: csv.writer(g).writerows([['rf_chains','hybrid_mean_rate','full_digital_mean_rate','mean_rate_ratio','hybrid_p10_rate'],*rows])
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='DFT analog + digital SVD'); plt.axhline(a[0,2],ls='--',label='Full-digital SVD'); plt.xlabel('RF chains'); plt.ylabel('Mean spectral efficiency (bit/s/Hz)'); plt.title('32x8 Sparse MIMO: Hybrid Beamforming vs RF-Chain Count'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'hybrid_beamforming_rate.png',dpi=180); plt.close()
if __name__=='__main__': main()
