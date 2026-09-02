from collections import deque
import numpy as np


def simulate_embb_urllc_slicing(n_minislots: int=5000, n_prbs: int=24,
                                urllc_arrival_rate: float=0.8,
                                urllc_prbs_per_packet: int=3,
                                urllc_deadline: int=2,
                                urllc_success_probability: float=0.995,
                                policy: str="preemptive",
                                fixed_reserved_prbs: int=6,
                                ewma_beta: float=0.92,
                                reserve_safety: float=1.25,
                                seed: int=1) -> dict:
    """Abstract eMBB/URLLC coexistence with mini-slot preemption/reservation.

    ``preemptive`` lets eMBB use all PRBs until queued URLLC packets puncture
    resources. ``reserved`` permanently withholds a fixed number of PRBs for
    URLLC. ``adaptive_reserve`` predicts near-term arrival load via an EWMA and
    reserves enough PRBs with a safety factor. Packets are served EDF and must
    finish before ``urllc_deadline`` mini-slots.

    This is a system-level resource abstraction, not a 3GPP scheduler.
    """
    if n_minislots<1 or n_prbs<1 or urllc_arrival_rate<0 or urllc_prbs_per_packet<1:
        raise ValueError("invalid slicing setup")
    if urllc_deadline<1 or not (0<=urllc_success_probability<=1):
        raise ValueError("invalid URLLC setting")
    if policy not in {"preemptive","reserved","adaptive_reserve"}:
        raise ValueError("invalid slicing policy")
    rng=np.random.default_rng(seed)
    q=deque(); arrivals=success=miss=attempts=0
    embb_payload=0.0; used_urllc_prbs=reserved_total=wasted_reserved=0
    ewma=float(urllc_arrival_rate)
    delay_success=[]; qhist=[]; reserve_hist=[]
    for t in range(int(n_minislots)):
        n_arr=int(rng.poisson(urllc_arrival_rate)); arrivals+=n_arr
        for _ in range(n_arr): q.append({"arrival":t,"deadline":t+urllc_deadline-1})
        # Expire before service if the absolute deadline has passed.
        while q and q[0]["deadline"]<t:
            q.popleft(); miss+=1
        if policy=="reserved":
            reserve=int(np.clip(fixed_reserved_prbs,0,n_prbs))
        elif policy=="adaptive_reserve":
            reserve=int(np.clip(np.ceil(reserve_safety*ewma*urllc_prbs_per_packet),0,n_prbs))
        else:
            reserve=n_prbs  # capacity available to preemption, not permanently withheld
        cap_packets=reserve//urllc_prbs_per_packet
        served_this=0
        for _ in range(min(cap_packets,len(q))):
            pkt=q.popleft(); attempts+=1; served_this+=1
            used_urllc_prbs+=urllc_prbs_per_packet
            if rng.random()<urllc_success_probability:
                success+=1; delay_success.append(t-pkt["arrival"]+1)
            elif pkt["deadline"]>t:
                q.appendleft(pkt)  # one immediate future retry under EDF
            else:
                miss+=1
        if policy=="preemptive":
            unavailable=served_this*urllc_prbs_per_packet
        else:
            unavailable=reserve; reserved_total+=reserve
            wasted_reserved+=max(reserve-served_this*urllc_prbs_per_packet,0)
        # eMBB spectral efficiency changes slowly/fades but is always backlogged.
        se=max(0.1,float(rng.normal(3.0,0.45)))
        embb_payload+=(n_prbs-unavailable)*se
        ewma=ewma_beta*ewma+(1-ewma_beta)*n_arr
        reserve_hist.append(unavailable if policy=="preemptive" else reserve)
        qhist.append(len(q))
    miss+=len(q)
    return {
        "embb_throughput_bits_per_minislot":float(embb_payload/n_minislots),
        "urllc_success_probability":float(success/max(arrivals,1)),
        "urllc_deadline_miss_rate":float(miss/max(arrivals,1)),
        "urllc_attempts":int(attempts),
        "mean_urllc_delay":float(np.mean(delay_success)) if delay_success else np.nan,
        "p95_urllc_delay":float(np.quantile(delay_success,.95)) if delay_success else np.nan,
        "mean_urllc_prb_fraction":float(used_urllc_prbs/max(n_minislots*n_prbs,1)),
        "reserved_prb_fraction":float(reserved_total/max(n_minislots*n_prbs,1)),
        "wasted_reserved_fraction":float(wasted_reserved/max(reserved_total,1)),
        "mean_queue":float(np.mean(qhist)),
        "mean_reserved_or_preempted_prbs":float(np.mean(reserve_hist)),
        "arrivals":int(arrivals),"successes":int(success),"misses":int(miss),
    }
