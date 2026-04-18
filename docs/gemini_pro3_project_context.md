# 智學AIGC賦能平台 (Smart-Edu AIGC Platform) - 專案完整說明文件

> 本文件旨在提供給 AI 助手(Gemini Pro 3)完整的專案背景、架構、功能與開發脈絡,以便進行後續開發討論。

---

## 📋 專案概述

### 核心定位
**智學AIGC賦能平台 (Smart-Edu AIGC Platform)** 是一個以「功文數學」教學理論為核心的 AI 驅動學習平台,專門針對「考不及格、數學較弱」的高中職學生設計,目標是透過手寫辨識、生成式 AI 分析與自適應題目推送,幫助學生打好基礎運算能力,達到及格門檻(60分)並建立學習信心。

### 教學理念
- **功文數學法**:基礎概念精熟、漸進式學習、重複練習、即時回饋
- **目標導向**:把未達標學生提升到及格為優先,而非追求高分
- **適用場域**:智慧校園 — 學習與教學優化、校園生活輔助、永續教育
- **競賽背景**:參加育秀盃 AI 應用競賽作品

---

## 🏗️ 技術架構

### 技術堆疊
```
後端框架:   Python 3.x + Flask 2.0+
ORM:        Flask-SQLAlchemy
資料庫:     SQLite (開發/部署) / PostgreSQL (生產環境)
前端:       原生 HTML5 + CSS3 + JavaScript
模板引擎:   Jinja2
AI 服務:    Google Gemini API (gemini-2.5-flash)
認證系統:   Flask-Login + bcrypt
數學渲染:   MathJax (LaTeX 公式顯示)
數據處理:   Pandas, NumPy
圖表繪製:   Matplotlib
```

### 專案目錄結構
```
math-master/
├── app.py                      # Flask 主應用入口
├── models.py                   # SQLAlchemy ORM 模型定義
├── config.py                   # 配置文件(資料庫、API Key、上傳路徑)
├── requirements.txt            # Python 依賴套件
│
├── core/                       # 核心業務邏輯模組
│   ├── routes.py              # 主要路由與業務邏輯(62KB,核心檔案)
│   ├── ai_analyzer.py         # Gemini AI 整合(手寫辨識、題目分析)
│   ├── exam_analyzer.py       # 考卷診斷分析
│   ├── exam_routes.py         # 考卷上傳相關路由
│   ├── utils.py               # 工具函式(課程資料查詢等)
│   ├── helpers.py             # 輔助函式
│   └── session.py             # Session 管理
│
├── skills/                     # 技能模組(718個獨立技能檔案)
│   ├── abs_eq_simple.py       # 範例:簡單絕對值方程式
│   ├── quadratic_function.py  # 範例:二次函數
│   ├── jh_*.py                # 國中(junior high)技能模組
│   └── ...                    # 涵蓋國中、高中普通科、技高課程
│
├── templates/                  # Jinja2 HTML 模板
│   ├── login.html             # 登入頁面
│   ├── register.html          # 註冊頁面
│   ├── dashboard.html         # 學生儀表板(課程/技能瀏覽)
│   ├── teacher_dashboard.html # 教師儀表板
│   ├── index.html             # 練習頁面(題目生成、手寫辨識)
│   ├── exam_upload.html       # 考卷上傳診斷
│   ├── admin_skills.html      # 管理:技能管理
│   ├── admin_curriculum.html  # 管理:課程綱要管理
│   ├── admin_prerequisites.html # 管理:前置技能管理
│   ├── db_maintenance.html    # 管理:資料庫維護
│   ├── similar_questions.html # 相似題生成頁面
│   └── image_quiz_generator.html # 圖片測驗生成
│
├── static/                     # 靜態資源
│   ├── css/
│   ├── js/
│   └── images/
│
├── datasource/                 # 課程資料來源(CSV/Excel)
│   └── (120個資料檔案)
│
├── instance/                   # Flask 實例資料夾
│   └── math_master.db         # SQLite 資料庫檔案
│
├── uploads/                    # 使用者上傳檔案儲存
│
├── docs/                       # 文件目錄
│   ├── SDD.md                 # 軟體設計文件
│   └── 軟體設計文件 (SDD).md
│
├── backup/                     # 備份檔案
│
└── 輔助腳本/
    ├── import_data.py         # 技能資料匯入
    ├── import_curriculum.py   # 課程綱要匯入
    ├── import_dependencies.py # 技能依賴匯入
    ├── generate_db_schema.py  # 資料庫 Schema 生成
    └── migrate_db.py          # 資料庫遷移腳本
```

---

## 🗄️ 資料庫設計

### 核心資料表

#### 1. `users` - 使用者表
```sql
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL
email           TEXT
role            TEXT DEFAULT 'student'  -- 'student' | 'teacher' | 'admin'
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### 2. `skills_info` - 技能資訊表
```sql
skill_id                      TEXT PRIMARY KEY        -- 如 'abs_eq_simple'
skill_en_name                 TEXT NOT NULL           -- 英文名稱
skill_ch_name                 TEXT NOT NULL           -- 中文名稱
category                      TEXT                    -- 分類(如'方程式')
description                   TEXT NOT NULL           -- 說明
input_type                    TEXT DEFAULT 'text'     -- 'text' | 'handwriting'
gemini_prompt                 TEXT NOT NULL           -- AI 批改用的 prompt
consecutive_correct_required  INTEGER DEFAULT 10      -- 連續答對幾題才算精熟
is_active                     BOOLEAN DEFAULT TRUE    -- 是否啟用
order_index                   INTEGER DEFAULT 0       -- 排序索引
suggested_prompt_1/2/3        TEXT                    -- 建議提示(K,L,M欄)
```

#### 3. `skill_curriculum` - 課程綱要映射表
```sql
id              INTEGER PRIMARY KEY
skill_id        TEXT NOT NULL (FK -> skills_info)
curriculum      TEXT NOT NULL  -- 'general'(普高) | 'vocational'(技高) | 'junior_high'(國中)
grade           INTEGER NOT NULL  -- 7,8,9(國中) | 10,11,12(高中)
volume          TEXT NOT NULL  -- '數學1上','數A','數B','數學甲(上)'等
chapter         TEXT NOT NULL  -- '第一章 多項式'
section         TEXT NOT NULL  -- '1-2 餘式定理'
paragraph       TEXT           -- 可選的段落
display_order   INTEGER DEFAULT 0
difficulty_level INTEGER DEFAULT 1  -- 難易度
```

#### 4. `skill_prerequisites` - 技能前置依賴表
```sql
id               INTEGER PRIMARY KEY
skill_id         TEXT NOT NULL (FK -> skills_info)
prerequisite_id  TEXT NOT NULL (FK -> skills_info)
-- 表示 skill_id 需要先學會 prerequisite_id
```

#### 5. `progress` - 學習進度表
```sql
user_id             INTEGER (FK -> users, PK)
skill_id            TEXT (PK)
consecutive_correct INTEGER DEFAULT 0  -- 連續答對次數
consecutive_wrong   INTEGER DEFAULT 0  -- 連續答錯次數(用於降級)
current_level       INTEGER DEFAULT 1  -- 當前難度等級
questions_solved    INTEGER DEFAULT 0  -- 總解題數
last_practiced      DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### 6. `mistake_logs` - 錯題記錄表
```sql
id                      INTEGER PRIMARY KEY
user_id                 INTEGER NOT NULL (FK -> users)
skill_id                TEXT NOT NULL
question_content        TEXT NOT NULL
user_answer             TEXT NOT NULL
correct_answer          TEXT NOT NULL
error_type              TEXT  -- 'calculation' | 'concept' | 'other'
error_description       TEXT  -- 錯誤描述
improvement_suggestion  TEXT  -- 改進建議
created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### 7. `exam_analysis` - 考卷診斷分析表
```sql
id                   INTEGER PRIMARY KEY
user_id              INTEGER NOT NULL (FK -> users)
skill_id             TEXT NOT NULL (FK -> skills_info)
curriculum           TEXT
grade                INTEGER
volume               TEXT
chapter              TEXT
section              TEXT
is_correct           BOOLEAN NOT NULL
error_type           TEXT  -- 'CALCULATION' | 'CONCEPTUAL' | 'LOGIC' | 'COMPREHENSION' | 'UNATTEMPTED'
confidence           FLOAT  -- 0.0 - 1.0
student_answer_latex TEXT
feedback             TEXT
image_path           TEXT NOT NULL  -- 上傳圖片路徑
created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### 8. `classes` - 班級表(教師功能)
```sql
id          INTEGER PRIMARY KEY
name        TEXT NOT NULL
teacher_id  INTEGER NOT NULL (FK -> users)
class_code  TEXT UNIQUE NOT NULL  -- 班級代碼
created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### 9. `class_students` - 班級學生關聯表
```sql
id          INTEGER PRIMARY KEY
class_id    INTEGER NOT NULL (FK -> classes)
student_id  INTEGER NOT NULL (FK -> users)
joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP
```

### 資料表關係圖
```
users (1) ----< (N) progress
users (1) ----< (N) mistake_logs
users (1) ----< (N) exam_analysis
users (teacher) (1) ----< (N) classes
classes (1) ----< (N) class_students >---- (N) users (student)

skills_info (1) ----< (N) skill_curriculum
skills_info (1) ----< (N) skill_prerequisites (自我參照)
skills_info (1) ----< (N) exam_analysis
```

---

## 🎯 核心功能模組

### 1. 技能模組系統 (Skills Module)

**設計理念**:每個數學知識點都是一個獨立的 Python 模組,實現「內容與程式碼分離」的高度模組化架構。

**技能模組標準介面**:
```python
# skills/abs_eq_simple.py (範例)
import random

def generate():
    """生成題目"""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    
    question_text = f"解方程式: |x - {a}| = {b}"
    solution1 = a + b
    solution2 = a - b
    
    return {
        "question_text": question_text,
        "question_latex": f"|x - {a}| = {b}",  # LaTeX 格式
        "solution": sorted([solution1, solution2]),
        "solution_steps": [
            f"根據絕對值定義,有兩種可能:",
            f"1) x - {a} = {b}  => x = {solution1}",
            f"2) x - {a} = -{b} => x = {solution2}"
        ]
    }

def check(user_answer, correct_answer):
    """檢查答案(可選實作)"""
    pass
```

**動態載入機制** (`core/routes.py`):
```python
import importlib

@bp.route('/skill/<skill_name>', methods=['GET', 'POST'])
def skill_practice(skill_name):
    # 動態載入技能模組
    module_path = f"skills.{skill_name}"
    skill_module = importlib.import_module(module_path)
    
    # 呼叫模組的 generate() 函式
    question_data = skill_module.generate()
    return render_template('index.html', question=question_data)
```

**技能涵蓋範圍**:
- 國中數學 (jh_*): 約 200+ 技能
- 高中普通科: 約 300+ 技能
- 高職技高: 約 200+ 技能
- 總計: **718 個獨立技能模組**

---

### 2. AI 整合系統 (Gemini API)

**核心檔案**: `core/ai_analyzer.py`

#### 功能 1: 手寫答案辨識與批改
```python
def analyze(image_data_url, context, api_key, prerequisite_skills=None):
    """
    分析學生手寫答案
    
    參數:
    - image_data_url: Base64 編碼的圖片
    - context: 題目內容
    - prerequisite_skills: 前置技能列表(用於建議補強)
    
    回傳 JSON:
    {
        "reply": "具體建議(Markdown格式)",
        "is_process_correct": true/false,
        "correct": true/false,
        "next_question": true/false,
        "error_type": "計算錯誤|觀念錯誤|粗心|其他",
        "error_description": "錯誤描述",
        "improvement_suggestion": "改進建議"
    }
    """
```

**Prompt 設計重點**:
- 扮演「有耐心、擅長鼓勵的數學家教」
- 針對「數學較弱、缺乏信心」的學生
- 提供具體、簡單、步驟清楚的建議
- 根據前置技能列表,建議回到哪個基礎技能練習

#### 功能 2: 題目技能識別
```python
def identify_skills_from_problem(problem_text):
    """
    從題目文字反向推斷所需技能
    用於「相似題生成」功能
    
    回傳: ['skill_id_1', 'skill_id_2', ...]
    """
```

#### 功能 3: 圖片測驗生成
```python
def generate_quiz_from_image(image_file, description):
    """
    從上傳的圖片(如課本截圖)生成測驗題
    
    回傳:
    [
        {
            "question_text": "...",
            "options": ["A", "B", "C"],
            "correct_answer": "B"
        },
        ...
    ]
    """
```

#### 功能 4: 考卷診斷分析
**核心檔案**: `core/exam_analyzer.py`

```python
def analyze_exam_image(image_path, curriculum, grade, volume):
    """
    分析考卷圖片,診斷學生弱點
    
    流程:
    1. OCR 辨識題目與學生作答
    2. 對應到 skill_curriculum 找出相關技能
    3. 判斷答對/答錯、錯誤類型
    4. 儲存到 exam_analysis 表
    5. 生成學習建議報告
    """
```

---

### 3. 學習路徑系統

**儀表板路由** (`app.py` - `/dashboard`):

#### 模式 1: 課程綱要瀏覽 (Curriculum View)
```
選擇課程類型(國中/普高/技高) 
  -> 選擇年級 
    -> 選擇冊別 
      -> 選擇章節 
        -> 顯示該章節所有技能
```

**資料查詢** (`core/utils.py`):
```python
def get_volumes_by_curriculum(curriculum):
    """取得某課程類型的所有冊別,按年級分組"""
    
def get_chapters_by_curriculum_volume(curriculum, volume):
    """取得某冊別的所有章節"""
    
def get_skills_by_volume_chapter(volume, chapter):
    """取得某章節的所有技能,含進度資訊"""
```

#### 模式 2: 技能分類瀏覽 (Category View)
```
顯示所有技能分類 
  -> 選擇分類 
    -> 顯示該分類所有技能
```

**進度顯示**:
- 連續答對次數 / 要求次數
- 總解題數
- 當前難度等級
- 最後練習時間

---

### 4. 練習系統

**練習頁面路由** (`core/routes.py` - `/practice/<skill_id>`):

**流程**:
1. **題目生成**: 呼叫 `skills/{skill_id}.py` 的 `generate()` 函式
2. **顯示題目**: 使用 MathJax 渲染 LaTeX 公式
3. **學生作答**: 
   - 文字輸入 (input_type='text')
   - 手寫上傳 (input_type='handwriting')
4. **AI 批改**: 
   - 文字答案: 直接比對
   - 手寫答案: 呼叫 `ai_analyzer.analyze()`
5. **即時回饋**: 
   - 顯示對錯、詳解、步驟
   - 記錄到 `progress` 表
   - 若答錯,記錄到 `mistake_logs` 表
6. **自適應推題**:
   - 連續答對 N 題 -> 提升難度 (current_level++)
   - 連續答錯 M 題 -> 降低難度 (current_level--)
   - 達到精熟標準 -> 建議學習下一個技能

**前置技能檢查**:
```python
def check_prerequisites(user_id, skill_id):
    """檢查使用者是否已精熟所有前置技能"""
    prerequisites = SkillPrerequisites.query.filter_by(skill_id=skill_id).all()
    for prereq in prerequisites:
        progress = Progress.query.filter_by(
            user_id=user_id, 
            skill_id=prereq.prerequisite_id
        ).first()
        if not progress or progress.consecutive_correct < threshold:
            return False, prereq.prerequisite_id
    return True, None
```

---

### 5. 管理系統 (Admin)

**路由前綴**: `/admin/*`

#### 5.1 技能管理 (`/admin/skills`)
- 新增/編輯/刪除技能
- 批次匯入技能資料 (Excel)
- 設定 Gemini Prompt
- 啟用/停用技能

#### 5.2 課程綱要管理 (`/admin/curriculum`)
- 技能與課程的映射關係
- 篩選器: 課程類型、年級、冊別、章節
- 批次匯入課程資料

#### 5.3 前置技能管理 (`/admin/prerequisites`)
- 設定技能之間的依賴關係
- 視覺化技能樹(未來功能)

#### 5.4 資料庫維護 (`/admin/db_maintenance`)
- 匯出資料庫為 Excel
- 清空特定資料表
- 刪除資料表
- 資料庫備份/還原

---

### 6. 教師功能

**教師儀表板** (`/teacher_dashboard`):
- 班級管理 (建立班級、生成班級代碼)
- 學生管理 (查看班級學生名單)
- 學習進度追蹤 (查看學生練習記錄)
- 錯題分析報告 (查看學生常見錯誤)

**權限控制**:
```python
@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('權限不足', 'warning')
        return redirect(url_for('dashboard'))
    # ...
```

---

## 🔄 資料流程

### 1. 資料匯入流程
```
Excel/CSV 資料檔案 (datasource/)
  |
  v
import_data.py / import_curriculum.py
  |
  v
Pandas DataFrame 處理
  |
  v
SQLAlchemy ORM 物件
  |
  v
db.session.add() + commit()
  |
  v
SQLite 資料庫 (instance/math_master.db)
```

### 2. 練習流程
```
使用者選擇技能
  |
  v
Flask 路由 (/practice/<skill_id>)
  |
  v
importlib 動態載入 skills/{skill_id}.py
  |
  v
呼叫 generate() 生成題目
  |
  v
Jinja2 渲染 index.html + MathJax
  |
  v
使用者作答 (文字/手寫)
  |
  v
POST 提交答案
  |
  v
[文字] 直接比對 / [手寫] Gemini API 分析
  |
  v
更新 progress 表 + (若錯誤) mistake_logs 表
  |
  v
顯示結果 + 詳解 + 下一題
```

### 3. 考卷診斷流程
```
教師/學生上傳考卷圖片
  |
  v
Flask 路由 (/exam/upload)
  |
  v
儲存圖片到 uploads/
  |
  v
Gemini Vision API 分析
  |
  v
OCR 辨識 + 技能對應 + 答案判斷
  |
  v
儲存到 exam_analysis 表
  |
  v
生成診斷報告 (弱點技能、建議練習順序)
```

---

## 🔧 開發環境設定

### 1. 環境變數 (`.env`)
```bash
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 初始化資料庫
```bash
python reset_and_init_db.py
```

### 4. 匯入資料
```bash
python import_data.py
python import_curriculum.py
python import_dependencies.py
```

### 5. 啟動應用
```bash
python app.py
# 訪問 http://127.0.0.1:5000
```

---

## 📝 最近開發歷程 (重要更新)

### 2025-12-02: 實作「跳過程式碼生成」功能
**背景**: 教科書匯入功能中,自動生成 Python 解題程式碼耗時較長
**實作**:
- 前端新增 `skip_code_gen` 核取方塊
- 後端接收參數,條件性執行 `auto_generate_skill_code` 迴圈
- 提供使用者選擇是否生成程式碼的彈性

### 2025-12-01: 資料庫 Schema 遷移
**目標**: 從舊 schema 遷移到新 schema
**新增資料表**:
- `mistake_logs` (錯題記錄)
- `classes` (班級)
- `class_students` (班級學生關聯)
- `exam_analysis` (考卷診斷)

**遷移腳本**: `migrate_db.py`

### 2025-11-28: 標準化管理頁面
**目標**: 統一 `admin_examples.html` 與 `admin_skills.html` 的 UI/UX
**實作**:
- 卡片式篩選器
- 動態級聯下拉選單 (課程->冊別->章節->技能)
- Flash 訊息顯示
- 自動提交篩選

### 2025-11-27: 更新 README.md
**目標**: 配合育秀盃競賽,強化專案說明
**重點**:
- 突出 AI 教科書匯入功能
- 對應「智慧校園」主題
- 說明如何幫助「數學弱勢學生」

### 2025-11-18: 圖片上傳功能完善
**新增**:
- `uploads/` 資料夾
- `UPLOAD_FOLDER` 設定
- `secure_filename` 安全性檢查
- 圖片儲存後再傳給 AI 分析

### 2025-11-17: 圖片測驗生成功能
**新增路由**:
- `/image-quiz-generator` (頁面)
- `/generate-quiz-from-image` (API)

**功能**: 上傳圖片(如課本截圖) + 文字描述 -> AI 生成測驗題

### 2025-11-16: 相似題生成功能
**新增**:
- `identify_skills_from_problem()` (AI 題目技能識別)
- `/generate-similar-questions` (API)
- `/similar-questions-page` (頁面)

**功能**: 輸入一道題目 -> AI 識別技能 -> 生成相似題

---

## 🎓 核心設計模式

### 1. 模組化 (Modularity)
- **技能模組**: 每個知識點獨立檔案,遵循統一介面
- **藍圖 (Blueprint)**: `core_bp` (管理功能), `practice_bp` (練習功能)
- **關注點分離**: models (資料) / routes (邏輯) / templates (視圖)

### 2. 資料驅動 (Data-Driven)
- 課程內容儲存在 CSV/Excel,非寫死在程式碼
- 技能定義、課程綱要、依賴關係都可透過匯入腳本更新
- 非技術人員也能管理課程內容

### 3. 動態載入 (Dynamic Loading)
- 使用 `importlib` 動態載入技能模組
- 無需修改核心程式碼即可新增技能
- 支援熱插拔

### 4. ORM 模式
- SQLAlchemy 提供物件導向的資料庫操作
- `db.relationship` 定義表格關聯
- 避免手寫 SQL,提高可維護性

### 5. 前後端分離 (部分)
- 部分功能使用 AJAX (如圖片測驗生成)
- 大部分使用傳統 Server-Side Rendering (Jinja2)

---

## 🚀 未來開發方向

### 短期目標
1. **完善考卷診斷功能**
   - 提高 OCR 準確率
   - 優化技能對應演算法
   - 生成視覺化診斷報告

2. **教師功能增強**
   - 班級學習進度儀表板
   - 匯出學生報告 (PDF/Excel)
   - 自訂作業指派

3. **學習路徑優化**
   - 基於錯題記錄的智慧推薦
   - 視覺化技能樹
   - 學習時間預估

### 中期目標
1. **多模態 AI 整合**
   - 語音輸入題目
   - 影片講解生成
   - 互動式解題步驟

2. **遊戲化機制**
   - 成就系統
   - 排行榜
   - 虛擬獎勵

3. **社群功能**
   - 學生討論區
   - 同儕互助
   - 題目分享

### 長期目標
1. **擴展學科**
   - 物理、化學
   - 英文、國文

2. **行動應用**
   - iOS/Android App
   - 離線模式

3. **大數據分析**
   - 學習行為分析
   - 預測學習成效
   - 個人化學習路徑

---

## 🔍 關鍵技術細節

### 1. Gemini API 使用
**模型**: `gemini-2.5-flash`
**配置**: `core/ai_analyzer.py` - `configure_gemini()`
**用途**:
- 手寫辨識 (Vision API)
- 題目分析 (Text API)
- 測驗生成 (Multimodal API)

**Prompt 工程重點**:
- 明確角色定位 (「功文數學助教」)
- 目標受眾 (「數學弱勢學生」)
- 輸出格式 (強制 JSON,避免 Markdown 標記)
- 重試機制 (最多 2 次)

### 2. 前置技能系統
**資料表**: `skill_prerequisites`
**查詢範例**:
```python
# 取得某技能的所有前置技能
prerequisites = db.session.query(SkillInfo)\
    .join(SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id)\
    .filter(SkillPrerequisites.skill_id == target_skill_id)\
    .all()
```

**應用**:
- 練習前檢查 (提示先學前置技能)
- AI 批改時建議補強 (傳入 `prerequisite_skills` 參數)
- 學習路徑規劃

### 3. 自適應難度
**邏輯** (`core/routes.py`):
```python
if is_correct:
    progress.consecutive_correct += 1
    progress.consecutive_wrong = 0
    if progress.consecutive_correct >= threshold:
        progress.current_level += 1  # 升級
        progress.consecutive_correct = 0
else:
    progress.consecutive_wrong += 1
    progress.consecutive_correct = 0
    if progress.consecutive_wrong >= 3:
        progress.current_level = max(1, progress.current_level - 1)  # 降級
        progress.consecutive_wrong = 0
```

### 4. LaTeX 渲染
**前端**: MathJax 3.x
**使用**:
```html
<script>
MathJax = {
  tex: {inlineMath: [['$', '$'], ['\\(', '\\)']]}
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

**後端生成**:
```python
from sympy import latex, sympify
question_latex = latex(sympify("x^2 + 2*x + 1"))
# 輸出: "x^{2} + 2 x + 1"
```

---

## 📊 專案統計

- **程式碼行數**: 約 15,000+ 行 (不含技能模組)
- **技能模組數**: 718 個
- **資料表數**: 9 個核心表
- **路由數**: 約 30+ 個
- **模板數**: 15 個
- **資料檔案**: 120 個 CSV/Excel

---

## 🤝 開發協作建議

### 與 AI 討論時的重點
1. **明確指定模組**: 如「修改 `core/routes.py` 的練習路由」
2. **提供上下文**: 如「這個功能與前置技能系統相關」
3. **說明目標使用者**: 如「針對數學弱勢學生,需要更簡單的提示」
4. **考慮資料庫影響**: 如「這個改動需要新增欄位嗎?」
5. **注意向後相容**: 如「現有的 718 個技能模組會受影響嗎?」

### 程式碼風格
- **命名**: 使用描述性名稱 (如 `get_skills_by_volume_chapter`)
- **註解**: 中文註解,說明業務邏輯
- **Docstring**: 重要函式提供說明
- **錯誤處理**: 使用 try-except,記錄到 log
- **Flash 訊息**: 使用者操作回饋 (success/warning/danger)

---

## 📚 參考資料

- [Flask 官方文件](https://flask.palletsprojects.com/)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)
- [Google Gemini API](https://ai.google.dev/docs)
- [MathJax 文件](https://docs.mathjax.org/)
- [功文數學教學法](https://www.kumon.com.tw/)

---

## 📞 聯絡資訊

**專案類型**: 教育科技 (EdTech) - AI 驅動學習平台
**目標用戶**: 高中職數學弱勢學生、數學教師
**開發狀態**: 持續開發中
**競賽**: 育秀盃 AI 應用競賽 - 智慧校園組

---

**文件版本**: v1.0
**最後更新**: 2025-12-03
**文件用途**: 提供給 Gemini Pro 3 進行後續開發討論

---

## ✅ 使用此文件的方式

當你與 Gemini Pro 3 討論專案時,可以:

1. **直接貼上整份文件**: 讓 AI 完整理解專案脈絡
2. **引用特定章節**: 如「請參考『核心功能模組 > 技能模組系統』部分」
3. **補充最新資訊**: 如「在此文件基礎上,我們新增了...」
4. **提出具體問題**: 如「根據資料庫設計,如何實作...」

**範例對話開場**:
```
我正在開發一個功文數學智慧學習平台,專案詳情請參考附上的文件。
我想討論如何優化考卷診斷功能的 OCR 準確率,特別是針對手寫數學公式的辨識。
目前使用 Gemini Vision API,但在複雜公式(如分數、根號)的辨識上還有改進空間。
```

這樣 AI 就能基於完整的專案背景,提供更精準、更符合專案架構的建議!
