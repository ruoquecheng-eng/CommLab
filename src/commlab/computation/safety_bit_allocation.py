import numpy as np


def simulate_safety_bit_allocation(slots=3500, policy='risk_bitalloc', mean_snr_db=-1.0, bit_budget=10, seed=0):
    """Joint component selection and precision allocation for safety-critical state updates.

    Three scalar state components have unequal control/safety importance. Each
    slot has a hard bit budget. ``risk_bitalloc`` greedily allocates 2/4/6-bit
    component packets according to estimated reduction in weighted control risk
    per bit. This is an educational goal-oriented communication abstraction.
    """
    if policy not in {'uniform_low','single_high','risk_bitalloc'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3205); n=3
    a=np.array([1.035,1.065,1.09]); k=np.array([.34,.42,.50]); q=np.array([.6,1.2,2.8]); bound=np.array([5.0,3.2,1.9])
    x=rng.normal(0,.35,n); xh=x.copy(); age=np.zeros(n,int); costs=[]; viol=0; bits_used=[]; delivered=0
    for t in range(slots):
        err=np.abs(x-xh); proximity=np.clip(np.abs(x)/bound,0,2)
        value=q*(err**2+.08*age)*(1+3*np.maximum(0,proximity-.55)**2)
        packets=[]
        if policy=='uniform_low':
            # Three low-precision components, 3 bits each.
            packets=[(i,3) for i in range(n)]
        elif policy=='single_high':
            i=int(np.argmax(value)); packets=[(i,min(6,bit_budget))]
        else:
            # Preserve coarse observability of all components first; use the
            # remaining budget to refine the most safety/control-relevant ones.
            allocated=np.zeros(n,int); rem=bit_budget
            if rem>=2*n:
                allocated[:]=2; rem-=2*n
            while rem>=2:
                cand=[]
                for i in range(n):
                    if allocated[i]>=6: continue
                    gain=value[i]*(.55 if allocated[i]==2 else .22 if allocated[i]==4 else 1.0)/2
                    cand.append((gain,i))
                if not cand: break
                _,i=max(cand); allocated[i]+=2; rem-=2
            packets=[(i,int(b)) for i,b in enumerate(allocated) if b>0]
        total=sum(b for _,b in packets); bits_used.append(total)
        for i,b in packets:
            snr=mean_snr_db+[-1.5,0,1.2][i]+1.0*np.sin(2*np.pi*t/79+i)
            gp=10**(snr/10); ps=1-np.exp(-gp/(1.9+.20*b))
            if rng.random()<ps:
                # Quantized innovation update.
                step=max(.02,3.2/(2**b)); innovation=x[i]-xh[i]
                qinnov=np.round(innovation/step)*step; xh[i]+=qinnov; age[i]=0; delivered+=1
        u=-k*xh; costs.append(float(np.mean(q*x*x+.05*u*u))); viol+=int(np.any(np.abs(x)>bound))
        w=rng.normal(0,[.08,.07,.055])
        if rng.random()<.018:
            j=int(rng.choice(n,p=[.1,.25,.65])); w[j]+=rng.normal(0,.55)
        x=a*x+u+w; xh=a*xh+u; age+=1; x=np.clip(x,-10,10); xh=np.clip(xh,-10,10)
    arr=np.asarray(costs)
    return {'policy':policy,'mean_control_cost':float(arr.mean()),'p95_control_cost':float(np.quantile(arr,.95)),
            'safety_violation_rate':float(viol/slots),'mean_payload_bits_per_slot':float(np.mean(bits_used)),
            'component_delivery_rate_per_slot':float(delivered/slots)}
