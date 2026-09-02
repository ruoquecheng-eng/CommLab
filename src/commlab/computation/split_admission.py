import numpy as np


def simulate_progressive_split_admission(
    slots=2200,
    arrival_rate=0.8,
    n_users=8,
    policy="backpressure",
    deadline_slots=9,
    backlog_threshold=8,
    seed=0,
):
    """Admission control plus completion-aware progressive split scheduling.

    Low-confidence requests may be admitted to the radio enhancement queue or
    terminated locally. Under overload, backpressure policies preserve radio
    capacity for requests with high expected task-value gain per required chunk.
    Late predictions never count as on-time utility.
    """
    if policy not in {"admit_all", "backlog_gate", "backpressure"}:
        raise ValueError("unknown policy")
    if slots < 50 or arrival_rate < 0 or backlog_threshold < 1:
        raise ValueError("invalid setup")
    rng=np.random.default_rng(seed+2804)
    user_snr=np.clip(rng.normal(4.0,5.0,n_users),-8,18)
    pending=[]; completed=expired=radio_uses=admitted=local_fallback=0
    utility_ok=total_value=0.0; correct_on_time=0
    backlog_hist=[]; delays=[]

    for t in range(slots):
        for _ in range(rng.poisson(arrival_rate)):
            u=int(rng.integers(n_users)); diff=rng.beta(2.0,2.4)
            conf=float(np.clip(1-diff+rng.normal(0,.07),.05,.98))
            value=float(.5+1.25*diff); total_value += value
            p_local=float(np.clip(.58+.36*conf,.55,.97))
            if conf>=.84:
                completed+=1; good=int(rng.random()<p_local); correct_on_time+=good; utility_ok+=value*good; delays.append(0); continue
            dscale=rng.choice([.65,1.,1.35],p=[.28,.47,.25]); d=max(3,int(round(deadline_slots*dscale)))
            # Expected value gain from a complete progressive refinement.
            snr=user_snr[u]; succ=1-np.exp(-10**(snr/10)/2.5)
            expected_gain=value*(1-p_local)*(0.78*succ)
            expected_chunks=1.25+1.1*diff
            if policy=="admit_all":
                take=True
            elif policy=="backlog_gate":
                take=len(pending)<backlog_threshold
            else:
                congestion=(len(pending)+1)/backlog_threshold
                price=.055*congestion*expected_chunks
                urgency_bonus=.04/d
                take=(expected_gain+urgency_bonus)>price and len(pending)<2.2*backlog_threshold
            if not take:
                completed+=1; local_fallback+=1; good=int(rng.random()<p_local); correct_on_time+=good; utility_ok+=value*good; delays.append(0); continue
            admitted+=1
            pending.append({"arrival":t,"deadline":t+d,"user":u,"p":p_local,"chunk":0,"value":value})

        still=[]
        for r in pending:
            if t>r["deadline"]:
                completed+=1; expired+=1; delays.append(t-r["arrival"])
            else: still.append(r)
        pending=still

        if pending:
            def score(r):
                remaining=max(r["deadline"]-t+1,1); snr=user_snr[r["user"]]
                succ=1-np.exp(-10**(snr/10)/2.5)
                marginal=(1-r["p"])*(.52/(1+.3*r["chunk"]))*succ*r["value"]
                completion=.24*(r["chunk"]/3)
                age=.035*(t-r["arrival"])/max(r["deadline"]-r["arrival"],1)
                return marginal/remaining+completion+age
            idx=max(range(len(pending)),key=lambda i:score(pending[i])); r=pending.pop(idx); radio_uses+=1
            snr=user_snr[r["user"]]+rng.normal(0,1.2); succ=1-np.exp(-10**(snr/10)/2.5)
            if rng.random()<succ:
                r["p"]=min(.995,r["p"]+(1-r["p"])*(.52/(1+.28*r["chunk"])))
            r["chunk"]+=1
            if r["chunk"]>=3 or r["p"]>=.90:
                completed+=1; good=int(rng.random()<r["p"]); correct_on_time+=good; utility_ok+=r["value"]*good; delays.append(t-r["arrival"]+1)
            else: pending.append(r)
        backlog_hist.append(len(pending))

    expired+=len(pending); completed+=len(pending); delays.extend([slots-r["arrival"] for r in pending])
    return {
        "policy":policy,
        "completed_requests":int(completed),
        "on_time_accuracy":float(correct_on_time/max(completed,1)),
        "on_time_task_utility":float(utility_ok/max(total_value,1e-12)),
        "deadline_miss_rate":float(expired/max(completed,1)),
        "radio_uses_per_request":float(radio_uses/max(completed,1)),
        "admission_fraction":float(admitted/max(admitted+local_fallback,1)),
        "local_fallback_fraction":float(local_fallback/max(completed,1)),
        "mean_backlog":float(np.mean(backlog_hist)),
        "p95_backlog":float(np.quantile(backlog_hist,.95)),
        "p95_delay_slots":float(np.quantile(delays,.95) if delays else 0.0),
    }
