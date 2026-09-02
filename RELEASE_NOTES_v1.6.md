# CommLab v1.6 Release Notes

v1.6 shifts from separate uncertainty/deployment modules toward **coupled control loops** where CSI age, feedback precision, retransmission cost, sensing overhead, and infrastructure energy are accounted for in the same experiment.

## New modules

- `commlab.ris.cellfree_imperfect`
  - Gauss-Markov-style delayed CSI for direct/AP-RIS/RIS-user links;
  - independent CSI quantization versus RIS phase resolution;
  - predicted channel ensembles for sample-average RIS control;
  - stale/robust/current-CSI evaluation helper.
- `commlab.scheduling.fbl_harq_queue`
  - multi-user FIFO packet queues;
  - finite-blocklength normal-approximation packet error;
  - PF/delay-PF scheduling;
  - Chase SNR combining and optional OLLA.
- `commlab.sensing.closed_loop`
  - covariance-only sensing-on-demand loop;
  - myopic and two-step predictive resource control;
  - explicit value-of-information limitation.
- `commlab.mimo.fronthaul_energy`
  - periodic quantized CSI updates under Gauss-Markov aging;
  - fronthaul energy-per-bit abstraction;
  - AP circuit + fronthaul + transmit power accounting.

## New v1.6 experiments

1. `cellfree_ris_aged_quantized_csi.py`
2. `fbl_harq_queue_coupled.py`
3. `isac_predictive_sensing_on_demand.py`
4. `cellfree_fronthaul_energy_joint.py`

## Headline observations

- RIS control benefits strongly from moving 2-bit CSI toward 4/6-bit CSI, after which the current experiment begins to saturate.
- Sample-average "robust" RIS is not universally superior: under severe aging it can sacrifice mean rate while modestly improving the lower tail. This negative result is retained.
- Chase HARQ eliminates most packet drops in the selected short-block traffic trace, but retransmission attempts and delay remain explicit costs. OLLA can further reduce NACK while selecting a more conservative operating point.
- Two-step sensing lookahead improves over a purely myopic controller, but an offline/hindsight-tuned fixed sensing fraction can still outperform it; the two-step policy is not presented as an optimal POMDP/RL solution.
- Fronthaul-energy optimal CSI refresh depends on channel mobility. Slow channels favor longer refresh intervals; faster channels shift the optimum toward fresher CSI.
- Joint AP/CSI/update optimization produces an interior energy-efficiency optimum rather than "activate all APs and update every slot."

## Validation

- **124/124 tests passed**
- **100 CSV datasets**
- **172 figures**
- **272 result artifacts** in the v1.6 SHA-256 manifest
- package version **1.6.0**
