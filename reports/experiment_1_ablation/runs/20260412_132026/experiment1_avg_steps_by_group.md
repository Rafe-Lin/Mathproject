# Experiment 1 Validation: Avg Steps by Student Level (MAX_STEPS=40)

| max_steps | strategy | student_group | avg_steps | Success(達標A) Rate% | n_success | n_failure |
|---:|---|---|---:|---:|---:|---:|
| 40 | Baseline | Careless (B+,B++) | 18.45 | 96.00% | 96 | 4 |
| 40 | Rule-Based | Careless (B+,B++) | 16.93 | 99.00% | 99 | 1 |
| 40 | Adaptive (Ours) | Careless (B+,B++) | 13.20 | 100.00% | 100 | 0 |
| 40 | Baseline | Average (B) | 32.39 | 64.00% | 64 | 36 |
| 40 | Rule-Based | Average (B) | 29.84 | 88.00% | 88 | 12 |
| 40 | Adaptive (Ours) | Average (B) | 24.14 | 98.00% | 98 | 2 |
| 40 | Baseline | Weak (C) | 39.99 | 3.00% | 3 | 97 |
| 40 | Rule-Based | Weak (C) | 40.00 | 0.00% | 0 | 100 |
| 40 | Adaptive (Ours) | Weak (C) | 39.48 | 9.00% | 9 | 91 |
