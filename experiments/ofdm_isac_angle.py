from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.sensing import C0, simulate_ofdm_sensing_array_channel, range_doppler_array_cube, bartlett_angle_spectrum
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1103)
    nsc=64; nsym=64; df=30e3; Ts=1/df; fc=24e9; dr=C0/(2*nsc*df); dv=(1/(nsym*Ts))*C0/(2*fc); X=np.ones((nsym,nsc),complex)
    R=5*dr; v=3*dv; angles=np.linspace(-60,60,481); rows=[]
    plt.figure(figsize=(7.4,5.0))
    for nrx in (4,8,16):
        targets=[(R,v,-18,1+0j),(R,v,22,.85+0.1j)]
        Y=simulate_ofdm_sensing_array_channel(X,df,Ts,targets,fc,n_rx=nrx,noise_var=10**(-18/10),rng=rng)
        cube=range_doppler_array_cube(Y,X,df,Ts,window=False); iv=np.argmin(abs(np.fft.fftshift(np.fft.fftfreq(nsym,d=Ts))*C0/(2*fc)-v)); ir=int(round(R/dr))
        p=bartlett_angle_spectrum(cube[:,iv,ir],angles); p_db=10*np.log10(p/np.max(p)+1e-12); plt.plot(angles,p_db,label=f'{nrx} Rx antennas')
        # find top two angle peaks with 5-degree suppression
        work=p.copy(); est=[]
        for _ in range(2):
            i=int(np.argmax(work)); est.append(float(angles[i])); work[np.abs(angles-angles[i])<5]=0
        est.sort(); rows.append((nrx,est[0],est[1],abs(est[0]+18)+abs(est[1]-22)))
        print(nrx,est)
    with open(DATA/'ofdm_isac_angle.csv','w',newline='') as f: csv.writer(f).writerows([['n_rx','estimated_angle_1_deg','estimated_angle_2_deg','sum_abs_angle_error_deg'],*rows])
    plt.axvline(-18,ls='--',alpha=.5); plt.axvline(22,ls='--',alpha=.5); plt.ylim(-40,1); plt.xlabel('Angle (deg)'); plt.ylabel('Normalized Bartlett power (dB)'); plt.title('OFDM-ISAC: Angular Resolution Improves with Receive Aperture'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ofdm_isac_angle_resolution.png',dpi=180); plt.close()
if __name__=='__main__': main()
