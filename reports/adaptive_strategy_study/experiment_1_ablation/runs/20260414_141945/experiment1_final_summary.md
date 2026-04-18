# Experiment 1 Final Summary

## Student Group Definition
- Careless (B+,B++): Push near-threshold learners across the mastery boundary
- Average (B): Stabilize and strengthen core understanding
- Weak (C): Lift foundational skills through remediation

成功指標：Success Rate 達標A (%)

## Main Setting
- MAX_STEPS = 40

## Official Figure Set
- fig_exp1_student_type_comparison_30_40_50.png (主圖, MAX_STEPS=30/40/50)
- fig_exp1_rq1_best_strategy_heatmap.png (總結圖, 3x3 全條件判讀)
- figure_caption_exp1_main.md (主圖圖說)
- figure_caption_exp1_heatmap.md (heatmap 圖說)

## Key Findings
- Experiment 1 first compares 30/40/50 step budgets.
- 30 steps is more constrained and more discriminative, but may under-allocate practice opportunities.
- 50 steps increases success for all methods and introduces stronger ceiling effects.
- 40 steps provides the best balance between fairness, realism, and strategy separability.
- Therefore, MAX_STEPS=40 is used as the main presentation setting.
- Careless (B+,B++) 的差距較小屬合理現象（高起點 ceiling effect）。
- Weak (C) 接近 floor，主要反映教學難度，不作為主比較族群。
- Average (B) 是最能區分策略優劣的核心族群。
- Adaptive (Ours): 97.0%
- Baseline: 69.0%
- Rule-Based: 80.0%

## Multi-Step Trend Focus
- 正式趨勢圖改為 Average (B) 單獨分析，避免 overall 曲線被 ceiling/floor 效果過度線性化。
- 在 30/40/50 下，Adaptive (Ours) 於 Average (B) 呈現穩定優勢。
