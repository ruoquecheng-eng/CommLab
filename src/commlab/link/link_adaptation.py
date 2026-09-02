import numpy as np


class OuterLoopLinkAdaptation:
    """Small outer-loop link-adaptation (OLLA) controller.

    ``offset_db`` is a conservative SNR backoff: the scheduler should select an
    MCS using ``snr_estimate_db - offset_db``. NACK increases the backoff; ACK
    decreases it. The ACK step is chosen so the expected offset drift is zero
    at ``target_bler``.
    """
    def __init__(self, target_bler: float = 0.1, nack_step_db: float = 0.25,
                 initial_offset_db: float = 0.0, min_offset_db: float = -8.0,
                 max_offset_db: float = 12.0):
        if not (0 < target_bler < 1) or nack_step_db <= 0:
            raise ValueError("invalid OLLA parameters")
        self.target_bler=float(target_bler)
        self.nack_step_db=float(nack_step_db)
        self.ack_step_db=self.nack_step_db*self.target_bler/(1.0-self.target_bler)
        self.min_offset_db=float(min_offset_db); self.max_offset_db=float(max_offset_db)
        self.offset_db=float(np.clip(initial_offset_db,self.min_offset_db,self.max_offset_db))

    def effective_snr_db(self, estimated_snr_db: float) -> float:
        return float(estimated_snr_db)-self.offset_db

    def update(self, ack: bool) -> float:
        if bool(ack): self.offset_db -= self.ack_step_db
        else: self.offset_db += self.nack_step_db
        self.offset_db=float(np.clip(self.offset_db,self.min_offset_db,self.max_offset_db))
        return self.offset_db


def select_mcs(effective_snr_db: float, thresholds_db, efficiencies) -> tuple[int,float]:
    """Select the highest MCS whose SNR threshold is met."""
    th=np.asarray(thresholds_db,dtype=float).reshape(-1)
    eff=np.asarray(efficiencies,dtype=float).reshape(-1)
    if len(th)!=len(eff) or len(th)<1 or np.any(np.diff(th)<0):
        raise ValueError("invalid MCS table")
    idx=int(np.searchsorted(th,float(effective_snr_db),side='right')-1)
    idx=max(0,min(idx,len(th)-1))
    return idx,float(eff[idx])


def logistic_bler(true_snr_db: float, threshold_db: float, width_db: float = 0.8,
                  midpoint_bler: float = 0.1) -> float:
    """Smooth educational BLER curve around an MCS operating threshold.

    The threshold is defined at ``midpoint_bler`` (default 10%), rather than
    at 50%, which makes threshold tables intuitive for target-BLER selection.
    """
    if width_db <= 0 or not (0 < midpoint_bler < 1):
        raise ValueError("invalid BLER curve parameters")
    # p = 1/(1+exp((snr-c)/w)); choose c so p(threshold)=midpoint_bler.
    center=float(threshold_db)-float(width_db)*np.log(1.0/midpoint_bler-1.0)
    z=np.clip((float(true_snr_db)-center)/float(width_db),-60,60)
    return float(1.0/(1.0+np.exp(z)))
