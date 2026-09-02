from __future__ import annotations

from collections import deque

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def _paired_failures(primary, secondary, correlation, shared, u_common, u1, u2):
    """Return paired Bernoulli failures from an explicit common-shock mixture."""
    if shared < correlation:
        return bool(u_common < primary), bool(u_common < secondary)
    return bool(u1 < primary), bool(u2 < secondary)


def simulate_observable_resilience(
    n_tasks=7000,
    policy="hybrid_feedback",
    drift_mode="mixed",
    budget_per_task=0.9,
    telemetry_probability=0.8,
    audit_rate=0.05,
    feedback_delay=8,
    adaptation_rate=0.025,
    target_miss_rate=0.18,
    radio_correlation=0.25,
    seed=0,
):
    """Study protection-masked feedback in a resilience controller.

    Final task outcomes are action dependent: duplication or a cross-domain
    replica can hide a primary component failure. ``outcome_only`` updates one
    debt from this protected label. ``component_telemetry`` instead consumes
    delayed primary-radio and primary-edge health telemetry when available.
    ``audit_feedback`` occasionally withholds protection from routine tasks to
    observe an unprotected outcome; important and critical tasks are never
    audited. ``hybrid_feedback`` prefers component telemetry and uses routine
    audits only when that telemetry channel is unavailable. ``oracle_components``
    sees synthetic probabilities but never realized outcomes.

    Hidden unprotected outcomes are reported for evaluation only. They are not
    placed in any online feedback queue unless an explicit audit reveals them.
    This is a transparent partial-feedback simulator, not a causal estimator,
    semi-bandit regret theorem, or production telemetry model.
    """
    policies={"outcome_only","component_telemetry","audit_feedback","hybrid_feedback","oracle_components"}
    modes={"none","radio","edge","mixed"}
    if policy not in policies or drift_mode not in modes:
        raise ValueError("unknown policy or drift mode")
    if n_tasks < 400 or budget_per_task < 0 or feedback_delay < 1 or adaptation_rate < 0 or not (0 < target_miss_rate < .5):
        raise ValueError("invalid online setup")
    if not (0 <= telemetry_probability <= 1 and 0 <= audit_rate <= .5 and 0 <= radio_correlation <= 1):
        raise ValueError("invalid observability setup")

    rng=np.random.default_rng(seed+3501)
    cls=rng.choice(3,n_tasks,p=[.68,.24,.08])
    weights=np.array([1.0,2.5,6.0])[cls]
    drift_start=int(.52*n_tasks)
    drift=_sigmoid((np.arange(n_tasks)-drift_start)/max(16,.025*n_tasks))
    radio_scale=1.0 if drift_mode in {"radio","mixed"} else 0.0
    edge_scale=1.0 if drift_mode in {"edge","mixed"} else 0.0

    radio_state=np.zeros(n_tasks); edge_state=np.zeros(n_tasks)
    for t in range(1,n_tasks):
        radio_state[t]=.965*radio_state[t-1]+rng.normal(0,.15)
        edge_state[t]=.970*edge_state[t-1]+rng.normal(0,.13)
    critical=(cls==2).astype(float)
    true_radio=np.clip(.055+.030*_sigmoid(radio_state)+radio_scale*(.145*drift+.045*critical*drift),.01,.48)
    true_edge=np.clip(.040+.026*_sigmoid(edge_state)+edge_scale*(.125*drift+.070*critical*drift),.008,.45)
    true_tail=np.clip(np.array([.018,.030,.050])[cls]+.018*drift,.005,.18)
    # Deployed component models are deliberately stale after the change.
    est_radio=np.clip(.055+.030*_sigmoid(radio_state)+radio_scale*(.035*drift+.010*critical*drift)+rng.normal(0,.007,n_tasks),.008,.42)
    est_edge=np.clip(.040+.026*_sigmoid(edge_state)+edge_scale*(.030*drift+.012*critical*drift)+rng.normal(0,.007,n_tasks),.006,.40)
    est_tail=np.clip(np.array([.018,.030,.050])[cls]+.006*drift,.004,.15)

    # All potential component outcomes are generated before decisions. Policies
    # see only the delayed subset authorized by their feedback mode.
    shared_radio=rng.random(n_tasks); common_radio=rng.random(n_tasks)
    r1u=rng.random(n_tasks); r2u=rng.random(n_tasks)
    shared_edge=rng.random(n_tasks); common_edge=rng.random(n_tasks)
    e1u=rng.random(n_tasks); e2u=rng.random(n_tasks)
    tail_u=rng.random(n_tasks)
    telemetry_up=rng.random(n_tasks)<telemetry_probability
    audit_draw=rng.random(n_tasks)

    C_DUP,C_REPLICA=.72,1.10
    bucket=0.0; bucket_cap=max(3.0,9.0*budget_per_task)
    target=float(target_miss_rate); radio_target=.075; edge_target=.065
    outcome_level=target; radio_level=radio_target; edge_level=edge_target
    outcome_debt=radio_debt=edge_debt=0.0
    feedback=deque()

    final_miss=np.zeros(n_tasks); base_miss=np.zeros(n_tasks)
    predicted_base=np.zeros(n_tasks); protected_risk=np.zeros(n_tasks)
    primary_radio_fail=np.zeros(n_tasks); primary_edge_fail=np.zeros(n_tasks)
    duplicate=np.zeros(n_tasks,dtype=bool); replica=np.zeros(n_tasks,dtype=bool); audit=np.zeros(n_tasks,dtype=bool)
    observed_components=np.zeros(n_tasks,dtype=bool); debt_trace=np.zeros((n_tasks,3))
    credits=0.0; detection_time=None

    for t in range(n_tasks):
        while feedback and feedback[0][0] <= t:
            _,payload=feedback.popleft()
            k,miss,base,reveal_components,rf,ef,was_audit=payload
            if policy=="outcome_only":
                outcome_level=float((1-adaptation_rate)*outcome_level+adaptation_rate*miss)
                outcome_debt=float(max(0,outcome_level-target))
            elif policy=="component_telemetry":
                if reveal_components:
                    radio_level=float((1-adaptation_rate)*radio_level+adaptation_rate*rf)
                    edge_level=float((1-adaptation_rate)*edge_level+adaptation_rate*ef)
                    radio_debt=float(max(0,radio_level-radio_target))
                    edge_debt=float(max(0,edge_level-edge_target))
            elif policy=="audit_feedback":
                # Non-audited protected outcomes remain biased; audited labels
                # are unprotected but sparse. The update is intentionally not
                # inverse-propensity weighted, avoiding explosive variance.
                label=base if was_audit else miss
                outcome_level=float((1-adaptation_rate)*outcome_level+adaptation_rate*label)
                outcome_debt=float(max(0,outcome_level-target))
            elif policy=="hybrid_feedback":
                if reveal_components:
                    radio_level=float((1-adaptation_rate)*radio_level+adaptation_rate*rf)
                    edge_level=float((1-adaptation_rate)*edge_level+adaptation_rate*ef)
                    radio_debt=float(max(0,radio_level-radio_target))
                    edge_debt=float(max(0,edge_level-edge_target))
                else:
                    label=base if was_audit else miss
                    rate=.55*adaptation_rate
                    outcome_level=float((1-rate)*outcome_level+rate*label)
                    outcome_debt=float(max(0,outcome_level-target))

        bucket=min(bucket_cap,bucket+budget_per_task)
        k=int(cls[t]); w=float(weights[t])
        telemetry_known=bool(telemetry_up[t])
        can_audit=(k==0 and audit_draw[t]<audit_rate)
        if policy=="audit_feedback": audit[t]=can_audit
        elif policy=="hybrid_feedback": audit[t]=can_audit and not telemetry_known

        if policy=="oracle_components":
            rh=float(true_radio[t]); eh=float(true_edge[t]); th=float(true_tail[t])
        else:
            rh=float(est_radio[t]); eh=float(est_edge[t]); th=float(est_tail[t])
        base_hat=1-(1-rh)*(1-eh)*(1-th); predicted_base[t]=base_hat
        dup_risk=1-(1-(radio_correlation*rh+(1-radio_correlation)*rh*min(.92*rh,rh)))*(1-eh)*(1-th)
        rep_edge=.18*max(eh,min(.90*eh,eh))+.82*eh*min(.90*eh,eh)
        rep_risk=1-(1-rh)*(1-rep_edge)*(1-th)

        if policy in {"component_telemetry","hybrid_feedback","oracle_components"}:
            rg=radio_debt+.35*outcome_debt; eg=edge_debt+.35*outcome_debt
        else:
            rg=eg=outcome_debt
        debt_trace[t]=[outcome_debt,radio_debt,edge_debt]
        if detection_time is None and t>=drift_start and max(outcome_debt,radio_debt,edge_debt)>.045:
            detection_time=t

        if not audit[t]:
            cand=[(w*max(0,base_hat-dup_risk)*(1+10*rg)/C_DUP,0,C_DUP),
                  (w*max(0,base_hat-rep_risk)*(1+10*eg)/C_REPLICA,1,C_REPLICA)]
            for score,action,cost in sorted(cand,reverse=True):
                if score<.105 or bucket+1e-12<cost: continue
                bucket-=cost; credits+=cost
                if action==0: duplicate[t]=True
                else: replica[t]=True
                # At most one mechanism for routine tasks; important/critical
                # tasks may buy orthogonal radio and edge protection.
                if k==0 or (duplicate[t] and replica[t]): break

        rf1,rf2=_paired_failures(float(true_radio[t]),float(min(.92*true_radio[t],true_radio[t])),
            radio_correlation,float(shared_radio[t]),float(common_radio[t]),float(r1u[t]),float(r2u[t]))
        ef1,ef2=_paired_failures(float(true_edge[t]),float(min(.90*true_edge[t],true_edge[t])),
            .18,float(shared_edge[t]),float(common_edge[t]),float(e1u[t]),float(e2u[t]))
        tf=bool(tail_u[t]<true_tail[t])
        protected_radio=rf1 and (not duplicate[t] or rf2)
        protected_edge=ef1 and (not replica[t] or ef2)
        bm=bool(rf1 or ef1 or tf); fm=bool(protected_radio or protected_edge or tf)
        primary_radio_fail[t]=rf1; primary_edge_fail[t]=ef1
        base_miss[t]=bm; final_miss[t]=fm
        actual_radio=true_radio[t] if not duplicate[t] else radio_correlation*true_radio[t]+(1-radio_correlation)*true_radio[t]*min(.92*true_radio[t],true_radio[t])
        actual_edge=true_edge[t] if not replica[t] else .18*true_edge[t]+.82*true_edge[t]*min(.90*true_edge[t],true_edge[t])
        protected_risk[t]=1-(1-actual_radio)*(1-actual_edge)*(1-true_tail[t])

        reveal=telemetry_known and policy in {"component_telemetry","hybrid_feedback"}
        observed_components[t]=reveal
        feedback.append((t+feedback_delay,(k,float(fm),float(bm),reveal,float(rf1),float(ef1),bool(audit[t]))))

    post=np.arange(n_tasks)>=drift_start
    masked=(base_miss>final_miss)
    total_weight=float(weights.sum()); post_weight=float(weights[post].sum())
    routine=cls==0; critical=cls==2
    if detection_time is None: detection_time=n_tasks
    return {
        "policy":policy,"drift_mode":drift_mode,"budget_per_task":float(budget_per_task),
        "target_miss_rate":float(target_miss_rate),
        "telemetry_probability":float(telemetry_probability),"audit_rate":float(audit_rate),
        "feedback_delay":int(feedback_delay),"protected_miss_rate":float(final_miss.mean()),
        "task_weighted_protected_miss_rate":float(np.sum(weights*final_miss)/total_weight),
        "post_drift_weighted_miss_rate":float(np.sum(weights[post]*final_miss[post])/post_weight),
        "unprotected_counterfactual_miss_rate":float(base_miss.mean()),
        "post_drift_unprotected_miss_rate":float(base_miss[post].mean()),
        "masked_failure_rate":float(masked.mean()),
        "masked_fraction_of_base_failures":float(masked.sum()/max(base_miss.sum(),1)),
        "routine_miss_rate":float(final_miss[routine].mean()),
        "critical_miss_rate":float(final_miss[critical].mean()),
        "audit_fraction":float(audit.mean()),
        "critical_audit_fraction":float(audit[critical].mean()),
        "audit_miss_rate":float(final_miss[audit].mean()) if audit.any() else 0.0,
        "component_observation_rate":float(observed_components.mean()),
        "primary_radio_failure_rate":float(primary_radio_fail.mean()),
        "primary_edge_failure_rate":float(primary_edge_fail.mean()),
        "base_risk_calibration_gap":float(base_miss.mean()-predicted_base.mean()),
        "protected_risk_calibration_gap":float(final_miss.mean()-protected_risk.mean()),
        "resilience_credits_per_task":float(credits/n_tasks),
        "duplicate_action_rate":float(duplicate.mean()),"replica_action_rate":float(replica.mean()),
        "mean_transmissions_per_task":float(1+duplicate.mean()),
        "detection_delay_tasks":int(max(0,detection_time-drift_start)),
        "mean_outcome_debt":float(debt_trace[:,0].mean()),
        "mean_radio_debt":float(debt_trace[:,1].mean()),
        "mean_edge_debt":float(debt_trace[:,2].mean()),
    }
