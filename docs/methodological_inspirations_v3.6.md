# Methodological Inspirations for v3.6

CommLab v3.6 borrows problem structure and diagnostic vocabulary, not algorithms or guarantees.

- Wang, Agarwal, and Dudík, *Optimal and Adaptive Off-policy Evaluation in Contextual Bandits* (ICML 2017), motivates explicit overlap and estimator mean-squared-error analysis: <https://proceedings.mlr.press/v70/wang17a/wang17a.pdf>
- Thomas, Theocharous, and Ghavamzadeh, *High Confidence Policy Improvement* (ICML 2015), motivates separating a numerical estimate from a policy-improvement certificate: <https://proceedings.mlr.press/v37/thomas15.pdf>
- Wan, Kveton, and Song, *Safe Exploration for Efficient Policy Evaluation and Comparison* (ICML 2022), motivates data-collection design that balances safety and evaluability: <https://proceedings.mlr.press/v162/wan22b/wan22b.pdf>
- Liu, Chandak, Thomas, and White, *Asymptotically Unbiased Off-Policy Policy Evaluation when Reusing Old Data in Nonstationary Environments* (AISTATS 2023), motivates explicitly testing stale-log reuse under drift: <https://proceedings.mlr.press/v206/liu23d/liu23d.pdf>

The v3.6 estimator formulas are transparent educational baselines. Its normal intervals, selector, temporal weighting, and synthetic protection process should not be attributed to these papers as equivalent implementations.
