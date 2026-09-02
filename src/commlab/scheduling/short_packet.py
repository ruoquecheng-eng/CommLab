from collections import deque
import numpy as np
from commlab.information_theory.finite_blocklength import normal_approximation_error_probability
from commlab.link.link_adaptation import select_mcs, OuterLoopLinkAdaptation


def simulate_short_packet_cross_layer(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray, arrivals: np.ndarray,
                                      thresholds_db, efficiencies, blocklength: int = 200,
                                      payload_bits: int = 256, target_bler: float = 1e-3,
                                      fbl_aware: bool = True, use_olla: bool = True,
                                      max_attempts: int = 3, seed: int = 1) -> dict:
    """Small event-driven short-packet scheduler with FBL BLER abstraction.

    One user is served per slot with PF-like metric. Retransmissions Chase-combine
    linear SNR. ``fbl_aware`` backs off MCS choices whose normal-approximation
    BLER at the estimated SNR exceeds the target.
    """
    T=np.asarray(true_snr_db,float); E=np.asarray(estimated_snr_db,float); A=np.asarray(arrivals,int)
    if T.ndim!=2 or E.shape!=T.shape or A.shape!=T.shape or blocklength<1 or payload_bits<1: raise ValueError('invalid arrays/config')
    S,U=T.shape; rng=np.random.default_rng(seed); qs=[deque() for _ in range(U)]
    olla=[OuterLoopLinkAdaptation(target_bler=target_bler,nack_step_db=.18) for _ in range(U)]
    avg=np.ones(U,float); delivered=np.zeros(U,float); delays=[]; tx=0; nacks=0; drops=0; selected=[]
    th=np.asarray(thresholds_db,float); eff=np.asarray(efficiencies,float)
    for t in range(S):
        for u in range(U):
            for _ in range(int(A[t,u])): qs[u].append({'arrival':t,'attempts':0,'snr_lin':0.0,'mcs':None})
        active=[u for u in range(U) if qs[u]]
        if not active: continue
        metric=[]
        choices=[]
        for u in active:
            es=olla[u].effective_snr_db(E[t,u]) if use_olla else E[t,u]
            idx,_=select_mcs(es,th,eff)
            if fbl_aware:
                snr_lin=10**(es/10)
                while idx>0 and float(normal_approximation_error_probability(snr_lin,blocklength,eff[idx]))>target_bler:
                    idx-=1
            choices.append(idx); metric.append(eff[idx]/max(avg[u],1e-9))
        ii=int(np.argmax(metric)); u=active[ii]; idx=choices[ii]; pkt=qs[u][0]
        if pkt['mcs'] is None: pkt['mcs']=idx
        idx=int(pkt['mcs']); pkt['attempts']+=1; tx+=1
        pkt['snr_lin']+=10**(T[t,u]/10)
        pe=float(normal_approximation_error_probability(pkt['snr_lin'],blocklength,eff[idx]))
        ack=bool(rng.random()>=pe)
        if use_olla: olla[u].update(ack)
        selected.append(idx)
        if ack:
            qs[u].popleft(); delivered[u]+=payload_bits; delays.append(t-pkt['arrival']+1); avg[u]=.98*avg[u]+.02*eff[idx]
        else:
            nacks+=1; avg[u]*=.98
            if pkt['attempts']>=max_attempts: qs[u].popleft(); drops+=1
    d=np.asarray(delays,float)
    return {'goodput_bits_per_slot':float(delivered.sum()/S),'nack_rate':float(nacks/max(tx,1)),
            'drops':int(drops),'completed_packets':int(len(delays)),
            'mean_delay_slots':float(np.mean(d)) if len(d) else np.nan,
            'p95_delay_slots':float(np.percentile(d,95)) if len(d) else np.nan,
            'mean_mcs_index':float(np.mean(selected)) if selected else np.nan}


def simulate_short_packet_goodput_trace(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray,
                                        thresholds_db, efficiencies, blocklength: int = 200,
                                        target_bler: float = 1e-2, fbl_aware: bool = True,
                                        use_olla: bool = False, seed: int = 1) -> dict:
    """Adaptive short-packet goodput over a scalar SNR trace.

    A successful block delivers ``blocklength * spectral_efficiency`` information
    bits; failed blocks deliver zero. This makes conservative MCS selection pay an
    explicit rate cost instead of receiving free reliability.
    """
    t=np.asarray(true_snr_db,float).reshape(-1); e=np.asarray(estimated_snr_db,float).reshape(-1)
    if len(t)!=len(e) or len(t)==0 or blocklength<1 or not (0<target_bler<.5): raise ValueError('invalid trace/config')
    th=np.asarray(thresholds_db,float); eff=np.asarray(efficiencies,float); rng=np.random.default_rng(seed)
    olla=OuterLoopLinkAdaptation(target_bler=target_bler,nack_step_db=.18)
    delivered=0.0; nacks=0; idxs=[]; pes=[]
    for td,ed in zip(t,e):
        es=olla.effective_snr_db(ed) if use_olla else float(ed)
        idx,_=select_mcs(es,th,eff)
        if fbl_aware:
            sl=10**(es/10)
            while idx>0 and float(normal_approximation_error_probability(sl,blocklength,eff[idx]))>target_bler:
                idx-=1
        pe=float(normal_approximation_error_probability(10**(td/10),blocklength,eff[idx]))
        ack=bool(rng.random()>=pe)
        if ack: delivered+=blocklength*eff[idx]
        else: nacks+=1
        if use_olla: olla.update(ack)
        idxs.append(idx); pes.append(pe)
    return {'goodput_bits_per_use':float(delivered/(len(t)*blocklength)),
            'nack_rate':float(nacks/len(t)),'mean_mcs_index':float(np.mean(idxs)),
            'mean_predicted_true_bler':float(np.mean(pes)),'final_olla_offset_db':float(olla.offset_db)}
