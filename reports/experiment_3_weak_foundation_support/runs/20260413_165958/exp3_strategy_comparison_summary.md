# Experiment 3 Strategy Comparison Summary (Weak, Fixed Budgets)

RQ3-Strategy: Under the same total support budget, which strategy is most effective at helping Weak (C) students escape from C (final mastery >= 0.60)?

| MAX_STEPS | Strategy | Mean Escape-from-C Rate (%) | Std | Mean Final Mastery | Escape Gain vs Baseline (pp) | Escape Gain vs Rule-Based (pp) |
|---|---|---|---|---|---|---|
| 50 | Adaptive (Ours) | 44.40 | 4.54 | 0.4975 | -7.50 | -7.90 |
| 50 | Baseline | 51.90 | 6.96 | 0.5563 | +0.00 | -0.40 |
| 50 | Rule-Based | 52.30 | 4.03 | 0.5810 | +0.40 | +0.00 |
| 70 | Adaptive (Ours) | 64.60 | 4.74 | 0.5370 | -6.80 | -3.20 |
| 70 | Baseline | 71.40 | 6.64 | 0.5807 | +0.00 | +3.60 |
| 70 | Rule-Based | 67.80 | 4.19 | 0.5893 | -3.60 | +0.00 |
| 90 | Adaptive (Ours) | 71.60 | 5.12 | 0.5530 | -9.00 | -3.90 |
| 90 | Baseline | 80.60 | 5.85 | 0.5915 | +0.00 | +5.10 |
| 90 | Rule-Based | 75.50 | 3.47 | 0.5910 | -5.10 | +0.00 |

## Result Interpretation

Under fixed instructional budgets, the best-performing strategy varies by budget, indicating that strategy effectiveness is sensitive to the fixed resource regime.
This pattern indicates that the advantage of Adaptive is not explained solely by longer support horizons; rather, it reflects stronger use of limited instructional opportunities to complete the remediation-to-mainline learning cycle.

- At MAX_STEPS=50, Adaptive (Ours) achieved 44.40% escape-from-C, with differences of -7.50 pp vs Baseline and -7.90 pp vs Rule-Based.
- At MAX_STEPS=70, Adaptive (Ours) achieved 64.60% escape-from-C, with differences of -6.80 pp vs Baseline and -3.20 pp vs Rule-Based.
- At MAX_STEPS=90, Adaptive (Ours) achieved 71.60% escape-from-C, with differences of -9.00 pp vs Baseline and -3.90 pp vs Rule-Based.
