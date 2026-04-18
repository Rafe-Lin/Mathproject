# 單元-題型-技能檔 架構說明

## 概述

本架構將原本「一個 skill 檔多題型」改為 **一題型一 skill 檔**，並支援「單元出題」：同一單元按下一題時，可抽到不同 pattern 的題目。

- **單元** = (curriculum, volume, chapter[, section])
- **題型** = pattern skill（獨立 skill_id、獨立 `skills/<skill_id>.py`）
- **選擇策略**：權重抽樣（可擴充為自適應）

## 流程圖

```
┌─────────────────┐    mode=unit     ┌──────────────────┐
│ /get_next_question│ ───────────────▶│ unit_selector     │
│ ?chapter=X&volume=Y│                │ 選出 pattern skill_id │
└─────────────────┘                   └─────────┬──────────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │ import skills.xxx │
                                    │ mod.generate(lv)  │
                                    └─────────┬──────────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │ 回傳 question_text │
                                    │ correct_answer... │
                                    └──────────────────┘
```

## 檔案結構

### 方式 A：一題型一資料夾（原有）

```
agent_skills/
  <pattern_skill_id>/
    SKILL.md       # 規格書（工程約束、Pattern Catalogue、API）
    skill.json     # 元資料（injected_apis, pattern_id 等）

skills/
  <pattern_skill_id>.py   # 一題型一檔，實作 generate() 與 check()
```

### 方式 B：單元 base + 題型 delta（進階）

```
agent_skills/
  <unit_id>/                    # 單元層
    SKILL.md                    # base：通用規格（工程約束、API）
    patterns/
      <pattern_id>.md           # delta：各題型專屬規格
    prompt_benchmark.md         # 可選：benchmark 模式額外說明
    prompt_liveshow.md          # 可選：liveshow 模式額外說明

skills/
  <unit_id>__<pattern_id>.py    # 產出檔：雙底線命名
```

**Pattern skill 命名規則**：`<unit_id>__<pattern_id>`（雙底線分隔），例如 `jh_數學2上_FourOperationsOfRadicals__RadicalSimplify`。

### 共用配置

```
config/
  unit_pattern_config.json  # 單元 → 題型清單與權重（進 git）
instance/
  unit_pattern_config.json  # 可選，覆蓋 config/ 版本（本地）
```

## 新增一個 pattern skill

### 1. 建立 agent_skills 目錄

```bash
mkdir agent_skills/jh_數學2上_RadicalDivide
```

### 2. 撰寫 SKILL.md

依既有 SKILL.md（如 `jh_數學2上_FourOperationsOfRadicals`）裁剪為單一題型規格，包含：

- 工程約束（嚴禁 sympy、RadicalOps 等）
- 該 pattern 的 ID、vars 結構
- API 呼叫方式

### 3. 撰寫 skill.json

```json
{
  "skill_id": "jh_數學2上_RadicalDivide",
  "display_name": "根式除法",
  "family": "radical",
  "injected_apis": ["RadicalOps"],
  "pattern_id": "p3c_div_direct"
}
```

### 4. 撰寫或生成 skills/*.py

- **手寫**：參考 `jh_數學2上_RadicalSimplify.py`，委派 `DomainFunctionHelper`
- **AI 生成（方式 A）**：執行 `auto_generate_skill_code(skill_id)`，會從 `agent_skills/<id>/SKILL.md` 讀取規格並經 healer/validator 產生程式碼
- **AI 生成（方式 B，base+delta）**：使用 `sync_unit_pattern_skills.py`，見下方說明

### 5. 註冊到單元

在 `config/unit_pattern_config.json`（或 `instance/` 覆蓋版）加入：

```json
{
  "junior_high|數學2上|第二章 二次方根與畢氏定理": [
    {"skill_id": "jh_數學2上_RadicalSimplify", "weight": 1},
    {"skill_id": "jh_數學2上_RadicalAddSub", "weight": 1},
    {"skill_id": "jh_數學2上_RadicalDivide", "weight": 1}
  ]
}
```

### 6. 寫入 skills_info（若需前台顯示）

```bash
python scripts/seed_unit_pattern_skills.py
```

或於管理後台手動新增技能與課綱對應。

## API 使用

### 單元出題

```
GET /get_next_question?mode=unit&chapter=第二章%20二次方根與畢氏定理&volume=數學2上
```

- `mode=unit`：啟用單元出題
- `chapter`：必填
- `volume`：該 chapter 僅對應單一 volume 時可省略（由 skill_curriculum 推斷）；否則必填，缺則 400
- `curriculum`：選填，預設取自 session 或 `junior_high`

### 舊行為（向下相容）

```
GET /get_next_question?skill=jh_數學2上_FourOperationsOfRadicals&level=1
```

未帶 `mode=unit` 時，行為與原本相同。

## 配置點

| 位置 | 說明 |
|------|------|
| `config/unit_pattern_config.json` | 單元 → pattern skills 清單與權重（進 git） |
| `instance/unit_pattern_config.json` | 可選覆蓋版（本地） |
| `skill_curriculum` 表 | Fallback：無 config 時依 (curriculum, volume, chapter) 查詢 |

之後可擴充：`enabled` 欄位、難度分配、自適應權重等。

## sync_unit_pattern_skills.py（base+delta 生成）

產生「單元 base + 題型 delta」的技能程式碼，適用於方式 B 的目錄結構。

### 用途

- 讀取 `agent_skills/<unit_id>/SKILL.md` + `patterns/<pattern_id>.md`
- 合併 base、delta，以及可選的 mode delta（`prompt_benchmark.md` / `prompt_liveshow.md`）
- 交給 `code_generator` 以 AST pipeline 生成 `skills/<unit_id>__<pattern_id>.py`
- 若產出檔已存在，預設會覆寫（可用 `--no-overwrite` 改為跳過）

### 用法

```bash
# 指定單一題型
python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --pattern RadicalSimplify

# 該單元下所有 pattern
python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --all

# 合併 mode delta（benchmark 或 liveshow）
python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --all --mode benchmark

# 不覆寫既有 skill 檔
python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --all --no-overwrite
```

### 參數

| 參數 | 說明 |
|------|------|
| `--unit <unit_id>` | 必填，單元 ID（對應 `agent_skills/<unit_id>/`） |
| `--pattern <pattern_id>` | 指定單一題型（對應 `patterns/<pattern_id>.md`） |
| `--all` | 處理該單元下所有 pattern |
| `--mode benchmark\|liveshow` | 可選，合併對應的 `prompt_*.md` |
| `--no-overwrite` | 若 skill 檔已存在則跳過 |

### 組合規則

- **base** = `agent_skills/<unit_id>/SKILL.md`
- **delta** = `agent_skills/<unit_id>/patterns/<pattern_id>.md`
- **mode delta（可選）** = `prompt_benchmark.md` 或 `prompt_liveshow.md`（若存在）
- 若找不到 delta 則報錯並跳過該 pattern
- 生成時使用 AST pipeline（`USE_AST_PIPELINE=1`）

### 產出檔名

規則：`<unit_id>__<pattern_id>.py`（雙底線），例：`jh_數學2上_FourOperationsOfRadicals__RadicalSimplify.py`

## 驗證

```bash
python scripts/verify_unit_pattern_mvp.py
```

應通過 unit selector、三個 pattern skill 的 generate()，以及完整單元出題流程。
