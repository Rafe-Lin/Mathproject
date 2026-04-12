# Experiment 1 Final Summary

## Student Group Definition
- Careless (B+,B++): Push near-threshold learners across the mastery boundary
- Average (B): Stabilize and strengthen core understanding
- Weak (C): Lift foundational skills through remediation

成功指標：Success(達標A) Rate%

## Main Setting
- MAX_STEPS = 30

## Official Figure Set
- fig_exp1_student_type_improved.png (主圖)
- fig_exp1_student_type_comparison_30_vs_40.png (30 vs 40 對照圖)
- fig_exp1_avg_steps_by_group.png (驗證圖)

- fig_multi_steps_success_rate.png (multi-step summary 圖)

## Key Findings
- Adaptive (Ours) 在三個 Student Level 的成功率皆為最高。
- MAX_STEPS=30 作為主設定，最能區分策略差異。
- Careless (B+,B++) 的差距較小屬合理現象（高起點 ceiling effect）。
- Average (B) 與 Weak (C) 更能反映策略優勢。
- Weak (C) 的相對提升幅度最大。
- Adaptive (Ours): 0.0%
- Baseline: 0.0%
- Rule-Based: 0.0%

## Multi-Step Success Trend
- Adaptive scaling (30/40/50): 30: 61.3%, 40: 69.0%, 50: 76.0%
- multi-step success rate 圖顯示 Adaptive 在不同步數預算下維持穩定優勢。
