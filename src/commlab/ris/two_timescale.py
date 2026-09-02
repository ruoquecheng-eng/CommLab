import numpy as np

from commlab.ris.cellfree import coordinate_optimize_cellfree_ris, effective_cellfree_ris_channel
from commlab.ris.robust import sample_average_optimize_cellfree_ris
from commlab.mimo.cell_free import clustered_mrt_precoder, per_user_rates


def apply_ris_phase_noise(phases: np.ndarray, std_deg: float, rng: np.random.Generator) -> np.ndarray:
    th=np.asarray(phases,float).reshape(-1)
    if std_deg<0: raise ValueError('phase-noise std must be nonnegative')
    return np.angle(np.exp(1j*(th+rng.normal(0,np.deg2rad(std_deg),len(th)))))


def simulate_two_timescale_cellfree_ris(channel_sequence, snr_linear: float,
                                         bits: int=2, ris_update_interval: int=8,
                                         history_window: int=8, phase_noise_std_deg: float=0.0,
                                         mask: np.ndarray | None=None, seed: int=1) -> dict:
    """Compare fast, stale and two-timescale RIS control over a channel trace.

    AP precoding is recomputed from the *current effective channel* each slot;
    only RIS control is slow.  The two-timescale RIS is updated every
    ``ris_update_interval`` slots by sample-average coordinate ascent over past
    channel snapshots.  This isolates passive-control overhead from AP CSI.
    """
    seq=list(channel_sequence)
    if len(seq)<2 or snr_linear<=0 or bits<1 or ris_update_interval<1 or history_window<1:
        raise ValueError('invalid two-timescale RIS setup')
    N=np.asarray(seq[0][1]).shape[0]; rng=np.random.default_rng(seed)
    for D,G,R in seq:
        if np.asarray(G).shape[0]!=N: raise ValueError('inconsistent RIS size')
    fast_rates=[]; slow_rates=[]; stale_rates=[]; random_rates=[]
    # Fixed stale design from first snapshot.
    stale,_=coordinate_optimize_cellfree_ris(*seq[0],snr_linear,bits=bits,iterations=1,mask=mask)
    slow=stale.copy(); rrng=np.random.default_rng(seed+99); random_phase=rrng.uniform(-np.pi,np.pi,N)
    slow_updates=0
    def eval_rate(ch,th):
        D,G,R=ch; applied=apply_ris_phase_noise(th,phase_noise_std_deg,rng)
        H=effective_cellfree_ris_channel(D,G,R,applied); W=clustered_mrt_precoder(H,mask)
        return per_user_rates(H,W,snr_linear)
    for t,ch in enumerate(seq):
        fast,_=coordinate_optimize_cellfree_ris(*ch,snr_linear,bits=bits,iterations=1,mask=mask)
        if t%ris_update_interval==0:
            lo=max(0,t-history_window+1); samples=seq[lo:t+1]
            slow,_=sample_average_optimize_cellfree_ris(samples,snr_linear,bits=bits,iterations=1,mask=mask,
                                                        initial_phases=slow)
            slow_updates+=1
        fast_rates.append(eval_rate(ch,fast)); slow_rates.append(eval_rate(ch,slow))
        stale_rates.append(eval_rate(ch,stale)); random_rates.append(eval_rate(ch,random_phase))
    def pack(x):
        a=np.asarray(x); return {'rates':a,'mean_sum_rate':float(a.sum(axis=1).mean()),
                                 'edge_rate':float(np.quantile(a,.05))}
    return {
        'fast':pack(fast_rates),'two_timescale':pack(slow_rates),'stale':pack(stale_rates),'random':pack(random_rates),
        'slow_updates':int(slow_updates),
        'ris_control_bits_per_slot_fast':float(N*bits),
        'ris_control_bits_per_slot_two_timescale':float(N*bits*slow_updates/len(seq)),
    }
