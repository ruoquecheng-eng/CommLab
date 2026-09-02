import numpy as np
from commlab.sensing.beam_tracking import expected_ula_rate_under_angle_uncertainty


def posterior_angle_std(prior_std_deg: float, sensing_fraction: float, reference_std_deg: float = 2.5,
                        reference_fraction: float = 0.05) -> float:
    """Simple information-fusion model for sensing overhead vs angle uncertainty."""
    if prior_std_deg<=0 or reference_std_deg<=0 or reference_fraction<=0 or not (0<=sensing_fraction<1):
        raise ValueError('invalid sensing uncertainty parameters')
    if sensing_fraction==0: return float(prior_std_deg)
    meas_std=reference_std_deg*np.sqrt(reference_fraction/float(sensing_fraction))
    precision=1/prior_std_deg**2+1/meas_std**2
    return float(1/np.sqrt(precision))


def joint_sensing_comm_resource_selection(prior_std_deg: float, candidate_elements,
                                          sensing_fractions, snr_per_element_linear: float,
                                          reference_std_deg: float = 2.5) -> dict:
    """Choose sensing time fraction and active ULA aperture for net throughput."""
    best=None; rows=[]
    for f in sensing_fractions:
        post=posterior_angle_std(prior_std_deg,float(f),reference_std_deg)
        for n in candidate_elements:
            raw=expected_ula_rate_under_angle_uncertainty(post,int(n),snr_per_element_linear)
            net=(1-float(f))*raw
            row={'sensing_fraction':float(f),'elements':int(n),'posterior_std_deg':post,
                 'raw_rate':float(raw),'net_rate':float(net)}
            rows.append(row)
            if best is None or row['net_rate']>best['net_rate']: best=row
    if best is None: raise ValueError('empty candidate grid')
    return {'best':best,'rows':rows}
