from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing import KalmanAngleTracker, KalmanAngleAccelerationTracker, ula_beam_gain
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1303); T=360; dt=.05; elements=32; snr=10**(12/10); meas_std=1.4; sensing_period=6; miss=.15
t=np.arange(T)*dt
# Constant-acceleration maneuver: sparse sensing makes prediction materially useful.
true=-30 + 3.0*t + 0.35*t*t
meas=np.full(T,np.nan); scheduled=np.arange(T)%sensing_period==0; valid=scheduled & (rng.random(T)>=miss)
meas[valid]=true[valid]+rng.normal(0,meas_std,np.sum(valid))
cv=KalmanAngleTracker(true[0],3.0,dt,measurement_std_deg=meas_std,angular_accel_std_dps2=.7)
ca=KalmanAngleAccelerationTracker(true[0],3.0,.7,dt,measurement_std_deg=meas_std,jerk_std_dps3=.4)
react=np.zeros(T); cvbeam=np.zeros(T); cabeam=np.zeros(T); last=true[0]
react[0]=cvbeam[0]=cabeam[0]=true[0]
m0=None if not np.isfinite(meas[0]) else float(meas[0])
cv.update(m0); ca.update(m0)
if m0 is not None: last=m0
for k in range(T-1):
    # Predict beam for slot k+1 from the posterior at slot k.
    ac,vc=cv.x; aa,va,xa=ca.x
    react[k+1]=last
    cvbeam[k+1]=ac+vc*dt
    cabeam[k+1]=aa+va*dt+.5*xa*dt*dt
    cv.predict(); ca.predict()
    mn=None if not np.isfinite(meas[k+1]) else float(meas[k+1])
    cv.update(mn); ca.update(mn)
    if mn is not None: last=mn
rows=[]
for name,beam in [('Reactive/hold',react),('CV predictive',cvbeam),('CA predictive',cabeam),('Oracle',true)]:
    gain=ula_beam_gain(true,beam,elements); rate=np.log2(1+snr*gain); err=np.abs(true-beam)
    rows.append(dict(scheme=name,mean_rate=rate.mean(),p10_rate=np.quantile(rate,.1),angle_mae_deg=err.mean(),outage_prob=np.mean(rate<1.0)))
summary=pd.DataFrame(rows); summary.to_csv(DATA/'isac_predictive_beam_tracking.csv',index=False)
pd.DataFrame({'time_s':t,'true_angle_deg':true,'measurement_deg':meas,'reactive_beam_deg':react,'cv_beam_deg':cvbeam,'ca_beam_deg':cabeam}).to_csv(DATA/'isac_predictive_beam_trace.csv',index=False)
fig,ax=plt.subplots(figsize=(8,4.5)); sl=slice(0,220); ax.plot(t[sl],true[sl],label='True angle'); ax.scatter(t[sl],meas[sl],s=13,alpha=.55,label='Sparse sensing'); ax.plot(t[sl],react[sl],label='Reactive hold'); ax.plot(t[sl],cvbeam[sl],label='CV prediction'); ax.plot(t[sl],cabeam[sl],label='CA prediction')
ax.set_xlabel('Time (s)'); ax.set_ylabel('Angle (deg)'); ax.grid(True,alpha=.25); ax.legend(ncol=2); fig.tight_layout(); fig.savefig(FIG/'isac_predictive_beam_trace.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.5)); x=np.arange(len(summary)); ax.bar(x,summary.mean_rate); ax.set_xticks(x,summary.scheme,rotation=10); ax.set_ylabel('Mean communication rate (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'isac_predictive_beam_rate.png',dpi=180); plt.close(fig)
print(summary.to_string(index=False))
