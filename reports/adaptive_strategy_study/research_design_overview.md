# 1. 研究背景與動機

台灣會考數學長期呈現明顯能力分層，學生在基礎概念、題型遷移與解題穩定性上存在系統性差異。相同教材與固定教學節奏，往往使高能力學生缺乏足夠挑戰、低能力學生無法及時補強，造成學習成效兩極化。

傳統教學模式以班級平均進度為主，難以即時回應個別學生在不同技能節點的落差。當學生在前置能力尚未穩定時直接進入高階內容，常導致錯誤累積與學習挫折。

- 基礎薄弱學生持續累積錯誤（形成 C）
- 中段學生缺乏整合能力（停留在 B）
- 高能力學生因粗心與策略錯誤無法穩定達 A

因此，本研究引入 Adaptive Learning System，以動態策略（何時補救、何時主線推進）對應學生當下能力狀態，評估其在不同能力群體上的整體效果、運作機制與教育價值。

## 1.1 研究問題（Research Questions）

本研究聚焦於三個核心問題：

- RQ1：在不同能力層學生下，Adaptive Learning System 是否優於傳統策略？
- RQ2：Adaptive 系統如何依學生狀態動態調整學習路徑？
- RQ3：Adaptive 系統是否能有效協助低成就學生脫離 C 等級？

本研究三個實驗分別對應上述三個問題。

---

# 2. 台灣會考數學能力分布建模

## 2.1 會考等級 × 分數 × 精熟度 × 人數比例

| 會考等級 | 數學加權分數區間 | 精熟度（Mastery） | 人數百分比 | 能力意義 |
|---|---|---|---|---|
| A++ | 93.20–100.00 | 0.90–0.96 | 6.56% | 高度精熟 |
| A+  | 85.70–93.19 | 0.85–0.90 | 6.58% | 接近完全掌握 |
| A   | 76.20–85.69 | 0.80–0.85 | 12.35% | 已達精熟 |
| B++ | 67.10–76.19 | 0.72–0.80 | 12.20% | 接近精熟 |
| B+  | 59.40–67.09 | 0.65–0.72 | 14.41% | 穩定基礎 |
| B   | 40.60–59.39 | 0.60–0.65 | 21.41% | 基本學力 |
| C   | 0.00–40.59  | 0.20–0.60 | 26.49% | 待加強 |

註：C 等級學生之 mastery 可能低於 0.20，本研究以 0.20–0.60 作為主要模擬區間。

A ≥ 0.80 → 精熟  
B = 0.60–0.80 → 基本學力  
C < 0.60 → 未達基本學力

👉 本研究：
- **Exp1：成功 = ≥ 0.80（達標A）**
- **Exp3：成功 = ≥ 0.60（脫離C）**

上述對照的設計目的，是將會考能力分級轉換為可連續建模的 mastery 空間，使模擬結果可同時具備教育解釋性與演算法可操作性。

---

## 2.2 學生分組（核心設計）

| 組別名稱 | 英文對應 | Mastery 區間 | 特徵 |
|---------|---------|-------------|------|
| 拔尖組 | Careless (B++, B+) | 0.68–0.79 | 高能力但易粗心 |
| 固本組 | Average (B) | 0.50–0.68 | 基礎穩定但整合不足 |
| 減C組 | Weak (C) | 0.20–0.50 | 基礎薄弱需補救 |

本研究所有圖表與結果皆以此三組為核心分析單位。

---

# 3. 模擬設計（Simulation & Reproducibility）

為確保可重現性與可比較性，本研究採用固定模擬設定（對齊目前程式）：

- Experiment 1（classic multi-step）：
  - N_PER_TYPE = 100
  - 每個 MAX_STEPS 設定下：3 組 × 3 策略 × 100 = 900 episodes
  - Multi-step sweep：MAX_STEPS = 30 / 40 / 50
  - 主展示設定（main presentation setting）：MAX_STEPS = 40
- 初始分布（Experiment 1 output_mode）：
  - Careless (B++, B+) → Uniform(0.68, 0.80)
  - Average (B) → Uniform(0.50, 0.68)
  - Weak (C) → Uniform(0.20, 0.50)
- Reproducibility（重現設定）：
  - 全域基準 seed 為 42
  - Exp1 multi-step 採條件化 seed：30→42、40→43、50→44
- Mastery update（精熟更新）：
  - correct → +Δ
  - incorrect → minimal
- Success criteria（成功判準）：
  - Exp1：final mastery ≥ 0.80
  - Exp3：mastery ≥ 0.60

上述設定的理由如下：第一，透過固定樣本量與步數上限，避免不同策略因資源不一致而產生比較偏差；第二，以區間初始化保留學生異質性；第三，使用分實驗門檻定義（0.80 與 0.60）對應不同研究目標（整體精熟 vs 減C成效）。  
另外，30/40/50 的多步數設計可同時觀察「受限步數」與「高步數天花板」情境，40 步在公平性、現實性與策略可分性之間較平衡，因此作為正式主敘事設定。

**程式實作目錄（與 RQ 對應）：** 本研究之模擬引擎、各實驗 runner 與共用繪圖／輸出整理程式，集中於 **`scripts/adaptive_strategy_study/`**。子目錄分工為：`exp1_effectiveness`（Exp1／RQ1）、`exp2_mechanism`（Exp2／RQ2）、`exp3_reduce_c`（Exp3／RQ3）、`common`（跨實驗繪圖與報表輸出整理）、`legacy`（已退役或延伸分析用腳本）。實驗產出之 CSV／MD／圖表寫入 **`reports/adaptive_strategy_study/`** 下對應子目錄；專案根目錄與路徑錨定（不依賴目前工作目錄）由 **`study_paths.study_reports_root()`** 與同層 **`study_paths.py`** 統一處理。

---

## Adaptive 系統定義（AB3）

本研究所使用之 Adaptive Learning System（AB3）包含三個核心模組：

1. Policy（決策）：  
   透過 PPO-like decision policy（目前以 heuristic proxy 實作）決定學習路徑（主線或補救）

2. Diagnosis（診斷）：  
   使用 RAG 機制判斷學生錯誤類型與前置技能缺口

3. Remediation（補救）：  
   根據診斷結果進行子技能補強

系統核心能力在於同時決定：
- 何時補救（timing）
- 補救什麼（routing）

---

# 4. 實驗一：為什麼選擇 Adaptive 系統

實驗一比較三種策略：Baseline、Rule-Based、Adaptive，並以以下指標進行評估：

- success rate
- avg steps
- final mastery
- unnecessary remediation

核心問題是：為什麼 Adaptive 較好。研究重點不只看最終分數，而是同時觀察達標效率與補救精準度。若策略能在較少無效補救下達到更高成功率，代表其決策具備實質效益。

目前正式流程採用「先做 30/40/50 multi-step 比較，再以 40 作為主展示設定」：  
- 30 步：較受限、策略差異通常更明顯  
- 50 步：所有方法都會上升，較易出現 ceiling effect  
- 40 步：兼顧可分性與實務合理性，作為主要比較基準

結論（帶數字）：在策略層級比較中，Adaptive 於三個步數條件皆為最高成功率，分別為 62.67%（MAX_STEPS=30）、66.00%（40）、71.00%（50）；同條件下 Baseline 為 45.00%/55.33%/62.33%，Rule-Based 為 45.33%/59.33%/64.67%。此結果顯示 Adaptive 的優勢不是單一條件偶然，而是跨步數預算的穩定領先。

---

# 5. 實驗二：Adaptive 系統的運作機制分析

## 5.1 Policy Behavior

實驗二首先檢視不同學生的補救比例（remediation ratio）與主線比例（mainline ratio）。若 Adaptive 具備真正自適應能力，三類學生應呈現不同資源分配，而非同質化處理。

本實驗主要觀察以下變數：
- remediation ratio
- mainline ratio
- mastery trajectory（per student type）

## 5.2 Mastery Trajectory

接著分析三類學生在學習過程中的 mastery trajectory，觀察前置能力與目標能力的變化速度與收斂型態。此步驟用於回答「策略差異是否真正反映到能力成長」。

## 5.3 關鍵說明（一定要寫）

平均曲線可能下降的原因：

1. 高分學生提早結束
2. 留下困難學生
3. 補救導致短期變慢

結論（帶數字）：Exp2 在固定 MAX_STEPS=40 下顯示明確分群差異：Careless 成功率 93.00%（mainline/remediation=0.673/0.327）、Average 成功率 91.00%（0.743/0.257）、Weak 成功率 0.00%（0.481/0.519）。因此曲線短期波動不能單獨解讀，必須結合分群終點指標（成功率、最終 mastery、步數配置）才能正確判斷機制效果。

此設計意義在於避免錯誤解讀：曲線短期波動不等於策略失效，需同時檢視分群終點表現與達標比例。

---

# 6. 實驗三：減C實驗（最重要）

實驗三聚焦於 Weak 學生，並以 Success（`final mastery >= 0.60`）定義是否脫離 C 區。

指標：

- 脫C率
- 最終 mastery

補充：本版 Exp3 核心輸出以「脫 C 率」與「最終 mastery」為主，不單列達標步數統計。

此實驗的核心不是少數學生衝高分，而是檢驗系統是否能有效提升低成就群體到基本學力帶。這與台灣教育現場「先降低學習落後比例」的政策與教學需求高度一致。

結論（帶數字）：以 Weak 組脫 C 指標（final mastery >= 0.60）檢視，Adaptive 在所有 MAX_STEPS（30–100）均為最高，且在 MAX_STEPS=100 時達 66.70%，高於 Baseline 的 59.80% 與 Rule-Based 的 50.20%。因此可直接支持「Adaptive 能有效降低 C 比例」。

---

# 7. 整體討論（Discussion）

Adaptive 有效的主要原因，在於能同時處理 timing 與 routing：前者決定何時補救、何時推進，後者決定補救哪一類技能與路徑。兩者共同作用，提升決策精準度。

教育意義上，該系統不只提升強者，更能實質幫助弱者。若研究僅強調高分群進步，難以回應教育公平；而本研究將減C納入核心，提供更符合教學現場需求的評估框架。

---

# 8. 結論（Conclusion）

本研究顯示，自適應學習系統不僅能提升整體學習成效，更能針對不同能力學生提供差異化學習路徑，並在降低低成就學生比例（減C）上展現實質教育價值，提供一種兼具技術與教育公平性的學習模式。

## 🔧 Mastery Update Mechanism（補救學習精熟度更新公式）

本系統在「前置技能補救階段（remediation）」中，當學生答對一題前置技能時，精熟度更新分為三層：

---

### 1️⃣ 前置技能本體更新（Target Subskill Update）

$$
\Delta_{target} = \text{BASE\_DELTA} \times \text{ZPD\_SCALE} \times \text{REMEDIATION\_BONUS} + \text{RAG\_BONUS}
$$

其中：

| 參數 | 意義 | 預設值 |
|------|------|--------|
| BASE_DELTA | 每題基礎學習增量 | 0.09 |
| ZPD_SCALE | 最近發展區調整係數 | 0.75 ~ 1.2 |
| REMEDIATION_BONUS | 補救學習加權 | 1.08 |
| RAG_BONUS | RAG 命中補強 | 0 ~ 0.02 |

👉 **典型範圍：**
$$
\Delta_{target} \approx 0.07 \sim 0.12
$$

---

### 2️⃣ 同 family 技能遷移（Intra-family Transfer）

$$
\Delta_{siblings} = \Delta_{target} \times \text{TRANSFER\_SCALE}
$$

| 參數 | 值 |
|------|----|
| TRANSFER_SCALE | 0.25 |

👉 **典型值：**
$$
\approx 0.02 \sim 0.03
$$

---

### 3️⃣ 主技能更新（Polynomial Mastery Update）

主技能不是直接加固定值，而是：

#### (A) 重新聚合（Aggregation）

$$
M_{poly}^{new} = f(\text{subskills})
$$

#### (B) 前置技能轉移 bonus

$$
\Delta_{poly\_bonus} = \alpha \cdot (1 - M_{poly})
$$

| 學生類型 | α |
|----------|---|
| Weak | 0.06 |
| Others | 0.03 |

👉 **典型範圍：**
$$
\Delta_{poly\_bonus} \approx 0.01 \sim 0.04
$$

---

### 4️⃣ 反向擴散（Reflect / Reverse Transfer）

當前置技能提升後，系統會進行「弱遷移反射」：

$$
\Delta_{other\_prereq} = \Delta_{target} \times \text{reflect\_scale}
$$

本研究設定：

| Student Type | reflect_scale |
|-------------|--------------|
| Careless | 0.15 |
| Average | 0.10 |
| Weak | 0.05 |

---

## 🧠 設計原則（理論對應）

本參數設計基於以下學習理論：

- **認知負荷理論（Cognitive Load Theory）**  
  工作記憶容量有限，初學者難以同時處理高階與底層結構。  

- **基模自動化（Schema Automation）**  
  高能力學生可直接調用長期記憶中的知識結構。  

- **證據可靠度（Knowledge Tracing / Guess-Slip）**  
  弱學生答對不等於真正掌握，需降低反向更新權重  

---

## 📌 核心結論

- 前置技能答對時，本體提升通常最大（約 0.07~0.12）。
- 主技能提升屬於「間接聚合 + bonus」機制。
- `reflect_scale` 控制的不是學習量，而是證據可信度。

👉 本模型本質為：
> **Evidence-weighted mastery update（證據加權精熟度更新）**

---

## 9. 最新數據校對與修正（2026-04-14）

以下內容依目前正式輸出檔校對（檔案位於 **`reports/adaptive_strategy_study/`**；產生程式見 **第 11 節** `scripts/adaptive_strategy_study/` 目錄）：

- Exp1：`reports/adaptive_strategy_study/experiment_1_ablation/latest/experiment1_multi_steps_overall.csv`
- Exp2：`reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/experiment2_student_type_summary.csv`
- Exp3：`reports/adaptive_strategy_study/experiment_3_weak_foundation_support/runs/20260414_145723/exp3_rq3_summary_table.csv`

### 9.1 Experiment 1（RQ1）最新整體結果

`MAX_STEPS = 30 / 40 / 50` 之策略層級成功率（達標 A）如下：

- 30 步：Baseline 45.00%、Rule-Based 45.33%、Adaptive 62.67%
- 40 步：Baseline 55.33%、Rule-Based 59.33%、Adaptive 66.00%
- 50 步：Baseline 62.33%、Rule-Based 64.67%、Adaptive 71.00%

校對結論：RQ1 主結論維持不變，Adaptive 在三個步數條件下皆為最高成功率。

### 9.2 Experiment 2（RQ2）最新分群結果（AB3，MAX_STEPS=40）

- Careless (B++, B+)：成功率 93.00%、平均步數 17.22、平均最終 mastery 0.7998
- Average (B)：成功率 91.00%、平均步數 28.93、平均最終 mastery 0.7939
- Weak (C)：成功率 0.00%、平均步數 40.00、平均最終 mastery 0.4301

路徑配置重點：

- Careless：mainline 0.6731 / remediation 0.3269
- Average：mainline 0.7428 / remediation 0.2572
- Weak：mainline 0.4810 / remediation 0.5190

校對結論：RQ2 的機制解讀維持一致，AB3 會依學生狀態重分配主線/補救資源；Weak 組在 40 步限制下仍難穩定達 A。

### 9.3 Experiment 3（RQ3）最新弱生脫 C 結果

成功定義為 `final mastery >= 0.60`，`MAX_STEPS = 30–100`。

關鍵數據：

- Adaptive 在所有步數條件下均為最高脫 C 率
- 最高值出現在 `MAX_STEPS=100`：Adaptive = 66.70%
- 對照同條件：Baseline = 59.80%、Rule-Based = 50.20%

校對結論：RQ3 主結論維持不變，Adaptive 能有效提升 Weak 學生脫離 C 等級的比例。

---

# 10. 參考文獻（References）

Sweller, J. (1988). Cognitive Load During Problem Solving: Effects on Learning. *Cognitive Science, 12*(2), 257–285.

Sweller, J., Ayres, P., & Kalyuga, S. (2011). *Cognitive Load Theory*. Springer.

Chi, M. T. H. (2006). Two Approaches to the Study of Experts’ Characteristics. In K. A. Ericsson, N. Charness, P. J. Feltovich, & R. R. Hoffman (Eds.), *The Cambridge Handbook of Expertise and Expert Performance*. Cambridge University Press.

Perkins, D. N., & Salomon, G. (1992). Transfer of Learning. In *International Encyclopedia of Education* (2nd ed.). Pergamon Press.

Corbett, A. T., & Anderson, J. R. (1995). Knowledge Tracing: Modeling the Acquisition of Procedural Knowledge. *User Modeling and User-Adapted Interaction, 4*, 253–278.

Bloom, B. S. (1968). Learning for Mastery. *Evaluation Comment, 1*(2), 1–12.

Guskey, T. R. (2007). Closing Achievement Gaps: Revisiting Benjamin S. Bloom’s “Learning for Mastery”. *Journal of Advanced Academics, 19*(1), 8–31.

---

# 11. 附錄：Experiment 1～3 相關程式清單（執行與報表）

本附錄整理目前與 Experiment 1～3 直接相關的核心程式，區分為「執行程式（Runner）」與「報表/繪圖程式（Reporting/Plotting）」。**正式原始碼**位於 **`scripts/adaptive_strategy_study/`**；**實驗輸出**統一寫入 **`reports/adaptive_strategy_study/...`**（與本附錄第 9 節所列報表路徑一致），不因腳本所在子資料夾而改變。

## 11.0 目錄架構與輔助檔案

**程式（scripts）：**

```
scripts/
└── adaptive_strategy_study/
    ├── study_paths.py          # repo 根目錄、study_reports_root()、各子套件 sys.path
    ├── exp1_effectiveness/     # Exp1：runner + Exp1 專用繪圖
    ├── exp2_mechanism/         # Exp2：核心模擬引擎 simulate_student（亦供 Exp1/3 等呼叫）
    ├── exp3_reduce_c/          # Exp3：RQ3 主流程與舊版 Weak support 流程
    ├── common/                 # 跨實驗繪圖與輸出整理／清理
    └── legacy/                 # 已退役 Exp1 stub、Exp3 延伸分析等
```

**產出（reports，與 scripts 結構對齊）：**

```
reports/
└── adaptive_strategy_study/
    ├── README.md
    ├── research_design_overview.md
    ├── experiment_1_ablation/
    ├── experiment_2_ab3_student_types/
    └── experiment_3_weak_foundation_support/
```

**向後相容（選用）：** 在 **`scripts/` 根目錄**另保留三個薄轉發腳本（`run_experiment1_multisteps.py`、`simulate_student.py`、`run_weak_foundation_support_strategy_comparison.py`），內部以 **`runpy`** 轉至上述 `adaptive_strategy_study` 內對應檔案。若文件或舊指令仍寫 `python scripts/run_experiment1_multisteps.py` 等形式，行為與直接執行新路徑相同。

## 11.1 執行程式（Runner）

| 程式路徑 | 對應實驗 | 類型 | 簡短說明 | 主要用途 |
|---|---|---|---|---|
| `scripts/adaptive_strategy_study/exp1_effectiveness/run_experiment1_multisteps.py` | Exp1 | 主執行程式 | 以 30/40/50 三組 MAX_STEPS 重跑三策略與三學生群。 | 產生 Exp1 正式多步數比較結果（CSV、MD、圖表）。 |
| `scripts/adaptive_strategy_study/exp2_mechanism/simulate_student.py` | Exp2（亦為核心模擬引擎） | 主執行程式（Exp2） | `main()` 目前固定走 Exp2（AB3、MAX_STEPS=40）流程。 | 產生 Exp2 的分群摘要、圖表與 caption。 |
| `scripts/adaptive_strategy_study/exp3_reduce_c/run_weak_foundation_support_strategy_comparison.py` | Exp3 | 主執行程式 | 針對 Weak 組跑 MAX_STEPS=30~100 的三策略比較（multi-seed）。 | 產生 Exp3（RQ3）主表、最佳法摘要與主圖。 |
| `scripts/adaptive_strategy_study/legacy/run_multi_steps_experiment.py` | Exp1 | 舊版執行程式（已退役） | 舊的 Exp1 runner，已由 `run_experiment1_multisteps.py` 取代；執行時僅印出退役訊息並結束。 | 僅供歷史追溯，不作正式結果來源。 |
| `scripts/adaptive_strategy_study/exp3_reduce_c/run_weak_foundation_support_experiment.py` | Exp3 | 舊版/延伸流程 | 早期 Weak support 分析流程（含延伸圖）。 | 非本版 RQ3 最小輸出主流程。 |
| `scripts/adaptive_strategy_study/legacy/run_weak_foundation_support_experiment_extended.py` | Exp3 | 延伸分析流程 | 針對 Exp3 的延伸區間/附加分析。 | 供擴展研究，不屬最小核心輸出。 |

## 11.2 報表與繪圖程式（Reporting / Plotting）

| 程式路徑 | 對應實驗 | 類型 | 簡短說明 | 主要用途 |
|---|---|---|---|---|
| `scripts/adaptive_strategy_study/exp1_effectiveness/plot_experiment1_multisteps.py` | Exp1 | 專用繪圖程式 | 產生 Exp1 多步數主圖、分群比較圖與圖說。 | 統一 Exp1 視覺風格與圖檔輸出。 |
| `scripts/adaptive_strategy_study/common/plot_experiment_results.py` | Exp1/Exp2/Exp3（共用） | 共用繪圖程式 | 提供通用繪圖工具與多實驗圖表函式（含 Exp3 主圖函式）。 | 供各 runner 呼叫產圖、套用一致圖表樣式。 |
| `scripts/adaptive_strategy_study/common/organize_experiment_outputs.py` | Exp1/Exp2/Exp3（共用） | 輸出整理程式 | 將不同實驗輸出同步/整理到對應報告目錄。 | 維護輸出目錄結構與交付一致性。 |
| `scripts/adaptive_strategy_study/common/cleanup_non_experiment1_outputs.py` | Exp1/Exp2（共用） | 輸出清理程式 | 清理或搬移非 Exp1 的混入輸出。 | 避免報告目錄污染與檔案混置。 |

## 11.3 建議使用順序（正式重現）

**建議（新路徑，語意最清晰）：**

1. Exp1：`python scripts/adaptive_strategy_study/exp1_effectiveness/run_experiment1_multisteps.py`
2. Exp2：`python scripts/adaptive_strategy_study/exp2_mechanism/simulate_student.py`
3. Exp3：`python scripts/adaptive_strategy_study/exp3_reduce_c/run_weak_foundation_support_strategy_comparison.py`

**相容寫法（等同轉發至上述檔案）：** `python scripts/run_experiment1_multisteps.py`、`python scripts/simulate_student.py`、`python scripts/run_weak_foundation_support_strategy_comparison.py`。

4. **路徑提醒**：舊版 Exp1 runner（`run_multi_steps_experiment.py`）請勿再依 `scripts/run_multi_steps_experiment.py` 或舊的 `scripts/temp/run_multi_steps_experiment.py` 尋找；正式位置為 **11.1** 表列之 `scripts/adaptive_strategy_study/legacy/run_multi_steps_experiment.py`，執行僅會印出退役訊息後結束。

補充：若僅需重畫圖（不重跑模擬），可改由 **11.2** 所列 `common/plot_experiment_results.py` 等模組之對應函式，讀既有 CSV 重新輸出圖檔。
