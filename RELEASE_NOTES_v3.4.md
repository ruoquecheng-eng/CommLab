# CommLab v3.4 Release Notes

## Theme: Adaptive Risk-Control Orchestration

v3.4 closes the loop around v3.3. Migration, cross-domain replica execution, and dual-radio duplication still share a finite token bucket, but the runtime no longer relies only on a fixed point-risk threshold. Delayed revealed misses update either one global risk debt or separate routine/important/critical debts.

All v3.3 and earlier modules, tests, experiments, Dashboard Labs, CSVs, figures, and documentation are retained.

## New policies

- `point_greedy`: stale point-risk estimates and a fixed deployment threshold;
- `static_guard`: fixed conservative margin;
- `adaptive_global`: one online risk debt updated from delayed outcomes;
- `adaptive_local`: separate class targets/debts and a criticality-aware spending gate;
- `oracle`: hidden synthetic probabilities, but never realized outcomes; diagnostic only.

## Main results

1. **Drift value/cost crossover.** At drift 0.8, adaptive-local gives about 16.56% post-drift weighted miss versus 20.62% for point-greedy, while using about 0.636 versus 0.223 credits/task. With no drift, adaptive control buys only a small reliability change at much higher spend.

2. **Global averages can hide a critical class.** At a 1.0-credit budget under strong drift, localized feedback gives about 24.22% weighted miss versus 27.44% for global feedback and about 26.99% critical miss versus 33.68%. At 0.35 credits, however, both adaptive policies are worse than the more selective point policy.

3. **Adaptation gain is not monotone.** Gain 0.015 reaches about 22.91% post-drift weighted miss versus 30.17% with zero adaptation. Increasing the gain beyond that raises activity and does not monotonically improve reliability.

4. **Immediate feedback can chase noise.** In the supplied trace, feedback delay 8 is slightly better than delay 1. Long delays worsen early post-drift behavior. This is retained as a stochastic-control boundary rather than reported as “lower delay is always better.”

5. **Reliability targets can be infeasible.** A requested 5% global target causes adaptive-local to spend about 0.92 credits/task yet produces about 24.16% post-drift weighted miss, worse than looser target settings. A target is a controller input, not a guarantee.

6. **Correlation still removes diversity.** Adaptive-local shifts away from duplication as radio-path correlation rises, but post-drift weighted miss still worsens from about 17.87% at correlation 0 to 26.50% at 0.95.

## Scientific boundaries

- Synthetic dependent traces and Bernoulli outcomes, not operational telemetry.
- The online debt update is inspired by adaptive risk control but is not claimed to satisfy conformal, PAC, or chance-constraint guarantees.
- The oracle knows synthetic probabilities only; it is not an optimization lower bound.
- Normalized credits are accounting units, not joules, dollars, or CPU-seconds.
- No realized current outcome enters its own decision.
- No production MEC, 3GPP PDCP duplication, safety certification, or hardware benchmark is claimed.

## Formal validation

- package/distribution/runtime: **3.4.0**;
- **243 / 243 tests passed**;
- **243 / 243 tests passed** with manual `PYTHONPATH` removed;
- six-experiment v3.4 suite completed;
- editable install, import-path check, and compileall passed;
- **208 CSV + 366 PNG = 574** SHA-256-verified result artifacts;
- full acceptance completed in about **30.6 seconds** in the release environment.
