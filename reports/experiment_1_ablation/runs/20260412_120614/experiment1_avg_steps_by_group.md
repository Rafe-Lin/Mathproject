# Experiment 1 Validation: Avg Steps by Student Level (MAX_STEPS=40)

| max_steps | strategy | student_group | avg_steps | Success(達標A) Rate% | n_success | n_failure |
|---:|---|---|---:|---:|---:|---:|
| 40 | Baseline | Careless (B+,B++) | 16.86 | 99.33% | 298 | 2 |
| 40 | Rule-Based | Careless (B+,B++) | 16.07 | 99.00% | 297 | 3 |
| 40 | Adaptive (Ours) | Careless (B+,B++) | 12.19 | 100.00% | 300 | 0 |
| 40 | Baseline | Average (B) | 32.21 | 71.33% | 214 | 86 |
| 40 | Rule-Based | Average (B) | 31.27 | 78.00% | 234 | 66 |
| 40 | Adaptive (Ours) | Average (B) | 24.11 | 98.00% | 294 | 6 |
| 40 | Baseline | Weak (C) | 39.92 | 1.67% | 5 | 295 |
| 40 | Rule-Based | Weak (C) | 39.95 | 1.67% | 5 | 295 |
| 40 | Adaptive (Ours) | Weak (C) | 39.67 | 8.00% | 24 | 276 |
