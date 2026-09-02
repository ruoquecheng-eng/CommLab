from collections import deque
import numpy as np

from commlab.sensing.resource_scheduling import posterior_angle_std
from commlab.sensing.beam_tracking import expected_ula_rate_under_angle_uncertainty


def simulate_queue_aware_isac_control(process_std_deg: np.ndarray, arrivals_bits: np.ndarray,
                                      ideal_user_rate_bits: np.ndarray, initial_std_deg: float,
                                      candidate_elements, sensing_fractions,
                                      snr_per_element_linear: float,
                                      sensing_value_weight: float=800.0,
                                      reference_std_deg: float=2.5,
                                      queue_aware: bool=True) -> dict:
    """Joint communication-queue / sensing-overhead controller.

    Each slot chooses sensing fraction, aperture, and one user to serve. Utility
    combines queue-weighted expected service with information gain
    ``log(prior/posterior)``.  Under congestion the queue term suppresses sensing;
    when tracking uncertainty grows the information-value term encourages it.
    This is a transparent myopic cross-layer baseline, not an optimal scheduler.
    """
    qproc=np.asarray(process_std_deg,float).reshape(-1); A=np.asarray(arrivals_bits,float); R=np.asarray(ideal_user_rate_bits,float)
    if A.ndim!=2 or R.shape!=A.shape or len(qproc)!=A.shape[0] or np.any(A<0) or np.any(R<0) or initial_std_deg<=0:
        raise ValueError('invalid ISAC queue traces')
    S,U=A.shape; backlog=np.zeros(U,float); prior=float(initial_std_deg); rows=[]; delivered=np.zeros(U)
    maxN=max(int(x) for x in candidate_elements)
    # Near-perfect steering reference for normalizing array/uncertainty loss.
    ref=max(expected_ula_rate_under_angle_uncertainty(.05,maxN,snr_per_element_linear),1e-12)
    backlog_hist=np.zeros((S,U)); post_hist=np.zeros(S)
    for t in range(S):
        backlog+=A[t]
        prior=float(np.sqrt(prior**2+qproc[t]**2))
        best=None
        for f in sensing_fractions:
            post=posterior_angle_std(prior,float(f),reference_std_deg)
            info=np.log(max(prior/post,1.0))
            for n in candidate_elements:
                beam=expected_ula_rate_under_angle_uncertainty(post,int(n),snr_per_element_linear)/ref
                for u in range(U):
                    service=min(backlog[u],(1-f)*R[t,u]*beam)
                    qweight=(1.0+backlog[u]/max(np.mean(R[t])+1e-9,1e-9)) if queue_aware else 1.0
                    utility=qweight*service+float(sensing_value_weight)*info
                    cand=(utility,float(f),int(n),u,float(service),float(post),float(info),float(beam))
                    if best is None or cand[0]>best[0]: best=cand
        _,f,n,u,service,post,info,beam=best
        backlog[u]-=service; delivered[u]+=service; prior=post
        backlog_hist[t]=backlog; post_hist[t]=post
        rows.append({'slot':t,'sensing_fraction':f,'elements':n,'user':u,'service_bits':service,
                     'posterior_std_deg':post,'information_gain':info,'beam_factor':beam,
                     'total_backlog_bits':float(backlog.sum())})
    return {
        'rows':rows,'delivered_bits':delivered,'total_delivered_bits':float(delivered.sum()),
        'mean_sensing_fraction':float(np.mean([r['sensing_fraction'] for r in rows])),
        'mean_posterior_std_deg':float(post_hist.mean()),
        'final_backlog_bits':float(backlog.sum()),'mean_backlog_bits':float(backlog_hist.sum(axis=1).mean()),
        'backlog_bits':backlog_hist,'posterior_std_deg':post_hist,
    }


def simulate_predictive_queue_aware_isac_control(process_std_deg: np.ndarray, arrivals_bits: np.ndarray,
                                                 ideal_user_rate_bits: np.ndarray, initial_std_deg: float,
                                                 candidate_elements, sensing_fractions,
                                                 snr_per_element_linear: float,
                                                 sensing_value_weight: float=800.0,
                                                 reference_std_deg: float=2.5,
                                                 lookahead_weight: float=.75) -> dict:
    """Two-slot lookahead version of the queue-aware ISAC controller.

    The next-slot score uses predicted queue state and tracking covariance. This
    is still a small model-predictive baseline, but it avoids the strongest
    myopia of deciding current sensing only from current queue/service utility.
    """
    qproc=np.asarray(process_std_deg,float).reshape(-1); A=np.asarray(arrivals_bits,float); R=np.asarray(ideal_user_rate_bits,float)
    if A.ndim!=2 or R.shape!=A.shape or len(qproc)!=A.shape[0] or lookahead_weight<0:
        raise ValueError('invalid predictive ISAC traces')
    S,U=A.shape; backlog=np.zeros(U,float); prior=float(initial_std_deg); rows=[]; delivered=np.zeros(U)
    maxN=max(int(x) for x in candidate_elements); ref=max(expected_ula_rate_under_angle_uncertainty(.05,maxN,snr_per_element_linear),1e-12)
    backlog_hist=np.zeros((S,U)); post_hist=np.zeros(S)
    def actions(pr,bl,rate):
        out=[]
        for f in sensing_fractions:
            post=posterior_angle_std(pr,float(f),reference_std_deg); info=np.log(max(pr/post,1.0))
            for n in candidate_elements:
                beam=expected_ula_rate_under_angle_uncertainty(post,int(n),snr_per_element_linear)/ref
                for u in range(U):
                    service=min(bl[u],(1-f)*rate[u]*beam)
                    qweight=1.0+bl[u]/max(np.mean(rate)+1e-9,1e-9)
                    util=qweight*service+float(sensing_value_weight)*info
                    out.append((util,float(f),int(n),u,float(service),float(post),float(info),float(beam)))
        return out
    for t in range(S):
        backlog+=A[t]; prior=float(np.sqrt(prior**2+qproc[t]**2)); best=None
        for cur in actions(prior,backlog,R[t]):
            util,f,n,u,service,post,info,beam=cur; score=util
            if t+1<S:
                bl2=backlog.copy(); bl2[u]-=service; bl2+=A[t+1]
                pr2=float(np.sqrt(post**2+qproc[t+1]**2))
                nxt=max(x[0] for x in actions(pr2,bl2,R[t+1]))
                score+=float(lookahead_weight)*float(nxt)
            if best is None or score>best[0]: best=(score,cur)
        _,cur=best; _,f,n,u,service,post,info,beam=cur
        backlog[u]-=service; delivered[u]+=service; prior=post
        backlog_hist[t]=backlog; post_hist[t]=post
        rows.append({'slot':t,'sensing_fraction':f,'elements':n,'user':u,'service_bits':service,
                     'posterior_std_deg':post,'information_gain':info,'beam_factor':beam,
                     'total_backlog_bits':float(backlog.sum())})
    return {'rows':rows,'delivered_bits':delivered,'total_delivered_bits':float(delivered.sum()),
            'mean_sensing_fraction':float(np.mean([r['sensing_fraction'] for r in rows])),
            'mean_posterior_std_deg':float(post_hist.mean()),'final_backlog_bits':float(backlog.sum()),
            'mean_backlog_bits':float(backlog_hist.sum(axis=1).mean()),'backlog_bits':backlog_hist,
            'posterior_std_deg':post_hist}
