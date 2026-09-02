from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.equalization import time_varying_ofdm_channel_matrix, linear_lmmse_ici_detect, ici_energy_fraction
from commlab.modulation import QAMModem
from commlab.metrics import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(702); modem=QAMModem(4); nfft=64; cp=16; snr_db=18; nv=10**(-snr_db/10)
    taps=np.array([1.0,0.52*np.exp(.35j),0.24*np.exp(-.5j)],complex); taps/=np.linalg.norm(taps)
    delays=np.array([0,3,8]); dopplers=(0.0,.5,1.0,1.5,2.0)
    methods=[('One-tap',0),('Banded ±1',1),('Banded ±2',2),('Banded ±4',4),('Full ICI',None)]
    rows=[]
    for nu in dopplers:
        H=time_varying_ofdm_channel_matrix(taps,delays,np.array([0.,nu,-.55*nu]),nfft,cp)
        ici=ici_energy_fraction(H)
        stats={name:[0,0] for name,_ in methods}
        for _ in range(260):
            bits=rng.integers(0,2,nfft*2,dtype=np.uint8); x=modem.modulate(bits)
            noise=np.sqrt(nv/2)*(rng.normal(size=nfft)+1j*rng.normal(size=nfft)); y=H@x+noise
            for name,bw in methods:
                xh=linear_lmmse_ici_detect(y,H,nv,bandwidth=bw)
                bh=modem.demodulate(xh); e=int(np.count_nonzero(bh!=bits)); stats[name][0]+=e; stats[name][1]+=len(bits)
        for name,_ in methods:
            ber,lo,hi=ber_with_wilson(*stats[name]); rows.append((nu,ici,name,ber,lo,hi))
        print(f'nu={nu:.2f} ICI={100*ici:.1f}% ' + ' '.join(f'{n}={stats[n][0]/stats[n][1]:.4g}' for n,_ in methods))
    with open(DATA/'ici_aware_equalization.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['doppler_bins','ici_energy_fraction','receiver','ber','ci95_low','ci95_high']); w.writerows(rows)
    plt.figure(figsize=(7.6,5.0))
    for name,_ in methods:
        q=np.array([[r[0],r[3]] for r in rows if r[2]==name],float); plt.semilogy(q[:,0],np.maximum(q[:,1],1e-5),'o-',label=name)
    plt.xlabel('Moving-path Doppler (subcarrier spacings)'); plt.ylabel('BER'); plt.title(f'ICI-Aware OFDM Equalization at {snr_db} dB'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ici_aware_equalization_ber.png',dpi=180); plt.close()
    q=np.array([[r[0],r[1]] for r in rows if r[2]=='One-tap'],float); plt.figure(figsize=(7.2,4.7)); plt.plot(q[:,0],100*q[:,1],'o-'); plt.xlabel('Moving-path Doppler (subcarrier spacings)'); plt.ylabel('Off-diagonal channel energy (%)'); plt.title('Doppler-Induced ICI Energy'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(FIG/'ici_energy_vs_doppler.png',dpi=180); plt.close()

if __name__=='__main__': main()
