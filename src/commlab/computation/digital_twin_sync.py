import numpy as np

from .downlink_differential import _packet_success_probability


def simulate_digital_twin_sync(
    slots=360,
    policy="semantic_delta",
    periodic_interval=8,
    error_threshold=1.5,
    mean_snr_db=3.0,
    delta_bits=5,
    incorrect_tolerance=2.0,
    seed=0,
):
    """Event-triggered physical-to-digital-twin state synchronization.

    The physical process is a 1-D position/velocity system with two maneuver
    episodes. The edge twin predicts with a constant-velocity model between
    received updates. Policies are periodic full-state updates, error-triggered
    full updates, and smaller quantized semantic innovations.

    ``mean_aoii`` is an educational Age-of-Incorrect-Information proxy: update
    age is accumulated only while position error exceeds ``incorrect_tolerance``.
    """
    if policy not in {"periodic", "error_full", "semantic_delta"}:
        raise ValueError("unknown policy")
    if slots < 20 or periodic_interval < 1 or delta_bits < 2:
        raise ValueError("invalid setup")
    rng=np.random.default_rng(seed+2805)

    true=np.array([0.0,1.0]); twin=true.copy(); age=0
    err_hist=[]; aoii_hist=[]; load_hist=[]; update_hist=[]; success=attempts=0

    for t in range(1,slots+1):
        # Maneuvers break the twin's constant-velocity predictor.
        if 105<=t<150: acc=.045
        elif 230<=t<265: acc=-.060
        else: acc=0.0
        acc += rng.normal(0,.008)
        true[0] += true[1] + .5*acc
        true[1] += acc
        twin[0] += twin[1]
        age += 1

        pos_err=true[0]-twin[0]; vel_err=true[1]-twin[1]
        trigger = (t % periodic_interval == 0) if policy=="periodic" else (abs(pos_err)>=error_threshold)
        size=0.0
        if trigger:
            attempts+=1
            snr=mean_snr_db+1.5*np.sin(2*np.pi*t/79)+rng.normal(0,.8)
            if policy=="semantic_delta":
                # State innovation is compressed more when the correction is small.
                magnitude=abs(pos_err)+4*abs(vel_err)
                size=float(min(.55,.10+.055*np.log1p(magnitude)))
            else:
                size=1.0
            p=float(_packet_success_probability(snr,size))
            if rng.random()<p:
                success+=1
                if policy=="semantic_delta":
                    # Uniform quantization range tracks the current innovation.
                    scale=max(abs(pos_err),4*abs(vel_err),.25)
                    levels=2**delta_bits-1
                    qstep=2*scale/levels
                    qpos=np.round(pos_err/qstep)*qstep
                    qvel=np.round(vel_err/(qstep/4))*(qstep/4)
                    twin[0]+=qpos; twin[1]+=qvel
                else:
                    twin=true.copy()
                age=0
        err=abs(true[0]-twin[0])
        err_hist.append(err)
        aoii_hist.append(age if err>incorrect_tolerance else 0)
        load_hist.append(size)
        update_hist.append(trigger)

    return {
        "policy":policy,
        "position_rmse":float(np.sqrt(np.mean(np.asarray(err_hist)**2))),
        "p95_position_error":float(np.quantile(err_hist,.95)),
        "mean_aoii":float(np.mean(aoii_hist)),
        "update_attempt_fraction":float(attempts/slots),
        "update_success_fraction":float(success/max(attempts,1)),
        "normalized_radio_load_per_slot":float(np.sum(load_hist)/slots),
        "mean_packet_size_when_triggered":float(np.sum(load_hist)/max(attempts,1)),
        "error_history":np.asarray(err_hist),
        "aoii_history":np.asarray(aoii_hist),
        "update_history":np.asarray(update_hist,dtype=bool),
    }
