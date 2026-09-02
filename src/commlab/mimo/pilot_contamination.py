import numpy as np


def mrt_leakage_from_pilot_estimate(h_desired: np.ndarray, h_interferer: np.ndarray,
                                    pilot_snr_linear: float, contamination_beta: float = 0.0,
                                    rng: np.random.Generator | None = None,
                                    leakage_beta: float | None = None) -> tuple[float,float,float]:
    """Estimate a channel from a reused pilot and report MRT desired/leakage power.

    h_hat = h_desired + sqrt(beta) h_interferer + pilot noise.  The returned
    tuple is (desired beamformed power, leakage toward contaminating user, SIR).
    This is a deliberately small pilot-contamination baseline.
    """
    h=np.asarray(h_desired,dtype=np.complex128).reshape(-1); g=np.asarray(h_interferer,dtype=np.complex128).reshape(-1)
    if h.shape!=g.shape or pilot_snr_linear<=0 or contamination_beta<0: raise ValueError("invalid pilot contamination inputs")
    lb=float(contamination_beta if leakage_beta is None else leakage_beta)
    if lb<0: raise ValueError("leakage_beta must be nonnegative")
    rg=np.random.default_rng() if rng is None else rng
    noise=(rg.normal(size=len(h))+1j*rg.normal(size=len(h)))/np.sqrt(2*pilot_snr_linear)
    hh=h+np.sqrt(float(contamination_beta))*g+noise; w=hh/ max(np.linalg.norm(hh),1e-15)
    desired=float(abs(np.vdot(h,w))**2); leak=float(abs(np.vdot(g,w))**2)*lb
    return desired,leak,desired/max(leak,1e-15)
