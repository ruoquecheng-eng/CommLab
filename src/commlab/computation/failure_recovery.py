import numpy as np


def simulate_edge_failure_recovery(n_tasks=7000,policy='checkpoint',failure_probability=.08,seed=0):
    """Long-running edge task recovery via restart, checkpoint migration, or replication."""
    if policy not in {'restart','checkpoint','replicate'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3103); lats=[]; traffic=[]; failures=0; deadline=160.
    miss=0; compute=0.; base_work=0.
    for _ in range(n_tasks):
        work=float(rng.lognormal(np.log(75),.35))
        base_work += work
        fail=rng.random()<failure_probability
        if policy=='restart':
            lat=work; tr=0.; comp=work
            if fail:
                failures+=1; frac=rng.uniform(.15,.95); lat += frac*work + 18 + work; comp += frac*work+work
        elif policy=='checkpoint':
            ckpt_int=25.; overhead=2.2*np.ceil(work/ckpt_int); lat=work+overhead; tr=.7*np.ceil(work/ckpt_int); comp=work
            if fail:
                failures+=1; lost=rng.uniform(0,ckpt_int); lat += lost+16+min(ckpt_int,work); tr += 4.0; comp += lost+min(ckpt_int,work)
        else:
            # Two replicas: higher compute/network cost, low recovery latency.
            lat=.92*work+4.; tr=3.5; comp=2*work
            f1=rng.random()<failure_probability; f2=rng.random()<failure_probability
            if f1 or f2: failures+=1
            if f1 and f2: lat += 22+work; comp += work
        lats.append(lat); traffic.append(tr); compute+=comp; miss+=int(lat>deadline)
    a=np.asarray(lats)
    return {'policy':policy,'mean_latency_ms':float(a.mean()),'p95_latency_ms':float(np.quantile(a,.95)),
            'deadline_miss_rate':float(miss/n_tasks),'recovery_event_rate':float(failures/n_tasks),
            'recovery_traffic_mb_per_task':float(np.mean(traffic)),'compute_load_ratio':float(compute/max(base_work,1e-12))}
