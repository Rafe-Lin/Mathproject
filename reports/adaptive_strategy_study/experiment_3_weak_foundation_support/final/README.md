# Experiment 3：弱基礎支持實驗（RQ3: Escape-from-C Analysis）

## 1. 實驗動機（Motivation）
Experiment 1 著重整體策略比較，Experiment 2 著重 AB3 的分群機制；但仍需回答一個更聚焦的研究問題：

> Adaptive 系統是否能有效協助低成就學生脫離 C 等級？

因此 Experiment 3 將分析對象固定為 Weak (C) 群體，並在不同 `MAX_STEPS` 預算下比較三種策略的達標能力。  
本實驗目的不是全面比較所有族群，而是檢驗在弱基礎條件下，策略是否能穩定提升「跨越 B 門檻」的機率。  

## 2. 實驗目的（Objective）
本實驗僅回答 RQ3：

- 哪個策略最能讓 Weak 學生達標 B（`final mastery >= 0.60`）
- 在步數預算從 30 到 100 時，各策略的達標趨勢如何變化

比較策略：

- Baseline
- Rule-Based
- Adaptive (Ours)

## 3. 實驗設定（Experimental Setup）

### 3.1 學生群體與策略（Student Group & Strategies）
- Student Group：`Weak (C)`（固定）
- Strategies：`AB1_Baseline` / `AB2_RuleBased` / `AB3_PPO_Dynamic`

---

### 3.2 步數預算與種子（Budget & Seeds）
- MAX_STEPS：`30, 40, 50, 60, 70, 80, 90, 100`
- Multi-seed：`42–51`（10 seeds）
- 每個 seed 與條件下皆使用相同 episode 規模進行彙整

---

### 3.3 關鍵參數（Key Parameters）
- Success 定義（Escape-from-C）：`final mastery >= 0.60`
- Reflect scale（統一設定）：
  - Careless = 0.15
  - Average = 0.10
  - Weak = 0.05

## 4. 方法（Method）
對每個 `MAX_STEPS × Strategy × Seed` 組合執行 Weak 學生模擬，並計算該條件下的 Escape-from-C Rate（%）與 Mean Final Mastery。  
接著在 seed 層級取平均，形成 budget-strategy 對應的 summary table，並繪製主圖 `fig_multi_steps_success_rate.png`。  
最終再由 summary 自動產生 best-method 摘要，以辨識整體最佳策略與對應步數預算。  

## 5. 執行方式（Execution）
```bash
python scripts/run_weak_foundation_support_strategy_comparison.py
```

## 6. 最新結果摘要（Run: 20260414_145723）
各步數預算下（Weak-only）Escape-from-C Rate 結果如下：

| MAX_STEPS | Baseline | Rule-Based | Adaptive (Ours) |
|---:|---:|---:|---:|
| 30 | 1.8% | 3.0% | 6.4% |
| 40 | 6.9% | 9.1% | 17.0% |
| 50 | 16.8% | 17.1% | 30.5% |
| 60 | 27.1% | 23.9% | 40.8% |
| 70 | 39.2% | 33.6% | 52.7% |
| 80 | 45.7% | 37.5% | 55.7% |
| 90 | 49.4% | 45.1% | 63.9% |
| 100 | 59.8% | 50.2% | 66.7% |

Best-method summary：
- Metric：Escape-from-C Rate (%)
- Best Strategy：Adaptive (Ours)
- Best MAX_STEPS：100
- Value：66.7

## 7. 結果分析（Analysis）
在所有步數預算下，Adaptive (Ours) 的 Escape-from-C Rate 皆高於 Baseline 與 Rule-Based，且優勢隨預算增加仍可維持。  
Rule-Based 在低預算區段（30–50）相對 Baseline 有小幅優勢，但在中高預算區段並未超越 Adaptive。  
Baseline 於高預算（90–100）有明顯回升，但整體仍落後 Adaptive。  
整體趨勢顯示：在弱基礎學生情境中，Adaptive 對「脫離 C 等級」具有最穩定且最強的提升效果。  

## 8. 輸出檔案（This Run）
本 run 目錄包含下列核心輸出：

1. `exp3_rq3_summary_table.csv`
2. `exp3_rq3_summary_table.md`
3. `exp3_rq3_best_method_summary.csv`
4. `exp3_rq3_best_method_summary.md`
5. `fig_multi_steps_success_rate.png`
6. `figure_caption_exp3_rq3_success.md`
7. `table_caption_exp3_rq3_summary.md`

## 9. 備註（Notes）
- Experiment 3 僅聚焦 Weak (C) 群體與 RQ3，不延伸至其他族群比較。
- 圖表樣式與輸出流程沿用既有 pipeline；本 README 只更新敘事與最新數據。
- 本實驗使用多 seed 彙整結果，降低單次隨機波動對結論的影響。
