# Experiment 2：AB3 學生類型行為分析

## 一、實驗目的（Purpose）

本實驗的核心研究問題為：在固定採用 AB3（RAG + PPO 動態策略）時，系統是否會對不同學生類型產生可辨識且可解釋的策略行為差異。

本研究強調自適應學習的本質在於：系統會依據學生當下狀態動態調整學習路徑，而非對所有學生套用相同教學流程。基於此，我們希望驗證兩件事：

- 不同能力層級學生（strong / medium / weak）是否呈現不同學習路徑與收斂模式。
- 補救策略是否具備個別化行為，而非僅由固定規則驅動。

---

## 二、實驗設計（Experiment Design）

本實驗使用 `simulate_student.py` 作為模擬主程式，並固定採用 AB3 策略進行 episode-based 模擬。

設計重點如下：

- 學生類型：設定多種 student type（如 strong / medium / weak），以反映不同初始能力條件。
- 初始狀態：各 student type 具有不同初始 mastery 分布與子技能剖面。
- 模擬流程：以 episode 為單位執行多步學習互動，每一步更新作答結果、路由狀態與 mastery。
- 更新機制：mastery 依答對/答錯與命中子技能進行遞增或修正，並保留補救階段訊號。
- 介入機制（高層）：
  - PPO 負責動態選題與路由決策。
  - RAG 在符合條件時提供概念層級支援，用於改善結構性卡關情境。

---

## 三、輸出資料說明（Output Files）

### 1️⃣ 主結果（Main Results）

- `experiment2_policy_behavior_summary.png`  
  回答問題：不同 student type 在 AB3 下的「策略行為分配」是否不同（如補救比例、主線比例、步數成本）。

- `mastery_trajectory_representative_episode.png`  
  回答問題：在具代表性的單一 episode 中，補救階段與目標能力成長之時序關係為何。

- `mastery_trajectory_average_by_student_type.png`  
  回答問題：不同 student type 的平均學習軌跡是否呈現系統性差異與不同收斂型態。

- `experiment2_student_type_summary.csv`  
  回答問題：各 student type 的策略行為統計（比例、步數、RAG 觸發）是否具有穩定差異。

- `ab3_student_type_summary.csv`  
  回答問題：各 student type 在 AB3 下的整體學習成效（成功率、平均步數、最終 mastery）如何比較。

---

### 2️⃣ 支援分析（Supporting Analysis）

- `ab3_student_type_detailed_summary.csv`  
  用於支撐主結論中的分群差異，補充更細緻的群組層級指標。

- `ab3_failure_breakpoint_summary.csv`  
  用於定位 weak learner 的主要卡關點（breakpoint），支撐「結構性瓶頸」判讀。

- `mastery_trajectory.csv`  
  為 step-level 核心資料來源，支撐所有行為比例與學習軌跡圖之重建與驗證。

---

### 3️⃣ 附錄資料（Appendix / Debug）

- `ab3_subskill_by_type_detailed_summary.csv`  
  提供 student type × subskill 的細部統計，用於 deeper analysis 與誤差追蹤。

- `ab3_subskill_progress_summary.csv`  
  提供子技能層級的前後測增益摘要，用於補充能力剖面變化。

- `mastery_trajectory_episode_*.png`  
  為多個 episode 的單例軌跡視覺化，主要用於 debug 與附錄展示，不作主圖依據。

---

## 四、核心觀察（Key Findings）

從本資料夾輸出可觀察到：AB3 並非對所有學生採一致路由，而是會依 student state 產生差異化決策。整體而言，strong student 在較少補救下即可快速回到主線，顯示其路徑更接近高效率收斂；medium student 通常呈現中度補救與穩定提升；weak student 則較易在特定結構性子技能形成 breakpoint，導致補救比例偏高且收斂速度較慢。

此結果支持一項重要研究判讀：AB3 的價值不僅是提高平均成績，而是能顯性化不同學生的學習動態，進而揭示哪些群體需要額外支援機制。

---

## 五、與實驗一的關係（Relation to Experiment 1）

- Experiment 1：重點在策略間比較（AB1 / AB2 / AB3），回答「哪個策略表現較佳」。
- Experiment 2：重點在 AB3 內部機制分析，回答「AB3 為何有效、對誰有效、在何處受限」。

因此，Experiment 2 的定位是解釋層分析：透過 student-type 行為與軌跡證據，補強 Experiment 1 的效能結果，使結論具備更高可解釋性與可辯護性。

---

## 六、重現方式（Reproducibility）

可透過以下指令重新產生本資料夾主要輸出：

```bash
python scripts/simulate_student.py
```

執行後將更新 AB3 student-type 相關 CSV 與圖表，並可用於後續論文圖表重繪與交叉驗證。
