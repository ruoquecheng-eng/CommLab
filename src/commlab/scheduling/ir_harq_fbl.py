from collections import deque
from statistics import NormalDist
import numpy as np

from commlab.information_theory.finite_blocklength import complex_awgn_capacity, complex_awgn_dispersion
from commlab.link.link_adaptation import OuterLoopLinkAdaptation, select_mcs


def block_fading_ir_error_probability(snr_linear, uses, information_bits: float,
                                      third_order: bool=True) -> float:
    """Normal-approximation error probability for accumulated IR observations.

    Independent redundancy blocks can experience different SNRs.  The mean
    information density and dispersion are accumulated across blocks.  This is
    an asymptotic finite-blocklength abstraction, not a code-specific IR decoder.
    """
    s=np.asarray(snr_linear,float).reshape(-1); n=np.asarray(uses,float).reshape(-1)
    if len(s)==0 or len(s)!=len(n) or np.any(s<0) or np.any(n<=0) or information_bits<0:
        raise ValueError('invalid IR-HARQ inputs')
    mean=float(np.sum(n*complex_awgn_capacity(s)))
    var=float(np.sum(n*complex_awgn_dispersion(s)))
    nt=float(n.sum())
    if third_order: mean+=0.5*np.log2(max(nt,1.0))
    z=(mean-float(information_bits))/np.sqrt(max(var,1e-15))
    return float(np.clip(1.0-NormalDist().cdf(z),0.0,1.0))


def simulate_fbl_ir_harq_queue(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray,
                                arrivals: np.ndarray, thresholds_db, efficiencies,
                                round_blocklength: int=80, target_bler: float=1e-2,
                                mode: str='ir', max_rounds: int=4, use_olla: bool=True,
                                policy: str='pf', seed: int=1) -> dict:
    """Short-packet queue comparing IR-HARQ with Chase combining.

    A packet selects its information payload from the first-round MCS. Every
    retransmission consumes another ``round_blocklength`` channel uses.
    * ``ir`` accumulates new redundancy, increasing total code length.
    * ``chase`` repeats the same codeword and combines SNR at fixed code length.
    """
    T=np.asarray(true_snr_db,float); E=np.asarray(estimated_snr_db,float); A=np.asarray(arrivals,int)
    th=np.asarray(thresholds_db,float); eff=np.asarray(efficiencies,float)
    if T.ndim!=2 or E.shape!=T.shape or A.shape!=T.shape or np.any(A<0): raise ValueError('invalid traces')
    if mode not in {'ir','chase'} or policy not in {'pf','max_rate'} or round_blocklength<1 or max_rounds<1:
        raise ValueError('invalid HARQ setup')
    if len(th)!=len(eff) or np.any(eff<=0): raise ValueError('invalid MCS table')
    S,U=T.shape; rng=np.random.default_rng(seed); qs=[deque() for _ in range(U)]
    olla=[OuterLoopLinkAdaptation(target_bler=target_bler,nack_step_db=.18) for _ in range(U)]
    avg=np.ones(U); delivered=0.0; delays=[]; drops=0; attempts=0; nacks=0; used=0
    rounds_hist=[]; backlog=np.zeros((S,U),int)
    for t in range(S):
        for u in range(U):
            for _ in range(int(A[t,u])):
                qs[u].append({'arrival':t,'mcs':None,'eff':None,'bits':None,'snrs':[],'rounds':0})
        active=[u for u in range(U) if qs[u]]
        if active:
            scores=[]; picks=[]
            for u in active:
                es=olla[u].effective_snr_db(E[t,u]) if use_olla else float(E[t,u])
                idx,e=select_mcs(es,th,eff)
                score=float(e)/(max(avg[u],1e-9) if policy=='pf' else 1.0)
                scores.append(score); picks.append(int(idx))
            j=int(np.argmax(scores)); u=active[j]; p=qs[u][0]
            if p['mcs'] is None:
                p['mcs']=picks[j]; p['eff']=float(eff[picks[j]])
                p['bits']=float(round_blocklength*p['eff'])
            p['rounds']+=1; attempts+=1; used+=round_blocklength
            p['snrs'].append(10**(T[t,u]/10))
            if mode=='ir':
                pe=block_fading_ir_error_probability(p['snrs'],np.full(len(p['snrs']),round_blocklength),p['bits'])
            else:
                comb=float(np.sum(p['snrs']))
                pe=block_fading_ir_error_probability([comb],[round_blocklength],p['bits'])
            ack=bool(rng.random()>=pe)
            if use_olla: olla[u].update(ack)
            rounds_hist.append((t,u,p['rounds'],pe,ack))
            if ack:
                qs[u].popleft(); delivered+=p['bits']; delays.append(t-p['arrival']+1)
                avg[u]=.98*avg[u]+.02*p['eff']
            else:
                nacks+=1; avg[u]*=.98
                if p['rounds']>=max_rounds:
                    qs[u].popleft(); drops+=1
        backlog[t]=[len(q) for q in qs]
    d=np.asarray(delays,float)
    return {
        'goodput_bits_per_channel_use':float(delivered/max(used,1)),
        'delivered_bits':float(delivered), 'channel_uses':int(used),
        'nack_rate':float(nacks/max(attempts,1)), 'drops':int(drops),
        'completed_packets':int(len(d)), 'pending_packets':int(sum(len(q) for q in qs)),
        'mean_delay_slots':float(np.mean(d)) if len(d) else np.nan,
        'p95_delay_slots':float(np.percentile(d,95)) if len(d) else np.nan,
        'mean_rounds_per_completed':float(attempts/max(len(d),1)),
        'backlog_packets':backlog, 'round_history':rounds_hist,
        'final_olla_offset_db':np.asarray([x.offset_db for x in olla]),
    }
