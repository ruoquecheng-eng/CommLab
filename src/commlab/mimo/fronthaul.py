import numpy as np


def quantize_complex_csi(h: np.ndarray, bits: int, clip_sigma: float = 3.0) -> np.ndarray:
    """Uniform scalar quantization of real/imaginary CSI components.

    The dynamic range is set independently for each input tensor from its RMS
    component scale. This is an educational fronthaul/CSI compression baseline,
    not a standards codebook or entropy-coded representation.
    """
    x=np.asarray(h,np.complex128)
    if bits<1 or clip_sigma<=0 or x.size==0: raise ValueError('invalid CSI quantizer parameters')
    if np.allclose(x,0): return np.zeros_like(x)
    comp=np.concatenate([x.real.reshape(-1),x.imag.reshape(-1)])
    sigma=float(np.sqrt(np.mean(comp**2)))
    # Use the larger of an RMS-based range and the observed peak so this
    # baseline measures quantization resolution rather than accidental clipping.
    lim=max(float(clip_sigma)*sigma,float(np.max(np.abs(comp))),1e-12)
    levels=2**int(bits)
    step=2*lim/(levels-1)
    def q(v):
        z=np.clip(v,-lim,lim)
        return -lim+np.rint((z+lim)/step)*step
    return q(x.real)+1j*q(x.imag)


def csi_quantization_nmse(h: np.ndarray, hq: np.ndarray) -> float:
    a=np.asarray(h,np.complex128); b=np.asarray(hq,np.complex128)
    if a.shape!=b.shape: raise ValueError('shape mismatch')
    return float(np.sum(np.abs(a-b)**2)/max(np.sum(np.abs(a)**2),1e-15))


def fronthaul_csi_bits(mask: np.ndarray, bits_per_component: int, updates_per_second: float = 1.0) -> float:
    """Abstract CSI fronthaul rate for selected AP-user links.

    Each complex coefficient uses two scalar components.  ``mask`` is users x
    APs and can represent user-centric clustering. The returned value is bits/s.
    """
    s=np.asarray(mask,bool)
    if s.ndim!=2 or bits_per_component<1 or updates_per_second<=0: raise ValueError('invalid fronthaul inputs')
    return float(s.sum()*2*int(bits_per_component)*float(updates_per_second))


def gauss_markov_channel_step(h: np.ndarray, beta: np.ndarray, correlation: float,
                              rng: np.random.Generator) -> np.ndarray:
    """One proper-complex Gauss-Markov fading step preserving variance ``beta``."""
    x=np.asarray(h,np.complex128); b=np.asarray(beta,float)
    if x.shape!=b.shape or not (0<=correlation<=1) or np.any(b<0): raise ValueError('invalid aging inputs')
    z=(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape))/np.sqrt(2)
    return float(correlation)*x+np.sqrt(max(1-float(correlation)**2,0))*np.sqrt(b)*z
