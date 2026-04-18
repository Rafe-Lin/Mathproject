# Experiment 2：AB3 學生分群機制分析（Student-Type Mechanism Analysis）

## 1. 實驗動機（Motivation）
Experiment 1 已驗證策略層級的整體效果，但仍需要進一步回答一個關鍵問題：同一個 Adaptive 策略，是否會對不同學生群體採取不同學習路徑。  
若只看整體平均成功率，容易掩蓋模型在不同能力層的資源配置差異。  
因此 Experiment 2 固定策略為 AB3，改以學生分群為分析主軸，觀察主線學習與補救學習的步數分配與學習成果。  
本實驗重點是機制解釋（mechanism analysis），不是策略排名重跑。  

## 2. 實驗目的（Objective）
本實驗旨在分析 AB3 在三種學生群體下的路徑配置與成效差異：

- Careless (B++, B+)
- Average (B)
- Weak (C)

在固定 `MAX_STEPS = 40` 下，主要觀察指標包含：

- Success Rate（達標 A，final mastery >= 0.80）
- Avg Steps
- Avg Final Mastery
- Mainline / Remediation 步數與比例
- Avg Mastery Gain

## 3. 實驗設定（Experimental Setup）

### 3.1 策略與步數（Strategy & Budget）
- Strategy：`AB3_PPO_Dynamic`（僅 AB3）
- MAX_STEPS：`40`（固定）
- Success threshold：`0.80`

---

### 3.2 學生分群與樣本數（Student Groups & Sample Size）
- 每個 student group：100 episodes
- 共 3 組：總計 300 episodes
- 分群標籤：
  - Careless (B++, B+)
  - Average (B)
  - Weak (C)

---

### 3.3 反射參數（Reflect Scale）
本次沿用目前統一設定：

- Careless = 0.15
- Average = 0.10
- Weak = 0.05

## 4. 方法（Method）
每個 episode 在 AB3 動態路由下進行，系統每一步決定主線（mainline）或補救（remediation）路徑，並累積 mastery 變化。  
實驗結束後，以學生分群彙整每組的成功率、平均步數、最終精熟度與步數結構，藉此比較 AB3 在不同群體上的資源分配行為。  
此流程可辨識「同一策略是否因學生能力差異而出現不同路徑配置」，並連結到最終成效。  

## 5. 執行方式（Execution）
```bash
python scripts/simulate_student.py
```

> `simulate_student.py` 的 `main()` 目前固定為 Experiment 2 pipeline（output_mode = experiment2）。

## 6. 最新結果摘要（Run: 20260414_145226）
在固定 `MAX_STEPS = 40` 下，各學生群體結果如下：

| Student Group | Success Rate | Avg Steps | Avg Final Mastery | Mainline Steps | Remediation Steps | Mainline Ratio | Remediation Ratio | Avg Mastery Gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Careless (B++, B+) | 93.0% | 17.22 | 0.7998 | 11.59 | 5.63 | 0.673 | 0.327 | 0.1537 |
| Average (B) | 91.0% | 28.93 | 0.7939 | 21.49 | 7.44 | 0.743 | 0.257 | 0.2685 |
| Weak (C) | 0.0% | 40.00 | 0.4301 | 19.24 | 20.76 | 0.481 | 0.519 | 0.1242 |

## 7. 結果分析（Analysis）
結果顯示 AB3 在不同群體上呈現明確的差異化路徑配置。  
Careless 組以較少步數達到高成功率，代表主線推進效率高、補救需求低。  
Average 組在主線與補救之間維持較平衡配置，並取得最高的平均 mastery 增量（Avg Mastery Gain = 0.2685）。  
Weak 組雖投入大量補救步數（remediation ratio 0.519），但在 40 步限制內仍難達 A-level，顯示步數預算與基礎缺口仍是主要瓶頸。  
整體而言，AB3 並非固定比例分配，而是依學生狀態進行資源重配；其中 Average 組受益最明顯，Weak 組需要更長時程或額外支持機制。  

## 8. 輸出檔案（This Run）
本 run 目錄包含下列核心輸出：

1. `mastery_trajectory.csv`
2. `experiment2_episode_metrics.csv`
3. `experiment2_student_type_summary.csv`
4. `experiment2_student_type_summary.md`
5. `experiment2_time_budget_by_student_type.png`
6. `experiment2_adaptive_gain_by_student_type.png`
7. `experiment2_learning_path_diagram.png`
8. `figure_caption_experiment2_time_budget.md`
9. `figure_caption_experiment2_gain.md`
10. `figure_caption_experiment2_learning_path.md`

## 9. 備註（Notes）
- Experiment 2 是機制分析，不是策略排序比較。
- 圖表與輸出格式沿用既有 pipeline，確保可重現性與版本一致性。
- `experiment2_learning_path_diagram.png` 為 schematic 視覺化，用於機制解釋，不直接代表逐步軌跡原始數值。
