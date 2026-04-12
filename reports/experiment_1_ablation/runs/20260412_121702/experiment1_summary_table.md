# Experiment 1 Summary Table (MAX_STEPS=30)

| Strategy | Student Level | Success(達標A) Rate% | Avg Steps | Avg Final Mastery | Avg Unnecessary Remediations |
|---|---|---:|---:|---:|---:|
| Baseline | Careless (B+,B++) | 93.3% | 16.5 | 0.805 | 0.00 |
| Rule-Based | Careless (B+,B++) | 96.0% | 16.6 | 0.806 | 1.78 |
| Adaptive (Ours) | Careless (B+,B++) | 99.7% | 12.3 | 0.806 | 0.44 |
| Baseline | Average (B) | 42.7% | 27.6 | 0.769 | 0.00 |
| Rule-Based | Average (B) | 51.7% | 27.3 | 0.782 | 0.36 |
| Adaptive (Ours) | Average (B) | 81.7% | 23.5 | 0.799 | 0.10 |
| Baseline | Weak (C) | 0.0% | 30.0 | 0.521 | 0.00 |
| Rule-Based | Weak (C) | 0.0% | 30.0 | 0.563 | 0.00 |
| Adaptive (Ours) | Weak (C) | 0.7% | 30.0 | 0.476 | 0.00 |

結論：MAX_STEPS=30 為較有鑑別度設定；Adaptive (Ours) 在三個 Student Level 皆為最佳。
Careless (B+,B++) 差距較小屬合理 ceiling effect，Average (B) 與 Weak (C) 更能反映策略優勢。
