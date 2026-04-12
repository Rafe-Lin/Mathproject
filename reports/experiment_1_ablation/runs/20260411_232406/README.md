# Experiment 1 (Formal)

## Purpose
Compare Baseline, Rule-Based, and Adaptive (Ours) under one fixed setting to answer: why choose Adaptive as the core system.

## Student Levels
- Careless (B+,B++)：起始精熟度約 0.68–0.80，基礎能力較高但表現不穩定
- Average (B)：起始精熟度約 0.50–0.68，屬一般中段學生
- Weak (C)：起始精熟度約 0.20–0.50，基礎較弱，需要補救

## Fixed Settings
- 成功定義：Success(達標A) Rate%
- MAX_STEPS = 30
- N_PER_GROUP = 300
- TOTAL = 900

## Output Files
- experiment1_summary_table.csv: strategy x student-level formal table
- experiment1_summary_table.md: markdown table + one-line conclusion
- experiment1_overall_summary.csv: strategy-level summary
- experiment1_group_summary.csv: student-level summary
- fig_exp1_overall_success_rate.png: overall success-rate comparison
- fig_exp1_overall_efficiency.png: overall avg-steps comparison
- fig_exp1_student_type_comparison.png: success-rate grouped comparison
- fig_exp1_mastery_gain_comparison.png: mastery-gain grouped comparison
