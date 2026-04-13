# Experiment 3 Weak Escape-from-C Summary

RQ3: How many additional total steps are needed for weak students to escape C (mastery >= 0.60)?

- Student group: Weak only（減C組）
- Success threshold: final mastery >= 0.60
- Policy A: total-step relaxation only (no forced intervention)
- Multi-seed summary: 10 seeds (42-51)

| max_steps | total_episodes | success_rate (%) | avg_final_mastery | avg_steps_used | avg_mastery_gain | cost_per_1pct_escape | interpretation |
|---:|---:|---:|---:|---:|---:|---:|---|
| 30 | 1000 | 12.8% | 0.438 | 29.35 | 0.136 | 2.293 | Some improvement observed, but many students remain below B threshold. |
| 40 | 1000 | 29.9% | 0.472 | 37.36 | 0.173 | 1.250 | Some improvement observed, but many students remain below B threshold. |
| 50 | 1000 | 44.4% | 0.498 | 44.02 | 0.198 | 0.991 | Some improvement observed, but many students remain below B threshold. |
| 60 | 1000 | 58.3% | 0.524 | 47.98 | 0.222 | 0.823 | Meaningful reduction of C-range population. |
| 70 | 1000 | 64.6% | 0.537 | 52.03 | 0.237 | 0.805 | Meaningful reduction of C-range population. |

## Key Message

Main interpretation should rely on multi-seed averages rather than single-run fluctuations.
Experiment 3 is a cost-effectiveness study of Adaptive support, not an A-level ranking task.
