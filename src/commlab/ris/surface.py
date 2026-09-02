import numpy as np


def optimal_ris_phases(h_bs_ris: np.ndarray, h_ris_user: np.ndarray, h_direct: complex = 0j) -> np.ndarray:
    """Continuous phase-only RIS configuration for a SISO cascaded channel.

    The reflected terms h_ru[n] * exp(j theta[n]) * h_br[n] are co-phased
    with the direct path when it is present, otherwise with the positive real
    axis. Unit reflection amplitude is assumed.
    """
    a=np.asarray(h_bs_ris,dtype=np.complex128).reshape(-1)
    b=np.asarray(h_ris_user,dtype=np.complex128).reshape(-1)
    if len(a)==0 or a.shape!=b.shape: raise ValueError("RIS channel vectors must be non-empty and equal length")
    casc=a*b
    target=np.angle(complex(h_direct)) if abs(h_direct)>1e-15 else 0.0
    return np.angle(np.exp(1j*(target-np.angle(casc))))


def quantize_phases(phases_rad: np.ndarray, bits: int) -> np.ndarray:
    """Nearest-neighbour uniform phase quantizer over [0, 2pi)."""
    p=np.asarray(phases_rad,dtype=float)
    b=int(bits)
    if b<1: raise ValueError("bits must be >= 1")
    levels=2**b; step=2*np.pi/levels
    wrapped=np.mod(p,2*np.pi)
    q=np.mod(np.round(wrapped/step)*step,2*np.pi)
    return np.angle(np.exp(1j*q))


def ris_effective_channel(h_bs_ris: np.ndarray, h_ris_user: np.ndarray,
                          phases_rad: np.ndarray, h_direct: complex = 0j,
                          amplitude: float = 1.0) -> complex:
    a=np.asarray(h_bs_ris,dtype=np.complex128).reshape(-1)
    b=np.asarray(h_ris_user,dtype=np.complex128).reshape(-1)
    th=np.asarray(phases_rad,dtype=float).reshape(-1)
    if len(a)==0 or a.shape!=b.shape or a.shape!=th.shape or not (0<=amplitude<=1):
        raise ValueError("invalid RIS dimensions/amplitude")
    return complex(h_direct) + float(amplitude)*np.sum(a*b*np.exp(1j*th))


def ris_spectral_efficiency(h_eff: complex, snr_linear: float) -> float:
    if snr_linear<=0: raise ValueError("snr_linear must be positive")
    return float(np.log2(1+float(snr_linear)*abs(complex(h_eff))**2))
