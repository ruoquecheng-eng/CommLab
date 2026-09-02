# CommLab v3.5 Release Notes

## Theme: Counterfactual Observability and Protected-Outcome Masking

v3.5 audits the feedback assumptions introduced in v3.4. Successful duplication or cross-domain replica execution can hide a failing primary radio or edge component, so a controller trained only on the final protected task outcome receives an action-dependent and selectively filtered label. The new simulator separates protected outcome, hidden unprotected counterfactual, component telemetry, and explicit routine-task audits.

All v3.4 and earlier modules, tests, experiments, Dashboard Labs, datasets, figures, and documents remain included.

## Feedback modes

- `outcome_only`: delayed final protected task miss only;
- `component_telemetry`: delayed primary radio/edge health when telemetry is available;
- `audit_feedback`: sometimes withholds protection from routine tasks to reveal an unprotected label;
- `hybrid_feedback`: prefers component telemetry and audits routine tasks only when telemetry is missing;
- `oracle_components`: synthetic probability diagnostic; never sees realized outcomes before acting.

Critical tasks are never audited. Hidden counterfactual outcomes are evaluation-only and do not enter online feedback except when an explicit routine audit reveals them.

## Main results

1. **Protection creates self-reassuring feedback.** As budget rises from 0.2 to 1.2 credits/task, outcome-only masked failures rise from about 8.1% to 28.5% of underlying base failures, while learned outcome debt falls from about 0.086 to 0.037.
2. **Component attribution helps in a radio-drift regime.** Post-drift weighted miss falls from about 18.80% outcome-only to 16.81% with component telemetry, while duplication rises from 49.85% to 67.09%.
3. **Correct attribution is not sufficient.** Under edge drift, component telemetry shifts replication from 20.78% to 35.50%, yet weighted miss is about 18.82% versus 18.61% outcome-only. Under mixed drift it also does not dominate.
4. **Audits are a fallback, not free information.** With telemetry entirely absent, hybrid feedback uses about 5.37% routine audits and lowers post-drift weighted miss from 27.16% for the telemetry-only controller to 25.77%. As telemetry reaches 100%, audits shut off.
5. **Safe exploration has a class trade-off.** Raising the requested routine audit rate to 35% produces a realized 23.56% audit fraction. Routine miss rises from about 21.00% to 22.46%, while critical miss falls from about 19.01% to 16.82% on the paired finite traces. This is not claimed as a universal causal effect.
6. **Faster detection is not better control by itself.** Component feedback detects the synthetic mixed drift far earlier than outcome-only feedback, but its task loss is not consistently lower.
7. **Observability cannot create diversity.** At radio correlation 0.95, duplication nearly disappears and post-drift weighted miss reaches roughly 32.6–33.1% regardless of richer component feedback.

## Scientific boundaries

- Synthetic paired potential outcomes, not an identified causal estimator or production telemetry system.
- No inverse-propensity weighting, semi-bandit regret guarantee, or selective-label correction theorem is claimed.
- Audits are limited to routine tasks by construction; this is a safety guard, not proof of safe exploration.
- Oracle probabilities are diagnostics, not a lower bound.
- Normalized credits remain accounting units, not physical energy or cost.

## Formal validation

- package/distribution/runtime: **3.5.0**;
- **252 / 252 tests passed**;
- **252 / 252 tests passed** with manual `PYTHONPATH` removed;
- six-experiment v3.5 suite completed in about **14.5 seconds**;
- editable install, import-path check, and compileall passed;
- **214 CSV + 378 PNG = 592** SHA-256-verified result artifacts;
- full acceptance completed in about **27.6 seconds** in the release environment.
