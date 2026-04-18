# 專案架構與實作邏輯詳細說明

本文檔旨在深入解析 MathMaster 專案的架構、設計模式與核心功能的具體實作方式，為開發者提供一份清晰、詳盡的指南。

## 1. 總體架構與設計理念

本專案採用了經典的 **Python Flask + SQLAlchemy** Web 框架組合，其核心設計理念是 **模組化** 與 **資料驅動**。

- **模組化 (Modularity)**：專案最大的特色是將每一個數學知識點（技能）都設計成一個獨立的 Python 模組（存放於 `skills/` 目錄）。這種設計讓新增、修改或移除一個知識點變得極為簡單，只需操作對應的檔案，而無需改動核心業務邏輯，大大提高了專案的可擴充性和可維護性。

- **資料驅動 (Data-Driven)**：專案的課程內容、知識點清單及其依賴關係，都儲存在外部的 CSV/Excel 檔案中（`datasource/` 目錄）。透過獨立的匯入腳本 (`import_*.py`) 將這些資料載入資料庫。這實現了「內容與程式碼的分離」，讓非技術人員（如課程設計者）也能方便地管理和更新課程內容。

---

## 2. 應用程式執行流程

一個典型的使用者請求到接收回應的完整流程如下：

1.  **啟動應用**：開發者在終端執行 `python app.py`。
2.  **Flask 初始化**：`app.py` 建立 Flask app 實例，載入 `config.py` 中的設定（如資料庫路徑），初始化 SQLAlchemy，並註冊 `core` 藍圖。
3.  **使用者發出請求**：使用者在瀏覽器中輸入網址，例如 `http://127.0.0.1:5000/dashboard`。
4.  **路由匹配**：Flask 接收到請求，並在已註冊的 `core` 藍圖中尋找匹配 `@bp.route('/dashboard')` 的視圖函式。
5.  **執行視圖函式**：Flask 執行對應的函式。該函式會：
    a. **與資料庫互動**：透過 `models.py` 中定義的 ORM 模型（如 `User`, `UserSkill`）向資料庫查詢所需資料。
    b. **執行業務邏輯**：進行必要的計算或資料處理。
    c. **渲染模板**：呼叫 `render_template('dashboard.html', ...)`，並將查詢到的資料作為參數傳遞給前端模板。
6.  **Jinja2 模板引擎**：Flask 的 Jinja2 引擎會解析 `dashboard.html` 檔案。它會執行模板中的邏輯（如迴圈、條件判斷），並將從後端傳來的變數填入 HTML 的指定位置。
7.  **回傳 HTML**：伺服器最終生成一個純 HTML 頁面，將其回傳給使用者的瀏覽器。
8.  **瀏覽器渲染**：瀏覽器接收到 HTML 後，進行解析和渲染，最終呈現出使用者看到的網頁。

---

## 3. 核心檔案與模組詳解

### 3.1. `models.py` - 資料庫模型層

此檔案是應用程式的資料基礎，它定義了所有業務實體的結構以及它們之間的關係。

```python
# models.py (示意程式碼)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    # ...
    # 'skills' 屬性讓你可以透過 user.skills 訪問該使用者所有相關的 UserSkill 記錄
    skills = db.relationship('UserSkill', backref='user', lazy='dynamic')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(128), unique=True) # 程式內部使用的名稱, e.g., "abs_eq_simple"
    display_name = db.Column(db.String(128)) # 顯示給使用者的名稱, e.g., "簡單絕對值方程式"
    # ...

# 關聯表：Prerequisite (技能前置依賴)
class Prerequisite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 'skill_id' 指的是需要先修技能的那個技能
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    # 'prerequisite_id' 指的是作為前置條件的技能
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('skill.id'))

# 關聯表：UserSkill (使用者與技能的關係)
class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    proficiency = db.Column(db.Float, default=0.0) # 熟練度
    # ...
```

**實作詳解**：
- **ORM 對應**：每個類別對應資料庫中的一個表格。類別的屬性（如 `User.username`）對應表格的一個欄位。
- **`db.relationship`**：這是 SQLAlchemy ORM 的精華。它定義了類別之間的關聯，但**不會**在資料庫中建立實際的欄位。它是一個高階的視圖，讓你能用物件導向的方式進行查詢。
    - `backref='user'`：這是一個非常方便的參數。它會自動在 `UserSkill` 模型上建立一個名為 `user` 的屬性，讓你可以透過 `user_skill.user` 直接反向查詢到對應的 `User` 物件。
    - `lazy='dynamic'`：表示當你訪問 `user.skills` 時，SQLAlchemy 不會立刻載入所有相關的 `UserSkill` 記錄，而是回傳一個查詢物件 (Query Object)。這在大數據量下非常高效，因為你可以接著對這個查詢物件套用過濾條件（如 `user.skills.filter_by(...)`）。
- **`db.ForeignKey`**：這是定義**外鍵**的關鍵，它在資料庫層面建立了表格之間的引用約束。`Prerequisite` 和 `UserSkill` 都是典型的**多對多關聯**的實現方式。

### 3.2. `core/routes.py` - 路由與業務邏輯層

這是處理使用者互動的核心，它將 URL、後端邏輯和前端頁面串連起來。

```python
# core/routes.py (示意程式碼)
from flask import render_template, request, redirect, url_for
from . import bp # 藍圖
from app.models import User, Skill
import importlib

@bp.route('/skill/<skill_name>', methods=['GET', 'POST'])
def skill_practice(skill_name):
    # 1. 動態載入技能模組
    try:
        # 安全地組合模組路徑，並使用 importlib 動態匯入
        module_path = f"app.skills.{skill_name}"
        skill_module = importlib.import_module(module_path)
    except ImportError:
        return "Skill not found", 404

    if request.method == 'POST':
        # 3. 處理使用者提交的答案
        user_answer = request.form.get('answer')
        correct_answer = request.form.get('correct_answer_hidden') # 從隱藏欄位取得正確答案
        # ... 進行答案比對、更新 UserSkill 的熟練度等 ...
        # 接著可以產生下一題或導向到結果頁面
        return redirect(url_for('core.skill_practice', skill_name=skill_name))

    # 2. 產生問題並渲染頁面 (GET 請求)
    question_data = skill_module.generate_question() # 呼叫模組的函式
    return render_template('skill_practice.html', question=question_data, skill_name=skill_name)
```

**實作詳解**：
- **動態路由**：`<skill_name>` 語法讓這個函式可以處理所有符合 `/skill/...` 格式的 URL。
- **動態模組載入**：這是此專案的**核心技巧**。
    1.  `importlib.import_module(module_path)` 是 Python 的標準函式庫，它允許程式在執行期間根據一個字串來動態地匯入一個模組。
    2.  程式根據 URL 傳入的 `skill_name` (例如 `abs_eq_simple`)，組合出模組的完整路徑 `app.skills.abs_eq_simple`。
    3.  `importlib` 載入這個模組，`skill_module` 就變成了 `abs_eq_simple.py` 這個檔案的物件表示。
    4.  接著就可以像正常的模組一樣呼叫它內部的函式，如 `skill_module.generate_question()`。
- **GET 與 POST 分流**：在同一個 URL 下，使用 `request.method` 來區分是初次載入頁面 (GET) 還是提交表單 (POST)，這是 Web 開發的標準實踐。
- **隱藏欄位傳遞答案**：為了在使用者提交答案 (POST) 後能進行比對，正確答案在產生題目 (GET) 時，被一併儲存在前端頁面的一個隱藏 `<input type="hidden">` 欄位中。這是一種簡單的狀態保持方法。

### 3.3. `skills/abs_eq_simple.py` - 技能模組層

這是專案的內容產生引擎，每個檔案都是一個獨立的、可插拔的知識點。

```python
# skills/abs_eq_simple.py (示意程式碼)
import random
from sympy import sympify, latex

def generate_question():
    # 1. 隨機化參數
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    
    # 2. 構建問題
    # 使用 LaTeX 格式以利於前端顯示 (例如透過 MathJax 函式庫)
    question_text = f"解方程式: |x - {a}| = {b}"
    question_latex = latex(sympify(question_text, evaluate=False))

    # 3. 計算答案與解法
    solution1 = a + b
    solution2 = a - b
    solutions = sorted([solution1, solution2])
    
    steps = [
        f"根據絕對值的定義，我們有兩種可能：",
        f"1) x - {a} = {b}  =>  x = {a} + {b} = {solution1}",
        f"2) x - {a} = -{b}  =>  x = {a} - {b} = {solution2}",
        f"所以解為 x = {solution1} 或 x = {solution2}"
    ]

    # 4. 格式化回傳
    return {
        "question_text": question_text,
        "question_latex": question_latex,
        "solution": solutions, # 答案可能有多個，用列表儲存
        "solution_steps": steps
    }
```

**實作詳解**：
- **標準化介面**：此檔案提供了一個 `generate_question()` 函式，這是它與主程式 `routes.py` 溝通的**契約 (Contract)**。所有技能模組都應遵循此介面。
- **隨機化**：使用 `random` 函式庫來產生不同的題目參數，實現「無限題庫」的效果。
- **使用 SymPy 進行 LaTeX 轉換**：`sympy` 是一個強大的符號運算函式庫。這裡使用 `latex()` 函式將純文字的數學式轉換成 LaTeX 格式。前端網頁可以利用 MathJax 或 KaTeX 等 JS 函式庫將 LaTeX 優美地渲染成數學符號。
- **結構化回傳**：函式回傳一個字典 (Dictionary)，清晰地組織了題目、答案和解題步驟。這種結構化的資料讓前端模板處理起來非常方便。

### 3.4. `import_data.py` - 資料匯入腳本

此腳本是資料從靜態檔案流入動態資料庫的橋樑。

```python
# import_data.py (示意程式碼)
import pandas as pd
from app import create_app # 引入 app factory
from app.models import db, Skill, Prerequisite

def import_skills(filepath):
    app = create_app() # 建立 app context
    with app.app_context():
        df = pd.read_csv(filepath)
        for index, row in df.iterrows():
            # 檢查技能是否已存在
            existing_skill = Skill.query.filter_by(skill_name=row['skill_name']).first()
            if not existing_skill:
                new_skill = Skill(
                    skill_name=row['skill_name'],
                    display_name=row['display_name'],
                    category=row['category']
                )
                db.session.add(new_skill)
        db.session.commit() # 一次性提交所有新技能

if __name__ == '__main__':
    import_skills('datasource/skill_curriculum.csv')
    # ... 同理可以寫 import_prerequisites ...
```

**實作詳解**：
- **App Context**：因為此腳本是獨立執行的，它沒有 Flask 的請求上下文。為了能使用 app 的設定（如資料庫連線）和擴充套件（如 SQLAlchemy 的 `db` 物件），必須手動建立一個應用程式上下文 (`with app.app_context():`)。
- **使用 Pandas**：`pandas` 函式庫是處理 CSV 或 Excel 的最佳工具。`pd.read_csv()` 可以輕鬆地將檔案讀取為一個 DataFrame。
- **ORM 操作**：
    1.  `df.iterrows()` 遍歷 DataFrame 的每一行。
    2.  `Skill.query.filter_by(...).first()`：這是一個典型的 ORM 查詢，用來檢查資料是否已存在，避免重複匯入。
    3.  `new_skill = Skill(...)`：建立一個 `Skill` 物件，將 CSV 中的資料填入。
    4.  `db.session.add(new_skill)`：將這個新物件加入到 SQLAlchemy 的「工作階段 (Session)」中。此時資料還在記憶體裡，並未寫入資料庫。
    5.  `db.session.commit()`：將 Session 中暫存的所有變更（新增、修改、刪除）一次性地寫入資料庫。這比每新增一筆就 commit 一次要高效得多。

### 3.5. `templates/skill_practice.html` - 前端模板層

這是使用者直接互動的介面，負責展示題目和收集答案。

```html
<!-- templates/skill_practice.html (示意程式碼) -->
{% extends "layout.html" %} <!-- 1. 繼承基礎模板 -->

{% block content %}
    <h2>練習：{{ question.display_name }}</h2>
    
    <!-- 2. 顯示題目 (MathJax 會自動渲染) -->
    <div id="question-body">
        <p>{{ question.question_latex }}</p>
    </div>

    <!-- 3. 提交答案的表單 -->
    <form method="POST" action="{{ url_for('core.skill_practice', skill_name=skill_name) }}">
        <input type="text" name="answer" placeholder="請輸入你的答案">
        
        <!-- 4. 隱藏欄位，用來向後端傳遞正確答案以供核對 -->
        <input type="hidden" name="correct_answer_hidden" value="{{ question.solution | join(',') }}">
        
        <button type="submit">提交答案</button>
    </form>
{% endblock %}
```

**實作詳解**：
1.  **模板繼承**：`{% extends "layout.html" %}` 表示此頁面繼承自 `layout.html`。`layout.html` 中定義了網站共用的 HTML 結構、導覽列、頁尾等。`{% block content %}` 和 `{% endblock %}` 之間的內容會被插入到父模板的相應位置。這避免了在每個頁面都重複寫相同的 HTML 程式碼。
2.  **渲染變數**：`{{ ... }}` 是 Jinja2 的變數渲染語法。Flask 視圖函式中 `render_template` 傳遞的 `question` 物件，其屬性可以在這裡被直接訪問和顯示，如 `{{ question.display_name }}`。
3.  **表單提交**：`<form>` 的 `action` 屬性使用 `url_for()` 函式來動態產生提交的目標 URL。這樣即使未來路由路徑改變，也不需要手動修改 HTML。
4.  **過濾器 (Filter)**：`{{ question.solution | join(',') }}` 中的 `| join(',')` 是一個 Jinja2 過濾器。如果後端傳來的 `question.solution` 是一個 Python 列表 (e.g., `[12, -8]`)，這個過濾器會將其轉換為一個用逗號分隔的字串 (e.g., `"12,-8"`)，以便儲存在 `value` 屬性中。

---
## 4. 總結

本專案是一個結構清晰、高度模組化、易於擴充的數學學習平台。它巧妙地利用了 Flask 的藍圖、SQLAlchemy 的 ORM、動態模組載入以及資料與程式碼分離的設計原則，構成了一個穩健且靈活的系統。理解以上各個模組的職責和它們之間的互動方式，是掌握此專案的關鍵。
