import numpy as np


def simulate_straggler_resilience(n_tasks=12, redundancy=4, rounds=20000,
                                   compute_mean_ms=12.0, comm_mean_ms=3.0,
                                   straggler_probability=.12, straggler_factor=6.0,
                                   strategy='mds', seed=0):
    """Transparent latency abstraction for synchronous edge learning.

    ``uncoded`` waits for all K independent tasks. ``replication`` gives every
    task two copies and waits for the faster copy. ``mds`` launches K+r coded
    workers and models recovery after any K results. The MDS mode is a latency
    abstraction, not an implementation of a specific gradient code.
    """
    if n_tasks<2 or redundancy<0 or rounds<10: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed)
    def worker_time(shape):
        t=rng.exponential(compute_mean_ms,size=shape)+rng.exponential(comm_mean_ms,size=shape)
        s=rng.random(shape)<straggler_probability
        return t*np.where(s,straggler_factor,1.0)
    if strategy=='uncoded':
        T=worker_time((rounds,n_tasks)); lat=T.max(axis=1); load=1.0; workers=n_tasks
    elif strategy=='replication':
        T=worker_time((rounds,n_tasks,2)); lat=T.min(axis=2).max(axis=1); load=2.0; workers=2*n_tasks
    elif strategy=='mds':
        workers=n_tasks+redundancy
        T=np.sort(worker_time((rounds,workers)),axis=1)
        lat=T[:,n_tasks-1]; load=workers/n_tasks
    else: raise ValueError('unknown strategy')
    return {'strategy':strategy,'mean_latency_ms':float(lat.mean()),
            'p95_latency_ms':float(np.quantile(lat,.95)),
            'p99_latency_ms':float(np.quantile(lat,.99)),
            'compute_load_ratio':float(load),'launched_workers':int(workers)}
