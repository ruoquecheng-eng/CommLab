from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.sensing import C0, simulate_ofdm_sensing_array_channel, range_doppler_array_cube, bartlett_covariance_spectrum, music_angle_spectrum
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'
def peaks(spec,grid,count=2,suppress=3):
    w=spec.copy(); out=[]
    for _ in range(count):
        i=int(np.argmax(w)); out.append(float(grid[i])); w[np.abs(grid-grid[i])<suppress]=0
    return sorted(out)
def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1108)
    nsc=64; nsym=64; nrx=10; snaps=80; df=30e3; Ts=1/df; fc=24e9; dr=C0/(2*nsc*df); dv=C0/(2*fc*nsym*Ts); R=5*dr; v=3*dv; X=np.ones((nsym,nsc),complex); spatial=[]
    for _ in range(snaps):
        g1=(rng.normal()+1j*rng.normal())/np.sqrt(2); g2=.9*(rng.normal()+1j*rng.normal())/np.sqrt(2)
        Y=simulate_ofdm_sensing_array_channel(X,df,Ts,[(R,v,-6,g1),(R,v,6,g2)],fc,n_rx=nrx,noise_var=.015,rng=rng)
        rd=range_doppler_array_cube(Y,X,df,Ts,window=False); vel=np.fft.fftshift(np.fft.fftfreq(nsym,d=Ts))*C0/(2*fc); iv=int(np.argmin(abs(vel-v))); spatial.append(rd[:,iv,5])
    S=np.column_stack(spatial); grid=np.linspace(-30,30,1201); pb=bartlett_covariance_spectrum(S,grid); pm=music_angle_spectrum(S,2,grid,diagonal_loading=1e-6); eb=peaks(pb,grid); em=peaks(pm,grid)
    print('Bartlett',eb,'MUSIC',em)
    with open(DATA/'isac_music_angle.csv','w',newline='') as f: csv.writer(f).writerows([['method','estimated_angle_1','estimated_angle_2','sum_abs_error_deg'],['Bartlett',*eb,abs(eb[0]+6)+abs(eb[1]-6)],['MUSIC',*em,abs(em[0]+6)+abs(em[1]-6)]])
    plt.figure(figsize=(7.5,5)); plt.plot(grid,10*np.log10(pb/np.max(pb)+1e-12),label='Bartlett covariance'); plt.plot(grid,10*np.log10(pm/np.max(pm)+1e-12),label='MUSIC, 2 sources'); plt.axvline(-6,ls='--',alpha=.5); plt.axvline(6,ls='--',alpha=.5); plt.ylim(-45,1); plt.xlabel('Angle (deg)'); plt.ylabel('Normalized spectrum (dB)'); plt.title('OFDM-ISAC Same-Range/Doppler Close-Angle Resolution'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'isac_music_superresolution.png',dpi=180); plt.close()
if __name__=='__main__': main()
