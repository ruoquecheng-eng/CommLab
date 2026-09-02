import numpy as np


def random_unit_codebook(n_tx: int, size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    """Generate an isotropic unit-norm complex beamforming codebook."""
    if n_tx<1 or size<1: raise ValueError("invalid codebook dimensions")
    g=rng or np.random.default_rng(); W=(g.normal(size=(size,n_tx))+1j*g.normal(size=(size,n_tx)))/np.sqrt(2)
    return W/np.linalg.norm(W,axis=1,keepdims=True)


def mrt_beamformer(channel: np.ndarray) -> np.ndarray:
    """Maximum-ratio transmit beamformer for MISO channel h (y=h w x+n)."""
    h=np.asarray(channel,dtype=np.complex128)
    norm=np.linalg.norm(h,axis=-1,keepdims=True)
    return np.conj(h)/np.maximum(norm,1e-30)


def select_codebook_beam(channel: np.ndarray, codebook: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    """Select codebook vector maximizing |h w|^2 for each channel sample."""
    h=np.asarray(channel,dtype=np.complex128); W=np.asarray(codebook,dtype=np.complex128)
    if h.shape[-1]!=W.shape[-1]: raise ValueError("channel/codebook dimension mismatch")
    gains=np.abs(np.einsum('...t,bt->...b',h,W))**2
    idx=np.argmax(gains,axis=-1); return W[idx],idx


def miso_effective_gain(channel: np.ndarray, beamformer: np.ndarray) -> np.ndarray:
    h=np.asarray(channel,dtype=np.complex128); w=np.asarray(beamformer,dtype=np.complex128)
    return np.abs(np.sum(h*w,axis=-1))**2
