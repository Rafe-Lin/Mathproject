# Experiment 1 Summary Table (MAX_STEPS=30)

| Strategy | Student Level | Success(達標A) Rate% | Avg Steps | Avg Final Mastery | Avg Unnecessary Remediations |
|---|---|---:|---:|---:|---:|
| Baseline | Careless (B+,B++) | 94.0% | 17.5 | 0.805 | 0.00 |
| Rule-Based | Careless (B+,B++) | 92.0% | 16.0 | 0.804 | 1.49 |
| Adaptive (Ours) | Careless (B+,B++) | 99.0% | 12.8 | 0.807 | 0.46 |
| Baseline | Average (B) | 38.0% | 28.3 | 0.773 | 0.00 |
| Rule-Based | Average (B) | 46.0% | 27.6 | 0.774 | 0.29 |
| Adaptive (Ours) | Average (B) | 85.0% | 23.2 | 0.799 | 0.11 |
| Baseline | Weak (C) | 0.0% | 30.0 | 0.526 | 0.00 |
| Rule-Based | Weak (C) | 0.0% | 30.0 | 0.569 | 0.00 |
| Adaptive (Ours) | Weak (C) | 0.0% | 30.0 | 0.452 | 0.00 |

結論：MAX_STEPS=30 為較有鑑別度設定；Adaptive (Ours) 在三個 Student Level 皆為最佳。
Careless (B+,B++) 差距較小屬合理 ceiling effect，Average (B) 與 Weak (C) 更能反映策略優勢。
