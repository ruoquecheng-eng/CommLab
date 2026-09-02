# Portfolio Summary — CommLab v2.1

## Recommended positioning

**CommLab — Wireless Communication Systems Laboratory** is a modular Python research simulator spanning PHY, MIMO/RF, high mobility, coding/HARQ, RIS/Cell-Free, ISAC, scheduling/random access, AirComp and edge intelligence. v2.1 focuses on a systems question that is easy to explain in an interview: **the communication policy that looks best at the link layer can bias learning, starve clients, or destroy shared task utility.**

## Best v2.1 figures

1. `v21_non_iid_selection_loss.png` — strongest-channel selection hurting the non-IID global objective.
2. `v21_non_iid_selection_fairness.png` — participation fairness collapsing as channel/data correlation increases.
3. `v21_random_access_fl_decode.png` — random-access load threshold controlling which FL updates arrive.
4. `v21_robust_ris_aircomp_mean.png` / `v21_robust_ris_aircomp_tail.png` — moderate-uncertainty gains and high-uncertainty limitations of robust RIS control.
5. `v21_multitask_semantic_accuracy.png` — shared rank-1 semantic representation failing as tasks become orthogonal.
6. `v21_cellfree_aircomp_imperfect_csi.png` — CSI-risk-aware distributed aggregation tail behavior.

## CV-style bullet

Built **CommLab**, a reproducible wireless-systems research laboratory spanning OFDM/MIMO, RF/DPD, coding/HARQ, high-mobility/OTFS, RIS/Cell-Free, ISAC, random access and wireless edge intelligence; implemented controlled studies showing non-IID federated-learning client-selection bias, random-access participation thresholds, uncertainty-aware AirComp/RIS trade-offs, and multi-task semantic-representation conflict.

## Interview story

A strong v2.1 story is the non-IID client-selection experiment: two client groups have different local optima and different long-term channel quality. Selecting only the strongest wireless links dramatically improves the weakest selected channel but over-represents one data population and worsens the global model. An age-aware scheduler gives up some channel quality to recover participation fairness and learning quality. This demonstrates cross-layer reasoning rather than only algorithm implementation.

## Scope language to keep

- **controlled non-IID FL toy problem**, not production FL;
- **communication-driven selection bias**, not a universal theorem about wireless FL;
- **heuristic uncertainty-aware RIS/Cell-Free control**, not globally optimal robust beamforming;
- **analytical multi-task semantic baseline**, not state-of-the-art learned semantic communication.
