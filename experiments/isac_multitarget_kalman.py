from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing import NearestNeighborMultiTargetTracker
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1204); dt=.2; frames=240
# Two targets cross in range while retaining distinct radial velocity.
t=np.arange(frames)*dt; truth=np.stack([np.column_stack([70+7*t, np.full(frames,7.)]),np.column_stack([150-4.5*t,np.full(frames,-4.5)])])
tracker=NearestNeighborMultiTargetTracker(dt,gate_d2=10.6,max_misses=5,range_std=2.0,velocity_std=.8,accel_std=.8)
records=[]; raw_err=[]; trk_err=[]; coverage=[]
for f in range(frames):
    meas=[]
    for j in range(2):
        if rng.random()<.86:
            z=(truth[j,f,0]+rng.normal(0,2.0),truth[j,f,1]+rng.normal(0,.8)); meas.append(z); raw_err.append((z[0]-truth[j,f,0])**2)
    # Sparse clutter in range/velocity space.
    for _ in range(rng.poisson(.25)): meas.append((rng.uniform(50,180),rng.uniform(-9,10)))
    out=tracker.step(meas)
    # For evaluation only, match truth to distinct current tracks by minimum normalized state error.
    candidates=list(out); used=set(); matched=[]
    for j in range(2):
        best=None
        for q,x in enumerate(candidates):
            if q in used: continue
            d=((x[1]-truth[j,f,0])/4)**2+((x[2]-truth[j,f,1])/1.5)**2
            if best is None or d<best[0]: best=(d,q,x)
        if best is not None and best[0]<25:
            used.add(best[1]); matched.append((j,best[2])); trk_err.append((best[2][1]-truth[j,f,0])**2)
    coverage.append(len(matched)/2)
    for j,x in matched: records.append(dict(frame=f,target=j,true_range=truth[j,f,0],estimated_range=x[1],estimated_velocity=x[2],track_id=x[0]))
df=pd.DataFrame(records); df.to_csv(DATA/'isac_multitarget_kalman_tracks.csv',index=False)
frags=df.groupby('target').track_id.nunique().to_dict(); confirmed=sum(tr.hits>=5 for tr in tracker.tracks)
summary=pd.DataFrame([dict(raw_measurement_range_rmse=np.sqrt(np.mean(raw_err)),tracker_range_rmse=np.sqrt(np.mean(trk_err)),mean_target_coverage=np.mean(coverage),target0_track_fragments=frags.get(0,0),target1_track_fragments=frags.get(1,0),final_confirmed_tracks=confirmed,frames=frames)])
summary.to_csv(DATA/'isac_multitarget_kalman_summary.csv',index=False)
fig,ax=plt.subplots(figsize=(8,4.8)); ax.plot(t,truth[0,:,0],label='Target 1 truth'); ax.plot(t,truth[1,:,0],label='Target 2 truth');
for j,g in df.groupby('target'): ax.scatter(g.frame*dt,g.estimated_range,s=6,alpha=.45,label=f'Target {j+1} track estimates')
ax.set_xlabel('Time (s)'); ax.set_ylabel('Range (m)'); ax.grid(True,alpha=.25); ax.legend(ncol=2); fig.tight_layout(); fig.savefig(FIG/'isac_multitarget_kalman_tracking.png',dpi=180); plt.close(fig)
print(summary.to_string(index=False)); print('active tracks final:',len(tracker.tracks))
