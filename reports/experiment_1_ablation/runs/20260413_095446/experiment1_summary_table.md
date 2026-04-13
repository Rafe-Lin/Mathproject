# Experiment 1 Summary Table (MAX_STEPS=40)

## Key Result

Adaptive (Ours) achieves the highest success rate across all tested step budgets (30, 40, 50).
Its advantage is especially clear for Average (B) students, while it also remains the best-performing strategy for Weak (C) students despite low absolute success rates.

| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Final Mastery |
|---:|---|---:|---:|---:|
| 40 | Baseline | 98.0% | 18.1 | 0.806 |
| 40 | Baseline | 66.0% | 32.4 | 0.791 |
| 40 | Baseline | 0.0% | 40.0 | 0.569 |
| 40 | Rule-Based | 98.0% | 17.5 | 0.807 |
| 40 | Rule-Based | 77.0% | 30.5 | 0.797 |
| 40 | Rule-Based | 0.0% | 40.0 | 0.616 |
| 40 | Adaptive (Ours) | 100.0% | 12.3 | 0.806 |
| 40 | Adaptive (Ours) | 99.0% | 24.4 | 0.809 |
| 40 | Adaptive (Ours) | 12.0% | 39.4 | 0.578 |

結論：MAX_STEPS=40 作為主展示設定，在公平性、現實性與策略可分性間較平衡。
在此設定下 Adaptive (Ours) 仍為最佳策略；Average (B) 為核心鑑別族群。
