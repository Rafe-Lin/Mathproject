# Experiment 2 (AB3 Student-Type Analysis)

## Fixed Setting
- MAX_STEPS = 40
- Strategy = AB3 only
- Student groups: 拔尖組 / 固本組 / 減C組

## Core Findings
- Adaptive uses different paths for different groups (mechanism analysis, not strategy re-ranking).
- Average (固本組) is the main beneficiary under MAX_STEPS = 40.
- Weak (減C組) is helped, but not fully rescued to A within 40 steps.
- 在固定 40 steps 的限制下，Adaptive 並非單純改變比例，而是重新分配有限學習資源；固本組從這種資源配置中獲益最大，而減C組則因補救成本過高，即使有進步仍難以達到 A 水準。

## Figures
- experiment2_time_budget_by_student_type.png
- experiment2_adaptive_gain_by_student_type.png
- experiment2_learning_path_diagram.png (schematic)
