from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.equalization import time_varying_ofdm_channel_matrix, estimate_banded_ici_matrix, linear_lmmse_ici_detect, band_limit_channel_matrix, ici_energy_fraction
from commlab.modulation import QAMModem
from commlab.metrics import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(9041); modem=QAMModem(4); n=64; cp=16; snr_db=18; nv=10**(-snr_db/10); bw=2
    taps=np.array([1.0,0.52*np.exp(.35j),0.24*np.exp(-.5j)],complex); taps/=np.linalg.norm(taps)
    delays=np.array([0,3,8]); dopplers=np.array([0.,1.5,-.825])
    H=time_varying_ofdm_channel_matrix(taps,delays,dopplers,n,cp); Hb=band_limit_channel_matrix(H,bw); ici=ici_energy_fraction(H)
    train_counts=[4,6,8,12,20,32]; rows=[]
    for P in train_counts:
        errors={'One-tap':0,'Estimated band ±2':0,'Genie band ±2':0,'Genie full':0}; total=0; nm=[]
        repeats=16
        for _ in range(repeats):
            train_bits=rng.integers(0,2,(P,n*2),dtype=np.uint8)
            X=np.stack([modem.modulate(b) for b in train_bits])
            Nn=np.sqrt(nv/2)*(rng.normal(size=(P,n))+1j*rng.normal(size=(P,n)))
            Y=X@H.T+Nn
            He=estimate_banded_ici_matrix(X,Y,bw,ridge=1e-3)
            nm.append(np.linalg.norm(He-Hb)**2/np.linalg.norm(Hb)**2)
            for _ in range(35):
                bits=rng.integers(0,2,n*2,dtype=np.uint8); x=modem.modulate(bits); y=H@x+np.sqrt(nv/2)*(rng.normal(size=n)+1j*rng.normal(size=n))
                for name,A,b in [('One-tap',H,0),('Estimated band ±2',He,None),('Genie band ±2',H,bw),('Genie full',H,None)]:
                    xh=linear_lmmse_ici_detect(y,A,nv,bandwidth=b)
                    errors[name]+=int(np.count_nonzero(modem.demodulate(xh)!=bits))
                total+=len(bits)
        for name,e in errors.items():
            ber,lo,hi=ber_with_wilson(e,total); rows.append((P,name,ber,lo,hi,float(np.mean(nm)),ici))
        print(f'P={P:2d} NMSE={np.mean(nm):.4g} one={errors["One-tap"]/total:.4g} est={errors["Estimated band ±2"]/total:.4g} genie-band={errors["Genie band ±2"]/total:.4g} full={errors["Genie full"]/total:.4g}')
    with open(DATA/'ici_matrix_estimation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['training_symbols','receiver','ber','ci95_low','ci95_high','band_matrix_nmse','ici_energy_fraction']); w.writerows(rows)
    plt.figure(figsize=(7.8,5.0))
    for name in ['One-tap','Estimated band ±2','Genie band ±2','Genie full']:
        q=np.array([[r[0],r[2]] for r in rows if r[1]==name],float); plt.semilogy(q[:,0],np.maximum(q[:,1],1e-5),'o-',label=name)
    plt.xlabel('Random full-band training OFDM symbols'); plt.ylabel('BER'); plt.title(f'High-Doppler ICI Acquisition ({100*ici:.1f}% off-diagonal energy)'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ici_matrix_estimation_ber.png',dpi=180); plt.close()
    q=np.array([[r[0],r[5]] for r in rows if r[1]=='Estimated band ±2'],float); plt.figure(figsize=(7.2,4.7)); plt.semilogy(q[:,0],q[:,1],'o-'); plt.xlabel('Training OFDM symbols'); plt.ylabel('Banded channel NMSE'); plt.title('Structured LS ICI-Matrix Estimation'); plt.grid(True,which='both',alpha=.3); plt.tight_layout(); plt.savefig(FIG/'ici_matrix_estimation_nmse.png',dpi=180); plt.close()

if __name__=='__main__': main()
