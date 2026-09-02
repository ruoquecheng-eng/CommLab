import numpy as np

from commlab.coding import systematic_circular_rv_indices
from commlab.mimo import mmse_sic_detect, mu_mrt_precoder, mu_zf_precoder, downlink_sinr, favorable_propagation_metric
from commlab.sensing import (
    C0, simulate_ofdm_sensing_array_channel, strongest_range_doppler_angle,
    AlphaBetaRangeTracker,
)
from commlab.otfs import otfs_modulate, otfs_demodulate, apply_fractional_delay_doppler_paths, refine_fractional_delay_doppler_paths


def test_systematic_circular_rv_repeats_systematic_and_moves_parity():
    a=systematic_circular_rv_indices(48,96,72,0,4)
    b=systematic_circular_rv_indices(48,96,72,1,4)
    assert len(a)==72 and len(np.unique(a))==72
    assert np.array_equal(a[:48],np.arange(48)) and np.array_equal(b[:48],np.arange(48))
    assert not np.array_equal(a[48:],b[48:])


def test_mmse_sic_noiseless_2x2_qpsk():
    const=np.array([1+1j,1-1j,-1+1j,-1-1j])/np.sqrt(2)
    H=np.array([[1.0+.2j,.3-.1j],[.1+.4j,1.2-.2j]])
    x=np.array([const[0],const[3]])
    y=H@x
    xh=mmse_sic_detect(y,H,const,noise_var=1e-9)
    assert np.allclose(xh,x)


def test_mu_zf_precoder_cancels_interuser_interference():
    H=np.array([[1+.1j,.2+.3j, .5-.1j],[.3-.2j,1-.1j,-.2+.4j]])
    W=mu_zf_precoder(H)
    G=H@W
    assert abs(G[0,1])<1e-10 and abs(G[1,0])<1e-10
    assert np.all(downlink_sinr(H,W,10)>0)
    assert favorable_propagation_metric(H)>=0


def test_array_sensing_recovers_on_grid_range_velocity_angle():
    nsc=64; nsym=64; df=15e3; Ts=1/df; fc=24e9; nrx=12
    dr=C0/(2*nsc*df); dv=(1/(nsym*Ts))*C0/(2*fc)
    X=np.ones((nsym,nsc),complex)
    target=(4*dr,3*dv,20.0,1+0j)
    Y=simulate_ofdm_sensing_array_channel(X,df,Ts,[target],fc,n_rx=nrx)
    peaks,*_=strongest_range_doppler_angle(Y,X,df,Ts,fc,np.arange(-40,41,1),count=1,window=False)
    R,v,a,_=peaks[0]
    assert abs(R-target[0])<.1*dr and abs(v-target[1])<.1*dv and abs(a-target[2])<=1


def test_alpha_beta_tracker_reduces_noisy_range_rmse():
    rng=np.random.default_rng(3); dt=.1; true_v=12.0; n=150
    truth=100+true_v*dt*np.arange(1,n+1); meas=truth+rng.normal(scale=2.5,size=n)
    tr=AlphaBetaRangeTracker(100,true_v,dt,alpha=.45,beta=.08)
    est=np.array([tr.update(float(z))[0] for z in meas])
    assert np.sqrt(np.mean((est-truth)**2)) < np.sqrt(np.mean((meas-truth)**2))


def test_otfs_fractional_delay_doppler_refinement_improves_parameters():
    N=M=8; P=np.zeros((N,M),complex); P[0,0]=1
    true=(2.35,1.42,0.9+.15j); x=otfs_modulate(P,0)
    y=apply_fractional_delay_doppler_paths(x,[true],M,N); Y=otfs_demodulate(y,N,M,0)
    coarse=[(2,1.0,1+0j)]
    refined,res=refine_fractional_delay_doppler_paths(Y,P,coarse,delay_half_width=.6,doppler_half_width=.7,points=13,coordinate_passes=2)
    d,k,_=refined[0]
    assert abs(d-true[0])<abs(2-true[0]) and abs(k-true[1])<abs(1-true[1]) and res<.25

def test_pilot_contamination_function_returns_positive_sir():
    from commlab.mimo import mrt_leakage_from_pilot_estimate
    rng=np.random.default_rng(7); h=np.ones(8,complex); g=1j*np.ones(8,complex)
    d,l,s=mrt_leakage_from_pilot_estimate(h,g,100,0.5,rng)
    assert d>0 and l>0 and s>0

def test_hybrid_beamforming_rate_is_bounded_by_full_digital_svd():
    from commlab.mimo import sparse_geometric_mimo_channel, full_digital_svd_rate, hybrid_dft_svd_rate
    H,_,_=sparse_geometric_mimo_channel(8,32,4,np.random.default_rng(12))
    full=full_digital_svd_rate(H,10,2); hyb=hybrid_dft_svd_rate(H,10,2,4)
    assert hyb>0 and hyb<=full+1e-10

def test_music_resolves_two_independent_sources():
    from commlab.sensing import ula_steering_vector, music_angle_spectrum
    rng=np.random.default_rng(19); n_ant=10; n_snap=120
    A=np.column_stack([ula_steering_vector(-12,n_ant),ula_steering_vector(17,n_ant)])
    S=(rng.normal(size=(2,n_snap))+1j*rng.normal(size=(2,n_snap)))/np.sqrt(2)
    X=A@S+0.08*(rng.normal(size=(n_ant,n_snap))+1j*rng.normal(size=(n_ant,n_snap)))/np.sqrt(2)
    grid=np.linspace(-40,40,801); p=music_angle_spectrum(X,2,grid); work=p.copy(); est=[]
    for _ in range(2):
        i=int(np.argmax(work)); est.append(grid[i]); work[np.abs(grid-grid[i])<4]=0
    est.sort(); assert abs(est[0]+12)<1 and abs(est[1]-17)<1
