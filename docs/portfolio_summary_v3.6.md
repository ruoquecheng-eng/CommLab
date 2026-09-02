# CommLab v3.6 Portfolio Summary

v3.6 turns CommLab's v3.5 observability problem into an offline decision-evaluation problem. Historical logs now record known action propensities, enabling direct, importance-weighted, self-normalized, doubly robust, and clipped estimators to evaluate alternate resilience policies without deploying them on critical tasks.

The release's distinctive contribution is not a claim that DR solves counterfactual reliability. It makes three failure boundaries visible and testable: overlap can reduce a large log to a tiny effective sample; critical-task safety can create counterfactuals that are fundamentally unsupported; and nonstationarity can make a statistically precise full-history estimate irrelevant to the current system.

Six formal experiments, sixteen new invariant/estimator tests, a Dashboard Lab, paired synthetic traces, support warnings, and release verification make those boundaries reproducible.
