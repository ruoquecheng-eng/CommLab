import numpy as np


def simulate_component_selective_control(slots=2600,policy='value_component',mean_snr_db=0.0,seed=0):
    """Transmit selected components of a vector state over a constrained link.

    A 3-D state has unequal control sensitivity. One slot can carry either one
    high-precision component or all components at low precision.
    """
    if policy not in {'round_robin','all_low','value_component'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3105)
    a=np.array([1.06,1.035,.99]); k=np.array([.48,.36,.18]); q=np.array([2.4,1.1,.35])
    x=rng.normal(0,.5,3); xh=x.copy(); ages=np.zeros(3,int); costs=[]; bits=[]; succ=0
    for t in range(slots):
        snr=mean_snr_db+2*np.sin(2*np.pi*t/71)+rng.normal(0,1.0)
        err=np.abs(x-xh)
        if policy=='all_low': idx=np.arange(3); bpc=2; total=6
        elif policy=='round_robin': idx=np.array([t%3]); bpc=7; total=7
        else:
            score=q*(err**2+.04*ages)
            idx=np.array([int(np.argmax(score))]); bpc=7; total=7
        p=1-np.exp(-10**(snr/10)/(1.7+.16*total))
        if rng.random()<p:
            succ+=1
            # Quantization error relative to bounded state range.
            step=8/(2**bpc); noise=rng.uniform(-.5*step,.5*step,len(idx)); xh[idx]=x[idx]+noise; ages[idx]=0
        u=-k*xh; costs.append(float(np.sum(q*x*x)+.04*np.sum(u*u))); bits.append(total)
        w=rng.normal(0,[.07,.06,.05]); x=a*x+u+w; xh=a*xh+u; ages+=1
        x=np.clip(x,-15,15); xh=np.clip(xh,-15,15)
    c=np.asarray(costs)
    return {'policy':policy,'mean_control_cost':float(c.mean()),'p95_control_cost':float(np.quantile(c,.95)),
            'mean_payload_bits_per_slot':float(np.mean(bits)),'update_success_rate':float(succ/slots),
            'mean_component_age':float(np.mean(ages))}
