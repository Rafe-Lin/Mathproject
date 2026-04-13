# Experiment 2 Student-Type Summary

| student_group | student_group_zh | max_steps | total_episodes | success_rate | avg_steps | avg_final_mastery | mainline_steps_mean | remediation_steps_mean | mainline_ratio | remediation_ratio | avg_reached_mastery_step | avg_mastery_gain |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| careless | 拔尖組 | 40 | 100 | 94.0% | 16.82 | 0.801 | 11.57 | 5.25 | 0.688 | 0.312 | 15.51 | 0.149 |
| average | 固本組 | 40 | 100 | 91.0% | 29.18 | 0.799 | 21.40 | 7.78 | 0.733 | 0.267 | 28.11 | 0.274 |
| weak | 減C組 | 40 | 100 | 1.0% | 39.96 | 0.475 | 19.94 | 20.02 | 0.499 | 0.501 | 36.00 | 0.177 |

## Experiment 2 Scope

The Experiment 2 runtime path is: `scripts/simulate_student.py` -> `main(output_mode="experiment2")` -> `run_batch_experiments(strategies=["AB3_PPO_Dynamic"], student_types=["Careless","Average","Weak"])` -> `simulate_episode()`.  
This experiment is a mechanism analysis under a fixed condition, not a strategy-ranking study.

- Strategy: `AB3_PPO_Dynamic` only
- MAX_STEPS: `40` (hard cap)
- Success definition: final mastery `>= 0.80`
- Student groups: 拔尖組（Careless）, 固本組（Average）, 減C組（Weak）

## Student-Type Interpretation

- 拔尖組：Mostly stayed on mainline with minimal remediation; already near mastery.
- 固本組：Received balanced mainline and remediation support; achieved the largest overall improvement.
- 減C組：Spent significant time in remediation; improved but rarely reached stable A-level within 40 steps.

## Analysis

1. Path Allocation Difference
- AB3 does not apply one fixed path to all groups.
- 拔尖組與固本組以主線為主（mainline ratio 分別為 `0.688`、`0.733`）。
- 減C組幾乎主線/補救各半（`0.499 / 0.501`），顯示更多前置補救需求。

2. Time Budget Difference
- 拔尖組平均僅使用 `16.82` 步，且補救步數較少（`5.25`）。
- 固本組平均 `29.18` 步，在有限步數內取得平衡配置（主線 `21.40`、補救 `7.78`）。
- 減C組幾乎用滿 40 步（`39.96`），其中補救成本最高（`20.02` 步）。

3. Benefit Difference
- 固本組的 `avg_mastery_gain = 0.274` 為三組最高，是 40-step budget 下的主要受益者。
- 減C組並非沒有進步（`avg_mastery_gain = 0.177`），但成功率僅 `1.0%`，表示在 40 步限制下從 C 穩定到 A 難度仍高。
- 拔尖組成功率高（`94.0%`），但 gain 較小（`0.149`），符合高起點族群的邊際提升特性。

## Conclusion

Experiment 2 supports a clear mechanism-level conclusion:

- Adaptive（AB3）不是同一種教法套用所有學生，而是依群體差異重分配主線與補救資源。
- 固本組是固定 40 步預算下的最大受益者。
- 減C組有明顯改善，但受限於高補救成本與步數上限，仍難在 40 步內穩定達 A。

因此，Experiment 2 的重點是解釋 AB3 的資源配置機制，而非重新證明策略勝負。
