# Experiment 1 Summary Table (MAX_STEPS=40)

| Strategy | Student Level | Success(達標A) Rate% | Avg Steps | Avg Final Mastery | Avg Unnecessary Remediations |
|---|---|---:|---:|---:|---:|
| Baseline | Careless (B+,B++) | 96.0% | 18.4 | 0.806 | 0.00 |
| Rule-Based | Careless (B+,B++) | 99.0% | 16.9 | 0.807 | 1.75 |
| Adaptive (Ours) | Careless (B+,B++) | 100.0% | 13.2 | 0.807 | 0.52 |
| Baseline | Average (B) | 64.0% | 32.4 | 0.794 | 0.00 |
| Rule-Based | Average (B) | 88.0% | 29.8 | 0.803 | 0.58 |
| Adaptive (Ours) | Average (B) | 98.0% | 24.1 | 0.806 | 0.15 |
| Baseline | Weak (C) | 3.0% | 40.0 | 0.574 | 0.00 |
| Rule-Based | Weak (C) | 0.0% | 40.0 | 0.603 | 0.00 |
| Adaptive (Ours) | Weak (C) | 9.0% | 39.5 | 0.539 | 0.00 |

結論：MAX_STEPS=40 作為主展示設定，在公平性、現實性與策略可分性間較平衡。
在此設定下 Adaptive (Ours) 仍為最佳策略；Average (B) 為核心鑑別族群。
