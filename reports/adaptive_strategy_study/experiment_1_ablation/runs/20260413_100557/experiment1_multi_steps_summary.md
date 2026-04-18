# Experiment 1 Multi-Steps Summary

## Student Group Definition

- Careless (B+,B++): Push near-threshold learners across the mastery boundary
- Average (B): Stabilize and strengthen core understanding
- Weak (C): Lift foundational skills through remediation

主要指標：Success Rate 達標A (%)

## Main Presentation Setting
- 30 steps: more constrained and more discriminative, but may under-allocate practice opportunities.
- 50 steps: increases success for all methods and introduces stronger ceiling effects.
- 40 steps: best balance between fairness, realism, and strategy separability.
- Therefore, MAX_STEPS = 40 is used as the main presentation setting.

## Condition Seed Policy
- MAX_STEPS=30 uses seed 42
- MAX_STEPS=40 uses seed 43
- MAX_STEPS=50 uses seed 44
- Sample size per (strategy x student_group x max_steps): N=100

| MAX_STEPS | Strategy | Success Rate 達標A (%) | Avg Steps |
|---:|---|---:|---:|
| 30 | Adaptive (Ours) | 61.3% | 22.0 |
| 30 | Baseline | 44.0% | 25.3 |
| 30 | Rule-Based | 46.0% | 24.6 |
| 40 | Adaptive (Ours) | 70.3% | 25.4 |
| 40 | Baseline | 54.7% | 30.2 |
| 40 | Rule-Based | 58.3% | 29.3 |
| 50 | Adaptive (Ours) | 75.3% | 28.0 |
| 50 | Baseline | 62.7% | 34.1 |
| 50 | Rule-Based | 65.7% | 32.9 |
