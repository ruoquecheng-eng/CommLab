import numpy as np
from .core import otfs_pilot_dictionary


def refine_delay_doppler_paths(received_dd: np.ndarray, pilot_grid: np.ndarray,
                               coarse_paths: list[tuple[int,float,complex]],
                               doppler_half_width: float = 0.6,
                               doppler_points: int = 25,
                               cp_len: int = 0,
                               coordinate_passes: int = 2) -> tuple[list[tuple[int,float,complex]],float]:
    """Local off-grid Doppler refinement around coarse sparse OTFS paths.

    Delays remain integer-sample in this small prototype. For each coarse path,
    a dense local Doppler grid is searched while the other paths are held fixed;
    gains are re-solved jointly by least squares after each coordinate update.
    This closes part of the grid-mismatch gap without claiming a standards-level
    fractional-delay/fractional-Doppler estimator.
    """
    y=np.asarray(received_dd,dtype=np.complex128).reshape(-1)
    P=np.asarray(pilot_grid,dtype=np.complex128)
    if P.ndim!=2 or not coarse_paths or doppler_points<3 or doppler_half_width<=0:
        raise ValueError("invalid OTFS refinement inputs")
    params=[(int(d),float(k)) for d,k,_ in coarse_paths]

    def column(d,k):
        D,_=otfs_pilot_dictionary(P,[d],[k],cp_len)
        return D[:,0]

    cols=[column(d,k) for d,k in params]
    for _ in range(int(coordinate_passes)):
        for q,(d,k0) in enumerate(params):
            best=None
            candidates=np.linspace(k0-doppler_half_width,k0+doppler_half_width,int(doppler_points))
            for kc in candidates:
                trial_cols=cols.copy(); trial_cols[q]=column(d,float(kc))
                D=np.column_stack(trial_cols)
                c=np.linalg.lstsq(D,y,rcond=None)[0]
                resid=float(np.linalg.norm(y-D@c))
                if best is None or resid<best[0]: best=(resid,float(kc),trial_cols,c)
            _,kb,cols,c=best; params[q]=(d,kb)
    D=np.column_stack(cols); gains=np.linalg.lstsq(D,y,rcond=None)[0]
    rel=float(np.linalg.norm(y-D@gains)/max(np.linalg.norm(y),1e-15))
    return [(d,k,complex(g)) for (d,k),g in zip(params,gains)],rel


def _fractional_delay_linear(x: np.ndarray, delay_samples: float) -> np.ndarray:
    """Finite-record fractional delay via complex linear interpolation."""
    s=np.asarray(x,dtype=np.complex128).reshape(-1); t=np.arange(len(s),dtype=float)-float(delay_samples)
    base=np.arange(len(s),dtype=float)
    re=np.interp(t,base,s.real,left=0.0,right=0.0); im=np.interp(t,base,s.imag,left=0.0,right=0.0)
    return re+1j*im


def apply_fractional_delay_doppler_paths(waveform: np.ndarray,
                                         paths: list[tuple[float,float,complex]],
                                         n_subcarriers: int, n_slots: int) -> np.ndarray:
    """Educational fractional-delay/fractional-Doppler OTFS channel."""
    x=np.asarray(waveform,dtype=np.complex128).reshape(-1); y=np.zeros_like(x); n=np.arange(len(x),dtype=float)
    denom=float(n_subcarriers*n_slots)
    for delay,doppler,gain in paths:
        shifted=_fractional_delay_linear(x,float(delay))
        y += complex(gain)*shifted*np.exp(1j*2*np.pi*float(doppler)*n/denom)
    return y


def refine_fractional_delay_doppler_paths(received_dd: np.ndarray, pilot_grid: np.ndarray,
                                           coarse_paths: list[tuple[int,float,complex]],
                                           delay_half_width: float = 0.6,
                                           doppler_half_width: float = 0.6,
                                           points: int = 15, cp_len: int = 0,
                                           coordinate_passes: int = 2):
    """Local 2-D fractional delay/Doppler coordinate refinement.

    Uses the same compact linear-interpolation channel model for dictionary
    generation and therefore serves as a controlled grid-mismatch experiment,
    not a standards-grade fractional-delay estimator.
    """
    from .core import otfs_modulate, otfs_demodulate
    y=np.asarray(received_dd,dtype=np.complex128).reshape(-1); P=np.asarray(pilot_grid,dtype=np.complex128)
    if P.ndim!=2 or not coarse_paths or points<5: raise ValueError("invalid fractional refinement inputs")
    N,M=P.shape; x=otfs_modulate(P,cp_len)
    params=[(float(d),float(k)) for d,k,_ in coarse_paths]
    def col(d,k):
        w=apply_fractional_delay_doppler_paths(x,[(d,k,1+0j)],M,N)
        return otfs_demodulate(w,N,M,cp_len).reshape(-1)
    cols=[col(d,k) for d,k in params]
    for _ in range(int(coordinate_passes)):
        for q,(d0,k0) in enumerate(params):
            best=None
            for dc in np.linspace(max(0,d0-delay_half_width),d0+delay_half_width,int(points)):
                for kc in np.linspace(k0-doppler_half_width,k0+doppler_half_width,int(points)):
                    trial=cols.copy(); trial[q]=col(float(dc),float(kc)); D=np.column_stack(trial)
                    c=np.linalg.lstsq(D,y,rcond=None)[0]; resid=float(np.linalg.norm(y-D@c))
                    if best is None or resid<best[0]: best=(resid,float(dc),float(kc),trial)
            _,db,kb,cols=best; params[q]=(db,kb)
    D=np.column_stack(cols); gains=np.linalg.lstsq(D,y,rcond=None)[0]
    rel=float(np.linalg.norm(y-D@gains)/max(np.linalg.norm(y),1e-15))
    return [(d,k,complex(g)) for (d,k),g in zip(params,gains)],rel
