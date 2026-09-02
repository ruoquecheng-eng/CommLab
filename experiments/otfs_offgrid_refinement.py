from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.otfs import otfs_modulate, otfs_demodulate, apply_delay_doppler_paths, otfs_pilot_dictionary, refine_delay_doppler_paths

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(10003); N=M=8; P=np.zeros((N,M),complex); P[0,0]=1
    true_paths=[(1,1.35,0.9+0.1j),(3,-2.42,0.48-0.25j)]
    x=otfs_modulate(P,0); clean=apply_delay_doppler_paths(x,true_paths,M,N)
    # This experiment isolates off-grid refinement after a coarse sparse detector
    # has already found the correct integer delay cells and nearest Doppler bins.
    coarse_params=[(1,1.0),(3,-2.0)]
    cols=[]
    for d,k in coarse_params:
        D,_=otfs_pilot_dictionary(P,[d],[k],0); cols.append(D[:,0])
    D0=np.column_stack(cols)
    rows=[]
    for snr in [10,15,20,25,30]:
        err_c=[]; err_r=[]; res_c=[]; res_r=[]
        nv=np.mean(np.abs(clean)**2)/10**(snr/10)
        for _ in range(80):
            y=clean+np.sqrt(nv/2)*(rng.normal(size=len(clean))+1j*rng.normal(size=len(clean))); Y=otfs_demodulate(y,N,M,0); yy=Y.reshape(-1)
            gains=np.linalg.lstsq(D0,yy,rcond=None)[0]; coarse=[(d,k,complex(g)) for (d,k),g in zip(coarse_params,gains)]
            rc=float(np.linalg.norm(yy-D0@gains)/np.linalg.norm(yy))
            refined,rr=refine_delay_doppler_paths(Y,P,coarse,.65,27,0,2)
            c_sorted=sorted(coarse,key=lambda z:z[0]); r_sorted=sorted(refined,key=lambda z:z[0]); t_sorted=sorted(true_paths,key=lambda z:z[0])
            err_c.append(np.mean([abs(a[1]-t[1]) for a,t in zip(c_sorted,t_sorted)])); err_r.append(np.mean([abs(a[1]-t[1]) for a,t in zip(r_sorted,t_sorted)]))
            res_c.append(rc); res_r.append(rr)
        rows.append((snr,np.mean(err_c),np.mean(err_r),np.mean(res_c),np.mean(res_r)))
        print(f'{snr} dB doppler MAE coarse={rows[-1][1]:.3f}, refined={rows[-1][2]:.3f}, residual {rows[-1][3]:.3f}->{rows[-1][4]:.3f}')
    with open(DATA/'otfs_offgrid_refinement.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['pilot_snr_db','coarse_doppler_mae_bins','refined_doppler_mae_bins','coarse_relative_residual','refined_relative_residual']); w.writerows(rows)
    a=np.array(rows,float)
    plt.figure(figsize=(7.5,5)); plt.semilogy(a[:,0],a[:,1],'o-',label='Integer-grid coarse support'); plt.semilogy(a[:,0],a[:,2],'o-',label='Local off-grid refinement'); plt.xlabel('Pilot SNR (dB)'); plt.ylabel('Doppler MAE (bins)'); plt.title('OTFS Grid-Mismatch Reduction'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_offgrid_doppler_mae.png',dpi=180); plt.close()
    plt.figure(figsize=(7.5,5)); plt.plot(a[:,0],a[:,3],'o-',label='Coarse integer-grid model'); plt.plot(a[:,0],a[:,4],'o-',label='Refined'); plt.xlabel('Pilot SNR (dB)'); plt.ylabel('Relative pilot residual'); plt.title('OTFS Off-grid Refinement Residual'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_offgrid_residual.png',dpi=180); plt.close()

if __name__=='__main__': main()
