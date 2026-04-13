# Experiment 1 Summary Table (MAX_STEPS=40)

## Key Result

Adaptive (Ours) achieves the highest success rate across all tested step budgets (30, 40, 50).
Its advantage is especially clear for Average (B) students, while it also remains the best-performing strategy for Weak (C) students despite low absolute success rates.

| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Final Mastery |
|---:|---|---:|---:|---:|
| 40 | Baseline | 96.0% | 18.4 | 0.806 |
| 40 | Baseline | 64.0% | 32.4 | 0.794 |
| 40 | Baseline | 3.0% | 40.0 | 0.574 |
| 40 | Rule-Based | 99.0% | 16.9 | 0.807 |
| 40 | Rule-Based | 88.0% | 29.8 | 0.803 |
| 40 | Rule-Based | 0.0% | 40.0 | 0.603 |
| 40 | Adaptive (Ours) | 100.0% | 13.2 | 0.807 |
| 40 | Adaptive (Ours) | 98.0% | 24.1 | 0.806 |
| 40 | Adaptive (Ours) | 9.0% | 39.5 | 0.539 |

結論：MAX_STEPS=40 作為主展示設定，在公平性、現實性與策略可分性間較平衡。
在此設定下 Adaptive (Ours) 仍為最佳策略；Average (B) 為核心鑑別族群。
