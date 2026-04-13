# Experiment 3 Multi-Seed Summary: Escape-from-C under Total-Step Relaxation

This table reports the average escape-from-C performance of weak students across multiple random seeds under different total step budgets. Success is defined as final mastery >= 0.60.

| MAX_STEPS | Seeds | Mean Escape-from-C Rate (%) | Std | Mean Final Mastery | Mean Steps Used | Interpretation |
|---:|---:|---:|---:|---:|---:|---|
| 30 | 10 | 12.80% | 3.82% | 0.4378 | 29.35 | Low escape rate under constrained budget. |
| 40 | 10 | 29.90% | 6.50% | 0.4723 | 37.36 | Substantial improvement with moderate extra steps. |
| 50 | 10 | 44.40% | 4.54% | 0.4975 | 44.02 | Performance continues to improve, but gains become less stable. |
| 60 | 10 | 58.30% | 5.08% | 0.5236 | 47.98 | Performance improves, though cross-seed variance remains visible. |
| 70 | 10 | 64.60% | 4.74% | 0.5370 | 52.03 | Performance continues to improve, but gains become less stable. |
