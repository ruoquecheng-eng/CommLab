import numpy as np
from .ofdm_radar import C0


def ula_steering_vector(angle_deg: float, n_antennas: int, spacing_wavelength: float = 0.5) -> np.ndarray:
    if n_antennas < 1 or spacing_wavelength <= 0:
        raise ValueError("invalid ULA geometry")
    theta=np.deg2rad(float(angle_deg)); n=np.arange(int(n_antennas),dtype=float)
    return np.exp(1j*2*np.pi*float(spacing_wavelength)*n*np.sin(theta))


def simulate_ofdm_sensing_array_channel(
    tx_grid: np.ndarray,
    subcarrier_spacing_hz: float,
    symbol_period_s: float,
    targets: list[tuple[float,float,float,complex]],
    carrier_frequency_hz: float,
    n_rx: int = 8,
    spacing_wavelength: float = 0.5,
    noise_var: float = 0.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """OFDM sensing channel with a receive ULA.

    Each target is ``(range_m, radial_velocity_mps, angle_deg, complex_gain)``.
    Output shape is ``(n_rx, n_symbols, n_subcarriers)``.
    """
    X=np.asarray(tx_grid,dtype=np.complex128)
    if X.ndim!=2 or n_rx<1 or noise_var<0: raise ValueError("invalid array sensing inputs")
    nsym,nsc=X.shape; k=np.arange(nsc,dtype=float)-nsc//2; m=np.arange(nsym,dtype=float)
    Y=np.zeros((n_rx,nsym,nsc),dtype=np.complex128)
    for R,v,ang,gain in targets:
        tau=2*float(R)/C0; fd=2*float(v)*float(carrier_frequency_hz)/C0
        rp=np.exp(-1j*2*np.pi*k*float(subcarrier_spacing_hz)*tau)
        dp=np.exp(1j*2*np.pi*fd*m*float(symbol_period_s))
        a=ula_steering_vector(float(ang),n_rx,spacing_wavelength)
        Y += complex(gain)*a[:,None,None]*X[None,:,:]*dp[None,:,None]*rp[None,None,:]
    if noise_var>0:
        rg=np.random.default_rng() if rng is None else rng
        Y += np.sqrt(noise_var/2)*(rg.normal(size=Y.shape)+1j*rg.normal(size=Y.shape))
    return Y


def range_doppler_array_cube(rx_array: np.ndarray, tx_grid: np.ndarray,
                             subcarrier_spacing_hz: float, symbol_period_s: float,
                             window: bool = True) -> np.ndarray:
    """Return per-antenna complex range-Doppler cube (ant, doppler, range)."""
    Y=np.asarray(rx_array,dtype=np.complex128); X=np.asarray(tx_grid,dtype=np.complex128)
    if Y.ndim!=3 or Y.shape[1:]!=X.shape or np.any(np.abs(X)<1e-12):
        raise ValueError("invalid array/tx grids")
    Z=Y/X[None,:,:]; nsym,nsc=X.shape
    if window:
        Z=Z*np.hanning(nsym)[None,:,None]*np.hanning(nsc)[None,None,:]
    delay=np.fft.ifft(np.fft.ifftshift(Z,axes=2),axis=2)
    return np.fft.fftshift(np.fft.fft(delay,axis=1),axes=1)


def bartlett_angle_spectrum(spatial_snapshot: np.ndarray, angle_grid_deg: np.ndarray,
                            spacing_wavelength: float = 0.5) -> np.ndarray:
    """Conventional Bartlett beamformer power over an angle grid."""
    x=np.asarray(spatial_snapshot,dtype=np.complex128).reshape(-1)
    ang=np.asarray(angle_grid_deg,dtype=float).reshape(-1)
    if len(x)<1 or len(ang)<1: raise ValueError("empty spatial snapshot/angle grid")
    A=np.column_stack([ula_steering_vector(a,len(x),spacing_wavelength) for a in ang])
    # Unit-norm steering avoids antenna-count scaling ambiguity.
    A=A/np.sqrt(len(x)); return np.abs(A.conj().T@x)**2


def strongest_range_doppler_angle(rx_array: np.ndarray, tx_grid: np.ndarray,
                                   subcarrier_spacing_hz: float, symbol_period_s: float,
                                   carrier_frequency_hz: float, angle_grid_deg: np.ndarray,
                                   spacing_wavelength: float = 0.5,
                                   count: int = 1, window: bool = True):
    """Greedy 3-D Bartlett peak picker: (range, velocity, angle, power)."""
    cube=range_doppler_array_cube(rx_array,tx_grid,subcarrier_spacing_hz,symbol_period_s,window)
    n_rx,nsym,nsc=cube.shape
    ranges=np.arange(nsc)*C0/(2*nsc*float(subcarrier_spacing_hz))
    fd=np.fft.fftshift(np.fft.fftfreq(nsym,d=float(symbol_period_s)))
    velocities=fd*C0/(2*float(carrier_frequency_hz))
    angles=np.asarray(angle_grid_deg,dtype=float)
    P=np.empty((len(angles),nsym,nsc),dtype=float)
    A=np.column_stack([ula_steering_vector(a,n_rx,spacing_wavelength) for a in angles])/np.sqrt(n_rx)
    # beamform every RD cell at once: (angle, ant) @ (ant, cells)
    B=A.conj().T@cube.reshape(n_rx,-1); P=np.abs(B.reshape(len(angles),nsym,nsc))**2
    work=P.copy(); out=[]
    for _ in range(min(int(count),work.size)):
        ia,iv,ir=np.unravel_index(int(np.argmax(work)),work.shape)
        out.append((float(ranges[ir]),float(velocities[iv]),float(angles[ia]),float(work[ia,iv,ir])))
        work[max(0,ia-2):min(len(angles),ia+3),max(0,iv-1):min(nsym,iv+2),max(0,ir-1):min(nsc,ir+2)]=0
    return out,P,ranges,velocities,angles


def bartlett_covariance_spectrum(snapshots: np.ndarray, angle_grid_deg: np.ndarray,
                                  spacing_wavelength: float = 0.5) -> np.ndarray:
    """Conventional covariance Bartlett spectrum from spatial snapshots.

    ``snapshots`` has shape (antennas, snapshots). The result is beam power
    ``a^H R a`` evaluated on the supplied angle grid.
    """
    X=np.asarray(snapshots,dtype=np.complex128)
    ang=np.asarray(angle_grid_deg,dtype=float).reshape(-1)
    if X.ndim!=2 or X.shape[0]<1 or X.shape[1]<1 or len(ang)<1:
        raise ValueError("invalid snapshot matrix/angle grid")
    R=X@X.conj().T/X.shape[1]
    A=np.column_stack([ula_steering_vector(a,X.shape[0],spacing_wavelength) for a in ang])
    return np.maximum(np.real(np.einsum('ai,ab,bi->i',A.conj(),R,A)),0.0)


def music_angle_spectrum(snapshots: np.ndarray, n_sources: int, angle_grid_deg: np.ndarray,
                         spacing_wavelength: float = 0.5, diagonal_loading: float = 0.0) -> np.ndarray:
    """Narrowband MUSIC pseudospectrum for a ULA spatial-snapshot matrix.

    The caller supplies the assumed source count. This educational baseline
    intentionally exposes that model-order assumption rather than estimating it
    internally with AIC/MDL.
    """
    X=np.asarray(snapshots,dtype=np.complex128)
    ang=np.asarray(angle_grid_deg,dtype=float).reshape(-1)
    if X.ndim!=2 or X.shape[1]<1 or not (1<=int(n_sources)<X.shape[0]) or len(ang)<1 or diagonal_loading<0:
        raise ValueError("invalid MUSIC inputs")
    R=X@X.conj().T/X.shape[1]
    if diagonal_loading:
        R=R+float(diagonal_loading)*np.trace(R).real/X.shape[0]*np.eye(X.shape[0])
    vals,vecs=np.linalg.eigh(R); En=vecs[:,:X.shape[0]-int(n_sources)]
    A=np.column_stack([ula_steering_vector(a,X.shape[0],spacing_wavelength) for a in ang])
    proj=En.conj().T@A; den=np.sum(np.abs(proj)**2,axis=0)
    return 1.0/np.maximum(den,1e-15)


def estimate_source_count_mdl(snapshots: np.ndarray, max_sources: int | None = None) -> tuple[int,np.ndarray]:
    """Estimate narrowband source count with Wax-Kailath-style MDL.

    Returns ``(k_hat, mdl_scores)`` for candidate source counts 0..max_sources.
    This is a compact educational implementation and assumes spatially white
    noise and more snapshots than sensors for reliable operation.
    """
    X=np.asarray(snapshots,dtype=np.complex128)
    if X.ndim!=2 or X.shape[0]<2 or X.shape[1]<2: raise ValueError("invalid snapshot matrix")
    m,n=X.shape; kmax=m-1 if max_sources is None else int(max_sources)
    if not (0<=kmax<m): raise ValueError("invalid max_sources")
    R=X@X.conj().T/n
    eig=np.maximum(np.linalg.eigvalsh(R)[::-1].real,1e-15)
    scores=[]
    for k in range(kmax+1):
        noise=eig[k:]
        q=len(noise)
        gm=np.exp(np.mean(np.log(noise))); am=np.mean(noise)
        ll=-n*q*np.log(max(gm/am,1e-15))
        penalty=0.5*k*(2*m-k)*np.log(n)
        scores.append(ll+penalty)
    sc=np.asarray(scores,dtype=float)
    return int(np.argmin(sc)),sc
