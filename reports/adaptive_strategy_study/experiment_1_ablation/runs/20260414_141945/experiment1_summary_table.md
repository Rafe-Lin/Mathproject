# Experiment 1 Summary Table (MAX_STEPS=40)

## Key Result

Adaptive (Ours) achieves the highest success rate across all tested step budgets (30, 40, 50).
Its advantage is especially clear for Average (B) students, while it also remains the best-performing strategy for Weak (C) students despite low absolute success rates.

| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Final Mastery |
|---:|---|---:|---:|---:|
| 40 | Baseline | 97.0% | 18.7 | 0.805 |
| 40 | Baseline | 69.0% | 32.4 | 0.790 |
| 40 | Baseline | 0.0% | 40.0 | 0.487 |
| 40 | Rule-Based | 98.0% | 17.0 | 0.808 |
| 40 | Rule-Based | 80.0% | 30.8 | 0.799 |
| 40 | Rule-Based | 0.0% | 40.0 | 0.535 |
| 40 | Adaptive (Ours) | 100.0% | 12.7 | 0.806 |
| 40 | Adaptive (Ours) | 97.0% | 25.1 | 0.807 |
| 40 | Adaptive (Ours) | 1.0% | 40.0 | 0.439 |

結論：MAX_STEPS=40 作為主展示設定，在公平性、現實性與策略可分性間較平衡。
在此設定下 Adaptive (Ours) 仍為最佳策略；Average (B) 為核心鑑別族群。
