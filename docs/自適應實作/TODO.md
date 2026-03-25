# TODO

更新日期: 2026-03-25  
對應文件: `docs/自適應實作/ARCHITECTURE_NOTES.md`

---

## 0. 目標

把目前 rule-based adaptive 練習流程，升級成論文對齊的三層閉環：

1. AKT + PPO 決策  
2. 微技能腳本在線出題  
3. Review 觸發 Hybrid RAG 補救

---

## 1. 高優先（必做）

### 1.1 建立 `adaptive_learning_logs`（主資料表）

必備欄位：

- `log_id`
- `student_id`
- `session_id`
- `step_number`
- `target_family_id`
- `target_subskills` (JSON)
- `is_correct`
- `current_apr` (Local APR)
- `ppo_strategy` (0/1/2/3)
- `frustration_index`
- `execution_latency`

### 1.2 建立 `skill_manifest.json` 與 registry 載入器

任務：

- 定義 manifest schema
- 實作 `core/adaptive/manifest_registry.py`
- 在離線生成腳本流程加入 manifest 註冊

### 1.3 固定 `subskill_nodes` SSOT 驗證

任務：

- 以 `skill_breakpoint_catalog.csv` 作為唯一真源
- 實作 `core/adaptive/schema.py`
- 對腳本輸出 JSON 做 schema 驗證

### 1.4 實作主 API

建立：

- `POST /api/adaptive/submit_and_get_next`
- `GET /api/adaptive/rag_hint`

規範：

- API response 必須包含 `current_apr`, `ppo_strategy`, `frustration_index`, `new_question_data`

### 1.5 固定 PPO 策略編碼

全系統固定：

- `0`: Max-Fisher
- `1`: ZPD
- `2`: Diversity
- `3`: Review

---

## 2. 中優先（v1.1 要進）

### 2.1 AKT/PPO adapter 介面層

建立：

- `core/adaptive/akt_adapter.py`
- `core/adaptive/ppo_adapter.py`

要求：

- 可先 stub，但介面與輸出字段要固定
- 便於後續替換成真模型推論

### 2.2 前端 `adaptive_practice` 升級

任務：

- 顯示 mastery trajectory（Y 軸 Local APR）
- 顯示策略切換標記（Review 用明顯 icon）
- Review 時自動呼叫 `rag_hint`

### 2.3 RAG 混合來源落地

建立：

- `core/adaptive/rag_hint_engine.py`

要求：

- 明確三層來源（圖譜、課本、SKILL.md）
- 以 `subskill_nodes` 為 query anchor

---

## 3. 低優先（v1.2+）

### 3.1 subprocess -> in-process

任務：

- 將腳本執行切換為 `importlib` 動態載入
- 逐步補受限執行（AST 黑名單 / namespace 限制）

### 3.2 Traceability 增強

在 manifest / logs 記錄：

- 模型版本
- prompt 版本
- healer 使用狀態
- 腳本版本

---

## 4. 論文圖表輸出任務（必留）

從 `adaptive_learning_logs` 可直接產生：

1. Local APR 走勢圖（含達標線）
2. 策略切換分布圖（0/1/2/3 比例）
3. 路徑多樣性（DIV）統計圖
4. frustration_index 變化圖
5. execution_latency 分布圖（證明低延遲目標）

---

## 5. 失敗保護（Demo 不中斷）

### 5.1 AKT/PPO fallback

- AKT 失敗時沿用上一狀態
- PPO 失敗時退回 rule-based family 選題

### 5.2 腳本 fallback

- 主腳本失敗時切備援腳本
- 仍回傳合法 `new_question_data`

### 5.3 RAG fallback

- 檢索失敗時回最小補救提示模板

---

## 6. 文件與口試同步

需要同步更新：

1. `docs/自適應實作/ARCHITECTURE_NOTES.md`
2. 作品說明書「系統架構設計與討論」
3. 作品說明書「研究限制與未來工作」

---

## 7. v1.1 實作順序（直接照做）

1. 資料表 `adaptive_learning_logs`
2. manifest + schema + catalog loader
3. `submit_and_get_next` API
4. `rag_hint` API
5. `adaptive_practice` 前端儀表板
6. AKT/PPO adapter 接入
7. fallback 保護
