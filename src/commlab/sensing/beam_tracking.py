import numpy as np


def ula_beam_gain(true_angle_deg: float | np.ndarray, beam_angle_deg: float | np.ndarray,
                  elements: int, spacing_wavelength: float = 0.5) -> np.ndarray:
    """Normalized ULA power gain |a(theta)^H a(phi)|^2 in [0,1]."""
    if elements<1 or spacing_wavelength<=0: raise ValueError("invalid array")
    t=np.deg2rad(np.asarray(true_angle_deg,float)); b=np.deg2rad(np.asarray(beam_angle_deg,float))
    delta=2*np.pi*float(spacing_wavelength)*(np.sin(t)-np.sin(b))
    n=np.arange(int(elements),dtype=float)
    # Broadcast angle dimensions against element axis.
    s=np.mean(np.exp(1j*np.expand_dims(delta,-1)*n),axis=-1)
    return np.abs(s)**2


class KalmanAngleTracker:
    """Constant-angular-velocity Kalman tracker with optional missed updates."""
    def __init__(self, angle0_deg: float, angular_velocity0_dps: float, dt: float,
                 measurement_std_deg: float = 1.5, angular_accel_std_dps2: float = 4.0):
        if dt<=0 or measurement_std_deg<=0 or angular_accel_std_dps2<=0: raise ValueError("invalid tracker parameters")
        self.dt=float(dt); self.x=np.array([angle0_deg,angular_velocity0_dps],float)
        d=self.dt; q=angular_accel_std_dps2**2
        self.F=np.array([[1,d],[0,1]],float)
        self.Q=q*np.array([[d**4/4,d**3/2],[d**3/2,d**2]],float)
        self.H=np.array([[1.,0.]]); self.R=np.array([[measurement_std_deg**2]])
        self.P=np.diag([measurement_std_deg**2*4,angular_accel_std_dps2**2])

    def predict(self) -> tuple[float,float]:
        self.x=self.F@self.x; self.P=self.F@self.P@self.F.T+self.Q
        return float(self.x[0]),float(self.x[1])

    def update(self, measured_angle_deg: float | None) -> tuple[float,float]:
        if measured_angle_deg is None or not np.isfinite(measured_angle_deg):
            return float(self.x[0]),float(self.x[1])
        z=np.array([float(measured_angle_deg)]); y=z-self.H@self.x; S=self.H@self.P@self.H.T+self.R
        K=self.P@self.H.T@np.linalg.inv(S); self.x=self.x+(K@y).reshape(-1); self.P=(np.eye(2)-K@self.H)@self.P
        return float(self.x[0]),float(self.x[1])

    def step(self, measured_angle_deg: float | None) -> tuple[float,float]:
        self.predict(); return self.update(measured_angle_deg)

class KalmanAngleAccelerationTracker:
    """Constant-angular-acceleration tracker [angle, rate, acceleration]."""
    def __init__(self, angle0_deg: float, angular_velocity0_dps: float, angular_accel0_dps2: float,
                 dt: float, measurement_std_deg: float = 1.5, jerk_std_dps3: float = 8.0):
        if dt<=0 or measurement_std_deg<=0 or jerk_std_dps3<=0: raise ValueError("invalid tracker parameters")
        d=float(dt); self.dt=d; self.x=np.array([angle0_deg,angular_velocity0_dps,angular_accel0_dps2],float)
        self.F=np.array([[1,d,.5*d*d],[0,1,d],[0,0,1]],float)
        q=jerk_std_dps3**2
        g=np.array([d**3/6,d**2/2,d],float)[:,None]; self.Q=q*(g@g.T)
        self.H=np.array([[1.,0.,0.]]); self.R=np.array([[measurement_std_deg**2]])
        self.P=np.diag([measurement_std_deg**2*4,25.,100.])

    def predict(self):
        self.x=self.F@self.x; self.P=self.F@self.P@self.F.T+self.Q
        return tuple(map(float,self.x))

    def update(self, measured_angle_deg: float | None):
        if measured_angle_deg is None or not np.isfinite(measured_angle_deg): return tuple(map(float,self.x))
        z=np.array([float(measured_angle_deg)]); y=z-self.H@self.x; S=self.H@self.P@self.H.T+self.R
        K=self.P@self.H.T@np.linalg.inv(S); self.x=self.x+(K@y).reshape(-1); self.P=(np.eye(3)-K@self.H)@self.P
        return tuple(map(float,self.x))

    def step(self, measured_angle_deg: float | None):
        self.predict(); return self.update(measured_angle_deg)

def expected_ula_rate_under_angle_uncertainty(angle_std_deg: float, elements: int,
                                              snr_per_element_linear: float,
                                              quadrature_points: int = 81) -> float:
    """Expected rate for a beam pointed at the estimated mean angle.

    Angle error is Gaussian. Array peak SNR scales linearly with element count,
    while the normalized beam pattern narrows with aperture. This exposes the
    robustness-vs-array-gain trade-off without assuming a particular RF chain.
    """
    if angle_std_deg<0 or elements<1 or snr_per_element_linear<=0 or quadrature_points<11:
        raise ValueError("invalid uncertainty/array parameters")
    if angle_std_deg==0: return float(np.log2(1+snr_per_element_linear*elements))
    x=np.linspace(-4*angle_std_deg,4*angle_std_deg,int(quadrature_points))
    w=np.exp(-.5*(x/angle_std_deg)**2); w/=w.sum()
    gain=ula_beam_gain(x,0.0,elements)
    return float(np.sum(w*np.log2(1+float(snr_per_element_linear)*elements*gain)))


def select_robust_ula_aperture(angle_std_deg: float, candidate_elements,
                               snr_per_element_linear: float) -> tuple[int,dict[int,float]]:
    vals={int(n):expected_ula_rate_under_angle_uncertainty(angle_std_deg,int(n),snr_per_element_linear) for n in candidate_elements}
    if not vals: raise ValueError("empty candidate set")
    return max(vals,key=vals.get),vals
