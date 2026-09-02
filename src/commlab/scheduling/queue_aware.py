from collections import deque
import numpy as np


def _hol_delay(queue, slot: int) -> int:
    return 0 if not queue else int(slot - queue[0][1] + 1)


def simulate_packet_scheduler(
    achievable_bits: np.ndarray,
    arrivals: np.ndarray,
    packet_size_bits: int = 12000,
    policy: str = "pf",
    beta: float = 0.98,
    delay_weight: float = 2.0,
    target_delay_slots: float = 20.0,
    max_delay_slots: int | None = None,
) -> dict:
    """Packet-queue OFDMA scheduler with RR, max-rate, PF or delay-aware PF.

    Parameters
    ----------
    achievable_bits : (slots, users, resources)
        Service capacity in bits if a resource is assigned to a user.
    arrivals : (slots, users)
        Integer number of fixed-size packets arriving at each slot.
    policy : {'round_robin','max_rate','pf','delay_pf'}
        ``delay_pf`` multiplies the PF metric by a normalized HOL-delay term.

    The model is intentionally MAC/link abstraction rather than a standards
    scheduler: one user gets each resource and packets are served FIFO.
    """
    C=np.asarray(achievable_bits,dtype=float); A=np.asarray(arrivals,dtype=int)
    if C.ndim!=3 or A.shape!=C.shape[:2] or np.any(C<0) or np.any(A<0):
        raise ValueError("invalid capacity/arrival arrays")
    if packet_size_bits<1 or not (0<beta<1) or target_delay_slots<=0:
        raise ValueError("invalid scheduler parameters")
    if policy not in {"round_robin","max_rate","pf","delay_pf"}:
        raise ValueError("unknown policy")
    S,U,R=C.shape; queues=[deque() for _ in range(U)]
    avg=np.ones(U,dtype=float); delivered=np.zeros(U,float); alloc=np.full((S,R),-1,int)
    delays=[]; dropped=0; rr=0; backlog=np.zeros((S,U),float)
    for t in range(S):
        for u in range(U):
            for _ in range(int(A[t,u])): queues[u].append([float(packet_size_bits),t])
        if max_delay_slots is not None:
            for q in queues:
                while q and t-q[0][1]>=int(max_delay_slots): q.popleft(); dropped+=1
        served_slot=np.zeros(U,float)
        for r in range(R):
            active=np.array([len(q)>0 for q in queues],bool)
            if not np.any(active): continue
            if policy=="round_robin":
                chosen=None
                for _ in range(U):
                    u=rr%U; rr+=1
                    if active[u]: chosen=u; break
            else:
                metric=np.full(U,-np.inf,float)
                if policy=="max_rate": metric[active]=C[t,active,r]
                else:
                    metric[active]=C[t,active,r]/np.maximum(avg[active],1e-9)
                    if policy=="delay_pf":
                        hol=np.array([_hol_delay(queues[u],t) for u in range(U)],float)
                        boost=1.0+float(delay_weight)*(hol/max(float(target_delay_slots),1e-9))
                        metric[active]*=boost[active]
                chosen=int(np.argmax(metric))
            if chosen is None: continue
            alloc[t,r]=chosen; cap=float(C[t,chosen,r]); served=0.0
            q=queues[chosen]
            while cap>1e-12 and q:
                amount=min(cap,q[0][0]); q[0][0]-=amount; cap-=amount; served+=amount
                if q[0][0]<=1e-9:
                    _,arr=q.popleft(); delays.append(t-int(arr)+1)
            served_slot[chosen]+=served; delivered[chosen]+=served
        avg=beta*avg+(1-beta)*served_slot
        backlog[t]=[sum(pkt[0] for pkt in q) for q in queues]
    pending=sum(len(q) for q in queues)
    delay_arr=np.asarray(delays,dtype=float)
    return {
        "allocations":alloc,
        "delivered_bits":delivered,
        "total_delivered_bits":float(delivered.sum()),
        "packet_delays":delay_arr,
        "mean_delay_slots":float(np.mean(delay_arr)) if len(delay_arr) else float('nan'),
        "p95_delay_slots":float(np.percentile(delay_arr,95)) if len(delay_arr) else float('nan'),
        "completed_packets":int(len(delays)),
        "dropped_packets":int(dropped),
        "pending_packets":int(pending),
        "backlog_bits":backlog,
        "final_average_service":avg,
    }
