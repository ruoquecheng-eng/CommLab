# Methodological Inspirations for v3.7

v3.7 borrows problem structure, not theorem-level guarantees, from several primary research lines.

- Sondhi, Arbour, and Dimmery, **Balanced Off-Policy Evaluation in General Action Spaces**, motivates balancing observed covariates rather than relying only on volatile inverse weights: <https://proceedings.mlr.press/v108/sondhi20a/sondhi20a.pdf>
- Kallus et al., **Confounding-Robust Policy Evaluation in Infinite-Horizon Reinforcement Learning**, illustrates distributionally robust evaluation under unobserved confounding: <https://proceedings.mlr.press/v162/kallus22a/kallus22a.pdf>
- Kallus and Zhou, **Confounding-Robust Policy Improvement**, motivates marginal odds-ratio sensitivity and baseline-aware improvement: <https://arxiv.org/pdf/1805.08593>
- Xu et al., **Instrumental Variable Value Iteration for Causal Offline Reinforcement Learning**, shows that identification with unobserved confounding requires additional structure such as valid instruments; CommLab v3.7 does not assume one: <https://proceedings.mlr.press/v202/xu23x/xu23x.pdf>
- Ishikawa and He, **Kernel Conditional Moment Test for Confounded Off-Policy Evaluation**, motivates diagnosing whether observed conditional moments remain compatible with a policy model: <https://proceedings.mlr.press/v206/ishikawa23a/ishikawa23a.pdf>
- Zhao et al., **Positivity-free Policy Learning with Observational Data**, motivates treating positivity as an identification boundary instead of repairing unsupported actions numerically: <https://proceedings.mlr.press/v238/zhao24a/zhao24a.pdf>
- Liu et al., **Off-Policy Evaluation in Nonstationary Environments**, motivates separating current-policy value from a historical-mixture estimand under logging drift: <https://proceedings.mlr.press/v206/liu23d/liu23d.pdf>

CommLab remains a transparent NumPy simulator. It does not implement the cited papers' full estimators, assumptions, asymptotic theory, or guarantees. The citations explain why the new failure axes matter and where stronger future methods would need to go.
