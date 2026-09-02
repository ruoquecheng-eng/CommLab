import numpy as np

C0 = 299_792_458.0


def simulate_ofdm_sensing_channel(tx_grid: np.ndarray, subcarrier_spacing_hz: float,
                                  symbol_period_s: float,
                                  targets: list[tuple[float,float,complex]],
                                  carrier_frequency_hz: float,
                                  noise_var: float = 0.0,
                                  rng: np.random.Generator | None = None) -> np.ndarray:
    """Frequency-domain communication-centric OFDM sensing model.

    ``targets`` entries are ``(range_m, radial_velocity_mps, complex_gain)``.
    A monostatic two-way delay ``2R/c`` and Doppler ``2v fc/c`` are used.
    The narrowband model neglects range migration and ICI within one symbol,
    making it suitable for range-Doppler processing demonstrations.
    """
    X=np.asarray(tx_grid,dtype=np.complex128)
    if X.ndim!=2 or subcarrier_spacing_hz<=0 or symbol_period_s<=0 or carrier_frequency_hz<=0 or noise_var<0:
        raise ValueError("invalid OFDM sensing parameters")
    nsym,nsc=X.shape
    k=np.arange(nsc,dtype=float)-nsc//2
    m=np.arange(nsym,dtype=float)
    Y=np.zeros_like(X)
    for range_m,velocity_mps,gain in targets:
        tau=2.0*float(range_m)/C0
        fd=2.0*float(velocity_mps)*float(carrier_frequency_hz)/C0
        range_phase=np.exp(-1j*2*np.pi*k*float(subcarrier_spacing_hz)*tau)
        doppler_phase=np.exp(1j*2*np.pi*fd*m*float(symbol_period_s))
        Y += complex(gain)*X*doppler_phase[:,None]*range_phase[None,:]
    if noise_var>0:
        rg=np.random.default_rng() if rng is None else rng
        Y += np.sqrt(noise_var/2)*(rg.normal(size=Y.shape)+1j*rg.normal(size=Y.shape))
    return Y


def range_doppler_map(rx_grid: np.ndarray, tx_grid: np.ndarray,
                      subcarrier_spacing_hz: float, symbol_period_s: float,
                      carrier_frequency_hz: float,
                      window: bool = True) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Estimate a monostatic OFDM range-Doppler map from known symbols.

    Data modulation is removed via ``rx/tx``. An IFFT across subcarriers maps
    frequency slope to delay/range; an FFT across OFDM symbols maps slow-time
    phase rotation to Doppler/velocity.
    """
    Y=np.asarray(rx_grid,dtype=np.complex128); X=np.asarray(tx_grid,dtype=np.complex128)
    if Y.shape!=X.shape or Y.ndim!=2 or np.any(np.abs(X)<1e-12):
        raise ValueError("rx/tx grids must match and contain nonzero known symbols")
    nsym,nsc=X.shape
    Z=Y/X
    if window:
        Z=Z*np.hanning(nsym)[:,None]*np.hanning(nsc)[None,:]
    delay=np.fft.ifft(np.fft.ifftshift(Z,axes=1),axis=1)
    rd=np.fft.fftshift(np.fft.fft(delay,axis=0),axes=0)
    ranges=np.arange(nsc,dtype=float)*C0/(2.0*nsc*float(subcarrier_spacing_hz))
    fd=np.fft.fftshift(np.fft.fftfreq(nsym,d=float(symbol_period_s)))
    velocities=fd*C0/(2.0*float(carrier_frequency_hz))
    return rd,ranges,velocities


def strongest_targets(rd_map: np.ndarray, ranges_m: np.ndarray, velocities_mps: np.ndarray,
                      count: int = 1, guard_cells: tuple[int,int] = (1,1)) -> list[tuple[float,float,float]]:
    """Greedy peak picker returning ``(range_m, velocity_mps, magnitude)``."""
    A=np.abs(np.asarray(rd_map,dtype=np.complex128)).copy()
    rr=np.asarray(ranges_m,dtype=float); vv=np.asarray(velocities_mps,dtype=float)
    if A.ndim!=2 or A.shape!=(len(vv),len(rr)) or count<1:
        raise ValueError("invalid range-Doppler dimensions")
    out=[]; gd,gk=map(int,guard_cells)
    for _ in range(min(int(count),A.size)):
        i,j=np.unravel_index(int(np.argmax(A)),A.shape); mag=float(A[i,j])
        out.append((float(rr[j]),float(vv[i]),mag))
        A[max(0,i-gd):min(A.shape[0],i+gd+1),max(0,j-gk):min(A.shape[1],j+gk+1)]=0
    return out


def ca_cfar_2d(rd_map: np.ndarray, training: tuple[int,int] = (4,4),
               guard: tuple[int,int] = (1,1), pfa: float = 1e-3) -> tuple[np.ndarray,np.ndarray]:
    """Rectangular 2-D cell-averaging CFAR on range-Doppler power.

    Returns ``(detections, threshold_power)``. Edges where the complete
    training window is unavailable are left undetected. The scale factor uses
    the exponential-noise CA-CFAR approximation.
    """
    Z=np.asarray(rd_map,dtype=np.complex128)
    if Z.ndim!=2 or not (0<pfa<1): raise ValueError("invalid CFAR inputs")
    td,tr=map(int,training); gd,gr=map(int,guard)
    if min(td,tr)<1 or min(gd,gr)<0: raise ValueError("invalid CFAR windows")
    P=np.abs(Z)**2; nr,nc=P.shape
    wd=td+gd; wr=tr+gr
    det=np.zeros_like(P,dtype=bool); thr=np.full_like(P,np.nan,dtype=float)
    n_total=(2*wd+1)*(2*wr+1); n_guard=(2*gd+1)*(2*gr+1); n_train=n_total-n_guard
    alpha=n_train*(pfa**(-1.0/n_train)-1.0)
    # Integral image for O(1) rectangular sums.
    S=np.pad(P,((1,0),(1,0))).cumsum(0).cumsum(1)
    def rect_sum(r0,r1,c0,c1):
        return S[r1+1,c1+1]-S[r0,c1+1]-S[r1+1,c0]+S[r0,c0]
    for i in range(wd,nr-wd):
        for j in range(wr,nc-wr):
            outer=rect_sum(i-wd,i+wd,j-wr,j+wr)
            inner=rect_sum(i-gd,i+gd,j-gr,j+gr)
            noise=max(float((outer-inner)/n_train),1e-30); threshold=alpha*noise
            thr[i,j]=threshold; det[i,j]=P[i,j]>threshold
    return det,thr
