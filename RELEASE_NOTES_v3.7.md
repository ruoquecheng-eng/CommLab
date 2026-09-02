# CommLab v3.7 Release Notes

## Theme: Propensity Uncertainty and Confounding Stress Tests

v3.7 removes v3.6's most convenient offline-evaluation assumption: that the logging propensity is known and current. It separates true synthetic propensities, nominal recorded propensities, stale metadata, in-sample estimated propensities, cross-fitted estimates, and a deliberately misspecified model. A hidden time-correlated severity variable can influence both protection and failure, creating controlled confounding that observed-feature re-fitting cannot repair.

All v3.6 and earlier modules, tests, experiments, results, Dashboard Labs, and documentation remain included.

## Main results

1. **Recorded does not mean correct.** With hidden-confounding strength 0.8, DR mean absolute error is about **0.31 percentage points** with the synthetic true propensity, **0.54** with nominal recorded metadata, **0.63** with cross-fitting, and **1.02** with stale metadata.
2. **Observable logging drift is recoverable in part.** At drift strength 1.0 without hidden confounding, stale propensity metadata has about **12.17-point propensity MAE** and **0.56-point OPE error**. The updated cross-fitted model reduces these to about **4.78** and **0.21 points**. This does not extend to an omitted common cause.
3. **Cross-fitting is not deconfounding.** At hidden-confounding strength 1.5, nominal-propensity DR error is about **0.70 points** and cross-fitted DR error about **0.92 points**, while the true-propensity diagnostic remains around **0.47 points**. Cross-fitting changes sample reuse; it cannot infer a variable that was never logged.
4. **Sensitivity coverage has a width price.** In the hidden-confounding stress test, gamma 1 has zero-width intervals and zero paired-oracle coverage. Gamma 1.25 gives about **2.87-point mean width** and full empirical paired-oracle coverage in the supplied 16 seeds; gamma 2 widens to about **9.57 points**, and gamma 10 to about **63.13 points**.
5. **Aggregate coverage is not row-wise protection.** The median maximum synthetic odds gap is about **37.1**, far above gamma 1.25 even when the aggregate interval happens to cover the paired oracle. The release reports these as different diagnostics.
6. **Cross-fitting can lose at small samples.** At 1,200 logs, cross-fitted error is about **0.73 points** versus **0.64** for the in-sample full propensity model, with a larger maximum weight. At 8,000 logs the two are nearly tied near **0.165 points**.
7. **A robust guard can become permanent fallback.** The point selector's regret rises from about **0.15** to **0.41 objective points** as hidden confounding strengthens. The sensitivity guard holds near **0.20 points** but falls back to baseline in **100%** of supplied runs. It trades adaptation for protection; it is not a universally superior selector.

## Scientific boundaries

- Synthetic binary-action contextual bandit, not production MEC telemetry.
- `recorded_true` and paired outcomes are simulation-only diagnostics.
- The odds envelope is empirical and deliberately transparent; it is not a sharp marginal-sensitivity bound, causal confidence interval, or partial-identification theorem.
- Propensity calibration against hidden synthetic truth is possible only because this is a simulator.
- Cross-fitting is tested as a nuisance-estimation discipline, not presented as a cure for overlap failure or hidden confounding.
- No instrumental variable, proximal identification, or safe-deployment guarantee is claimed.

## Formal validation

- package/distribution/runtime: **3.7.0**;
- **287 / 287 tests passed** twice, including a run with project-source `PYTHONPATH` removed;
- six-experiment v3.7 suite completed in about **17.5 seconds**;
- editable install, import-path check, and compileall passed;
- **226 CSV + 402 PNG = 628** SHA-256-verified result artifacts;
- full acceptance completed in about **31.2 seconds** in the release environment.
