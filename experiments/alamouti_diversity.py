from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.modulation import QAMModem
from commlab.mimo import alamouti_encode, alamouti_decode
from commlab.metrics import bit_error_rate

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def noise(shape,nv,rng): return np.sqrt(nv/2)*(rng.normal(size=shape)+1j*rng.normal(size=shape))

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    modem=QAMModem(4); rng0=np.random.default_rng(901); bits=rng0.integers(0,2,400000,dtype=np.uint8); s=modem.modulate(bits); rows=[]
    for snr in range(0,25,4):
        nv=10**(-snr/10); rng=np.random.default_rng(9100+snr)
        # SISO: independent flat Rayleigh symbol fading, perfect CSI.
        h=(rng.normal(size=len(s))+1j*rng.normal(size=len(s)))/np.sqrt(2); y=h*s+noise(s.shape,nv,rng); shat=y/np.where(np.abs(h)>1e-12,h,1e-12); b0=bit_error_rate(bits,modem.demodulate(shat))
        # Alamouti: channel remains constant over each two-slot block.
        x=alamouti_encode(s); hh=(rng.normal(size=(len(x),2))+1j*rng.normal(size=(len(x),2)))/np.sqrt(2); yy=np.sum(x*hh[:,None,:],axis=2)+noise((len(x),2),nv,rng); ahat=alamouti_decode(yy,hh); b1=bit_error_rate(bits,modem.demodulate(ahat))
        rows.append((snr,b0,b1)); print(f'SNR={snr:2d} SISO={b0:.5g} Alamouti={b1:.5g}')
    with open(DATA/'alamouti_diversity.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','siso_rayleigh_ber','alamouti_2x1_ber']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(bits); plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='SISO Rayleigh'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='2x1 Alamouti STBC'); plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('Transmit Diversity: Reliability without Spatial Multiplexing'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'alamouti_diversity.png',dpi=180); plt.close()
if __name__=='__main__': main()
