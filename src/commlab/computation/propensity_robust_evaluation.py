from __future__ import annotations

import numpy as np

from .offline_resilience_evaluation import _ridge_predictions, _sigmoid, _target_propensity


def _logit(p):
    p=np.clip(p,1e-6,1-1e-6)
    return np.log(p/(1-p))


def _fit_logistic(x,y,ridge=1.0,max_iter=35):
    beta=np.zeros(x.shape[1])
    penalty=np.eye(x.shape[1])*ridge; penalty[0,0]=0.0
    for _ in range(max_iter):
        p=_sigmoid(x@beta); w=np.clip(p*(1-p),1e-5,None)
        grad=x.T@(p-y)+penalty@beta
        hess=(x.T*w)@x+penalty
        step=np.linalg.solve(hess,grad)
        beta-=step
        if np.max(np.abs(step))<1e-7: break
    return beta


def _ece(pred,truth,bins=10):
    edges=np.linspace(0,1,bins+1); total=0.0
    for i in range(bins):
        take=(pred>=edges[i])&(pred<(edges[i+1] if i<bins-1 else edges[i+1]+1e-12))
        if take.any(): total+=take.mean()*abs(pred[take].mean()-truth[take].mean())
    return float(total)


def _generate_confounded_log(n_tasks,exploration_floor,hidden_confounding,
                             propensity_drift,seed):
    rng=np.random.default_rng(seed+3701)
    task_class=rng.choice(3,n_tasks,p=[.70,.24,.06])
    weights=np.array([1.0,2.5,6.0])[task_class]
    time=np.arange(n_tasks)/max(n_tasks-1,1)
    drift=_sigmoid((np.arange(n_tasks)-.57*n_tasks)/max(18,.035*n_tasks))
    latent=np.zeros(n_tasks); hidden=np.zeros(n_tasks)
    for t in range(1,n_tasks):
        latent[t]=.965*latent[t-1]+rng.normal(0,.17)
        hidden[t]=.91*hidden[t-1]+rng.normal(0,.27)
    hidden=np.clip(hidden,-2.5,2.5)
    important=(task_class==1).astype(float); critical=(task_class==2).astype(float)
    uncertainty=np.clip(.16+.20*np.abs(latent)+.16*np.abs(hidden)+.18*drift+rng.normal(0,.035,n_tasks),.03,1.2)
    risk=np.clip(_sigmoid(-2.45+.82*latent+.48*important+1.0*critical+.26*drift+rng.normal(0,.15,n_tasks)),.01,.78)
    outcome_logit=-2.55+.82*latent+.85*hidden+.48*important+1.02*critical+1.05*drift
    p0=np.clip(_sigmoid(outcome_logit),.012,.82)
    residual=np.clip(.24+.11*uncertainty,.18,.52); p1=np.minimum(p0,p0*residual)

    stale_logit=-.55+8.2*(risk-.12)+.72*important+.48*uncertainty
    nominal_logit=stale_logit+1.45*propensity_drift*drift
    true_logit=nominal_logit+1.10*hidden_confounding*hidden
    p_stale=np.clip(_sigmoid(stale_logit),exploration_floor,1-exploration_floor)
    p_nominal=np.clip(_sigmoid(nominal_logit),exploration_floor,1-exploration_floor)
    p_true=np.clip(_sigmoid(true_logit),exploration_floor,1-exploration_floor)
    p_stale=np.where(task_class==2,1.0,p_stale)
    p_nominal=np.where(task_class==2,1.0,p_nominal)
    p_true=np.where(task_class==2,1.0,p_true)
    action=(rng.random(n_tasks)<p_true).astype(int)
    u=rng.random(n_tasks); y0=(u<p0).astype(float); y1=(u<p1).astype(float)
    observed=np.where(action==1,y1,y0)
    noise=rng.normal(size=(n_tasks,18))
    x_full=np.column_stack([np.ones(n_tasks),risk,risk*risk,uncertainty,time,time*time,important,
                            critical,risk*time,uncertainty*risk,noise])
    x_simple=np.column_stack([np.ones(n_tasks),risk,important,critical])
    x_outcome=np.column_stack([np.ones(n_tasks),risk,important,critical])
    return {"task_class":task_class,"weights":weights,"risk":risk,"uncertainty":uncertainty,
            "time":time,"p_true":p_true,"p_nominal":p_nominal,"p_stale":p_stale,
            "action":action,"y0":y0,"y1":y1,"observed":observed,
            "x_full":x_full,"x_simple":x_simple,"x_outcome":x_outcome}


def _estimate_propensity(mode,log,folds,ridge):
    critical=log["task_class"]==2; y=log["action"].astype(float)
    if mode=="recorded_true": pred=log["p_true"].copy()
    elif mode=="recorded_nominal": pred=log["p_nominal"].copy()
    elif mode=="stale_recorded": pred=log["p_stale"].copy()
    elif mode in {"estimated_full","estimated_crossfit","misspecified"}:
        x=log["x_simple"] if mode=="misspecified" else log["x_full"]
        if mode=="estimated_crossfit":
            pred=np.zeros(len(y)); fold_id=np.arange(len(y))%folds
            for fold in range(folds):
                train=fold_id!=fold; test=~train
                pred[test]=_sigmoid(x[test]@_fit_logistic(x[train],y[train],ridge=ridge))
        else:
            pred=_sigmoid(x@_fit_logistic(x,y,ridge=ridge))
        pred=np.clip(pred,.003,.997); pred[critical]=1.0
    else: raise ValueError("unknown propensity mode")
    return pred


def simulate_propensity_robust_evaluation(
    n_tasks=10000,
    propensity_mode="estimated_crossfit",
    estimator="dr",
    target_policy="balanced",
    exploration_floor=.06,
    hidden_confounding=0.0,
    propensity_drift=1.0,
    sensitivity_gamma=1.5,
    clip_weight=12.0,
    folds=5,
    propensity_ridge=1.0,
    protection_cost=.06,
    seed=0,
):
    """Stress off-policy evaluation when logging propensities are uncertain.

    ``recorded_true`` is a synthetic diagnostic. Other modes omit the hidden
    severity that can affect both action and outcome. The returned sensitivity
    interval is an empirical odds-envelope diagnostic; it is not a sharp
    marginal-sensitivity bound or a causal confidence interval.
    """
    modes={"recorded_true","recorded_nominal","stale_recorded","estimated_full",
           "estimated_crossfit","misspecified"}
    estimators={"ips","snips","dr","clipped_dr"}
    if propensity_mode not in modes or estimator not in estimators: raise ValueError("unknown evaluation mode")
    if n_tasks<800 or not (0<exploration_floor<.5) or folds<2 or folds>10 or propensity_ridge<0:
        raise ValueError("invalid logging setup")
    if hidden_confounding<0 or propensity_drift<0 or sensitivity_gamma<1 or clip_weight<=1:
        raise ValueError("invalid robustness setup")
    log=_generate_confounded_log(n_tasks,exploration_floor,hidden_confounding,propensity_drift,seed)
    p_hat=_estimate_propensity(propensity_mode,log,folds,propensity_ridge)
    cls=log["task_class"]; weights=log["weights"]; action=log["action"]; observed=log["observed"]
    p_target=_target_propensity(target_policy,log["risk"],log["uncertainty"],cls)
    m0,m1=_ridge_predictions(log["x_outcome"],action,observed,ridge=2.0)
    m_target=(1-p_target)*m0+p_target*m1; m_obs=np.where(action==1,m1,m0)
    residual=observed-m_obs
    observed_hat=np.where(action==1,p_hat,1-p_hat)
    target_obs=np.where(action==1,p_target,1-p_target)
    ratio=np.divide(target_obs,observed_hat,out=np.zeros_like(target_obs),where=observed_hat>0)
    if estimator=="clipped_dr": used_ratio=np.minimum(ratio,clip_weight)
    else: used_ratio=ratio
    mean_w=float(weights.mean())
    if estimator=="ips": terms=weights*ratio*observed/mean_w; estimate=float(terms.mean())
    elif estimator=="snips":
        denom=max(float(np.sum(weights*ratio)),1e-12)
        estimate=float(np.sum(weights*ratio*observed)/denom)
        terms=weights*ratio*(observed-estimate)/max(np.mean(weights*ratio),1e-12)+estimate
    else:
        terms=weights*(m_target+used_ratio*residual)/mean_w; estimate=float(terms.mean())

    oracle=float(np.sum(weights*((1-p_target)*log["y0"]+p_target*log["y1"]))/np.sum(weights))
    # Same estimator with the hidden synthetic behavior propensity; diagnostic only.
    true_obs=np.where(action==1,log["p_true"],1-log["p_true"])
    true_ratio=np.divide(target_obs,true_obs,out=np.zeros_like(target_obs),where=true_obs>0)
    if estimator=="ips": true_est=float(np.mean(weights*true_ratio*observed/mean_w))
    elif estimator=="snips": true_est=float(np.sum(weights*true_ratio*observed)/max(np.sum(weights*true_ratio),1e-12))
    else:
        tr=np.minimum(true_ratio,clip_weight) if estimator=="clipped_dr" else true_ratio
        true_est=float(np.mean(weights*(m_target+tr*residual)/mean_w))

    # Row-wise odds envelope around the propensity used by the evaluator.
    odds=np.exp(np.clip(_logit(p_hat),-15,15)); gamma=float(sensitivity_gamma)
    p_low=(odds/gamma)/(1+odds/gamma); p_high=(odds*gamma)/(1+odds*gamma)
    critical=cls==2; p_low[critical]=p_high[critical]=1.0
    ratio_low=np.where(action==1,p_target/np.clip(p_high,1e-9,1),
                       (1-p_target)/np.clip(1-p_low,1e-9,1))
    ratio_high=np.where(action==1,p_target/np.clip(p_low,1e-9,1),
                        (1-p_target)/np.clip(1-p_high,1e-9,1))
    if estimator=="clipped_dr": ratio_low=np.minimum(ratio_low,clip_weight); ratio_high=np.minimum(ratio_high,clip_weight)
    if estimator in {"ips","snips"}:
        low_terms=weights*ratio_low*observed/mean_w; high_terms=weights*ratio_high*observed/mean_w
    else:
        low_ratio=np.where(residual>=0,ratio_low,ratio_high)
        high_ratio=np.where(residual>=0,ratio_high,ratio_low)
        low_terms=weights*(m_target+low_ratio*residual)/mean_w
        high_terms=weights*(m_target+high_ratio*residual)/mean_w
    sens_low=float(min(low_terms.mean(),high_terms.mean()))
    sens_high=float(max(low_terms.mean(),high_terms.mean()))
    noncritical=~critical
    log_odds_gap=np.abs(_logit(log["p_true"][noncritical])-_logit(p_hat[noncritical]))
    required_gamma=float(np.exp(min(12,float(log_odds_gap.max(initial=0)))))
    propensity_mae=float(np.mean(np.abs(p_hat-log["p_true"])))
    propensity_brier=float(np.mean(np.square(p_hat-log["p_true"])))
    ece=_ece(p_hat[noncritical],log["p_true"][noncritical])
    stderr=float(np.std(terms,ddof=1)/np.sqrt(n_tasks))
    protect_rate=float(p_target.mean())
    return {"propensity_mode":propensity_mode,"estimator":estimator,"target_policy":target_policy,
        "n_tasks":int(n_tasks),"exploration_floor":float(exploration_floor),
        "hidden_confounding":float(hidden_confounding),"propensity_drift":float(propensity_drift),
        "sensitivity_gamma":gamma,"estimated_weighted_miss":estimate,"oracle_weighted_miss":oracle,
        "true_propensity_estimate":true_est,"absolute_error":float(abs(estimate-oracle)),
        "signed_error":float(estimate-oracle),"propensity_induced_gap":float(estimate-true_est),
        "standard_error":stderr,"ci95_low":float(max(0,estimate-1.96*stderr)),
        "ci95_high":float(min(1,estimate+1.96*stderr)),"propensity_mae":propensity_mae,
        "propensity_brier":propensity_brier,"propensity_ece":ece,
        "max_importance_weight":float(ratio.max(initial=0)),
        "effective_sample_fraction":float(np.square((weights*ratio).sum())/max(np.square(weights*ratio).sum(),1e-12)/n_tasks),
        "required_sensitivity_gamma":required_gamma,"sensitivity_low":sens_low,
        "sensitivity_high":sens_high,"sensitivity_width":float(sens_high-sens_low),
        "sensitivity_contains_oracle":bool(sens_low<=oracle<=sens_high),
        "sensitivity_contains_true_propensity_estimate":bool(sens_low<=true_est<=sens_high),
        "target_protection_rate":protect_rate,
        "estimated_objective":float(estimate+protection_cost*protect_rate),
        "oracle_objective":float(oracle+protection_cost*protect_rate),
        "critical_logging_unprotected_rate":float(np.mean(action[critical]==0)) if critical.any() else 0.0}


def select_propensity_robust_policy(
    n_tasks=6000,
    propensity_mode="estimated_crossfit",
    selector="point",
    exploration_floor=.06,
    hidden_confounding=0.0,
    propensity_drift=1.0,
    sensitivity_gamma=1.5,
    protection_cost=.10,
    seed=0,
):
    """Select among safe policies by a point estimate or sensitivity envelope."""
    if selector not in {"point","sensitivity_guard"}: raise ValueError("unknown selector")
    candidates=("baseline","sparse","balanced","aggressive")
    results={p:simulate_propensity_robust_evaluation(n_tasks=n_tasks,propensity_mode=propensity_mode,
        estimator="dr",target_policy=p,exploration_floor=exploration_floor,
        hidden_confounding=hidden_confounding,propensity_drift=propensity_drift,
        sensitivity_gamma=sensitivity_gamma,protection_cost=protection_cost,seed=seed) for p in candidates}
    if selector=="point":
        selected=min(candidates,key=lambda p:results[p]["estimated_objective"]); fallback=False
    else:
        base=results["baseline"]; base_lower=base["sensitivity_low"]+protection_cost*base["target_protection_rate"]
        eligible=[p for p in candidates if p!="baseline" and
                  results[p]["sensitivity_high"]+protection_cost*results[p]["target_protection_rate"]<base_lower]
        selected=min(eligible,key=lambda p:results[p]["sensitivity_high"]+protection_cost*results[p]["target_protection_rate"]) if eligible else "baseline"
        fallback=not bool(eligible)
    oracle_best=min(candidates,key=lambda p:results[p]["oracle_objective"])
    return {"selector":selector,"selected_policy":selected,"oracle_best_policy":oracle_best,
        "selection_regret":float(results[selected]["oracle_objective"]-results[oracle_best]["oracle_objective"]),
        "baseline_fallback":bool(fallback),"candidate_results":results}
