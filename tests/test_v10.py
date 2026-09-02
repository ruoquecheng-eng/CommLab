import numpy as np

from commlab.coding import SparseAccumulatorLDPC, ldpc_incremental_redundancy_schedule, IncrementalRedundancyCombiner
from commlab.link import OuterLoopLinkAdaptation, select_mcs, logistic_bler
from commlab.sensing import C0, simulate_ofdm_sensing_channel, range_doppler_map, strongest_targets
from commlab.otfs import otfs_modulate, otfs_demodulate, apply_delay_doppler_paths, omp_estimate_delay_doppler_paths, refine_delay_doppler_paths


def test_ir_schedule_and_combiner_cover_mother_code():
    sch=ldpc_incremental_redundancy_schedule(96,192,4)
    assert len(sch)==4
    assert len(sch[0])==120 and all(len(x)==24 for x in sch[1:])
    assert np.array_equal(np.sort(np.concatenate(sch)),np.arange(192))
    c=IncrementalRedundancyCombiner(8)
    c.add(np.array([0,2,4]),np.array([1.,2.,3.]))
    c.add(np.array([2,5]),np.array([4.,6.]))
    assert np.allclose(c.llr[[0,2,4,5]],[1,6,3,6])
    assert c.transmitted_bits==5 and c.transmissions==2


def test_ir_full_redundancy_noiseless_ldpc_decode():
    rng=np.random.default_rng(10); code=SparseAccumulatorLDPC(k=96,seed=1701)
    u=rng.integers(0,2,code.k,dtype=np.uint8); cw=code.encode(u)
    sch=ldpc_incremental_redundancy_schedule(code.k,code.n,4); buf=IncrementalRedundancyCombiner(code.n)
    for idx in sch:
        llr=(1-2*cw[idx].astype(float))*40.0
        full=buf.add(idx,llr)
    dec,it,ok=code.decode_min_sum(full,max_iter=40)
    assert ok and np.array_equal(dec,u)


def test_olla_direction_and_target_curve():
    olla=OuterLoopLinkAdaptation(target_bler=0.1,nack_step_db=.3)
    a=olla.offset_db; olla.update(False); assert olla.offset_db>a
    b=olla.offset_db; olla.update(True); assert olla.offset_db<b
    idx,eff=select_mcs(7.1,[0,4,8],[1,2,4]); assert idx==1 and eff==2
    assert abs(logistic_bler(4.0,4.0,midpoint_bler=.1)-.1)<1e-12


def test_ofdm_sensing_single_on_grid_target():
    nsc=64; nsym=64; df=15e3; Ts=1/df; fc=24e9
    dr=C0/(2*nsc*df); dv=(1/(nsym*Ts))*C0/(2*fc)
    target=(3*dr,5*dv,1+0j)
    X=np.ones((nsym,nsc),dtype=np.complex128)
    Y=simulate_ofdm_sensing_channel(X,df,Ts,[target],fc)
    rd,r,v=range_doppler_map(Y,X,df,Ts,fc,window=False)
    peak=strongest_targets(rd,r,v,1)[0]
    assert abs(peak[0]-target[0])<dr*.1
    assert abs(peak[1]-target[1])<dv*.1


def test_otfs_offgrid_refinement_improves_residual_and_doppler():
    N=M=8; P=np.zeros((N,M),complex); P[0,0]=1
    true=[(2,1.35,0.8+0.25j)]
    x=otfs_modulate(P,0); y=apply_delay_doppler_paths(x,true,M,N); Y=otfs_demodulate(y,N,M,0)
    coarse,res0=omp_estimate_delay_doppler_paths(Y,P,range(0,4),range(-3,4),1,0)
    refined,res1=refine_delay_doppler_paths(Y,P,coarse,doppler_half_width=.6,doppler_points=31,coordinate_passes=2)
    assert abs(refined[0][1]-1.35) < abs(coarse[0][1]-1.35)
    assert res1 < res0


def test_ca_cfar_detects_isolated_peak():
    from commlab.sensing import ca_cfar_2d
    rng=np.random.default_rng(11); z=(rng.normal(size=(40,50))+1j*rng.normal(size=(40,50)))*0.1
    z[20,25]=10+0j
    det,thr=ca_cfar_2d(z,training=(3,3),guard=(1,1),pfa=1e-3)
    assert det[20,25] and np.isfinite(thr[20,25])
