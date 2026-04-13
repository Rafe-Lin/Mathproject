# Experiment 3 Marginal Cost Summary

This table reports the incremental cost of improving escape-from-C performance under larger total-step budgets.

| from_max_steps | to_max_steps | from_mean_escape_rate_pct | to_mean_escape_rate_pct | delta_escape_rate_pct | from_mean_steps_used | to_mean_steps_used | delta_steps_used | marginal_cost_per_1pct_escape | interpretation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 30 | 40 | 12.80 | 29.90 | +17.10 | 29.35 | 37.36 | 8.01 | 0.468 | Highly efficient interval for reducing the C population. |
| 40 | 50 | 29.90 | 44.40 | +14.50 | 37.36 | 44.02 | 6.66 | 0.459 | Improvement continues with acceptable efficiency. |
| 50 | 60 | 44.40 | 58.30 | +13.90 | 44.02 | 47.98 | 3.96 | 0.285 | Improvement continues with acceptable efficiency. |
| 60 | 70 | 58.30 | 64.60 | +6.30 | 47.98 | 52.03 | 4.05 | 0.644 | Improvement continues with acceptable efficiency. |
