import numpy as np


def simulate_capture_irsa(offered_load=.7, frame_slots=200, n_frames=300,
                          power_spread_db=6.0, sinr_threshold_db=3.0,
                          noise_power=.03, repetition_distribution=((2,.5),(3,.28),(8,.22)),
                          seed=0):
    """IRSA with power-domain capture and iterative SIC.

    Perfect replica pointers and perfect cancellation are assumed after a packet
    is decoded. A collision can be decoded if its strongest unresolved packet
    exceeds ``sinr_threshold_db``. Setting zero power spread recovers a regime
    close to singleton-only IRSA for positive capture thresholds.
    """
    if offered_load<0 or frame_slots<4 or n_frames<1: raise ValueError('bad setup')
    rng=np.random.default_rng(seed); th=10**(sinr_threshold_db/10)
    deg=np.array([d for d,_ in repetition_distribution],int)
    prob=np.array([p for _,p in repetition_distribution],float); prob/=prob.sum()
    total_arr=0; total_dec=0; iter_counts=[]
    for _ in range(n_frames):
        K=rng.poisson(offered_load*frame_slots); total_arr+=K
        reps=[]; powers=[]; slots=[set() for _ in range(frame_slots)]
        for k in range(K):
            d=min(int(rng.choice(deg,p=prob)),frame_slots)
            ss=rng.choice(frame_slots,size=d,replace=False); reps.append(ss)
            # Log-normal received-power spread around unit median.
            p=10**(rng.normal(0,power_spread_db/6)/10); powers.append(p)
            for s in ss: slots[int(s)].add(k)
        unresolved=set(range(K)); decoded=set(); it=0
        while True:
            it+=1; newly=set()
            for members in slots:
                cand=[k for k in members if k in unresolved]
                if not cand: continue
                if len(cand)==1: newly.add(cand[0]); continue
                ps=np.array([powers[k] for k in cand]); j=int(np.argmax(ps))
                sinr=ps[j]/(noise_power+ps.sum()-ps[j])
                if sinr>=th: newly.add(cand[j])
            if not newly: break
            for k in newly:
                unresolved.discard(k); decoded.add(k)
            if it>K+2: break
        total_dec+=len(decoded); iter_counts.append(it)
    return {'throughput':float(total_dec/(n_frames*frame_slots)),
            'packet_loss_rate':float(1-total_dec/max(total_arr,1)),
            'mean_sic_iterations':float(np.mean(iter_counts)),
            'offered_load':float(offered_load),'power_spread_db':float(power_spread_db)}
