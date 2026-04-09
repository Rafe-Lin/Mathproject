# Experiment 1：策略消融實驗（Strategy Ablation）

本資料夾收錄 Experiment 1 的完整輸出，核心目標是比較 `AB1_Baseline`、`AB2_RuleBased`、`AB3_PPO_Dynamic` 三種策略在不同 `MAX_STEPS` 條件下的學習成效差異。
重點觀察指標包含成功率、平均步數、不必要補救次數與最終 mastery，並提供可重現的原始與彙整資料。
初步結果顯示，動態策略（AB3_PPO_Dynamic）在多數設定下可同時提升成功率並降低不必要補救，展現較佳整體效率。

## 🔥 核心結果（論文 / 簡報用）

- `experiment1_summary_table.md`：實驗一主結果總表（跨 `MAX_STEPS × Strategy`），可直接貼入論文或簡報。
- `fig_multi_steps_success_rate.png`：比較三種策略在不同 `MAX_STEPS` 下的成功率趨勢。
- `fig_multi_steps_efficiency.png`：呈現平均步數與成功率之間的效率/權衡關係。
- `fig_ablation_strategy_breakdown.png`：同圖比較各策略的四項核心指標（Success Rate、Avg Steps、Avg Final Mastery、Avg Unnecessary Remediations）。
- `fig_ablation_by_student_type.png`：比較不同學生類型（high/mid/low）在各策略下的成功率差異。

## 📊 支援分析資料（Supporting Tables）

- `experiment1_summary_table.csv`
- `multi_steps_strategy_summary.csv`
- `multi_steps_strategy_by_type_summary.csv`
- `ablation_strategy_summary.csv`
- `ablation_strategy_by_student_type_summary.csv`

上述檔案為圖表生成與交叉驗證所使用的中間統計資料，適合做二次分析、重繪圖表與數值核對。

## ⚙️ 原始模擬輸出（Raw Simulation Outputs）

- `ablation_simulation_results_*.csv`
- `ablation_strategy_summary_steps*.csv`
- `ablation_strategy_by_student_type_summary_steps*.csv`

這些檔案保存各輪模擬（不同 `MAX_STEPS`）的詳細輸出，可用於重現實驗、追查差異來源與除錯分析。

## ▶️ 如何重現本實驗

執行以下指令即可重新產生本資料夾的主要結果與圖表：

```bash
python scripts/run_multi_steps_experiment.py
```

重現流程摘要：
- 依序執行 `MAX_STEPS = 30 / 40 / 50`。
- 產出每輪 step-suffixed 原始/中間 CSV。
- 生成 cross-step summary 表與 Experiment 1 主表。
- 自動更新核心圖表（success rate、efficiency、strategy breakdown、student-type comparison）。

---

備註：
- 本資料夾聚焦 Experiment 1（Ablation）。
- 所有統計數值來自實際模擬結果，不使用手動填值。


## 📌 實驗設定（Experiment Configuration）

- 策略（Strategies）：
  - AB1_Baseline：無診斷與補救機制
  - AB2_RuleBased：固定規則補救策略
  - AB3_PPO_Dynamic：動態決策（PPO-based）

- MAX_STEPS：
  - 30 / 40 / 50

- 評估指標（Metrics）：
  - Success Rate (%)：最終成功率
  - Avg Steps：完成任務所需平均步數
  - Avg Unnecessary Remediations：不必要補救次數
  - Avg Final Mastery：最終能力值（mastery）


