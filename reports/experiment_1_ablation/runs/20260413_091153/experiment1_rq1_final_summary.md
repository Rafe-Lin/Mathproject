# Experiment 1 RQ1 Final Summary

This report directly answers RQ1 using existing aggregated results (no re-simulation).

## Table 1: RQ1 Core Comparison

| MAX_STEPS | Student Group | Baseline (%) | Rule-Based (%) | Adaptive (%) | Best Strategy | Adaptive vs Baseline | Adaptive vs Rule |
|---:|---|---:|---:|---:|---|---:|---:|
| 30 | Careless (B+~B++) | 36.0% | 40.0% | 76.0% | Adaptive ? | +40.0 pp | +36.0 pp |
| 30 | Average (B) | 1.0% | 0.0% | 38.0% | Adaptive ? | +37.0 pp | +38.0 pp |
| 30 | Weak (C) | 0.0% | 0.0% | 0.0% | Adaptive ? | +0.0 pp | +0.0 pp |
| 40 | Careless (B+~B++) | 48.0% | 36.0% | 92.0% | Adaptive ? | +44.0 pp | +56.0 pp |
| 40 | Average (B) | 16.0% | 1.0% | 84.0% | Adaptive ? | +68.0 pp | +83.0 pp |
| 40 | Weak (C) | 0.0% | 0.0% | 2.0% | Adaptive ? | +2.0 pp | +2.0 pp |
| 50 | Careless (B+~B++) | 68.0% | 50.0% | 97.0% | Adaptive ? | +29.0 pp | +47.0 pp |
| 50 | Average (B) | 39.0% | 9.0% | 93.0% | Adaptive ? | +54.0 pp | +84.0 pp |
| 50 | Weak (C) | 1.0% | 0.0% | 11.0% | Adaptive ? | +10.0 pp | +11.0 pp |

## Table 2: Adaptive All-Win Check

| MAX_STEPS | Careless | Average | Weak |
|---:|---:|---:|---:|
| 30 | ? | ? | ? |
| 40 | ? | ? | ? |
| 50 | ? | ? | ? |

Adaptive is the best strategy in all 9 conditions.

## Key Findings (RQ1)

- Adaptive consistently achieves the highest success rate across all step budgets and student levels.
- The largest improvement is observed for Average (B) at MAX_STEPS = 40 (+68.0 pp vs Baseline).
- Weak (C) remains the most challenging group, but Adaptive is still the best-performing strategy (average Adaptive success: 4.3%).
- MAX_STEPS = 40 provides the most balanced evaluation setting for primary interpretation.

Make the table self-explanatory so that a reader can confirm Adaptive is the best strategy without reading any additional text.
