from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.mimo import mrt_leakage_from_pilot_estimate
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'
def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1106); rows=[]
    for M in (8,16,32,64,128):
        sir0=[]; sirc=[]
        for _ in range(4000):
            h=(rng.normal(size=M)+1j*rng.normal(size=M))/np.sqrt(2); g=(rng.normal(size=M)+1j*rng.normal(size=M))/np.sqrt(2)
            # Tiny beta for the orthogonal-pilot curve only to define an SIR-like leakage metric.
            _,_,a=mrt_leakage_from_pilot_estimate(h,g,100,0.0,rng,leakage_beta=.5); _,_,b=mrt_leakage_from_pilot_estimate(h,g,100,.5,rng,leakage_beta=.5)
            sir0.append(10*np.log10(a)); sirc.append(10*np.log10(b))
        rows.append((M,np.median(sir0),np.median(sirc),np.percentile(sirc,10)))
        print(M,rows[-1])
    with open(DATA/'massive_mimo_pilot_contamination.csv','w',newline='') as f: csv.writer(f).writerows([['n_antennas','orthogonal_like_median_sir_db','reused_pilot_median_sir_db','reused_pilot_p10_sir_db'],*rows])
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='Orthogonal-pilot-like estimate'); plt.plot(a[:,0],a[:,2],'s-',label='Pilot reuse / contamination'); plt.xlabel('Base-station antennas'); plt.ylabel('Median desired/leakage ratio (dB)'); plt.title('Massive MIMO: Pilot Contamination Creates Coherent Leakage'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'massive_mimo_pilot_contamination.png',dpi=180); plt.close()
if __name__=='__main__': main()
