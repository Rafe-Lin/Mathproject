# Experiment 3（RQ3）結果總表

## 一、研究問題（RQ3）

**Adaptive 系統是否能有效協助低成就（Weak，C 等級）學生脫離 C 等級？**

- 評估對象：Weak (C) 學生
- 成功定義：`final mastery >= 0.60`（達標 B）
- 比較方法：Baseline / Rule-Based / Adaptive (Ours)
- 步數預算：`MAX_STEPS = 30, 40, 50, 60, 70, 80, 90, 100`

## 二、核心結果表（最新）

| MAX_STEPS | 策略 | 脫離 C 比率 Escape-from-C Rate (%) | 平均最終精熟度 Mean Final Mastery |
|---:|---|---:|---:|
| 30  | Baseline        | 1.80  | 0.4046 |
| 30  | Rule-Based      | 3.00  | 0.4725 |
| 30  | Adaptive (Ours) | 6.40  | 0.3915 |
| 40  | Baseline        | 6.90  | 0.4420 |
| 40  | Rule-Based      | 9.10  | 0.4997 |
| 40  | Adaptive (Ours) | 17.00 | 0.4242 |
| 50  | Baseline        | 16.80 | 0.4740 |
| 50  | Rule-Based      | 17.10 | 0.5207 |
| 50  | Adaptive (Ours) | 30.50 | 0.4499 |
| 60  | Baseline        | 27.10 | 0.4960 |
| 60  | Rule-Based      | 23.90 | 0.5316 |
| 60  | Adaptive (Ours) | 40.80 | 0.4722 |
| 70  | Baseline        | 39.20 | 0.5177 |
| 70  | Rule-Based      | 33.60 | 0.5432 |
| 70  | Adaptive (Ours) | 52.70 | 0.4931 |
| 80  | Baseline        | 45.70 | 0.5299 |
| 80  | Rule-Based      | 37.50 | 0.5476 |
| 80  | Adaptive (Ours) | 55.70 | 0.5037 |
| 90  | Baseline        | 49.40 | 0.5367 |
| 90  | Rule-Based      | 45.10 | 0.5544 |
| 90  | Adaptive (Ours) | 63.90 | 0.5252 |
| 100 | Baseline        | 59.80 | 0.5513 |
| 100 | Rule-Based      | 50.20 | 0.5569 |
| 100 | Adaptive (Ours) | 66.70 | 0.5275 |

## 三、表格解讀方式

- **主指標**：`Escape-from-C Rate (%)`（越高代表越多 Weak 學生成功跨過 B 門檻）。
- **輔助指標**：`Mean Final Mastery`（反映整體精熟度平均水位）。
- 回答 RQ3 時，以主指標為主要判準。

## 四、關鍵發現

1. Adaptive (Ours) 在所有 MAX_STEPS 條件下，脫 C 比率均為三策略最高。  
2. 最高脫 C 比率出現在 `MAX_STEPS = 100`：Adaptive = `66.70%`。  
3. 在中高預算區間（60–100），Adaptive 的優勢持續存在，顯示其對弱學生脫 C 具有穩定效果。  

## 五、重現流程與設定

流程：

`run_weak_foundation_support_strategy_comparison.py`  
→ 依序執行 Baseline / Rule-Based / Adaptive  
→ 針對每個 MAX_STEPS 進行 multi-seed 模擬  
→ 聚合為 Escape-from-C Rate 與 Mean Final Mastery

本版本固定設定：

- MAX_STEPS sweep：30 到 100（每 10 一級）
- Weak 成功門檻：`final mastery >= 0.60`
- reflect scale：Careless = 0.15 / Average = 0.10 / Weak = 0.05

## 六、報告用結論

依據 RQ3 主指標（Escape-from-C Rate），Adaptive 在所有資源條件下皆提供最強的弱學生脫 C 成效，可支持「Adaptive 系統能有效協助低成就學生脫離 C 等級」之結論。
