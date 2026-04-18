# 論文實作落地藍圖 v1.1

更新日期: 2026-03-25  
對應論文: 《基於人工智慧之自適應輔助學習架構探究》  
目標: 準備進入實作

---

## 1. 版本目標

`v1.1` 的目標是把系統升級到**論文對齊 PoC**：

1. 可跑「三層閉環」  
2. 可留下可分析研究軌跡  
3. 可在 demo 場景下穩定運行

不追求：

- 一次完成最終最優模型
- 一次取代整個既有 practice 路線

---

## 2. 三層架構對應實作

### 2.1 大腦層（AKT + PPO）

新增檔案：

- `core/adaptive/akt_adapter.py`
- `core/adaptive/ppo_adapter.py`
- `core/adaptive/session_engine.py`

責任：

- 接收作答結果
- 更新 Local APR
- 輸出 `ppo_strategy` + `target_family_id`

### 2.2 雙手層（微技能腳本）

新增/擴充：

- `scripts/generate_micro_skills_scripts.py`
- `core/adaptive/manifest_registry.py`
- `core/adaptive/schema.py`

責任：

- 離線生成腳本
- 註冊 manifest
- 在線腳本執行與 JSON 驗證

### 2.3 嘴巴層（Hybrid RAG）

新增：

- `core/adaptive/rag_hint_engine.py`

責任：

- 根據 `subskill_nodes` 做三層檢索
- 回傳 `hint_html`

---

## 3. 資料層設計

### 3.1 新表：`adaptive_learning_logs`

必要欄位：

- `log_id`
- `student_id`
- `session_id`
- `step_number`
- `target_family_id`
- `target_subskills`
- `is_correct`
- `current_apr`
- `ppo_strategy`
- `frustration_index`
- `execution_latency`

可選欄位（建議）：

- `unit_id`
- `hint_triggered`
- `fallback_used`
- `error_code`
- `question_payload_json`

### 3.2 Registry：`skill_manifest.json`

必要欄位：

- `family_id`
- `script_path`
- `version`
- `subskill_nodes`
- `generated_at`
- `model_name`
- `healer_applied`

---

## 4. API 契約（v1.1）

### 4.1 `POST /api/adaptive/submit_and_get_next`

request:

- `student_id`
- `session_id`
- `step_number`
- `is_correct`
- `last_family_id`
- `last_subskills`

response:

- `current_apr`
- `ppo_strategy`
- `frustration_index`
- `target_family_id`
- `target_subskills`
- `new_question_data`
- `execution_latency`

### 4.2 `GET /api/adaptive/rag_hint`

query:

- `session_id`
- `subskill_nodes` (array/stringified array)

response:

- `hint_html`
- `sources` (optional)

---

## 5. 前端頁面（adaptive_practice v2）

目標頁面：

- `templates/adaptive_practice.html`（原檔升級）或
- `templates/adaptive_practice_v2.html`（並行開發）

必備元件：

1. Mastery Trajectory 圖（Y 軸 Local APR）
2. 達標線（0.65）
3. 策略標記（`ppo_strategy == 3` 顯示 Review 介入）
4. 即時題目區（MathJax）
5. Auto-Hint 面板（Review 觸發）

---

## 6. 與現況差距（必修）

目前系統已有：

- `/adaptive_practice`
- `/get_adaptive_question`
- `/check_answer`
- `student_abilities`
- `adaptive_engine.py`（rule-based）

尚缺：

- AKT/PPO 真正決策流
- family/subskill 主導的路由
- `adaptive_learning_logs`
- `submit_and_get_next` / `rag_hint`
- 三層 RAG source 明確實作

---

## 7. 實作里程碑（可直接排工）

### M1（資料骨架）

1. 建 `adaptive_learning_logs`
2. 建 `skill_manifest.json` 載入器
3. 建 schema 驗證器

### M2（API 可跑）

1. 完成 `submit_and_get_next`
2. 完成 `rag_hint`
3. 串接 logging

### M3（前端可演示）

1. APR 走勢圖
2. 策略標記
3. Auto-Hint 互動

### M4（模型接入）

1. AKT adapter 由 stub 替換為真模型
2. PPO adapter 由 stub 替換為真策略
3. 驗證 fallback 保護

---

## 8. 風險與保護

### 8.1 模型推論失敗

- AKT fallback：沿用上一狀態
- PPO fallback：退回 rule-based family

### 8.2 腳本執行失敗

- 用 manifest 備援腳本
- 保證回傳合法題目 JSON

### 8.3 RAG 檢索失敗

- 回最小提示模板，主流程不中斷

---

## 9. 論文對齊聲明（v1.1）

本版本不是「全部最終成果」，但已可作為論文核心架構的概念驗證：

1. 決策：AKT + PPO 介面化  
2. 出題：family->script 在線執行  
3. 補救：Review->RAG 自動提示  
4. 研究數據：全軌跡寫入 `adaptive_learning_logs`

---

## 10. 開工建議（下一步）

建議先從 `M1` 開始，先穩資料層與 API 契約，再做前端與模型替換。  
這樣能最短路徑拿到可 demo、可記錄、可答辯的版本。
