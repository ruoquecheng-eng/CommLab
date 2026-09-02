from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.information_theory import complex_awgn_capacity,normal_approximation_rate
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    snr_db=np.arange(-5,21,1); snr=10**(snr_db/10); eps=1e-3; lengths=[100,300,1000,10000]
    rows=[]; C=complex_awgn_capacity(snr)
    for db,c in zip(snr_db,C): rows.append((db,'Shannon',np.nan,c,eps))
    for n in lengths:
        R=normal_approximation_rate(snr,n,eps)
        for db,r in zip(snr_db,R): rows.append((db,f'n={n}',n,r,eps))
    with open(DATA/'finite_blocklength_awgn.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','curve','blocklength','rate_bits_per_complex_use','target_error_probability']); w.writerows(rows)
    plt.figure(figsize=(7.8,5.0)); plt.plot(snr_db,C,'k--',label='Shannon capacity')
    for n in lengths: plt.plot(snr_db,normal_approximation_rate(snr,n,eps),label=f'n={n}')
    plt.xlabel('SNR (dB)'); plt.ylabel('Approx. achievable rate (bit/complex use)'); plt.title(r'Finite-Blocklength Penalty at $\epsilon=10^{-3}$'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'finite_blocklength_rate.png',dpi=180); plt.close()
    # Fixed 10 dB cross section highlights latency/rate trade-off.
    ns=np.unique(np.logspace(1.7,4.3,70).astype(int)); rates=normal_approximation_rate(10.0,ns,eps); cap=float(complex_awgn_capacity(10.0))
    plt.figure(figsize=(7.6,4.8)); plt.semilogx(ns,rates,label='Normal approximation'); plt.axhline(cap,ls='--',label='Shannon limit'); plt.xlabel('Blocklength (complex channel uses)'); plt.ylabel('Rate at 10 dB (bit/use)'); plt.title('Coding Delay vs Achievable Rate'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'finite_blocklength_vs_blocklength.png',dpi=180); plt.close()
    for n in lengths: print(f'10 dB n={n:5d}: R={float(normal_approximation_rate(10.0,n,eps)):.3f} vs C={cap:.3f} bit/use')
if __name__=='__main__': main()
