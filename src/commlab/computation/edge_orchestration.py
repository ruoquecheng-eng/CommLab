import numpy as np


def simulate_failure_aware_edge_orchestration(n_tasks=5000,n_nodes=5,policy='risk_aware',load=1.0,seed=0):
    """Queue-, energy-, and reliability-aware edge task placement.

    Tasks arrive sequentially. Edge nodes have heterogeneous radio delay, service
    speed, energy cost, and state-dependent failure probability. ``risk_aware``
    adds a tail/recovery penalty to the expected-latency objective. All metrics are
    abstract system proxies rather than measurements from a specific edge platform.
    """
    if policy not in {'latency_only','trust_aware','risk_aware'}: raise ValueError('unknown policy')
    if n_nodes<2: raise ValueError('need multiple nodes')
    rng=np.random.default_rng(seed+3003)
    service=np.linspace(1.45,.75,n_nodes)  # work units/request step
    radio=np.linspace(7,22,n_nodes)+rng.uniform(-2,2,n_nodes)
    energy=np.linspace(1.35,.65,n_nodes)
    # Low-radio-latency nodes are deliberately less reliable, creating a real
    # latency-versus-trust conflict rather than a dominated choice.
    base_fail=np.linspace(.105,.015,n_nodes)
    queue=np.zeros(n_nodes); trust=np.full(n_nodes,.96)
    lats=[]; failures=deadlines=0; e_sum=0.; sel=np.zeros(n_nodes,int)
    deadline_ms=105.
    for t in range(n_tasks):
        queue=np.maximum(0,queue-service)
        # Bursty background load and slowly varying reliability.
        queue+=rng.exponential(.10*load,n_nodes)
        task=float(rng.lognormal(mean=-.05,sigma=.38)*load)
        hot=np.clip(queue/5,0,1)
        fail=np.clip(base_fail+.11*hot+.045*(1-trust),.005,.32)
        pred=radio+9*(queue+task)/service
        if policy=='latency_only': score=pred
        elif policy=='trust_aware': score=pred+55*fail+6*energy
        else:
            recovery=95+35*hot
            # Approximate p95/CVaR penalty of rare node failure and queue burst.
            score=pred+38*fail+6*energy+1.15*fail*recovery+4.5*np.sqrt(queue+1)
        i=int(np.argmin(score)); sel[i]+=1
        queue[i]+=task
        failed=rng.random()<fail[i]
        lat=float(pred[i]+(95+35*hot[i] if failed else 0)+rng.exponential(2.0))
        failures+=int(failed); deadlines+=int(lat>deadline_ms); lats.append(lat); e_sum+=energy[i]*task
        # Observed outcome updates a simple reliability score.
        trust[i]=.985*trust[i]+.015*(0.0 if failed else 1.0)
    a=np.asarray(lats)
    return {'policy':policy,'mean_latency_ms':float(a.mean()),'p95_latency_ms':float(np.quantile(a,.95)),
            'failure_rate':float(failures/n_tasks),'deadline_miss_rate':float(deadlines/n_tasks),
            'energy_proxy_per_task':float(e_sum/n_tasks),
            'selection_jain':float(sel.sum()**2/(n_nodes*np.sum(sel.astype(float)**2)+1e-12)),
            'mean_final_trust':float(trust.mean())}
