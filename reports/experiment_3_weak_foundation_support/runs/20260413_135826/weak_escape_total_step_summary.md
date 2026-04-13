# Experiment 3 Weak Escape-from-C Summary

RQ3: How many additional total steps are needed for weak students to escape C (mastery >= 0.60)?

- Student group: Weak only（減C組）
- Success threshold: final mastery >= 0.60
- Policy A: total-step relaxation only (no forced intervention)

| max_steps | total_episodes | success_rate (%) | avg_final_mastery | avg_steps_used | avg_mastery_gain | cost_per_1pct_escape | interpretation |
|---:|---:|---:|---:|---:|---:|---:|---|
| 30 | 100 | 7.0% | 0.426 | 29.64 | 0.126 | 4.234 | Some improvement observed, but many students remain below B threshold. |
| 40 | 100 | 29.0% | 0.471 | 37.58 | 0.172 | 1.296 | Some improvement observed, but many students remain below B threshold. |
| 50 | 100 | 48.0% | 0.501 | 43.72 | 0.202 | 0.911 | Some improvement observed, but many students remain below B threshold. |
| 60 | 100 | 60.0% | 0.525 | 48.09 | 0.226 | 0.801 | Meaningful reduction of C-range population. |
| 70 | 100 | 56.0% | 0.519 | 53.09 | 0.215 | 0.948 | Additional steps show diminishing returns in this region. |

## Key Message

More total steps can improve weak students' escape-from-C rate, but marginal returns may decline.
Experiment 3 is a cost-effectiveness study of Adaptive support, not an A-level ranking task.
