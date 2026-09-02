import numpy as np


def _quantize_scalar(x,bits,limit=24.0):
    levels=2**int(bits); step=2*limit/(levels-1)
    return np.clip(np.round((np.clip(x,-limit,limit)+limit)/step)*step-limit,-limit,limit)


def simulate_variable_rate_control(slots=2400,n_plants=5,policy='adaptive',mean_snr_db=0.0,seed=0):
    """Variable-rate state updates for wireless feedback control.

    Payload precision and packet reliability compete: larger state packets quantize
    better but are harder to deliver. The adaptive policy selects 3/6/10 bits from
    the current control-value proxy. This is a scalar semantic/control abstraction,
    not a source/channel coding standard.
    """
    if policy not in {'fixed_low','fixed_high','adaptive'}: raise ValueError('unknown policy')
    rng=np.random.default_rng(seed+3002)
    a=np.linspace(1.025,1.10,n_plants); k=np.linspace(.40,.52,n_plants); q=np.linspace(.8,1.4,n_plants)
    x=rng.normal(0,.5,n_plants); xh=x.copy(); age=np.zeros(n_plants,int)
    snr0=np.linspace(mean_snr_db+2,mean_snr_db-2,n_plants)
    costs=[]; bits_hist=[]; succ=0
    for t in range(slots):
        err=np.abs(x-xh); snr=snr0+rng.normal(0,1.2,n_plants)
        # Scheduler picks the most valuable stale loop; rate controller decides precision.
        link_base=1-np.exp(-10**(snr/10)/2.4)
        value=link_base*q*(err**2+.06*x*x)*(1+.04*age)
        i=int(np.argmax(value))
        if policy=='fixed_low': bits=3
        elif policy=='fixed_high': bits=10
        else:
            z=err[i]*(1+.06*age[i])*np.sqrt(q[i])
            # Link-aware precision: do not request a long high-precision packet
            # when the instantaneous channel is unlikely to deliver it.
            if snr[i] < -1.0: bits=3
            elif snr[i] < 3.0: bits=6 if z>.30 else 3
            else: bits=10 if z>.75 else (6 if z>.22 else 3)
        # Longer packets have lower delivery probability at the same SNR.
        p=1-np.exp(-10**(snr[i]/10)/(1.45+.13*bits))
        if rng.random()<p:
            # Predictive/semantic update: quantize only the innovation relative to
            # the controller's current estimate instead of the full dynamic range.
            delta=x[i]-xh[i]
            xh[i]=xh[i]+_quantize_scalar(delta,bits,limit=6.0); age[i]=0; succ+=1
        u=-k*xh; costs.append(float(np.mean(q*x*x+.05*u*u))); bits_hist.append(bits)
        w=rng.normal(0,.085,n_plants); x=a*x+u+w; xh=a*xh+u; age+=1
        x=np.clip(x,-80,80); xh=np.clip(xh,-80,80)
    c=np.asarray(costs)
    return {'policy':policy,'mean_control_cost':float(c.mean()),'p95_control_cost':float(np.quantile(c,.95)),
            'mean_payload_bits_per_slot':float(np.mean(bits_hist)),'update_success_rate':float(succ/slots),
            'mean_information_age':float(np.mean(age))}
