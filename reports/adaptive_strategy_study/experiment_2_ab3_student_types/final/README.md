# Experiment 2：AB3 學生分層機制分析（MAX_STEPS = 40）

## 1. 實驗動機（Motivation）
Experiment 1 已經回答「Adaptive 是否有效」。  
Experiment 2 的重點改為回答「Adaptive 為什麼有效、對誰最有效」：在固定步數預算下，AB3 是否會對不同學生採取不同路徑配置，並造成不同的成本與受益分布。

## 2. 實驗目的（Objective）
本實驗聚焦機制分析（mechanism analysis），固定單一策略與單一步數條件：

- Strategy：`AB3_PPO_Dynamic`（only）
- MAX_STEPS：`40`（only）
- Student Groups：拔尖組 / 固本組 / 減C組

評估重點：

- 路徑分配（mainline vs remediation）
- 時間使用（步數成本）
- 受益差異（mastery gain 與達標率）

## 3. 實驗設定（Experimental Setup）

### 3.1 固定條件
- AB3 only（不比較 AB1/AB2）
- MAX_STEPS = 40（不做 30/40/50 sweep）
- Success threshold：final mastery `>= 0.80`

### 3.2 樣本數設計（Sample Size）
- 每組學生：100 episodes
- 三組學生合計：300 episodes
- 採平衡設計，避免群體樣本數不均造成偏誤

### 3.3 隨機性設定（Reproducibility）
- 使用固定 global seed（`RANDOM_SEED = 42`）
- 本 run 輸出目錄：`runs/20260413_131235/`

## 4. 方法（Method）
模擬器於每一步記錄路徑屬性（`mainline` / `remediation`）與狀態變化，並於 episode 結束後彙整：

- `steps_taken`
- `final_mastery`
- `success`
- `mainline_steps`
- `remediation_steps`
- `reached_mastery_step`
- `total_mastery_gain`

最後按學生群體聚合，形成 `experiment2_student_type_summary.csv` 與對應圖表。

## 5. 執行方式（Execution）
```bash
python scripts/simulate_student.py
```

輸出位置：
- Run: `reports/adaptive_strategy_study/experiment_2_ab3_student_types/runs/20260413_131235/`
- Latest: `reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/`

## 6. 最新結果摘要（Run: 20260413_131235）

| 學生群體 | Success Rate | Avg Steps | Avg Final Mastery | Mainline Ratio | Remediation Ratio | Avg Mastery Gain |
|---|---:|---:|---:|---:|---:|---:|
| 拔尖組 | 94.0% | 16.82 | 0.801 | 0.688 | 0.312 | 0.149 |
| 固本組 | 91.0% | 29.18 | 0.799 | 0.733 | 0.267 | 0.274 |
| 減C組 | 1.0% | 39.96 | 0.475 | 0.499 | 0.501 | 0.177 |

## 7. 結果分析（Analysis）

1. 路徑分配差異  
- Adaptive 並未使用同一路徑教所有學生。  
- 減C組補救比例最高（`0.501`），顯示先備缺口較大；拔尖組與固本組則以主線為主。

2. 時間成本差異  
- 減C組平均步數幾乎用滿上限（`39.96`），其中補救步數高（`20.02`），代表大量資源先投入前置修補。  
- 固本組在有限步數下達到較平衡配置，形成效率與成效兼顧的典型案例。

3. 受益差異  
- 固本組 `avg_mastery_gain = 0.274` 為最高，是 40-step budget 下主要受益者。  
- 減C組雖有進步（gain `0.177`），但成功率仍低（`1.0%`），反映「有改善但 40 步不足以穩定達 A」。

## 8. 圖表輸出（This Run）
本 run 的核心圖表為：

1. `experiment2_time_budget_by_student_type.png`
2. `experiment2_adaptive_gain_by_student_type.png`
3. `experiment2_learning_path_diagram.png`（Schematic）

## 9. 結論（Conclusion）
在固定 40 steps 的限制下，Adaptive 並非單純改變比例，而是重新分配有限學習資源；固本組從這種資源配置中獲益最大，而減C組則因補救成本過高，即使有進步仍難以達到 A 水準。  

因此，Experiment 2 的定位是「機制分析」：說明 AB3 如何因材分配學習路徑，而不是重新做策略勝負比較。

## 10. 備註（Notes）
- 本實驗與 Experiment 1 輸出路徑隔離。
- Learning path diagram 為示意圖（schematic），用於可解釋性溝通，不是 raw trajectory 直接作圖。
