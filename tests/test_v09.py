import numpy as np


def _qpsk():
    from commlab.modulation import QAMModem
    m=QAMModem(4)
    labels=((np.arange(4)[:,None] >> np.array([1,0])) & 1).astype(np.uint8)
    return m,m.modulate(labels.reshape(-1)),labels


def test_soft_ml_llr_noiseless_signs_correct():
    from commlab.mimo import maxlog_ml_llr
    _,const,labels=_qpsk(); rng=np.random.default_rng(901)
    H=(rng.normal(size=(40,2,2))+1j*rng.normal(size=(40,2,2)))/np.sqrt(2)
    idx=rng.integers(0,4,size=(40,2)); x=const[idx]
    y=np.einsum('bij,bj->bi',H,x)
    L=maxlog_ml_llr(y,H,const,labels,noise_var=1e-3)
    assert np.array_equal((L<0).astype(np.uint8),labels[idx])


def test_soft_kbest_full_list_matches_clipped_ml():
    from commlab.mimo import maxlog_ml_llr,k_best_soft_llr
    _,const,labels=_qpsk(); rng=np.random.default_rng(902)
    H=(rng.normal(size=(20,2,2))+1j*rng.normal(size=(20,2,2)))/np.sqrt(2)
    idx=rng.integers(0,4,size=(20,2)); x=const[idx]
    nv=.2; y=np.einsum('bij,bj->bi',H,x)+np.sqrt(nv/2)*(rng.normal(size=(20,2))+1j*rng.normal(size=(20,2)))
    a=maxlog_ml_llr(y,H,const,labels,nv); b=k_best_soft_llr(y,H,const,labels,nv,k_best=16,llr_clip=40)
    assert np.max(np.abs(np.clip(a,-40,40)-b)) < 1e-9


def test_crc16_detects_bit_flip_and_chase_accumulates():
    from commlab.link import append_crc16,check_crc16,ChaseCombiner
    b=np.random.default_rng(903).integers(0,2,100,dtype=np.uint8); f=append_crc16(b)
    assert check_crc16(f); f2=f.copy(); f2[17]^=1; assert not check_crc16(f2)
    c=ChaseCombiner(3); c.add([1.,-2.,3.]); z=c.add([2.,1.,-1.])
    assert c.transmissions==2 and np.allclose(z,[3.,-1.,2.])


def test_packet_scheduler_delay_pf_runs():
    from commlab.scheduling.queue_aware import simulate_packet_scheduler
    C=np.ones((30,3,4))*1000; C[:,0]*=.5; C[:,2]*=1.5
    A=np.zeros((30,3),int); A[:20]=1
    r=simulate_packet_scheduler(C,A,packet_size_bits=3000,policy='delay_pf',beta=.9)
    assert r['completed_packets']>0 and r['backlog_bits'].shape==(30,3)


def test_otfs_omp_recovers_integer_paths_noiseless():
    from commlab.otfs import otfs_modulate,otfs_demodulate,apply_delay_doppler_paths,omp_estimate_delay_doppler_paths
    N,M=6,12; P=np.zeros((N,M),complex); P[0,0]=1
    paths=[(1,1,0.8+0.2j),(3,-2,-0.35+0.4j)]
    x=otfs_modulate(P); y=apply_delay_doppler_paths(x,paths,M,N); Y=otfs_demodulate(y,N,M)
    est,rel=omp_estimate_delay_doppler_paths(Y,P,range(0,5),range(-2,3),2)
    true={(d,float(k)) for d,k,_ in paths}; got={(d,float(k)) for d,k,_ in est}
    assert got==true and rel<1e-10


def test_banded_ici_ls_recovers_noiseless_matrix():
    from commlab.equalization import estimate_banded_ici_matrix
    rng=np.random.default_rng(904); n=20; bw=2
    H=np.zeros((n,n),complex)
    for i in range(n):
        lo=max(0,i-bw); hi=min(n,i+bw+1)
        H[i,lo:hi]=(rng.normal(size=hi-lo)+1j*rng.normal(size=hi-lo))/np.sqrt(2*(2*bw+1))
    X=(rng.normal(size=(20,n))+1j*rng.normal(size=(20,n)))/np.sqrt(2)
    Y=X@H.T
    He=estimate_banded_ici_matrix(X,Y,bw)
    assert np.linalg.norm(He-H)/np.linalg.norm(H)<1e-10


def test_finite_blocklength_rate_approaches_capacity():
    from commlab.information_theory import complex_awgn_capacity,normal_approximation_rate
    s=10.0; c=float(complex_awgn_capacity(s)); r100=float(normal_approximation_rate(s,100,1e-3)); r10000=float(normal_approximation_rate(s,10000,1e-3))
    assert 0<r100<r10000<c and c-r10000 < c-r100
