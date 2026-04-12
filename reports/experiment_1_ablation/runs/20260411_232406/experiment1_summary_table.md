# Experiment 1 Summary Table

本實驗成功指標為：Success(達標A) Rate%
學生分為三類：
- Careless (B+,B++)：起始精熟度約 0.68–0.80，基礎能力較高但表現不穩定
- Average (B)：起始精熟度約 0.50–0.68，屬一般中段學生
- Weak (C)：起始精熟度約 0.20–0.50，基礎較弱，需要補救

| Strategy | Student Level | Success(達標A) Rate% | Avg Steps | Avg Mastery Gain | Avg Unnecessary Remediations |
|---|---|---:|---:|---:|---:|
| Baseline | Careless (B+,B++) | 91.00 | 17.30 | 0.0750 | 0.00 |
| Baseline | Average (B) | 40.67 | 27.60 | 0.1999 | 0.00 |
| Baseline | Weak (C) | 0.00 | 30.00 | 0.1949 | 0.00 |
| Rule-Based | Careless (B+,B++) | 92.67 | 16.60 | 0.0756 | 1.75 |
| Rule-Based | Average (B) | 49.67 | 27.10 | 0.2051 | 0.35 |
| Rule-Based | Weak (C) | 0.00 | 30.00 | 0.2393 | 0.00 |
| Adaptive (Ours) | Careless (B+,B++) | 99.33 | 12.93 | 0.0771 | 0.50 |
| Adaptive (Ours) | Average (B) | 80.00 | 23.54 | 0.2235 | 0.08 |
| Adaptive (Ours) | Weak (C) | 0.67 | 29.99 | 0.1435 | 0.00 |

結論：在 Success(達標A) Rate% 指標下，Adaptive (Ours) 於達標率領先，且在效率或補救精準度至少一項更優。
