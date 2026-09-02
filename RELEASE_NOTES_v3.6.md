# CommLab v3.6 Release Notes

## Theme: Safe Offline Counterfactual Reliability Evaluation

v3.6 continues the v3.5 observability audit. Instead of asking only what the online controller can see, it asks whether a new protection policy can be evaluated from historical action-dependent logs without deploying it on safety-critical work.

The synthetic logger records action propensities and observed protected/unprotected outcomes. Direct Method (DM), IPS, self-normalized IPS, Doubly Robust (DR), and clipped DR are compared against paired potential outcomes that remain evaluation-only. All safe target policies always protect critical tasks. An intentionally unsafe critical probe is included solely to verify that support violations are detected.

All v3.5 and earlier modules, experiments, results, Dashboard Labs, tests, and documentation remain included.

## Main results

1. **Nominal samples are not effective support.** At a 0.5% exploration floor, maximum importance weight is about 110.8 and effective sample fraction only about 4.53%. DR mean absolute error is about 0.93 percentage points. At 10% exploration, maximum weight falls to about 6.04, effective fraction rises to 43.98%, and DR error falls to about 0.17 points.
2. **Clipping has a real bias/variance frontier.** With 1% exploration, a DR clip of 2 gives about 0.83-point MAE, 0.45-point signed bias, and 1.00-point empirical error standard deviation. A clip of 120 lowers bias to about 0.11 points but raises MAE to 1.05 and error deviation to 1.33 points.
3. **Doubly robust is not magic.** With usable overlap and strong unmodeled nonlinearity, DM error is about 0.42 points, versus about 0.31 for DR/SNIPS. Under weak overlap, DR can still be noisier than the biased direct model.
4. **A number is not identification.** A deterministic logger leaves about 27.35% of the balanced target-policy mass unsupported. IPS then underestimates weighted miss by about 3.82 points. DM and DR may output smaller numerical errors only by extrapolation; the release flags them as non-identifiable.
5. **Critical safety creates an explicit boundary.** Because critical tasks are never logged without protection, the unsafe critical probe has about 10.81% unsupported weighted mass even under otherwise randomized safe logging. No estimator is allowed to reinterpret that as identified evidence.
6. **More history can answer the wrong question.** At drift strength 2, full-history DR estimates current weighted miss near 15.87% while the current paired benchmark is about 30.26%, a 14.39-point error. Using the latest 20% lowers error to about 0.54 points; using only 10% raises it again to about 1.41 because variance returns.
7. **Conservative selection can freeze.** In the supplied approximate-interval selector, the conservative rule falls back to baseline in 100% of runs across 1,200–20,000 logged tasks. It avoids some greedy selection regret at small samples but never certifies an update. This is retained as a limitation, not called a safety guarantee.

## Scientific boundaries

- Synthetic contextual-bandit abstraction, not production MEC telemetry.
- Paired potential outcomes are simulation diagnostics, not observable deployment labels.
- The normal intervals ignore temporal dependence and are not HCOPE certificates.
- The conservative selector is a transparent heuristic, not a proven safe policy-improvement algorithm.
- Support violations are reported rather than repaired through hidden assumptions.
- Propensities are known by construction; estimated-propensity error is outside this release.

## Formal validation

- package/distribution/runtime: **3.6.0**;
- **268 / 268 tests passed**;
- **268 / 268 tests passed** with manual `PYTHONPATH` removed;
- six-experiment v3.6 suite completed in about **23.8 seconds**;
- editable install, import-path check, and compileall passed;
- **220 CSV + 390 PNG = 610** SHA-256-verified result artifacts;
- full acceptance completed in about **37.4 seconds** in the release environment.
