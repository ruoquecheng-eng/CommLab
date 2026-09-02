import numpy as np
from commlab.mimo import user_centric_mask, clustered_mrt_precoder, cell_free_user_rates
from commlab.ris import coordinate_optimize_ris, ris_mu_sum_rate
from commlab.sensing import ula_beam_gain, KalmanAngleTracker


def test_user_centric_mask_has_exact_cluster_size():
    beta=np.array([[1,4,2,3],[8,1,2,7]],float)
    m=user_centric_mask(beta,2)
    assert np.all(m.sum(axis=1)==2)
    assert set(np.where(m[0])[0])=={1,3}


def test_clustered_mrt_dimensions_and_rates():
    H=np.array([[1,0.2j,0.5],[0.1,1,-0.3j]],complex)
    m=np.array([[1,0,1],[0,1,1]],bool)
    W=clustered_mrt_precoder(H,m)
    r=cell_free_user_rates(H,W,10)
    assert W.shape==(3,2) and np.all(np.isfinite(r)) and np.all(r>=0)


def test_ris_coordinate_ascent_is_non_decreasing():
    rng=np.random.default_rng(13); k,nt,n=2,3,8
    D=.2*(rng.normal(size=(k,nt))+1j*rng.normal(size=(k,nt)))/np.sqrt(2)
    G=(rng.normal(size=(n,nt))+1j*rng.normal(size=(n,nt)))/np.sqrt(2*n)
    R=(rng.normal(size=(k,n))+1j*rng.normal(size=(k,n)))/np.sqrt(2*n)
    init=rng.uniform(-np.pi,np.pi,n)
    base=ris_mu_sum_rate(D,G,R,init,10)
    _,hist=coordinate_optimize_ris(D,G,R,10,bits=2,iterations=2,initial_phases=init)
    assert hist[0]>=base-1e-10 and np.all(np.diff(hist)>=-1e-10) and hist[-1]>=hist[0]


def test_ula_beam_gain_peaks_at_true_angle():
    true=17.0
    assert np.isclose(ula_beam_gain(true,true,16),1.0,atol=1e-12)
    assert ula_beam_gain(true,true,16)>ula_beam_gain(true,true+15,16)


def test_kalman_angle_tracker_predicts_through_missed_measurement():
    tr=KalmanAngleTracker(0,5,1,measurement_std_deg=.5,angular_accel_std_dps2=.5)
    tr.step(5.1); a,_=tr.step(None)
    assert 8<a<12

from commlab.sensing import KalmanAngleAccelerationTracker

def test_constant_acceleration_tracker_predicts_quadratic_motion():
    tr=KalmanAngleAccelerationTracker(0,2,1,1,measurement_std_deg=.1,jerk_std_dps3=.05)
    # Feed nearly exact positions for a few seconds then coast one step.
    for t in range(1,5): tr.step(2*t+.5*t*t)
    a,_,_=tr.step(None)
    assert abs(a-(2*5+.5*25))<1.0
from commlab.sensing import select_robust_ula_aperture

def test_robust_aperture_shrinks_when_angle_uncertainty_is_large():
    low,_=select_robust_ula_aperture(.2,[8,16,32,64],1.0)
    high,_=select_robust_ula_aperture(8.0,[8,16,32,64],1.0)
    assert low>=high
from commlab.mimo import clustered_mrt_directions, max_min_sinr_power_allocation, rates_with_power

def test_max_min_power_allocation_equalizes_fixed_direction_sinr():
    H=np.array([[2,0.2],[0.1,0.7]],complex)
    V=clustered_mrt_directions(H,np.eye(2,dtype=bool))
    p,g=max_min_sinr_power_allocation(H,V,10,total_power=1)
    r=rates_with_power(H,V,p,10); sinr=2**r-1
    assert np.isclose(p.sum(),1.0) and g>0
    assert abs(sinr[0]-sinr[1])/max(sinr)<1e-6
