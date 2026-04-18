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
| 30 | Adaptive (Ours) | 62.7% | 22.0 |
| 30 | Baseline | 45.0% | 24.9 |
| 30 | Rule-Based | 45.3% | 24.3 |
| 40 | Adaptive (Ours) | 66.0% | 25.9 |
| 40 | Baseline | 55.3% | 30.4 |
| 40 | Rule-Based | 59.3% | 29.3 |
| 50 | Adaptive (Ours) | 71.0% | 29.0 |
| 50 | Baseline | 62.3% | 34.6 |
| 50 | Rule-Based | 64.7% | 33.4 |
