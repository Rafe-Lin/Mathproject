# 模擬學生功能 (Simulated Student) — 技術文件

> **版本**: v1.0  
> **建立日期**: 2026-04-07  
> **目的**: 提供無 GUI 的程式化學生模擬，用於測試自適應評量與教學系統  
> **位置**: `Simulated_student/`

---

## 目錄

1. [功能概述](#1-功能概述)
2. [架構設計](#2-架構設計)
3. [檔案說明](#3-檔案說明)
4. [模擬策略與隨機依據](#4-模擬策略與隨機依據)
5. [產出圖表說明](#5-產出圖表說明)
6. [API 使用說明](#6-api-使用說明)
7. [除錯指南](#7-除錯指南)
8. [修改紀錄](#8-修改紀錄)

---

## 1. 功能概述

本模組提供模擬學生的機制，讓開發者可以：
- **程式化驅動完整的自適應學習 session**，不需要透過瀏覽器 GUI
- **批量測試不同能力等級的學生**（弱/中/強）在教學 (teaching) 與評量 (assessment) 模式下的表現
- **比較自適應教學 vs 傳統順序教學** 的能力成長差異
- **接入本地 LLM (Ollama)** 以 AI 模擬學生作答
- **記錄每步能力值** 輸出 JSON 檔案，並自動產生視覺化圖表

### 核心流程

```
┌─────────────────┐    直接呼叫    ┌──────────────────────┐
│ SimulatedStudent │ ────────────▶ │ submit_and_get_next()│
│ (sim_core.py)   │              │ (session_engine.py)  │
└────────┬────────┘              └──────────┬───────────┘
         │                                   │
    ╔════╧════════════╗              ╔═══════╧══════════╗
    ║ 決定 is_correct ║              ║ PPO 策略選擇     ║
    ║ (random/fixed/  ║              ║ 補救機制觸發     ║
    ║  LLM judge)     ║              ║ 題目生成         ║
    ╚════╤════════════╝              ║ APR 更新         ║
         │                           ╚═══════╤══════════╝
    ╔════╧════════════╗                       │
    ║ 記錄每步數值    ║◀──────────────────────┘
    ║ → JSON file     ║
    ║ → 視覺化圖表    ║
    ╚═════════════════╝
```

**重點**：模擬直接在 Python 層呼叫 `submit_and_get_next()`，跳過 Flask session/login 層，但經過完整的自適應引擎（PPO 路由、補救機制、RAG 診斷）。

---

## 2. 架構設計

### 三層分離

遵守 `AGENTS.md` 規範，模擬學生**不觸碰**三層架構的內部：
- **Progression 層** (textbook sequence) — 模擬只呼叫公開 API
- **Routing 層** (PPO) — 引擎內部決策，模擬不干涉
- **Remediation 層** (RAG) — 引擎自動觸發，模擬不跳過

### 與主系統的關係

```
Simulated_student/            ← 新增（全部新檔案）
├── __init__.py
├── sim_core.py              ← 核心引擎
├── sim_llm_judge.py         ← LLM-as-a-judge
├── sim_api.py               ← Flask Blueprint
├── run_sim_fixed.py         ← 批量測試腳本
├── run_sim_llm.py           ← LLM 測試腳本
└── outputs/                 ← 每次執行產出新檔案（時間戳命名）

app.py                       ← 修改：註冊 sim_bp blueprint
core/adaptive/               ← 未修改，但被模擬呼叫
```

### 修改 app.py 的內容

在 `create_app()` 中新增：
```python
# [模擬學生 API] 註冊模擬學生 blueprint（本地開發用）
try:
    from Simulated_student.sim_api import sim_bp
    app.register_blueprint(sim_bp)
except ImportError:
    pass  # Simulated_student 套件未安裝時不影響主程式
```

用 `try/except` 包裹，確保 `Simulated_student/` 不存在時不影響主程式。

---

## 3. 檔案說明

### 3.1 `sim_core.py` — 模擬核心引擎

#### `SimulatedStudent` 類別

主要的模擬驅動器。

**建構參數**:
| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `skill_id` | str | 多項式四則運算 | 目標技能 ID |
| `mode` | str | `"teaching"` | `"teaching"` 或 `"assessment"` |
| `ability` | str | `"medium"` | `"weak"` / `"medium"` / `"strong"` |
| `correct_probability` | float | None | 覆蓋能力等級的正確率 (0~1) |
| `answer_strategy` | str | `"random"` | `"random"` / `"fixed"` / `"llm"` |
| `fixed_pattern` | list[bool] | `[T, T, F]` | fixed 策略的循環答對/錯序列 |
| `llm_judge` | LLMJudge | None | LLM 模式時的判斷器實例 |
| `student_label` | str | 自動生成 | 輸出檔案標籤 |
| `seed` | int | None | 亂數種子（可重現結果） |

**主要方法**:
- `run_session(max_steps=30)` — 跑一整場 session，回傳 summary dict
- `save_log(output_path)` — 儲存 JSON 紀錄檔

**每步記錄的欄位** (step_record):
| 欄位 | 說明 |
|------|------|
| `step_number` | 步驟編號 (0-based) |
| `is_correct` | 該步是否答對 (None = 第一步無答案) |
| `target_family_id` | 引擎選擇的題目家族 ID (如 F1, F2) |
| `target_subskills` | 該題的子技能列表 |
| `current_apr` | 當步的 APR 能力估計值 (0~1) |
| `frustration_index` | 挫折指數（連續錯誤累加） |
| `ppo_strategy` | PPO 選擇的策略 (0=Max-Fisher, 1=ZPD, 2=Diversity, 3=Review) |
| `current_mode` | 當前模式（mainline=主線 / remediation=補救） |
| `remediation_triggered` | 是否在此步觸發補救 |
| `return_to_mainline` | 是否在此步從補救返回主線 |
| `completed` | session 是否結束 |
| `unit_completed` | 單元是否通過 |
| `mastery_snapshot` | 能力快照 (APR, frustration, in_remediation) |
| `question_data` | 題目內容 (question_text, correct_answer, family_name) |
| `timestamp` | UTC 時間戳 |

#### `BaselineStudent` 類別

**非自適應對照組**。模擬一個學生按照教科書預設順序 (`F1 → F2 → F5 → F11 → F9 → F10`) 循環做題，**不使用 PPO 路由、不觸發補救、不走 RAG 診斷**。

APR 更新使用與自適應引擎完全相同的 `update_local_apr()` 函式（來自 `akt_adapter.py`），確保對比公平。

### 3.2 `sim_llm_judge.py` — LLM-as-a-judge

使用 Ollama 本地模型模擬學生作答。Prompt 設計為「LLM-as-a-judge」模式：
- LLM 被要求**角色扮演**一個指定能力等級的國中生
- LLM 需要展示思考過程，然後給出答案
- LLM 自己判斷答案是否正確
- 回傳結構化 JSON: `{thinking, student_answer, is_correct, confidence}`

**能力角色設定**:
| 等級 | LLM 被告知的角色描述 |
|------|---------------------|
| weak | 基礎薄弱，常在正負號/括號犯錯，正確率~30% |
| medium | 能力中等，多步驟計算偶爾犯錯，正確率~55% |
| strong | 能力很強，很少犯錯，正確率~85% |

**容錯處理**:
1. 先嘗試直接 JSON parse
2. 移除 markdown code fence 後再試
3. 用 regex 尋找 JSON 物件
4. 最後 heuristic 判斷 is_correct

### 3.3 `sim_api.py` — REST API

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/sim/run` | POST | 執行一場模擬，回傳完整結果 |
| `/api/sim/results` | GET | 列出本次 server 執行期間的所有模擬結果 |
| `/api/sim/presets` | GET | 回傳可用的能力等級與策略預設值 |

不需要登入驗證（本地開發用途）。

### 3.4 `run_sim_fixed.py` — 固定/隨機批量測試

一次跑 **弱/中/強 × 教學/評量 = 6 組** 模擬 + **3 組** 基線對照。
每次執行都會在 `outputs/` 產生帶時間戳的新檔案，不覆蓋舊結果。

### 3.5 `run_sim_llm.py` — LLM 測試

透過命令列參數指定能力/模式/步數/模型，跑單場 LLM 模擬。
支援 `--ability`, `--mode`, `--steps`, `--model`, `--api-url` 參數。

---

## 4. 模擬策略與隨機依據

### 4.1 隨機策略 (`answer_strategy = "random"`)

**正確率依據**：每一步以 `random.random() < correct_probability` 決定答對或答錯。

| 能力等級 | correct_probability | 設計依據 |
|----------|--------------------|----|
| weak (弱) | 0.30 | 模擬連續錯誤的弱學生，容易觸發補救機制（引擎設定連續錯 2 題觸發）。30% 正確率代表多數題都答錯。 |
| medium (中等) | 0.55 | 模擬有時對有時錯的學生，正確率略高於 50%，偶爾會累積連錯觸發補救，但也有機會恢復。 |
| strong (強) | 0.85 | 模擬幾乎都答對的學生，很少連續錯誤，APR 會快速上升，不太需要補救。 |

**RNG seed**：預設 `seed=42`，確保每次執行**同一組**的結果可重現。不同能力等級使用相同 seed，但因為引擎的內部狀態不同（不同的路由決策 → 不同的題目 → 不同的隨機判斷時機），最終路徑會不同。

### 4.2 固定策略 (`answer_strategy = "fixed"`)

按照 `fixed_pattern` 循環，例如 `[True, True, False]` 表示每三題答對兩題、錯一題。
適合用來測試特定的連錯/連對場景是否觸發預期的引擎行為。

### 4.3 LLM 策略 (`answer_strategy = "llm"`)

讓 Ollama 本地模型扮演國中生作答。正確率不由機率決定，而是由 LLM 根據題目內容和角色設定自行判斷。

### 4.4 基線對照 (`BaselineStudent`)

使用與自適應引擎**完全相同**的 APR 更新公式 (`update_local_apr()`)，但：
- 題目順序固定為教科書主線序列 `[F1, F2, F5, F11, F9, F10]` 循環
- 不觸發 PPO 路由決策
- 不觸發補救機制
- 不走 RAG 診斷

這提供了一個公平的對照組：**如果學生能力相同 (同 correct_probability, 同 seed)，自適應系統能否讓 APR 成長更快？**

---

## 5. 產出圖表說明

所有圖表都存放在 `Simulated_student/outputs/` 下，每次執行用時間戳命名（`YYYYMMDD_HHMMSS`），不會覆蓋之前的結果。

### 5.1 `plot_apr_curves` — APR 能力值變化曲線

| 項目 | 說明 |
|------|------|
| **呈現內容** | 三條 APR 曲線（弱/中/強），分為教學與評量兩個子圖 |
| **X 軸** | 步驟編號 |
| **Y 軸** | APR 值 (0~1)，表示系統對學生能力的即時估計 |
| **灰色虛線** | 目標 APR (0.65)，超過此值代表系統認為學生能力足夠 |
| **▼ 三角標記** | 補救機制觸發的步驟 |
| **圖例中 p=xx%** | 該模擬組的實際正確率 |
| **意義** | 觀察不同能力學生的 APR 走勢：弱學生 APR 應該低且波動大，強學生應該快速達到高 APR |

### 5.2 `plot_frustration` — 挫折指數變化

| 項目 | 說明 |
|------|------|
| **呈現內容** | 三條挫折指數曲線 |
| **X 軸** | 步驟 |
| **Y 軸** | Frustration index（答對歸零，連續答錯累加） |
| **意義** | 弱學生的挫折指數應該經常維持高值（連續犯錯），強學生應該幾乎為 0。挫折指數 ≥ 2 會影響 PPO 決策和補救觸發。 |

### 5.3 `plot_family_coverage` — Family 覆蓋數

| 項目 | 說明 |
|------|------|
| **呈現內容** | 柱狀圖，每組模擬經過了多少不同的 family |
| **意義** | 強學生在教學模式應該覆蓋更多 family（快速通關），弱學生可能因為卡在補救而覆蓋較少。評量模式有固定的 family 序列，覆蓋數較為一致。 |

### 5.4 `plot_ppo_strategy` — PPO 策略分佈

| 項目 | 說明 |
|------|------|
| **呈現內容** | 圓餅圖，顯示 PPO 在每組模擬中選擇各策略的比例 |
| **策略 0: Max-Fisher** | 選擇「資訊量最大」的 family（最能區分學生能力的題目） |
| **策略 1: ZPD** | 選擇在學生「最近發展區」的 family |
| **策略 2: Diversity** | 選擇學生較少練習的 family（增加覆蓋度） |
| **策略 3: Review** | 選擇學生曾做錯的 family（複習） |
| **意義** | 觀察 PPO 在不同能力學生上是否會選擇不同的策略組合 |

### 5.5 `plot_remediation_timeline` — 補救機制時間線

| 項目 | 說明 |
|------|------|
| **呈現內容** | 三個子圖（弱/中/強），顯示主線/補救模式的切換時間 |
| **紅色區塊** | 學生處於補救模式的步驟 |
| **▼ 紅色標記** | 觸發補救的步驟 |
| **▲ 綠色標記** | 從補救返回主線的步驟 |
| **曲線** | APR 變化 |
| **意義** | 弱學生預期長時間在補救模式震盪，中等學生應該進入補救後成功返回主線，強學生應該不進入補救 |

### 5.6 `plot_summary_comparison` — 結果總覽比較

| 項目 | 說明 |
|------|------|
| **呈現內容** | 三組柱狀圖：最終 APR、正確率、覆蓋 Family 數 |
| **意義** | 快速總覽所有模擬組的整體表現差異 |

### 5.7 `plot_adaptive_vs_baseline` — 自適應 vs 傳統順序教學

| 項目 | 說明 |
|------|------|
| **呈現內容** | 三個子圖（弱/中/強），每圖兩條曲線：自適應 (實線) vs 傳統順序 (虛線) |
| **彩色實線** | 使用自適應系統的學生 APR |
| **灰色虛線** | 使用傳統固定順序的學生 APR（同 correct_probability + 同 seed） |
| **意義** | **最重要的圖**。顯示自適應教學帶來的能力成長加速效果。因為兩組使用相同的正確率和相同 APR 更新公式，唯一差異是：自適應系統會根據學生表現動態調整題目順序和觸發補救 |

---

## 6. API 使用說明

### 啟動方式

```bash
# 方式 1: 跑批量測試腳本（不需要啟動伺服器）
python Simulated_student/run_sim_fixed.py

# 方式 2: 跑 LLM 測試（需要 Ollama）
python Simulated_student/run_sim_llm.py --ability medium --mode teaching --steps 20

# 方式 3: 透過 REST API（需要啟動 Flask 伺服器）
python app.py
# 然後用 curl 或 Postman 呼叫 /api/sim/run
```

### REST API 範例

```bash
# 執行一場模擬
curl -X POST http://localhost:5000/api/sim/run \
  -H "Content-Type: application/json" \
  -d '{
    "ability": "medium",
    "mode": "teaching",
    "max_steps": 20,
    "answer_strategy": "random"
  }'

# 查看所有結果
curl http://localhost:5000/api/sim/results

# 查看可用預設值
curl http://localhost:5000/api/sim/presets
```

### Python 腳本直接使用

```python
from Simulated_student.sim_core import SimulatedStudent

sim = SimulatedStudent(
    ability="medium",
    mode="teaching",
    seed=42,
)
result = sim.run_session(max_steps=20)
log_path = sim.save_log()  # 自動存到 outputs/ 帶時間戳
```

---

## 7. 除錯指南

### 常見問題

#### Q: 執行時出現 `ImportError: cannot import 'submit_and_get_next'`
**A**: 確認工作目錄是專案根目錄 (`Mathproject/`)，或確認 `sys.path` 包含專案根目錄。腳本已有 path bootstrap 程式碼自動處理。

#### Q: 第一次執行很慢
**A**: 引擎需要初始化 RAG (Chroma + SentenceTransformer)，首次載入模型約需 10~30 秒。後續步驟會快很多。

#### Q: `ModuleNotFoundError: No module named 'chromadb'`
**A**: 安裝依賴：
```bash
pip install chromadb sentence-transformers
```

#### Q: LLM 模式顯示「無法連線到 Ollama」
**A**: 確認：
1. Ollama 已啟動: `ollama serve`
2. 模型已下載: `ollama pull qwen3-vl:8b-instruct-q4_k_m`
3. API URL 正確: 預設 `http://localhost:11434/api/generate`

#### Q: 模擬學生帳號會影響真實資料嗎？
**A**: 模擬學生使用獨立帳號 (`sim_student_weak_teaching` 等)，與真實學生帳號分離。但**學習歷程記錄** (`adaptive_learning_logs`) 會寫入同一張表。若要清除，可用：
```sql
DELETE FROM adaptive_learning_logs
WHERE student_id IN (
  SELECT id FROM users WHERE username LIKE 'sim_student_%'
);
```

#### Q: 圖表中文字型顯示為方塊
**A**: 腳本使用 `Microsoft JhengHei` (微軟正黑體)，如果系統沒有中文字型，需要安裝或修改 `_setup_chinese_font()` 中的字型路徑。

### 核心函式呼叫路徑

```
SimulatedStudent.run_session()
  ├── SimulatedStudent._ensure_app_context()    # 建立 Flask context
  │     └── app.create_app()                     # 初始化 DB, RAG
  ├── SimulatedStudent._ensure_student_user()   # 建立/取得模擬學生帳號
  └── [loop] for step in range(max_steps):
        ├── SimulatedStudent._decide_answer()    # 決定 is_correct
        │     ├── (random) random.Random.random() < correct_probability
        │     ├── (fixed)  fixed_pattern[step % len]
        │     └── (llm)    LLMJudge.judge()
        ├── submit_and_get_next(payload)          # ← 核心引擎呼叫
        │     ├── update_local_apr()              # APR 更新
        │     ├── choose_strategy()               # PPO 策略選擇
        │     ├── route_policy.select_action()    # PPO 路由決策
        │     ├── rag_diagnose()                  # RAG 診斷
        │     └── _generate_question_payload()    # 題目生成
        └── SimulatedStudent._record_step()       # 記錄數值
```

---

## 8. 修改紀錄

### 2026-04-07 v1.0 — 初始版本

**新增檔案**:
| 檔案 | 說明 |
|------|------|
| `Simulated_student/__init__.py` | Package init |
| `Simulated_student/sim_core.py` | 核心引擎：`SimulatedStudent` + `BaselineStudent` |
| `Simulated_student/sim_llm_judge.py` | LLM-as-a-judge 模組 |
| `Simulated_student/sim_api.py` | Flask Blueprint REST API |
| `Simulated_student/run_sim_fixed.py` | 固定/隨機批量測試 + 7 張圖 |
| `Simulated_student/run_sim_llm.py` | LLM 測試 + 5 張圖 |
| `docs/simulated_student.md` | 本文件 |

**修改檔案**:
| 檔案 | 修改內容 |
|------|---------|
| `app.py` | 在 `create_app()` 中新增 `sim_bp` blueprint 註冊 |

**未修改的核心檔案** (只被呼叫，未被修改):
- `core/adaptive/session_engine.py` — submit_and_get_next()
- `core/adaptive/akt_adapter.py` — update_local_apr()
- `core/adaptive/state_builder.py` — build_agent_state()
- `core/adaptive/textbook_progression.py` — 主線序列定義
- `core/adaptive/judge.py` — 答案判斷
- `models.py` — AdaptiveLearningLog, User
