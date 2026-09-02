import numpy as np


def simulate_mixed_control_inference(slots=5000, policy='task_value', mean_snr_db=0.0,
                                     inference_arrival=.45, seed=0):
    """One wireless resource shared by control updates and edge-inference packets.

    The scheduler chooses either a plant-state update or one inference request in
    each slot. The task-value policy compares expected reduction in physical
    control error against deadline-weighted inference utility. This deliberately
    exposes cross-service competition; it is not a 3GPP slicing implementation.
    """
    if policy not in {'control_first','inference_first','age_first','task_value'}:
        raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3202)
    n=3; a=np.array([1.055,1.075,1.095]); k=np.array([.42,.46,.50]); q=np.array([.8,1.2,2.0])
    bounds=np.array([4.5,3.2,2.2]); x=rng.normal(0,.45,n); xh=x.copy(); age=np.zeros(n,int)
    snr0=mean_snr_db+np.array([-1.5,0,1.5]); queue=[]
    c_cost=[]; violations=0; inf_total=inf_done=inf_miss=0; inf_utility=0.; served_control=0
    for t in range(slots):
        # Heterogeneous inference jobs with deadlines and values.
        if rng.random()<inference_arrival:
            inf_total+=1
            queue.append({'deadline':t+int(rng.integers(3,9)),
                          'value':float(rng.uniform(.5,2.2)),
                          'snr':float(mean_snr_db+rng.normal(1.0,2.0))})
        # Expire old jobs before scheduling.
        alive=[]
        for job in queue:
            if t>job['deadline']:
                inf_miss+=1
            else: alive.append(job)
        queue=alive
        err=np.abs(x-xh); snr=snr0+1.5*np.sin(2*np.pi*t/83+np.arange(n))+rng.normal(0,.8,n)
        p_ctrl=1-np.exp(-10**(snr/10)/2.6)
        # Best control candidate and its approximate value of information.
        ci=int(np.argmax(q*err**2*(1+.8*np.clip(np.abs(x)/bounds,0,2))*p_ctrl + .01*age))
        cval=float(q[ci]*err[ci]**2*(1+2*np.clip(np.abs(x[ci])/bounds[ci]-.55,0,1))*p_ctrl[ci])
        if queue:
            # Earliest deadline among jobs of similar value; compute expected delivered utility.
            scores=[]
            for j,job in enumerate(queue):
                gp=10**(job['snr']/10); ps=1-np.exp(-gp/2.3)
                slack=max(1,job['deadline']-t+1)
                scores.append(job['value']*ps*(1+1.4/slack))
            ji=int(np.argmax(scores)); ival=float(scores[ji])
        else: ji=-1; ival=-1
        choose_control=True
        if policy=='inference_first': choose_control=not queue
        elif policy=='control_first': choose_control=True
        elif policy=='age_first': choose_control=(age[ci]>=4 or not queue)
        elif policy=='task_value': choose_control=(cval>=ival or not queue)
        if choose_control:
            served_control+=1
            if rng.random()<p_ctrl[ci]: xh[ci]=x[ci]; age[ci]=0
        elif ji>=0:
            job=queue.pop(ji); gp=10**(job['snr']/10); ps=1-np.exp(-gp/2.3)
            if rng.random()<ps:
                inf_done+=1; inf_utility+=job['value']
            else:
                # Failed packet remains if deadline permits.
                queue.append(job)
        u=-k*xh; c_cost.append(float(np.mean(q*x*x+.04*u*u)))
        violations+=int(np.any(np.abs(x)>bounds))
        w=rng.normal(0,[.10,.08,.06])
        if rng.random()<.012:
            j=int(rng.choice(n,p=[.15,.30,.55])); w[j]+=rng.normal(0,.7)
        x=a*x+u+w; xh=a*xh+u; age+=1; x=np.clip(x,-10,10); xh=np.clip(xh,-10,10)
    # Remaining queued tasks count as missed at horizon.
    inf_miss += len(queue)
    arr=np.asarray(c_cost)
    return {'policy':policy,'mean_control_cost':float(arr.mean()),
            'p95_control_cost':float(np.quantile(arr,.95)),
            'safety_violation_rate':float(violations/slots),
            'inference_completion_rate':float(inf_done/max(inf_total,1)),
            'inference_deadline_miss_rate':float(inf_miss/max(inf_total,1)),
            'inference_utility_per_slot':float(inf_utility/slots),
            'control_slot_fraction':float(served_control/slots)}
