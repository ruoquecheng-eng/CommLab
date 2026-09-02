import numpy as np


class AlphaBetaRangeTracker:
    """Minimal constant-velocity alpha-beta tracker for range measurements."""
    def __init__(self, range0: float, velocity0: float, dt: float, alpha: float = 0.65, beta: float = 0.18):
        if dt<=0 or not (0<alpha<=1) or beta<0: raise ValueError("invalid tracker parameters")
        self.range=float(range0); self.velocity=float(velocity0); self.dt=float(dt)
        self.alpha=float(alpha); self.beta=float(beta); self.steps=0

    def predict(self) -> tuple[float,float]:
        self.range += self.velocity*self.dt; self.steps += 1
        return self.range,self.velocity

    def update(self, measured_range: float | None) -> tuple[float,float]:
        self.predict()
        if measured_range is not None and np.isfinite(measured_range):
            residual=float(measured_range)-self.range
            self.range += self.alpha*residual
            self.velocity += (self.beta/self.dt)*residual
        return self.range,self.velocity


class KalmanRangeVelocityTrack:
    """Constant-velocity Kalman track using joint range/velocity measurements."""
    def __init__(self, track_id: int, measurement: tuple[float,float], dt: float,
                 range_std: float = 2.0, velocity_std: float = 1.0,
                 accel_std: float = 2.0):
        if dt<=0 or min(range_std,velocity_std,accel_std)<=0: raise ValueError("invalid tracker parameters")
        self.id=int(track_id); self.dt=float(dt); self.x=np.asarray(measurement,dtype=float).reshape(2)
        self.P=np.diag([range_std**2*4,velocity_std**2*4]); self.R=np.diag([range_std**2,velocity_std**2])
        q=accel_std**2; d=self.dt
        self.F=np.array([[1,d],[0,1.]],float)
        self.Q=q*np.array([[d**4/4,d**3/2],[d**3/2,d**2]],float)
        self.hits=1; self.misses=0; self.age=1

    def predict(self):
        self.x=self.F@self.x; self.P=self.F@self.P@self.F.T+self.Q; self.age+=1; self.misses+=1
        return self.x.copy()

    def innovation_distance2(self, measurement: tuple[float,float]) -> float:
        z=np.asarray(measurement,dtype=float).reshape(2); y=z-self.x; S=self.P+self.R
        return float(y@np.linalg.solve(S,y))

    def update(self, measurement: tuple[float,float]):
        z=np.asarray(measurement,dtype=float).reshape(2); S=self.P+self.R; K=self.P@np.linalg.inv(S)
        self.x=self.x+K@(z-self.x); self.P=(np.eye(2)-K)@self.P
        self.hits+=1; self.misses=0; return self.x.copy()


class NearestNeighborMultiTargetTracker:
    """Small deterministic range/velocity multi-target Kalman tracker.

    Predictions are associated to measurements greedily by Mahalanobis distance
    under a chi-square-like gate. Unassigned detections spawn tentative tracks;
    stale tracks are removed after ``max_misses`` predictions.
    """
    def __init__(self, dt: float, gate_d2: float = 9.21, max_misses: int = 4,
                 range_std: float = 2.0, velocity_std: float = 1.0, accel_std: float = 2.0):
        if dt<=0 or gate_d2<=0 or max_misses<0: raise ValueError("invalid tracker configuration")
        self.dt=float(dt); self.gate=float(gate_d2); self.max_misses=int(max_misses)
        self.kw=dict(range_std=range_std,velocity_std=velocity_std,accel_std=accel_std)
        self.tracks=[]; self.next_id=0

    def step(self, measurements: list[tuple[float,float]]):
        Z=[tuple(map(float,z)) for z in measurements]
        for tr in self.tracks: tr.predict()
        pairs=[]
        for ti,tr in enumerate(self.tracks):
            for zi,z in enumerate(Z):
                d2=tr.innovation_distance2(z)
                if d2<=self.gate: pairs.append((d2,ti,zi))
        used_t=set(); used_z=set()
        for _,ti,zi in sorted(pairs):
            if ti in used_t or zi in used_z: continue
            self.tracks[ti].update(Z[zi]); used_t.add(ti); used_z.add(zi)
        self.tracks=[tr for tr in self.tracks if tr.misses<=self.max_misses]
        for zi,z in enumerate(Z):
            if zi not in used_z:
                self.tracks.append(KalmanRangeVelocityTrack(self.next_id,z,self.dt,**self.kw)); self.next_id+=1
        return [(tr.id,float(tr.x[0]),float(tr.x[1]),tr.hits,tr.misses) for tr in self.tracks]
