# CommLab v2.1 Release Notes

v2.1 extends the v2.0 Wireless Edge Intelligence branch from **aggregation mechanics** to **selection bias, access uncertainty, task conflict, and CSI uncertainty**.

## New modules

- `computation/federated_selection.py`
  - two-group non-IID federated regression with channel/data correlation;
  - random, strongest-channel, participation-age, and gradient×channel selection;
  - participation Jain fairness, group-loss gap, and selected-link quality.
- `computation/random_access_fl.py`
  - ALOHA / graph-IRSA client-update delivery;
  - decoded-client fraction, empty-round probability, learning loss, and modeled channel-use accounting.
- `computation/robust_aircomp.py`
  - uncertainty-sampled finite-bit RIS-AirComp phase design;
  - heterogeneous-CSI Cell-Free AirComp candidate search;
  - lower-confidence-bound receive combining for tail-risk studies.
- `computation/multitask_semantic.py`
  - controlled two-task Gaussian source;
  - raw features, task-specific sufficient statistics, shared rank-1 and rank-2 semantic representations.

## New experiments

- `v21_non_iid_client_selection.py`
- `v21_random_access_federated.py`
- `v21_robust_aircomp_uncertainty.py`
- `v21_multitask_semantic.py`

## Selected results

### Non-IID FL client-selection bias

With a 12 dB long-term channel disparity correlated with two different local-data groups:

- random participation: final objective about **0.257**, Jain participation fairness about **0.989**;
- strongest-channel participation: final objective about **0.464**, Jain fairness about **0.515**, with about **98.3%** of selections going to the strong-channel group;
- participation-age/channel selection: final objective about **0.281**, Jain fairness about **0.886**.

The experiment deliberately shows that maximizing instantaneous wireless quality can bias the learning objective under non-IID data.

### Random access controls federated participation

For 20 clients with 80% activity and the tested `{2:.50,3:.28,8:.22}` IRSA repetition law:

- a severely overloaded 8-slot frame yields no decoded IRSA updates in the tested trace;
- by 20 slots, IRSA decodes about **52%** of active clients;
- by 24 slots, about **87%** are decoded.

The convex FL toy problem remains tolerant to substantial random subsampling until empty-round probability becomes dominant. The result is intentionally a protocol/load study, not a claim that IRSA universally beats ALOHA.

### RIS-AirComp under CSI uncertainty

The uncertainty-sampled RIS heuristic improves the true weakest-device gain over the naive point-estimate max-min design in the moderate uncertainty region of the tested Monte Carlo. At relative CSI error `0.2`, mean weakest gain is roughly **0.287** versus **0.267**; at `0.3`, roughly **0.271** versus **0.236**. At very high uncertainty the lower tail can still deteriorate, so robustness is not monotonic or guaranteed.

### Cell-Free AirComp tail-risk control

With heterogeneous AP CSI quality, the lower-confidence-bound combiner is designed for tail risk rather than median performance. At the largest tested AP error `0.5`, p90 aggregation MSE improves from about **1.35e-3** to **1.00e-3**, while smaller-error regimes can show negligible or negative median changes.

### Multi-task task-oriented communication

At 10 dB, when two task-relevant directions are aligned, one shared semantic scalar retains about **90.5%** mean task accuracy. At 90 degrees separation the same rank-1 representation falls to about **70.0%**, while a rank-2 shared subspace remains around **90.1%** using only two channel uses instead of 16 raw-feature uses.

This exposes a concrete semantic-sharing limit: a representation that is sufficient for one task need not be sufficient for multiple conflicting tasks.

## Dashboard

New interactive labs:

- Non-IID FL Client Selection
- Random-Access FL
- Robust RIS AirComp
- Cell-Free AirComp CSI Risk
- Multi-Task Semantic

## Validation

The release is validated with the full historical regression suite plus v2.1-specific tests and deterministic experiment scripts. See `docs/reproducibility_v2.1.md`.
