from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.modulation import QAMModem
from commlab.channels import add_awgn, noise_power_for_snr
from commlab.metrics import bit_error_rate
from commlab.otfs import (
    ofdm_grid_modulate,ofdm_grid_demodulate,otfs_modulate,otfs_demodulate,
    apply_delay_doppler_paths,effective_channel_matrix,linear_mmse_detect,
)

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    N,M,cp=5,10,3; modem=QAMModem(4); rng=np.random.default_rng(761); shape=(N,M); n=N*M
    # A direct path plus one delayed moving scatterer. Doppler is in normalized DD bins.
    rows=[]
    for dop in (0.0,0.75,1.5,2.25):
        paths=[(0,0.0,1+0j),(2,dop,0.65*np.exp(0.6j))]
        chan=lambda w: apply_delay_doppler_paths(w,paths,M,N)
        mod_o=lambda g: ofdm_grid_modulate(g,cp); dem_o=lambda w: ofdm_grid_demodulate(w,N,M,cp)
        mod_t=lambda g: otfs_modulate(g,cp); dem_t=lambda w: otfs_demodulate(w,N,M,cp)
        Aof=effective_channel_matrix(mod_o,dem_o,shape,chan)
        Aot=effective_channel_matrix(mod_t,dem_t,shape,chan)
        diag=np.diag(Aof); off=np.linalg.norm(Aof-np.diag(diag))**2/np.linalg.norm(Aof)**2
        # Energy concentration: mean fraction captured by 2 largest DD-domain coefficients per column.
        e=np.abs(Aot)**2; top2=np.partition(e,-2,axis=0)[-2:,:].sum(axis=0); concentration=float(np.mean(top2/(e.sum(axis=0)+1e-30)))
        ber_o=[]; ber_t=[]
        for rep in range(24):
            bits=rng.integers(0,2,n*2,dtype=np.uint8); s=modem.modulate(bits).reshape(shape)
            xo=mod_o(s); xt=mod_t(s)
            yo=add_awgn(chan(xo),18.0,np.random.default_rng(770000+rep+int(100*dop)))
            yt=add_awgn(chan(xt),18.0,np.random.default_rng(780000+rep+int(100*dop)))
            Yo=dem_o(yo).reshape(-1); Yt=dem_t(yt).reshape(-1)
            # OFDM: conventional one-tap diagonal receiver. OTFS: small-grid full LMMSE
            # baseline using the known effective DD channel matrix. This is illustrative,
            # not a complexity-matched standards benchmark.
            oh=Yo/np.where(np.abs(diag)>1e-10,diag,1e-10)
            nv=noise_power_for_snr(xt,18.0)
            th=linear_mmse_detect(Yt,Aot,nv)
            ber_o.append(bit_error_rate(bits,modem.demodulate(oh)))
            ber_t.append(bit_error_rate(bits,modem.demodulate(th)))
        row=(dop,float(np.mean(ber_o)),float(np.mean(ber_t)),off,concentration)
        rows.append(row); print('dop=%3.1f OFDM=%.4g OTFS=%.4g OFDMoff=%.3f DDtop2=%.3f'%row)
    with open(DATA/'otfs_high_doppler.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['moving_path_doppler_bins','ofdm_one_tap_ber','otfs_full_lmmse_ber','ofdm_offdiagonal_energy_fraction','otfs_top2_energy_concentration']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1.0/(24*n*2); plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='OFDM one-tap diagonal EQ'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='OTFS effective-channel LMMSE'); plt.xlabel('Moving-path Doppler (DD bins)'); plt.ylabel('BER'); plt.title('Illustrative High-Doppler Receiver Comparison'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_vs_ofdm_high_doppler.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,3],'o-',label='OFDM off-diagonal channel energy'); plt.plot(a[:,0],a[:,4],'s-',label='OTFS top-2 DD energy concentration'); plt.xlabel('Moving-path Doppler (DD bins)'); plt.ylabel('Fraction'); plt.title('High-Doppler Channel Structure by Signal Domain'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_channel_structure.png',dpi=180); plt.close()

if __name__=='__main__': main()
