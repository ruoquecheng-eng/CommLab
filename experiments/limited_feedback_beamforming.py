from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.mimo import random_unit_codebook, mrt_beamformer, select_codebook_beam, miso_effective_gain
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(816)
    n=70000; nt=4; snr_db=5; snr=10**(snr_db/10); h=(rng.normal(size=(n,nt))+1j*rng.normal(size=(n,nt)))/np.sqrt(2)
    no_bf=np.abs(h[:,0])**2; perfect=miso_effective_gain(h,mrt_beamformer(h)); rows=[]
    base_rate=np.mean(np.log2(1+snr*no_bf)); perf_rate=np.mean(np.log2(1+snr*perfect)); rows.append((0,1,base_rate,float(np.percentile(np.log2(1+snr*no_bf),5)),0.0))
    print(f'single-antenna rate={base_rate:.3f}, perfect-MRT={perf_rate:.3f}')
    for b in (1,2,3,4,6,8):
        W=random_unit_codebook(nt,2**b,np.random.default_rng(1000+b)); w,_=select_codebook_beam(h,W); gain=miso_effective_gain(h,w); rate=np.log2(1+snr*gain); loss=perf_rate-float(np.mean(rate)); rows.append((b,2**b,float(np.mean(rate)),float(np.percentile(rate,5)),loss)); print(f'feedback={b} bits codebook={2**b:3d} mean-rate={np.mean(rate):.3f} loss-to-MRT={loss:.3f}')
    rows.append((99,-1,perf_rate,float(np.percentile(np.log2(1+snr*perfect),5)),0.0))
    with open(DATA/'limited_feedback_beamforming.csv','w',newline='') as f: w=csv.writer(f); w.writerow(['feedback_bits','codebook_size','mean_rate_bphz','p05_rate_bphz','loss_to_perfect_mrt']); w.writerows(rows)
    plot=[r for r in rows if 0<r[0]<90]; x=np.array([r[0] for r in plot]); y=np.array([r[2] for r in plot]); p5=np.array([r[3] for r in plot])
    plt.figure(figsize=(7.3,4.8)); plt.axhline(base_rate,ls='--',label='Single Tx antenna'); plt.axhline(perf_rate,ls=':',label='Perfect CSI MRT'); plt.plot(x,y,'o-',label='Quantized codebook beamforming'); plt.xlabel('CSI feedback bits'); plt.ylabel('Mean spectral efficiency (bit/s/Hz)'); plt.title('4x1 MISO: CSI Feedback Overhead vs Beamforming Gain'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'limited_feedback_beamforming_rate.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.8)); plt.plot(x,p5,'s-'); plt.xlabel('CSI feedback bits'); plt.ylabel('5th-percentile rate (bit/s/Hz)'); plt.title('Limited Feedback and Cell-Edge/Outage-Like Rate'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(FIG/'limited_feedback_beamforming_p05.png',dpi=180); plt.close()
if __name__=='__main__': main()
