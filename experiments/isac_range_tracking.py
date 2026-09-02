from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.sensing import AlphaBetaRangeTracker
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1104)
    dt=.1; n=220; true_v=14.; truth=80+true_v*dt*np.arange(1,n+1); measurements=truth+rng.normal(0,3.2,n); missed=rng.random(n)<.12; measurements[missed]=np.nan
    tr=AlphaBetaRangeTracker(80,10,dt,alpha=.42,beta=.07); est=[]; vest=[]
    for z in measurements:
        r,v=tr.update(None if np.isnan(z) else float(z)); est.append(r); vest.append(v)
    est=np.array(est); raw=np.where(np.isnan(measurements),np.nan,measurements)
    raw_rmse=np.sqrt(np.nanmean((raw-truth)**2)); track_rmse=np.sqrt(np.mean((est-truth)**2)); rows=list(zip(np.arange(n)*dt,truth,measurements,est,vest))
    with open(DATA/'isac_range_tracking.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['time_s','true_range_m','measurement_m','tracked_range_m','tracked_velocity_mps']); w.writerows(rows)
    print('raw RMSE',raw_rmse,'track RMSE',track_rmse,'misses',np.sum(missed))
    plt.figure(figsize=(8,4.8)); plt.plot(np.arange(n)*dt,truth,label='True range'); plt.scatter(np.arange(n)*dt,measurements,s=8,alpha=.45,label='Noisy/missed detections'); plt.plot(np.arange(n)*dt,est,label='Alpha-beta track'); plt.xlabel('Time (s)'); plt.ylabel('Range (m)'); plt.title('ISAC Multi-frame Range Tracking under Measurement Noise and Misses'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'isac_range_tracking.png',dpi=180); plt.close()
    with open(DATA/'isac_range_tracking_summary.csv','w',newline='') as f: csv.writer(f).writerows([['raw_measurement_rmse_m','tracked_rmse_m','miss_fraction'],[raw_rmse,track_rmse,np.mean(missed)]])
if __name__=='__main__': main()
