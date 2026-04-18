# ARCHITECTURE_NOTES

更新日期: 2026-03-25  
專案: `D:\Python\Mathproject`  
範圍: `本單元自適應學習（總結性診斷）`

---

## 0. 系統定位（先講清楚）

本研究是**系統架構級（Architecture-level）**，不是單一演算法改良。  
最小可證明單元是「三位一體閉環」：

1. 大腦層：AKT 診斷 + PPO 策略導航  
2. 雙手層：Edge AI 微技能腳本（離線生成、在線執行）  
3. 嘴巴層：Hybrid RAG 補救提示（依 subskill 精準檢索）

此文件是 `v1` 實作的架構邊界與風險控制說明，供工程實作與論文答辯共用。

---

## 1. v1 PoC 範圍（避免過度宣稱）

`v1` 的定位是 **PoC（概念驗證）**，不是最終 full production。

`v1` 必須完成：

1. 從 `subskill_nodes` 更新診斷狀態（AKT adapter 或對應替代器）  
2. 由策略器輸出 `ppo_strategy` 與 `target_family_id`  
3. 依 `family_id` 執行對應微技能腳本產題  
4. 記錄完整 `adaptive_learning_logs` 軌跡  
5. Review 策略時自動觸發 RAG hint

`v1` 尚未要求：

1. PPO 最終最優策略收斂  
2. 所有單元全覆蓋  
3. 全平台替換既有 adaptive 路徑

---

## 2. 三層閉環到程式模組映射

### 2.1 大腦層（AKT + PPO）

- `core/adaptive/akt_adapter.py`
- `core/adaptive/ppo_adapter.py`
- `core/adaptive/session_engine.py`

輸入:

- `session_id`
- `step_number`
- `is_correct`
- `previous_subskill_nodes`

輸出:

- `current_apr`（Local APR）
- `ppo_strategy`
- `target_family_id`
- `frustration_index`

### 2.2 雙手層（Edge AI 腳本兵工廠）

- `scripts/generate_micro_skills_scripts.py`
- `core/adaptive/manifest_registry.py`
- `skills/*.py`（微技能腳本）

行為:

- 離線批次生成腳本
- 在線讀 manifest 定位腳本
- 快速執行腳本拿題目 JSON

### 2.3 嘴巴層（Hybrid RAG）

- `core/adaptive/rag_hint_engine.py`

觸發:

- 當 `ppo_strategy == 3`（Review）時

檢索來源（三層）:

1. 知識圖譜節點（骨架）
2. 課本文本（血肉）
3. SKILL.md（程序性解題鷹架）

---

## 3. 五大關鍵議題（正式版）

這五點是工程風險控制，也是在口試會被問的核心。

### 3.1 Registry：腳本映射不能靠猜

問題:

- 單靠檔名命名慣例，會造成尋址脆弱、版本不可追蹤。

對策:

- 建 `skill_manifest.json` 作為服務註冊表。

最小欄位:

- `family_id`
- `script_path`
- `version`
- `subskill_nodes`
- `generated_at`
- `model_name`
- `healer_applied`

### 3.2 SSOT：Q-Matrix 標籤一致性

問題:

- `subskill_nodes` 漂移會污染 AKT state，連帶破壞 PPO 決策品質。

對策:

- `skill_breakpoint_catalog.csv` 作為唯一真源（SSOT）
- 輸出 JSON 必須過 Pydantic / JSON Schema 驗證
- 嚴禁自由字串進入核心決策流程

### 3.3 APR 定義：採 Local APR

問題:

- 若用 Global APR 當決策信號，會混入無關技能噪音，credit assignment 失真。

對策:

- 決策層使用 `Local APR`  
- 報表層可同時留 `Global APR`

建議定義（pseudo）:

```text
LocalAPR_t = mean( P(correct | subskill in target_subskills_t) )
```

用途:

- PPO reward 主信號
- 前端 mastery trajectory 主 Y 軸

### 3.4 執行路徑：subprocess 是過渡方案

問題:

- `subprocess.run` 有 process fork / cold start 開銷，且安全隔離不足。

對策:

- MVP 可暫用 subprocess
- 正式版改成 in-process `importlib` + 限制命名空間
- 逐步導入 AST 黑名單 / Restricted execution

### 3.5 RAG Source：必須明確三層混合

問題:

- 若來源不明確，hint 會變泛答，失去論文主張的精準補救價值。

對策:

- 以 `subskill_nodes` 為查詢錨點，固定三層檢索：
  - 圖譜節點
  - 課本文本
  - SKILL.md 程序

---

## 4. PPO 策略編碼固定（不可漂移）

全系統固定使用：

- `0`: Max-Fisher
- `1`: ZPD
- `2`: Diversity
- `3`: Review

規範:

1. 前後端與資料庫一律同碼表  
2. 圖表 legend、log、論文圖標註必須一致  
3. 禁止在不同模組改名或重排編碼

---

## 5. 指標用語修正（避免答辯風險）

避免絕對化說法：

- 不用「零幻覺」
- 不用「零延遲」

建議用語：

- `顯著降低幻覺風險`
- `在線出題延遲目標 < 1 秒（以 execution_latency 實測）`

---

## 6. 與現有 adaptive v1 的差異（必備對照）

### 現有 v1（專案現況）

- 規則式推薦（rule-based）
- 以 `skill_id` / 題目為主
- 無 `adaptive_learning_logs` 專用軌跡表
- 無 `submit_and_get_next` 主 API
- 無 `subskill` 驅動 auto-hint

### 目標 v1.1（論文對齊版）

- AKT + PPO 決策流
- `family_id` action space + `subskill_nodes` state space
- 完整 `adaptive_learning_logs`
- `POST /api/adaptive/submit_and_get_next`
- `GET /api/adaptive/rag_hint`
- Review 自動觸發提示面板

---

## 7. 失敗保護（Demo 必備）

若 AKT/PPO 推論異常，系統不可中斷。

保護機制：

1. AKT fallback：沿用上一步狀態與 conservative APR  
2. PPO fallback：退回 rule-based 選題（同 family 範圍）  
3. 腳本執行 fallback：回退到同 family 備援腳本  
4. RAG fallback：最小提示模板（不阻塞主流程）

---

## 8. 口試可用一句話

本系統在 MVP 階段驗證閉環可行性；在正式架構上以 Registry、SSOT、Local APR、受限執行、Hybrid RAG 五項機制，確保可維護性、可擴展性、可重現性與答辯可防禦性。
