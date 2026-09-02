import numpy as np


def _degree_sampler(degree_probs: dict[int, float], rng: np.random.Generator, n: int) -> np.ndarray:
    if not degree_probs:
        raise ValueError("degree_probs must be non-empty")
    deg=np.array(sorted(int(k) for k in degree_probs),dtype=int)
    p=np.array([degree_probs[int(k)] for k in deg],dtype=float)
    if np.any(deg<1) or np.any(p<0) or not np.isfinite(p).all() or p.sum()<=0:
        raise ValueError("invalid repetition distribution")
    p=p/p.sum()
    return rng.choice(deg,size=n,p=p)


def simulate_irsa(n_slots: int, offered_load: float, n_frames: int=500,
                  degree_probs: dict[int,float] | None=None,
                  iterative_sic: bool=True, seed: int=1) -> dict:
    """Frame-based repetition slotted ALOHA / IRSA baseline.

    A Poisson number of users become active in each frame. Each active user
    repeats one packet in ``d`` distinct slots, where ``d`` follows
    ``degree_probs``. With iterative SIC, singleton slots decode a packet and
    all of its replicas are removed, possibly exposing new singletons.

    The model is graph-based: PHY capture, activity detection errors, channel
    estimation, and residual SIC are intentionally excluded.
    """
    if n_slots<2 or n_frames<1 or offered_load<0:
        raise ValueError("invalid IRSA setup")
    if degree_probs is None:
        degree_probs={2:0.50,3:0.28,8:0.22}
    if max(degree_probs)>n_slots:
        raise ValueError("repetition degree cannot exceed number of slots")
    rng=np.random.default_rng(seed)
    total_users=decoded_total=replicas_total=0
    iter_hist=[]; frame_throughput=[]
    for _ in range(int(n_frames)):
        n_users=int(rng.poisson(offered_load*n_slots))
        total_users+=n_users
        if n_users==0:
            iter_hist.append(0); frame_throughput.append(0.0); continue
        deg=_degree_sampler(degree_probs,rng,n_users)
        user_slots=[]
        slot_users=[set() for _ in range(n_slots)]
        for u,d in enumerate(deg):
            ss=rng.choice(n_slots,size=int(d),replace=False)
            user_slots.append(ss)
            replicas_total+=len(ss)
            for s in ss: slot_users[int(s)].add(u)
        if not iterative_sic:
            singleton_users=set()
            for us in slot_users:
                if len(us)==1: singleton_users.update(us)
            decoded=len(singleton_users); iterations=1 if decoded else 0
        else:
            unresolved=np.ones(n_users,dtype=bool)
            decoded=0; iterations=0
            while True:
                singletons=[]
                for us in slot_users:
                    live=[u for u in us if unresolved[u]]
                    if len(live)==1: singletons.append(live[0])
                if not singletons: break
                newly=np.unique(singletons)
                newly=newly[unresolved[newly]]
                if len(newly)==0: break
                iterations+=1
                for u in newly:
                    unresolved[u]=False; decoded+=1
                    for s in user_slots[int(u)]:
                        slot_users[int(s)].discard(int(u))
                if iterations>n_users:  # defensive guard
                    raise RuntimeError("IRSA SIC did not converge")
        decoded_total+=decoded
        iter_hist.append(iterations)
        frame_throughput.append(decoded/n_slots)
    return {
        "offered_load":float(offered_load),
        "throughput_packets_per_slot":float(decoded_total/max(n_frames*n_slots,1)),
        "packet_loss_rate":float(1-decoded_total/max(total_users,1)),
        "success_probability":float(decoded_total/max(total_users,1)),
        "mean_sic_iterations":float(np.mean(iter_hist)),
        "mean_replicas_per_user":float(replicas_total/max(total_users,1)),
        "replicas_per_decoded_packet":float(replicas_total/max(decoded_total,1)),
        "total_users":int(total_users),
        "decoded_packets":int(decoded_total),
        "frame_throughput":np.asarray(frame_throughput,float),
    }
