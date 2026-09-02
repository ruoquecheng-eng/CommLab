from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

from commlab.modulation import QAMModem
from commlab.metrics.confidence import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def simulate_point(ebn0_db, rng, target_errors=250, max_bits=4_000_000, chunk_bits=20000):
    modem=QAMModem(4); errors=0; bits_total=0; gamma=10**(ebn0_db/10); nv=1/(2*gamma)
    while errors < target_errors and bits_total < max_bits:
        n=min(chunk_bits,max_bits-bits_total); n-=n%2
        bits=rng.integers(0,2,n,dtype=np.uint8); x=modem.modulate(bits); noise=np.sqrt(nv/2)*(rng.normal(size=len(x))+1j*rng.normal(size=len(x))); bh=modem.demodulate(x+noise)
        errors+=int(np.count_nonzero(bits!=bh)); bits_total+=n
    ber,lo,hi=ber_with_wilson(errors,bits_total); theory=.5*erfc(np.sqrt(gamma))
    return errors,bits_total,ber,lo,hi,theory


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(706)
    rows=[]
    for snr in (0,2,4,6,8,10):
        row=(snr,)+simulate_point(snr,rng); rows.append(row)
        print('Eb/N0=%2d errors=%4d bits=%7d BER=%.3g CI=[%.3g,%.3g] theory=%.3g'%row)
    with open(DATA/'ber_confidence_intervals.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['ebn0_db','errors','bits','ber','ci95_low','ci95_high','theory']); w.writerows(rows)
    a=np.asarray(rows,float); yerr=np.vstack((a[:,3]-a[:,4],a[:,5]-a[:,3])); plt.figure(figsize=(7.3,4.9)); plt.errorbar(a[:,0],np.maximum(a[:,3],1e-8),yerr=yerr,fmt='o',capsize=3,label='Monte Carlo + 95% Wilson CI'); plt.semilogy(a[:,0],a[:,6],'-',label='QPSK theory'); plt.xlabel('Eb/N0 (dB)'); plt.ylabel('BER'); plt.title('Confidence-Aware BER Simulation'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ber_confidence_intervals.png',dpi=180); plt.close()

if __name__=='__main__': main()
