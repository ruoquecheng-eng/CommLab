# Methodological Inspirations for v3.5

CommLab v3.5 borrows problem structure, not algorithms or guarantees.

## Selective and one-sided labels

- De-Arteaga et al., *Learning under selective labels in the presence of expert consistency* (2018), motivates treating observed outcomes as a selected subset rather than an unbiased record: <https://arxiv.org/abs/1807.00905>
- Bechavod et al., *Individually Fair Learning with One-Sided Feedback* (ICML 2023), provides a useful formal contrast for decisions where only one side of an action reveals information: <https://proceedings.mlr.press/v202/bechavod23a/bechavod23a.pdf>

## Partial feedback and finite resources

- Sankararaman and Slivkins, *Combinatorial Semi-Bandits with Knapsacks* (2018), motivates separating component-level feedback from a shared resource budget: <https://arxiv.org/abs/1705.08110>
- Liu, Jiang, and Li, *Non-stationary Bandits with Knapsacks* (2022), motivates examining drift and resource scarcity together: <https://arxiv.org/abs/2205.12427>

## Deployment feedback loops

- Adam et al., *Error Amplification When Updating Deployed Machine Learning Models* (AISTATS 2022), motivates testing whether deployment changes the future data/feedback stream: <https://proceedings.mlr.press/v182/adam22a/adam22a.pdf>

v3.5 does not implement these papers' estimators or proofs. It uses transparent NumPy paired traces to expose analogous observability risks in cross-layer reliability orchestration.
