# CommLab v1.8 Release Notes

v1.8 focuses on **budgeted information acquisition, deadline/freshness-aware delivery, adaptive passive control, and random access**. The release deliberately keeps several non-monotonic results: more fronthaul does not need to be consumed if refresh quantization would add noise; the scheduler with the most successful transmissions can have terrible information freshness; EDF protects deadlines but may reduce spectral goodput; and ideal SIC only helps when colliding users have enough received-power separation.

## New modules

- `commlab.mimo.joint_csi_control`
  - joint AP refresh and scalar CSI-bit allocation under one hard per-slot fronthaul budget;
  - Gauss-Markov prediction plus innovation-only feedback;
  - round-robin and fixed-bit uncertainty baselines.
- `commlab.scheduling.deadline_harq`
  - finite-blocklength IR/Chase HARQ with packet deadlines;
  - PF, EDF and risk-aware scheduling;
  - explicit deadline expiration, HARQ drops, goodput and delay accounting.
- `commlab.scheduling.aoi`
  - generate-at-will status updating;
  - max-age, max-SNR and age×reliability scheduling;
  - fresh attempts versus Chase-style retransmission of an older update.
- `commlab.ris.event_triggered`
  - rate-degradation-triggered RIS refresh;
  - minimum/maximum refresh intervals;
  - passive-control overhead accounting.
- `commlab.sensing.budget_control`
  - long-term sensing budget enforced by cumulative tokens;
  - primal-dual online utility selection over sensing fraction and array aperture.
- `commlab.random_access.grant_free`
  - slotted grant-free access;
  - collision-only OMA baseline;
  - ideal power-domain SIC under heterogeneous received power.

## New v1.8 experiments

1. `joint_csi_fronthaul_control.py`
2. `deadline_harq_scheduling.py`
3. `aoi_status_updates.py`
4. `event_triggered_ris.py`
5. `budget_constrained_isac.py`
6. `grant_free_noma_random_access.py`

## Headline observations

- **Joint CSI refresh/precision control:** at temporal correlation `.98` and `96 bit/slot`, joint allocation gives mean CSI NMSE about `0.0324`, versus `0.0749` for fixed-bit uncertainty scheduling and `0.0913` for round-robin. Edge rate is about `0.916 bit/s/Hz` with the same hard budget.
- **Fixed-bit starvation under tight budgets:** with `64 bit/slot`, some user-centric APs cannot fit a 5-bit complex-CSI refresh at all, so fixed-bit policies exhibit very large AP ages. Variable-bit joint control can still refresh them at a lower precision.
- **Deadline-aware HARQ:** at load `.16/user/slot`, PF gives about `5.73%` deadline misses, EDF `1.95%`, and the risk score `2.56%`; risk scheduling has the highest goodput in that trace (`~0.950 bit/channel-use`) while EDF is the strictest deadline protector.
- **Information freshness:** max-SNR scheduling achieves almost one successful transmission per slot in the status experiment but mean AoI is about `139 slots` because weak users are starved. At rate `1 bit/use`, fresh age×reliability scheduling lowers mean AoI to about `9.90`, while Chase + max-age reaches about `5.22`.
- **Event-triggered RIS:** a 3% rate-drop trigger obtains about `3.811 bit/s/Hz` at `3.73 control bit/slot`, slightly exceeding fixed 4-slot refresh (`3.751` at `4 bit/slot`) by concentrating updates in the fast-fading segment.
- **Budget-constrained ISAC:** a 5% average sensing ceiling results in about `3.96%` actual use; the controller spends about `9.7%` during the rising-maneuver segment and below 1% in calm segments.
- **Grant-free NOMA/SIC:** at received-power spread `8 dB` and offered load about `.90 attempt/resource/slot`, collision-only access decodes about `7.40 packets/slot`, while ideal SIC decodes about `14.54`. At zero power spread the curves are identical.

## Important implementation correction

During v1.8 development, a round-robin CSI baseline was found to wrap more than once inside a slot at large budgets, allowing the same AP to consume the refresh budget twice while another AP starved. The baseline was fixed to make AP selections unique per slot, a regression test was added, and all affected results were discarded and regenerated.

## Validation

- **145/145 tests passed**
- package version **1.8.0**
- **111 CSV datasets / 194 figures / 305 hashed result artifacts**
