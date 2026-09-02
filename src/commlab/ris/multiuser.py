import numpy as np
from commlab.mimo.mu_precoding import zf_precoder, mrt_precoder, downlink_sinr, sum_rate_from_sinr


def effective_multiuser_channel(h_direct: np.ndarray, g_bs_ris: np.ndarray,
                                h_ris_user: np.ndarray, phases: np.ndarray,
                                amplitude: float = 1.0) -> np.ndarray:
    """Effective K x Nt MISO channel through a phase-only RIS."""
    D=np.asarray(h_direct,np.complex128); G=np.asarray(g_bs_ris,np.complex128)
    R=np.asarray(h_ris_user,np.complex128); th=np.asarray(phases,float).reshape(-1)
    if D.ndim!=2 or G.ndim!=2 or R.ndim!=2 or R.shape[0]!=D.shape[0] or G.shape[1]!=D.shape[1] or G.shape[0]!=R.shape[1] or len(th)!=G.shape[0] or not (0<=amplitude<=1):
        raise ValueError("invalid RIS/MISO dimensions")
    return D + float(amplitude)*(R*np.exp(1j*th)[None,:])@G


def ris_mu_sum_rate(h_direct: np.ndarray, g_bs_ris: np.ndarray, h_ris_user: np.ndarray,
                    phases: np.ndarray, snr_linear: float, precoder: str = "zf") -> float:
    H=effective_multiuser_channel(h_direct,g_bs_ris,h_ris_user,phases)
    if precoder=="zf": W=zf_precoder(H)
    elif precoder=="mrt": W=mrt_precoder(H)
    else: raise ValueError("precoder must be 'zf' or 'mrt'")
    return sum_rate_from_sinr(downlink_sinr(H,W,snr_linear))


def coordinate_optimize_ris(h_direct: np.ndarray, g_bs_ris: np.ndarray, h_ris_user: np.ndarray,
                            snr_linear: float, bits: int = 2, iterations: int = 2,
                            initial_phases: np.ndarray | None = None,
                            precoder: str = "zf") -> tuple[np.ndarray, list[float]]:
    """Discrete coordinate ascent over RIS phases for MU-MISO sum rate.

    This is deliberately transparent rather than globally optimal: each RIS
    element is swept over 2**bits phases while recomputing the digital precoder.
    The returned history is non-decreasing by construction.
    """
    N=np.asarray(g_bs_ris).shape[0]
    if bits<1 or iterations<1: raise ValueError("invalid optimization parameters")
    if initial_phases is None: th=np.zeros(N,float)
    else:
        th=np.asarray(initial_phases,float).reshape(-1).copy()
        if len(th)!=N: raise ValueError("invalid initial phases")
    levels=np.arange(2**int(bits))*2*np.pi/(2**int(bits))
    best=ris_mu_sum_rate(h_direct,g_bs_ris,h_ris_user,th,snr_linear,precoder)
    hist=[best]
    for _ in range(int(iterations)):
        for n in range(N):
            old=th[n]; local_best=best; best_phase=old
            for p in levels:
                th[n]=p
                val=ris_mu_sum_rate(h_direct,g_bs_ris,h_ris_user,th,snr_linear,precoder)
                if val>local_best+1e-12: local_best=val; best_phase=float(p)
            th[n]=best_phase; best=local_best
        hist.append(best)
    return np.angle(np.exp(1j*th)),hist
