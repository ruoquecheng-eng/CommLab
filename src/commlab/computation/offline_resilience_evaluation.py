from __future__ import annotations

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def _feature_matrix(risk, time, uncertainty, task_class):
    important=(task_class==1).astype(float)
    critical=(task_class==2).astype(float)
    # Deliberately compact/stale direct model. The environment contains time,
    # uncertainty, and nonlinear latent effects that this model cannot express.
    return np.column_stack([np.ones(len(risk)),risk,important,critical])


def _ridge_predictions(features, action, outcome, ridge=2.0):
    predictions=[]
    for arm in (0,1):
        take=action==arm
        if take.sum()<features.shape[1]+2:
            pred=np.full(len(outcome),outcome[take].mean() if take.any() else outcome.mean())
        else:
            x=features[take]; y=outcome[take]
            penalty=np.eye(x.shape[1])*ridge; penalty[0,0]=0.0
            beta=np.linalg.solve(x.T@x+penalty,x.T@y)
            pred=features@beta
        predictions.append(np.clip(pred,.001,.999))
    return predictions[0],predictions[1]


def _target_propensity(name, risk, uncertainty, task_class):
    if name=="baseline":
        p=_sigmoid(-1.0+8.0*(risk-.12)+.65*(task_class==1))
    elif name=="sparse":
        p=_sigmoid(-2.0+7.0*(risk-.14)+.35*(task_class==1))
    elif name=="balanced":
        p=_sigmoid(-.35+10.0*(risk-.12)+.80*(task_class==1))
    elif name=="aggressive":
        p=_sigmoid(.80+11.0*(risk-.10)+1.0*(task_class==1)+.7*uncertainty)
    elif name=="unsafe_critical_probe":
        p=_sigmoid(-.35+10.0*(risk-.12)+.80*(task_class==1))
        p=np.where(task_class==2,.5,p)
        return np.clip(p,.001,.999)
    else:
        raise ValueError("unknown target policy")
    # Safe target policies never request an unprotected critical task.
    return np.where(task_class==2,1.0,np.clip(p,.001,.999))


def _generate_log(n_tasks,logging_policy,exploration_rate,drift_strength,
                  nonlinearity,radio_correlation,seed):
    rng=np.random.default_rng(seed+3601)
    task_class=rng.choice(3,n_tasks,p=[.70,.24,.06])
    weights=np.array([1.0,2.5,6.0])[task_class]
    time=np.arange(n_tasks)/max(n_tasks-1,1)
    drift=_sigmoid((np.arange(n_tasks)-.58*n_tasks)/max(18,.035*n_tasks))
    latent=np.zeros(n_tasks)
    for t in range(1,n_tasks): latent[t]=.965*latent[t-1]+rng.normal(0,.17)
    uncertainty=np.clip(.20+.24*np.abs(latent)+.25*drift+rng.normal(0,.04,n_tasks),.04,1.2)
    class_term=.50*(task_class==1)+1.05*(task_class==2)
    nonlinear=nonlinearity*(.42*np.sin(4*np.pi*time)+.30*np.square(np.clip(latent,-2,2)))
    logit=-2.55+.78*latent+class_term+1.10*drift_strength*drift+nonlinear
    p0=np.clip(_sigmoid(logit),.015,.78)
    residual=np.clip(.22+.58*radio_correlation+.10*uncertainty,.18,.92)
    p1=np.minimum(p0,p0*residual)
    # The deployed risk score is stale and misses most nonlinear/drift structure.
    risk=np.clip(_sigmoid(-2.55+.78*latent+class_term+.24*drift_strength*drift+
                          rng.normal(0,.16,n_tasks)),.01,.72)

    if logging_policy=="safe_explore":
        core=(risk>.135)|(task_class==1)
        p_log=np.where(core,1-exploration_rate,exploration_rate).astype(float)
    elif logging_policy=="conservative":
        core=(risk>.085)|(task_class==1)
        floor=exploration_rate/2
        p_log=np.where(core,1-floor,floor).astype(float)
    elif logging_policy=="deterministic":
        p_log=((risk>.135)|(task_class>0)).astype(float)
    else:
        raise ValueError("unknown logging policy")
    # Safety constraint: the logging policy never withholds critical protection.
    p_log=np.where(task_class==2,1.0,p_log)
    action=rng.random(n_tasks)<p_log
    u=rng.random(n_tasks)
    y0=(u<p0).astype(float); y1=(u<p1).astype(float)
    observed=np.where(action,y1,y0)
    return {"task_class":task_class,"weights":weights,"time":time,"uncertainty":uncertainty,
            "risk":risk,"p0":p0,"p1":p1,"y0":y0,"y1":y1,"p_log":p_log,
            "action":action.astype(int),"observed":observed,"drift":drift}


def simulate_offline_resilience_evaluation(
    n_tasks=12000,
    logging_policy="safe_explore",
    target_policy="balanced",
    estimator="dr",
    exploration_rate=.08,
    drift_strength=1.0,
    nonlinearity=1.0,
    radio_correlation=.25,
    clip_weight=12.0,
    recency_fraction=1.0,
    protection_cost=.035,
    seed=0,
):
    """Evaluate a protection policy from action-dependent logged outcomes.

    Known logging propensities support DM, IPS, self-normalized IPS, doubly
    robust, and clipped-DR estimates. Paired potential outcomes provide an
    oracle benchmark only; neither potential outcome is exposed to an online
    decision. Critical tasks are always protected in the logging policy.

    Confidence intervals are simple influence-value normal approximations for
    the synthetic trace. They are diagnostics, not finite-sample certificates.
    """
    estimators={"dm","ips","snips","dr","clipped_dr"}
    if estimator not in estimators: raise ValueError("unknown estimator")
    if n_tasks<800 or not (0<=exploration_rate<.5) or not (0<recency_fraction<=1):
        raise ValueError("invalid logging setup")
    if drift_strength<0 or nonlinearity<0 or not (0<=radio_correlation<=1) or clip_weight<=1:
        raise ValueError("invalid environment setup")
    log=_generate_log(n_tasks,logging_policy,exploration_rate,drift_strength,
                      nonlinearity,radio_correlation,seed)
    current_start=int(.8*n_tasks)
    current=np.arange(n_tasks)>=current_start
    current_target=_target_propensity(target_policy,log["risk"][current],log["uncertainty"][current],
                                      log["task_class"][current])
    current_weights=log["weights"][current]
    current_oracle=float(np.sum(current_weights*((1-current_target)*log["y0"][current]+
                         current_target*log["y1"][current]))/np.sum(current_weights))
    start=int((1-recency_fraction)*n_tasks); take=np.arange(n_tasks)>=start
    cls=log["task_class"][take]; weights=log["weights"][take]; risk=log["risk"][take]
    time=log["time"][take]; uncertainty=log["uncertainty"][take]
    action=log["action"][take]; observed=log["observed"][take]; p_log=log["p_log"][take]
    y0=log["y0"][take]; y1=log["y1"][take]
    p_target=_target_propensity(target_policy,risk,uncertainty,cls)
    features=_feature_matrix(risk,time,uncertainty,cls)
    m0,m1=_ridge_predictions(features,action,observed)
    m_target=(1-p_target)*m0+p_target*m1
    m_observed=np.where(action==1,m1,m0)

    observed_prob=np.where(action==1,p_log,1-p_log)
    target_prob=np.where(action==1,p_target,1-p_target)
    ratio=np.divide(target_prob,observed_prob,out=np.zeros_like(target_prob),where=observed_prob>0)
    mean_weight=float(weights.mean())
    dm_terms=weights*m_target/mean_weight
    ips_terms=weights*ratio*observed/mean_weight
    dr_terms=weights*(m_target+ratio*(observed-m_observed))/mean_weight
    clipped=np.minimum(ratio,clip_weight)
    clipped_terms=weights*(m_target+clipped*(observed-m_observed))/mean_weight
    if estimator=="dm":
        terms=dm_terms; estimate=float(terms.mean())
    elif estimator=="ips":
        terms=ips_terms; estimate=float(terms.mean())
    elif estimator=="snips":
        denom=float(np.sum(weights*ratio))
        estimate=float(np.sum(weights*ratio*observed)/max(denom,1e-12))
        terms=weights*ratio*(observed-estimate)/max(np.mean(weights*ratio),1e-12)+estimate
    elif estimator=="dr":
        terms=dr_terms; estimate=float(terms.mean())
    else:
        terms=clipped_terms; estimate=float(terms.mean())

    oracle=float(np.sum(weights*((1-p_target)*y0+p_target*y1))/np.sum(weights))
    protect_rate=float(np.mean(p_target)); logging_rate=float(action.mean())
    objective=estimate+protection_cost*protect_rate
    oracle_objective=oracle+protection_cost*protect_rate
    stderr=float(np.std(terms,ddof=1)/np.sqrt(len(terms)))
    unsupported=(p_log<=1e-12)*(p_target>1e-12)*p_target
    unsupported+=(p_log>=1-1e-12)*(p_target<1-1e-12)*(1-p_target)
    support_violation=float(np.sum(weights*unsupported)/np.sum(weights))
    wr=weights*ratio
    ess=float(np.square(wr.sum())/max(np.square(wr).sum(),1e-12))
    critical=cls==2
    return {
        "estimator":estimator,"logging_policy":logging_policy,"target_policy":target_policy,
        "n_evaluation_tasks":int(len(observed)),"exploration_rate":float(exploration_rate),
        "recency_fraction":float(recency_fraction),"drift_strength":float(drift_strength),
        "nonlinearity":float(nonlinearity),"radio_correlation":float(radio_correlation),
        "clip_weight":float(clip_weight),
        "estimated_weighted_miss":estimate,"oracle_weighted_miss":oracle,
        "signed_error":float(estimate-oracle),"absolute_error":float(abs(estimate-oracle)),
        "current_oracle_weighted_miss":current_oracle,
        "current_signed_error":float(estimate-current_oracle),
        "current_absolute_error":float(abs(estimate-current_oracle)),
        "standard_error":stderr,"ci95_low":float(max(0,estimate-1.96*stderr)),
        "ci95_high":float(min(1,estimate+1.96*stderr)),
        "estimated_objective":float(objective),"oracle_objective":float(oracle_objective),
        "target_protection_rate":protect_rate,"logging_protection_rate":logging_rate,
        "effective_sample_size":ess,"effective_sample_fraction":float(ess/len(observed)),
        "max_importance_weight":float(ratio.max(initial=0)),
        "support_violation_mass":support_violation,"identifiable":bool(support_violation<1e-10),
        "critical_logging_unprotected_rate":float(np.mean(action[critical]==0)) if critical.any() else 0.0,
        "critical_target_unprotected_probability":float(np.mean(1-p_target[critical])) if critical.any() else 0.0,
    }


def select_offline_resilience_policy(
    n_tasks=12000,
    estimator="dr",
    selector="greedy",
    logging_policy="safe_explore",
    exploration_rate=.08,
    drift_strength=1.0,
    nonlinearity=1.0,
    radio_correlation=.25,
    protection_cost=.035,
    seed=0,
):
    """Select among safe target policies using offline estimates.

    ``conservative`` requires a candidate's approximate upper loss bound to be
    below the baseline's approximate lower bound; otherwise it retains the
    baseline. This is a transparent finite-trace heuristic, not HCOPE.
    """
    if selector not in {"greedy","conservative"}: raise ValueError("unknown selector")
    candidates=("baseline","sparse","balanced","aggressive")
    results={p:simulate_offline_resilience_evaluation(
        n_tasks=n_tasks,logging_policy=logging_policy,target_policy=p,estimator=estimator,
        exploration_rate=exploration_rate,drift_strength=drift_strength,nonlinearity=nonlinearity,
        radio_correlation=radio_correlation,protection_cost=protection_cost,seed=seed) for p in candidates}
    if selector=="greedy":
        selected=min(candidates,key=lambda p:results[p]["estimated_objective"])
        fallback=False
    else:
        baseline=results["baseline"]
        baseline_lower=baseline["estimated_objective"]-1.96*baseline["standard_error"]
        eligible=[p for p in candidates if p!="baseline" and
                  results[p]["estimated_objective"]+1.96*results[p]["standard_error"]<baseline_lower]
        selected=min(eligible,key=lambda p:results[p]["estimated_objective"]+1.96*results[p]["standard_error"]) if eligible else "baseline"
        fallback=not bool(eligible)
    oracle_best=min(candidates,key=lambda p:results[p]["oracle_objective"])
    return {"selector":selector,"estimator":estimator,"selected_policy":selected,
            "oracle_best_policy":oracle_best,"selection_regret":float(results[selected]["oracle_objective"]-results[oracle_best]["oracle_objective"]),
            "selected_estimated_objective":float(results[selected]["estimated_objective"]),
            "selected_oracle_objective":float(results[selected]["oracle_objective"]),
            "baseline_fallback":bool(fallback),"candidate_results":results}
