# SHOWREEL_LOGIC.md

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

