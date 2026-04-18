# Experiment 2 Summary

> Experiment 2 examines why AB3 works by analyzing how it allocates remediation and mainline steps across student types and how these choices shape mastery trajectories.

## 1. Experiment Goal
Experiment 2 focuses on mechanism analysis within AB3, not on re-ranking AB1/AB2/AB3. The goal is to explain why AB3 works by checking whether policy allocation differs by student type and whether those differences align with mastery dynamics.

The core question is whether AB3 adapts intervention rhythm (remediation vs mainline) per student type and whether this adaptive rhythm maps to different prerequisite/target mastery trajectories.

## 2. Experiment Hypotheses
- H1: AB3 will allocate different remediation/mainline ratios across student types.
- H2: Careless / Average / Weak will show different mastery growth trajectories under AB3.
- H3: Weak students will require more remediation and show slower target mastery growth, but stronger prerequisite growth.

## 3. Experimental Design
| Item | Value |
|---|---|
| Strategy analyzed | AB3 only |
| Student types | Careless / Average / Weak |
| Sample size per type | 100 episodes |
| Total episodes | 300 |
| MAX_STEPS (Experiment 2) | 50 |
| TARGET_MASTERY | 0.85 |
| Main output files | experiment2_student_type_summary.csv; ab3_student_type_summary.csv; ab3_student_type_detailed_summary.csv; ab3_failure_breakpoint_summary.csv; mastery_trajectory.csv; experiment2_policy_behavior_summary.png; mastery_trajectory_average_by_student_type.png; mastery_trajectory_representative_episode.png; figure captions |
| Main program path | scripts/simulate_student.py |
| experiments_overview source | Unable to recover from current outputs |

## 4. Runtime / Data Flow
The formal Experiment 2 entry is `scripts/simulate_student.py` (`main(output_mode="experiment2")`). It writes per-type behavior summaries, trajectory logs, policy behavior figure, average mastery trajectory figure, representative trajectory figure, and caption markdown files.

This summary primarily uses AB3 step-level trajectory logs (`mastery_trajectory.csv`) plus per-type summary CSVs to connect policy allocation with mastery growth patterns.

## 5. Core Results Table
| Student Type | Success Rate (%) | Avg Steps | Avg Final Mastery | Remediation Ratio | Mainline Ratio |
|---|---:|---:|---:|---:|---:|
| Careless | 97.00 | 23.69 | 0.8524 | 0.2816 | 0.7184 |
| Average | 93.00 | 35.02 | 0.8445 | 0.2493 | 0.7507 |
| Weak | 11.00 | 49.58 | 0.5689 | 0.4677 | 0.5323 |

## 6. Main Findings
- Careless and Average spend most steps on mainline (`0.7184` and `0.7507`), while Weak is lower at `0.5323`.
- Weak has the highest remediation ratio (`0.4677`), clearly above Careless (`0.2816`) and Average (`0.2493`).
- Final mastery differs strongly by type: Careless `0.8524`, Average `0.8445`, Weak `0.5689`.
- Success rate follows the same ordering: Careless `97.00%`, Average `93.00%`, Weak `11.00%`.
- Trajectory logs show Weak prerequisite growth is substantial (`+0.3222`), but target growth remains slower (`+0.2476`) than Careless (`+0.2018`) and Average (`+0.3106`).

## 7. Figure Interpretation
### Figure A: Policy Allocation by Student Type
This figure tests whether AB3 applies different policy allocation by student type.
Careless: remediation/mainline = `0.2816` / `0.7184`. Average: `0.2493` / `0.7507`. Weak: `0.4677` / `0.5323`. Weak receives much heavier remediation share, indicating explicit type-dependent intervention scheduling.

### Figure B: Average Mastery Trajectory under AB3 by Student Type
This figure tests whether differentiated allocation corresponds to different prerequisite/target trajectories.
Careless and Average show faster target mastery convergence (target end: `0.8524` and `0.8445`), while Weak remains lower (`0.5689`). Weak shows clear prerequisite rise (`0.3368` -> `0.6590`), but target rise is slower (`0.3213` -> `0.5689`). Higher mainline ratio does not directly imply highest final mastery because initial proficiency and mainline learning efficiency differ across student types.

## 8. Interpretation / Analysis
Policy allocation and final performance are not contradictory. AB3 can allocate more remediation to Weak students and still produce lower final mastery if baseline readiness is lower and target-family transfer remains slower.

Mainline ratio is not a direct proxy for outcome quality. A high mainline proportion reflects where steps are spent, not how much mastery gain each step yields. Step efficiency and precondition quality matter.

Weak students require more remediation because prerequisite consolidation is a bottleneck. The logs show meaningful prerequisite gains for Weak, but target mastery closes more slowly, which is consistent with staged learning dependencies.

The research value of AB3 in Experiment 2 is differentiated intervention scheduling, not simply maximizing or minimizing remediation globally.

## 9. Limitations
- Experiment 2 is descriptive/mechanistic, not a full causal proof.
- Results depend on simulated students rather than real classroom data.
- Mastery trajectory interpretation should distinguish allocation ratio from final outcome.

## 10. Final Conclusion
AB3 does not apply one fixed learning path. It adapts remediation/mainline allocation across Careless, Average, and Weak student types, and this differential allocation is reflected in distinct prerequisite/target mastery trajectories in the Experiment 2 outputs.

---
Data sources used in this document:
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/experiment2_student_type_summary.csv`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/ab3_student_type_summary.csv`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/ab3_student_type_detailed_summary.csv`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/ab3_failure_breakpoint_summary.csv`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/mastery_trajectory.csv`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/figure_caption_experiment2_summary.md`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/figure_caption_mastery_average.md`
- `reports/adaptive_strategy_study/experiment_2_ab3_student_types/figure_caption_mastery_episode.md`
- `scripts/simulate_student.py`
- `/mnt/data/experiments_overview.md` (Unable to recover from current outputs)