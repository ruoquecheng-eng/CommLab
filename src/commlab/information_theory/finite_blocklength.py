from statistics import NormalDist
import numpy as np


def complex_awgn_capacity(snr_linear):
    s=np.asarray(snr_linear,dtype=float)
    if np.any(s<0): raise ValueError("SNR must be nonnegative")
    return np.log2(1.0+s)


def complex_awgn_dispersion(snr_linear):
    """Channel dispersion in bit^2/complex-channel-use for complex AWGN."""
    s=np.asarray(snr_linear,dtype=float)
    if np.any(s<0): raise ValueError("SNR must be nonnegative")
    return (1.0-1.0/(1.0+s)**2)*(np.log2(np.e)**2)


def normal_approximation_rate(snr_linear, blocklength: int, error_probability: float, third_order: bool = True):
    """Finite-blocklength normal approximation for a complex AWGN channel.

    R ~= C - sqrt(V/n) Q^{-1}(eps) + log2(n)/(2n).
    The result is clipped at zero and is an asymptotic approximation, not a
    replacement for code-specific finite-length simulation.
    """
    n=np.asarray(blocklength,dtype=float); eps=float(error_probability)
    if np.any(n<1) or not (0<eps<0.5): raise ValueError("require n>=1 and 0<eps<0.5")
    s=np.asarray(snr_linear,dtype=float); C=complex_awgn_capacity(s); V=complex_awgn_dispersion(s)
    qinv=NormalDist().inv_cdf(1.0-eps)
    R=C-np.sqrt(V/n)*qinv
    if third_order: R=R+np.log2(n)/(2*n)
    return np.maximum(R,0.0)


def normal_approximation_error_probability(snr_linear, blocklength: int, rate: float, third_order: bool = True):
    """Invert the normal approximation to estimate packet error probability.

    This remains an asymptotic approximation and should not be interpreted as a
    code-specific decoder curve.
    """
    n=float(blocklength); r=float(rate); s=np.asarray(snr_linear,float)
    if n<1 or r<0 or np.any(s<0): raise ValueError('invalid finite-blocklength inputs')
    C=complex_awgn_capacity(s); V=np.maximum(complex_awgn_dispersion(s),1e-15)
    corr=np.log2(n)/(2*n) if third_order else 0.0
    z=(C+corr-r)*np.sqrt(n/V)
    nd=NormalDist()
    # Q(z)=1-Phi(z); vectorize the scalar stdlib CDF.
    q=np.vectorize(lambda t: 1.0-nd.cdf(float(t)))(z)
    return np.clip(q,0.0,1.0)
