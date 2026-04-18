# SHOWREEL_LOGIC.md

# 📘 Adaptive Learning System - SHOWREEL LOGIC (2026-03-27)

---

# 🎯 今日核心進展（一句話）

系統已從「state 表徵問題」進入「probe timing 控制問題」，並透過參數化 early-probe 機制，使 AB3 在三種 prototype 上整體表現趨於穩定優勢，特別是 Prototype B 從劣勢改善為近乎持平甚至部分指標優於 AB2。

---

# 🧠 系統架構（當前版本）

三層閉環：

1. Diagnosis（RAG / mock）
   → 識別錯誤 subskill

2. Decision（PPO / AB3 policy）
   → 決定 stay / remediate / return

3. Remediation（scaffold + routing）
   → 補救 prerequisite skill 並回主線

---

# 📊 State Representation 演進

## Phase 0（初始）
4 維：
- integer
- fraction
- radical
- polynomial

問題：
→ 無法區分不同 prerequisite 對 polynomial 的影響

---

## Phase 1（6 維）
拆 integer：

- int.sign_handling
- int.mul_div

問題：
→ polynomial 端仍混合（expand vs sign）

---

## Phase 2（7 維）✅

最終 state：

[
  int.sign_handling,
  int.mul_div,
  fraction,
  radical,
  polynomial_core,
  poly_sign_distribution_mastery,
  poly_expand_binomial_mastery
]

效果：
→ 解決 prerequisite 與主線 skill 的 aliasing 問題

---

# ⚙️ Effective Ability 設計

採用 prerequisite-aware mapping：

- poly.sign_distribution
  ← poly_sign_distribution_mastery + int.sign_handling

- poly.expand_binomial
  ← poly_expand_binomial_mastery + int.mul_div

👉 不再共用 polynomial 狀態

---

# 🔁 Learning Update 設計

## 主更新（direct update）
- int.sign → 更新 int.sign_handling
- int.mul_div → 更新 int.mul_div
- poly.sign → 更新 poly_sign_distribution_mastery
- poly.expand → 更新 poly_expand_binomial_mastery

## transfer（小幅）
- int.sign → poly_sign_distribution_mastery
- int.mul_div → poly_expand_binomial_mastery

---

# 🚨 Bottleneck 演進

## 原本問題
AB3 未全面勝過 AB2

原因：
- subskill routing 已細
- 但 state 太粗 → credit assignment 被稀釋

---

## 修正 1（7D state）
結果：
- Prototype A：改善
- Prototype C：改善
- Prototype B：仍未翻盤

👉 bottleneck 移轉

---

## 🚨 新 bottleneck（關鍵）

👉 **probe timing rigidity**

問題：
- return timing 固定（step / threshold）
- 無法反映學生動態學習進度

特別影響：
- Prototype B（弱起點 / 不均衡）

---

# 🔧 今日關鍵修改（核心）

## ✅ AB3 probe timing 改為動態 gating

新增三個參數：

- min_remediation_steps
- recent_correct_streak_threshold
- mastery_growth_delta_threshold

---

## 🎯 Early Probe 條件

允許提早 return 當：

- remediation_steps ≥ min_steps
- recent_correct_streak ≥ threshold
- mastery_delta ≥ threshold

---

## ⚠️ 保留：

- 原本 fallback probe
- readiness 檢查
- AB1 / AB2 完全不動

---

# 🧪 Parameter Sweep（今日完成）

搜尋空間：

- min_steps ∈ {1,2,3}
- streak ∈ {1,2,3}
- delta ∈ {0.00,0.01,0.02}

共 27 組

---

# 🏆 最佳參數（Prototype B 為主）

- min_remediation_steps = 1
- recent_correct_streak_threshold = 2
- mastery_growth_delta_threshold = 0.00

---

# 📊 實驗結果（關鍵）

## Prototype A
- success：持平
- steps：下降
- gain：上升

👉 穩定改善

---

## Prototype B（最重要）

AB2：
- success = 0.56
- steps = 25.61
- gain = 0.3458

AB3（最佳參數）：
- success = 0.61 ↑
- steps = 26.06（+0.45）
- gain = 0.3506 ↑

👉 關鍵結論：

- 成功率 ↑
- 學習增益 ↑
- steps 僅微幅增加

---

## Prototype C
- success ↑
- gain ↑
- steps 略增加

👉 偏保守策略（穩定但略犧牲效率）

---

# 🎯 關鍵研究結論

1. subskill-level state disentanglement 是必要條件
2. timing control 是下一層關鍵瓶頸
3. early probe 機制可顯著改善 weak-start learner（Prototype B）
4. AB3 優勢已從「被壓制」轉為「可觀察」

---

# 🧠 最重要 insight

👉 學習效果 ≠ mastery 靜態值  
👉 更重要的是「recent correctness（行為）」  

---

# ⚖️ Trade-off

AB3 現在呈現：

- 更高 success
- 更高 gain
- slightly higher steps

👉 可解釋為：

**用極小步數成本，換取更高學習成功率**

---

# 🚀 下一步（已規劃）

## 不再改架構，轉為收斂

1. 固定最佳參數（作為 v4）
2. 重跑正式結果
3. 產出圖表：
   - AB2 vs AB3（A/B/C）
   - Prototype B timing heatmap

---

# 🧾 論文可用結論句

在完成 subskill-level state disentanglement 與 probe timing 參數化後，AB3 在三種 prototype 上皆展現較穩定之優勢。其中 Prototype B 由原先落後於 AB2，改善為成功率與 polynomial gain 皆優於 AB2，顯示弱起點學生之瓶頸主要來自補救後回主線時機過於僵化。

---

# 🧠 最終一句（SHOWREEL）

👉 我們現在不是模型不夠強  
👉 而是已經開始優化「學習過程的時間控制」


最後更新：2026-03-26  
專案路徑：`D:\Python\Mathproject`

---

## 1. 專案現況總覽

本專案目前以 `adaptive_summative` 為核心，已完成以下主軸：

- Adaptive 診斷流程（submit_and_get_next）
- RAG × PPO 跨技能補救（MVP）
- Routing state / timeline / summary 可觀測性
- RAG diagnosis mapping layer
- PPO findings mapping layer
- 兩個 mapping layer 的 YAML 外部化設定

---

## 2. 今日重點完成事項（完整）

### 2.1 Routing 防呆測試（4 支）

已補上並通過：

1. `test_no_cross_skill_when_trigger_not_met`  
2. `test_remediation_lock_blocks_extra_routing`  
3. `test_forced_return_at_lock_max_steps`  
4. `test_bridge_state_clears_after_completion`

重點：驗證 trigger、lock、forced return、bridge completion 全鏈路行為。

### 2.2 Session-level routing summary

已在 `session_engine.py` 增加 session 級彙總，並在 response / debug 可讀：

- `total_routing_decisions`
- `ppo_routing_decisions`
- `fallback_routing_decisions`
- `remediation_entries`
- `successful_returns`
- `bridge_completions`
- `ppo_usage_rate`
- `return_success_rate`

### 2.3 單次作答軌跡（routing_timeline）JSON 匯出

每一步至少記錄：

- `step`
- `current_skill`
- `selected_agent_skill`
- `is_correct`
- `fail_streak`
- `frustration`
- `cross_skill_trigger`
- `allowed_actions`
- `ppo_action`
- `decision_source`
- `in_remediation`
- `remediation_step_count`
- `bridge_active`
- `final_route_reward`

### 2.4 Timeline summary helper

已新增 `summarize_routing_timeline(timeline) -> dict`，輸出：

- `total_steps`
- `unique_skills_visited`
- `remediation_entered`
- `remediation_count`
- `return_count`
- `bridge_count`
- `final_skill`
- `ppo_decision_count`
- `fallback_decision_count`
- `total_route_reward`
- `avg_route_reward`
- `first_remediation_step`
- `first_return_step`
- `first_bridge_step`

### 2.5 RAG diagnosis mapping layer（MVP）

新增模組：`core/adaptive/rag_diagnosis_mapping.py`  
已支援 concept 對應：

- `negative_sign_handling -> integer_arithmetic / signed_arithmetic`
- `division_misconception -> integer_arithmetic / division`
- `basic_arithmetic_instability -> integer_arithmetic / basic_operations`

保留欄位：`route_type`, `retrieval_confidence`, `top_concept`。

### 2.6 PPO policy findings integration layer（MVP）

新增模組：`core/adaptive/policy_findings_mapping.py`  
集中管理三類 hints：

- trigger hints（cross-skill 觸發傾向）
- reward hints（現有 reward components 的輕量微調）
- action prior hints（stay/remediate/return 傾向）

重點：不改 PPO model / training，只做 controller/routing 可選擇接入。

### 2.7 YAML 外部化設定（完成）

新增：

- `configs/rag_diagnosis_mapping.yaml`
- `configs/policy_findings_mapping.yaml`

已完成：

- config 不存在時 fallback default
- 部分欄位缺失時 default merge
- 不 crash

---

## 3. 本次主要修改檔案

### 核心程式

- `core/adaptive/session_engine.py`
- `core/adaptive/routing.py`
- `core/adaptive/rag_diagnosis_mapping.py`（新增）
- `core/adaptive/policy_findings_mapping.py`（新增）

### 設定檔

- `configs/rag_diagnosis_mapping.yaml`（新增）
- `configs/policy_findings_mapping.yaml`（新增）

### 測試

- `tests/test_adaptive_m2_api.py`（更新）
- `tests/test_rag_diagnosis_mapping.py`（更新）
- `tests/test_policy_findings_mapping.py`（更新）
- `tests/test_mapping_yaml_config.py`（新增）

---

## 4. 測試結果（最新）

已執行並通過：

- `pytest -q tests/test_adaptive_m2_api.py` -> `14 passed`
- `pytest -q tests/test_policy_findings_mapping.py tests/test_adaptive_m2_api.py` -> `16 passed`
- `pytest -q tests/test_mapping_yaml_config.py tests/test_rag_diagnosis_mapping.py tests/test_policy_findings_mapping.py tests/test_adaptive_m2_api.py` -> `23 passed`

---

## 5. Config 欄位說明

### 5.1 `configs/rag_diagnosis_mapping.yaml`

- `concept_to_prereq.<concept>.suggested_prereq_skill`
- `concept_to_prereq.<concept>.suggested_prereq_subskill`
- `concept_to_prereq.<concept>.concept_weight`
- `scoring.base`
- `scoring.retrieval_weight`
- `scoring.concept_weight`
- `scoring.unknown_concept_weight`

### 5.2 `configs/policy_findings_mapping.yaml`

- `trigger_hints.fail_streak_cross_skill_threshold`
- `trigger_hints.frustration_cross_skill_threshold`
- `trigger_hints.same_skill_cross_skill_threshold`
- `reward_hints.same_skill_streak_penalty_start`
- `reward_hints.stagnation_penalty_scale`
- `reward_hints.frustration_recovery_bonus_threshold`
- `reward_hints.frustration_recovery_bonus`
- `action_prior_hints.frustration_remediate_threshold`
- `action_prior_hints.remediate_bias`
- `action_prior_hints.stay_bias`
- `action_prior_hints.return_bias`

---

## 6. 可安全調整的參數（不動訓練）

可直接在 YAML 調整（不改 PPO training）：

- cross-skill trigger 門檻
- stagnation/recovery 的 bonus/penalty 係數
- action prior bias
- concept weight / diagnosis scoring 權重

---

## 7. 環境變數（可選）

- `ADAPTIVE_ENABLE_POLICY_FINDINGS=1`
- `ADAPTIVE_ROUTING_SUMMARY_LOG=1`
- `ADAPTIVE_RAG_DIAGNOSIS_MAPPING_CONFIG=<path>`
- `ADAPTIVE_POLICY_FINDINGS_MAPPING_CONFIG=<path>`

---

## 8. 回家接續工作建議（Next）

1. 用真實學生資料校準 YAML 門檻（目前仍是 MVP 係數）。  
2. 將 `routing_timeline_summary` 轉成前端圖表（session 報告卡）。  
3. 補「錯誤概念辨識品質」測試（精準率、過度補救率）。  
4. 建立 findings 版本控管（v1 / v1.1）與論文附錄對照表。  
5. 擴充 RAG concept mapping（依你們論文章節與知識圖譜節點）。  

---

## 9. 快速交接指令

```powershell
cd D:\Python\Mathproject
venv\Scripts\activate
python app.py
```

測試：

```powershell
pytest -q tests/test_mapping_yaml_config.py tests/test_rag_diagnosis_mapping.py tests/test_policy_findings_mapping.py tests/test_adaptive_m2_api.py
```

