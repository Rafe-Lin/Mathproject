# 錯題本功能執行邏輯文件

## 1. 功能概述
「錯題本」功能旨在提供學生一個介面，記錄並回顧他們在紙本考卷中做錯的題目。此功能支援手動新增錯題，並整合了自動記錄機制，以提升學習效率。

## 2. 資料庫設計
### 表格名稱
`mistake_notebook_entries`

### 檔案位置
*   `models.py`: 定義 ORM 模型 `MistakeNotebookEntry`。
*   `add_mistake_notebook_table.py`: 建立 `mistake_notebook_entries` 表格的腳本。

### 欄位 (Columns)
| 欄位名稱          | 類型                        | 說明                                           |
| :-------------- | :-------------------------- | :--------------------------------------------- |
| `id`            | `Integer`, Primary Key      | 錯題記錄的唯一識別碼                           |
| `student_id`    | `Integer`, Foreign Key      | 學生 ID，關聯至 `users` 表                     |
| `exam_image_path` | `String(255)`, Nullable     | 上傳的錯題圖片在伺服器上的相對路徑             |
| `question_data` | `JSON`, Nullable            | 題目相關的額外資料 (例如裁切座標、文字描述等) |
| `notes`         | `Text`, Nullable            | 學生針對此錯題的筆記或心得                     |
| `skill_id`      | `String(50)`, Foreign Key   | 關聯的知識點 ID，關聯至 `skills_info` 表      |
| `created_at`    | `DateTime`, Default: UTC Now | 記錄建立時間                                   |

### 關係 (Relationships)
*   `MistakeNotebookEntry` 與 `User` (通過 `student_id`) 之間存在多對一關係。
*   `MistakeNotebookEntry` 與 `SkillInfo` (通過 `skill_id`) 之間存在多對一關係。

## 3. 手動新增流程
### 後端邏輯
*   **檔案位置**: `core/routes.py`

#### API 端點 (API Endpoints)
1.  **上傳錯題圖片**:
    *   **路徑**: `POST /mistake-notebook/upload-image`
    *   **功能**: 處理圖片上傳請求，儲存至 `static/mistake_uploads/<user_id>/`，並返回圖片路徑。
2.  **新增錯題記錄**:
    *   **路徑**: `POST /mistake-notebook/add`
    *   **功能**: 將包含圖片路徑、知識點、筆記等資訊的錯題記錄儲存至資料庫。
3.  **獲取所有錯題記錄**:
    *   **路徑**: `GET /api/mistake-notebook`
    *   **功能**: 返回當前使用者所有的錯題記錄，供前端頁面動態渲染。
4.  **顯示頁面**:
    *   **路徑**: `GET /mistake-notebook` -> 渲染錯題本主頁 `mistake_notebook.html`。
    *   **路徑**: `GET /add_mistake_page` -> 渲染新增錯題的表單頁 `add_mistake.html`。

### 前端介面
*   **檔案位置**: `templates/`

1.  **儀表板 (`dashboard.html`)**:
    *   新增「📝 錯題本」導航連結。
2.  **錯題列表頁 (`mistake_notebook.html`)**:
    *   使用 JavaScript 調用 `/api/mistake-notebook` API 來動態顯示所有錯題記錄。
3.  **新增錯題頁 (`add_mistake.html`)**:
    *   提供一個表單，讓使用者上傳圖片、選擇知識點和填寫筆記。
    *   JavaScript 負責處理圖片預覽、上傳及最終表單提交。

## 4. 自動化記錄功能
### a. 自動記錄系統練習錯題
*   **觸發點**: 使用者在系統練習題頁面回答問題，且答案被判定為錯誤時。
*   **檔案位置**: `core/routes.py`
*   **函式**: `@practice_bp.route('/check_answer', methods=['POST'])`
*   **執行邏輯**:
    1.  在 `check_answer` 函式中，當 `is_correct` 變數為 `False` 時觸發。
    2.  為了避免重複記錄，系統會檢查資料庫中是否已存在針對同一使用者、同一知識點、同一題目的錯題記錄。
    3.  若無重複，則建立一個新的 `MistakeNotebookEntry` 物件。
    4.  `exam_image_path` 欄位設為 `None`。
    5.  `question_data` 欄位儲存該題的文字內容 (例如 `{'type': 'system_question', 'text': '...'}`)。
    6.  `notes` 欄位預設為「系統練習題自動記錄」。
    7.  將此記錄與使用者進度更新 (`update_progress`) 在同一個資料庫事務中提交。

### b. 自動記錄考卷診斷錯題
*   **觸發點**: 使用者上傳考卷圖片並經由 AI 診斷，其中有題目被分析為錯誤時。
*   **檔案位置**: `core/exam_analyzer.py`
*   **函式**: `save_analysis_result()`
*   **執行邏輯**:
    1.  在 `save_analysis_result` 函式儲存 `ExamAnalysis` 結果的過程中觸發。
    2.  當 AI 分析結果中的 `is_correct` 欄位為 `False` 時，執行額外邏輯。
    3.  為了避免重複，系統會檢查是否已針對同一張圖片路徑 (`exam_image_path`) 建立過錯題記錄。
    4.  若無重複，則建立一個新的 `MistakeNotebookEntry` 物件。
    5.  `exam_image_path` 欄位設為本次診斷的原始圖片路徑。
    6.  `question_data` 欄位儲存 AI 的分析結果，包括匹配的單元和錯誤分析詳情 (例如 `{'type': 'exam_diagnosis', 'matched_unit': ..., 'error_analysis': ...}`)。
    7.  `notes` 欄位預設為「考卷診斷自動記錄」。
    8.  將此錯題記錄與 `ExamAnalysis` 記錄在同一個資料庫事務中提交。

## 5. Git 版本控制
此文件的變更與功能實作已在以下 Git 提交中記錄：

*   **初始功能提交**: `feat: Implement Mistake Notebook feature` (commit `06fc329`)
    *   建立錯題本的資料庫模型、手動新增/查詢的後端 API 及前端頁面。
*   **自動化功能提交**: `feat: Auto-log incorrect answers to Mistake Notebook` (commit `77a31eb`)
    *   在 `check_answer` 和 `save_analysis_result` 中新增自動記錄錯題的邏輯。