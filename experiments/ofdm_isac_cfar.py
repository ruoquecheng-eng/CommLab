from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.modulation import QAMModem
from commlab.sensing import C0, simulate_ofdm_sensing_channel, range_doppler_map, ca_cfar_2d

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(10006); nsc=64; nsym=64; df=60e3; Ts=1/df; fc=24e9; modem=QAMModem(4)
    dr=C0/(2*nsc*df); dv=C0/(2*fc*nsym*Ts); true_bins=[(6,-7),(15,8)]
    targets=[(rb*dr,vb*dv,g) for (rb,vb),g in zip(true_bins,[1+0j,.08*np.exp(1j*.5)])]
    rows=[]; snapshot=None
    for snr in [-20,-16,-12,-8,-4,0]:
        hits=np.zeros(len(targets),int); false=0; trials=35
        for t in range(trials):
            X=modem.modulate(rng.integers(0,2,nsym*nsc*2,dtype=np.uint8)).reshape(nsym,nsc)
            clean=simulate_ofdm_sensing_channel(X,df,Ts,targets,fc); nv=np.mean(np.abs(clean)**2)/10**(snr/10)
            Y=clean+np.sqrt(nv/2)*(rng.normal(size=clean.shape)+1j*rng.normal(size=clean.shape))
            rd,r,v=range_doppler_map(Y,X,df,Ts,fc,window=False); det,thr=ca_cfar_2d(rd,training=(4,4),guard=(1,1),pfa=1e-3)
            inds=np.argwhere(det); assigned=set()
            for q,(rb,vb) in enumerate(true_bins):
                vi=(vb+nsym//2)%nsym; ri=rb
                ok=False
                for z,(ii,jj) in enumerate(inds):
                    if abs(int(ii)-vi)<=1 and abs(int(jj)-ri)<=1:
                        ok=True; assigned.add(z)
                hits[q]+=int(ok)
            false += max(0,len(inds)-len(assigned))
            if snr==0 and t==0: snapshot=(rd,det,r,v)
        for q in range(len(targets)):
            rows.append((snr,q+1,hits[q]/trials,false/trials))
        print(f'{snr:>2} dB detection={[round(h/trials,3) for h in hits]}, false alarms/map={false/trials:.2f}')
    with open(DATA/'ofdm_isac_cfar.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','target','detection_probability','mean_false_alarms_per_map']); w.writerows(rows)
    plt.figure(figsize=(7.5,5))
    for q in [1,2]:
        a=np.array([[r[0],r[2]] for r in rows if r[1]==q],float); plt.plot(a[:,0],a[:,1],'o-',label=f'Target {q}')
    plt.xlabel('Sensing SNR (dB)'); plt.ylabel('Detection probability'); plt.title('2-D CA-CFAR Target Detection with OFDM Sensing'); plt.grid(alpha=.3); plt.ylim(0,1.04); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ofdm_isac_cfar_detection.png',dpi=180); plt.close()
    if snapshot:
        rd,det,r,v=snapshot; db=20*np.log10(np.abs(rd)/np.max(np.abs(rd))+1e-12)
        plt.figure(figsize=(8,5.5)); plt.imshow(db,origin='lower',aspect='auto',extent=[r[0],r[-1],v[0],v[-1]],vmin=-40,vmax=0); ii,jj=np.nonzero(det); plt.scatter(r[jj],v[ii],s=22,facecolors='none',edgecolors='white',label='CA-CFAR detections'); plt.colorbar(label='Normalized magnitude (dB)'); plt.xlabel('Range (m)'); plt.ylabel('Velocity (m/s)'); plt.title('OFDM Sensing: CA-CFAR Detections at 0 dB'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ofdm_isac_cfar_snapshot.png',dpi=180); plt.close()

if __name__=='__main__': main()
