## Extended Plateau Analysis
- Why extend from 70 to 90: to test whether escape-from-C gains begin to saturate under larger total-step budgets.
- Plateau rule: interval is candidate if delta escape < 2.0 pp; plateau requires two consecutive candidate intervals.
- Main outputs:
  - exp3_extended_summary_table.csv/.md
  - exp3_delta_escape_summary.csv/.md
  - exp3_plateau_summary.csv/.md
  - fig_exp3_escape_rate_extended_multiseed.png
  - fig_exp3_cost_vs_benefit_extended_multiseed.png
  - fig_exp3_marginal_gain_extended.png
  - fig_exp3_plateau_detection.png
- One-line conclusion: No clear plateau observed up to MAX_STEPS=90

## Strategy Comparison under Fixed Budgets
- Why this view: to isolate system ability under equal resource limits rather than horizon length effects.
- Research meaning: this comparison tests which strategy is most effective at rescuing Weak (C) students under the same MAX_STEPS.
- Outputs:
  - exp3_strategy_comparison_summary.csv/.md
  - exp3_strategy_comparison_pivot.csv/.md
  - fig_exp3_strategy_comparison_escape_rate.png
  - fig_exp3_strategy_comparison_final_mastery.png
  - figure_caption_exp3_strategy_comparison.md
- One-line conclusion: Strategy effectiveness differs across fixed support budgets; therefore, system ability should be interpreted by budget-specific comparisons rather than a single universal winner.
