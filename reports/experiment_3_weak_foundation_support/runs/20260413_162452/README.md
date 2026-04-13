# Experiment 3: Weak Escape-from-C under Adaptive (Policy A)

## Research Question
Can Adaptive help weak students escape from C to B (mastery >= 0.60)?

## Method
- Weak only
- AB3 only
- Total-step relaxation only (no forced intervention)
- MAX_STEPS sweep: 30, 40, 50, 60, 70

## Multi-seed Evaluation
Experiment 3 is now summarized with multiple random seeds to reduce single-run noise.
Main conclusion should be based on multi-seed averages, not a single run.
- Seed list: [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]

## Main Outputs
- exp3_multiseed_summary.csv
- exp3_multiseed_summary.md
- fig_exp3_escape_rate_multiseed.png
- fig_exp3_mastery_multiseed.png
- fig_exp3_cost_vs_benefit_multiseed.png

## Single-run Compatibility Artifacts
Single-run results are retained for traceability, but the main interpretation should rely on multi-seed summaries.
- weak_escape_total_step_summary.csv (compatibility schema)
- weak_escape_total_step_summary.md
- exp3_escape_from_c_summary_table.csv
- exp3_escape_from_c_summary_table.md
