from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.modulation import QAMModem
from commlab.sensing import C0, simulate_ofdm_sensing_channel, range_doppler_map, strongest_targets

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(10005); nsc=128; nsym=128; df=60e3; Ts=1/df; fc=24e9; modem=QAMModem(4)
    dr=C0/(2*nsc*df); dv=(1/(nsym*Ts))*C0/(2*fc)
    targets=[(6*dr,-9*dv,1+0j),(14*dr,7*dv,.62*np.exp(1j*.7))]
    bits=rng.integers(0,2,nsym*nsc*2,dtype=np.uint8); X=modem.modulate(bits).reshape(nsym,nsc)
    sig=simulate_ofdm_sensing_channel(X,df,Ts,targets,fc)
    nv=np.mean(np.abs(sig)**2)/10**(12/10); Y=sig+np.sqrt(nv/2)*(rng.normal(size=sig.shape)+1j*rng.normal(size=sig.shape))
    rd,r,v=range_doppler_map(Y,X,df,Ts,fc,window=True); peaks=strongest_targets(rd,r,v,2,guard_cells=(3,3))
    true_sorted=sorted(targets,key=lambda z:z[0]); est_sorted=sorted(peaks,key=lambda z:z[0]); rows=[]
    for i,(t,e) in enumerate(zip(true_sorted,est_sorted),1):
        rows.append((i,t[0],e[0],e[0]-t[0],t[1],e[1],e[1]-t[1],e[2]))
        print(f'target {i}: range {t[0]:.2f}->{e[0]:.2f} m, velocity {t[1]:.2f}->{e[1]:.2f} m/s')
    with open(DATA/'ofdm_isac_range_doppler.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['target','true_range_m','estimated_range_m','range_error_m','true_velocity_mps','estimated_velocity_mps','velocity_error_mps','peak_magnitude']); w.writerows(rows)
    plt.figure(figsize=(8,5.5)); db=20*np.log10(np.abs(rd)/np.max(np.abs(rd))+1e-12); extent=[r[0],r[-1],v[0],v[-1]]; plt.imshow(db,origin='lower',aspect='auto',extent=extent,vmin=-45,vmax=0); plt.colorbar(label='Normalized magnitude (dB)'); plt.xlabel('Range (m)'); plt.ylabel('Radial velocity (m/s)'); plt.title('Communication-Centric OFDM Range-Doppler Map'); plt.tight_layout(); plt.savefig(FIG/'ofdm_isac_range_doppler_map.png',dpi=180); plt.close()
    # Resolution trade-off using coherent processing interval length.
    res=[]
    for n in [32,64,128,256]:
        vel_res=C0/(2*fc*n*Ts); cpi=n*Ts; res.append((n,cpi*1e3,vel_res))
    with open(DATA/'ofdm_isac_resolution.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['ofdm_symbols','coherent_processing_interval_ms','velocity_bin_mps']); w.writerows(res)
    a=np.array(res,float); plt.figure(figsize=(7.4,5)); plt.loglog(a[:,0],a[:,2],'o-'); plt.xlabel('Coherent OFDM symbols'); plt.ylabel('Velocity-bin spacing (m/s)'); plt.title('Sensing Resolution vs Coherent Processing Length'); plt.grid(True,which='both',alpha=.3); plt.tight_layout(); plt.savefig(FIG/'ofdm_isac_velocity_resolution.png',dpi=180); plt.close()

if __name__=='__main__': main()
