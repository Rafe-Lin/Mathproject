# 自適應學習系統實作報告 (2026年1月30日)

本文檔詳細記錄了根據「自適應學習系統實作計畫書」所進行的所有修改與新增功能。

## 總覽

本次實作將自適應學習功能分為三個層級：單一單元、多單元組合、以及總複習。從資料庫模型擴充、後端演算法、推薦引擎、前端介面，到 LLM 錯誤分析，所有功能均已按計畫完成。

---

## Phase 1: 資料庫模型擴充 (Data Foundation)

**檔案**: `models.py`

**修改說明**:
為了支援自適應學習演算法，在現有模型中新增了必要欄位，並新增 `StudentAbility` 模型來追蹤學生的個人化能力值。

**程式碼變更**:

1.  **`SkillInfo` 模型**:
    *   新增 `importance` 欄位，用於知識點重要性權重。
    ```python
    class SkillInfo(db.Model):
        # ... 現有欄位 ...
        importance = db.Column(db.Float, nullable=False, default=1.0) # 知識點重要性權重
        # ...
    ```

2.  **`TextbookExample` 模型**:
    *   新增 `difficulty_h` 欄位，用於演算法的 H 值。`difficulty_level` 欄位已存在，並在計畫中被保留。
    ```python
    class TextbookExample(db.Model):
        # ... 現有欄位 ...
        difficulty_level = db.Column(db.Integer, nullable=False, default=1) # 難度標籤 1-5
        difficulty_h = db.Column(db.Float, nullable=False, default=1.0) # 演算法 H 值
        # ...
    ```

3.  **新增 `StudentAbility` 模型**:
    *   建立新模型 `StudentAbility`，用於儲存學生的綜合能力 (A)、觀念能力 (U) 和計算熟練度 (C)。
    ```python
    from datetime import datetime

    class StudentAbility(db.Model):
        __tablename__ = 'student_abilities'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id'), nullable=False, index=True)
        ability_a = db.Column(db.Float, nullable=False, default=20.0) # 綜合能力 A (0-200)
        concept_u = db.Column(db.Float, nullable=False, default=20.0) # 觀念能力 U (0-100)
        calculation_c = db.Column(db.Float, nullable=False, default=20.0) # 計算熟練度 C (0-100)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc'),)
    ```

---

## Phase 2: 後端能力更新演算法實作

**檔案**: `core/adaptive_config.py`, `core/adaptive_engine.py`, `core/routes/practice.py`

**修改說明**:
實作了自適應學習演算法的核心邏輯，包括常數定義、能力值更新函數，並整合到答案檢查流程。

1.  **新增 `core/adaptive_config.py`**:
    *   定義了所有自適應演算法所需的常數，如能力值範圍、時間因子、懲罰因子和推薦系統權重。
    ```python
    # core/adaptive_config.py
    ABILITY_DEFAULT, ABILITY_MAX = 20.0, 200.0
    CONCEPT_DEFAULT, CONCEPT_MAX = 20.0, 100.0
    CALCULATION_DEFAULT, CALCULATION_MAX = 20.0, 100.0
    AVG_ANSWER_TIME_SECONDS, MAX_ANSWER_TIME_SECONDS = 60, 180
    T_FACTOR_FAST, T_FACTOR_NORMAL, T_FACTOR_SLOW = 1.2, 1.0, 0.8
    ERROR_PENALTY_FACTOR = 0.6
    # ... (其他推薦系統相關常數) ...
    ```

2.  **新增 `update_student_ability` 函式到 `core/adaptive_engine.py`**:
    *   此函式根據學生的答題表現（是否正確、作答時間），計算並更新其在特定知識點上的綜合能力 (A)、觀念能力 (U) 和計算熟練度 (C)。
    ```python
    # core/adaptive_engine.py
    # ... (imports) ...
    def update_student_ability(user_id, skill_id, question_id, is_correct, time_taken_seconds):
        # ... 根據公式更新 A, U, C 值 ...
        db.session.commit()
    ```

3.  **修改 `core/routes/practice.py`**:
    *   在 `check_answer` 路由中，當處於 `adaptive` 模式時，呼叫 `update_student_ability` 更新學生能力。
    ```python
    # core/routes/practice.py
    # ... (imports) ...
    from core.adaptive_engine import update_student_ability
    # ...
    @practice_bp.route('/check_answer', methods=['POST'])
    def check_answer():
        # ...
        is_adaptive_mode = request.json.get('mode') == 'adaptive'
        if is_adaptive_mode:
            # ... 計算 time_taken ...
            update_student_ability(user_id=current_user.id, skill_id=skill_id,
                                   question_id=question_id, is_correct=is_correct,
                                   time_taken_seconds=float(time_taken))
        # ...
    ```

---

## Phase 3: 題目推薦引擎實作

**檔案**: `core/adaptive_engine.py`, `core/routes/practice.py`

**修改說明**:
建立了智慧推薦系統，能夠根據學生能力和多種推薦模式，推薦最合適的題目。

1.  **重構 `recommend_question` 函式到 `core/adaptive_engine.py`**:
    *   函式簽名改為 `recommend_question(user_id, skill_ids: list)`，可接受一個技能 ID 列表。
    *   實作了五條推薦規則（難度適中性、變化性、觀念強化、計算強化、知識點重要性）來計算推薦分數 (RS)。
    *   引入 `get_all_prerequisites` 輔助函式，用於在多單元和總複習模式下獲取所有相關技能（包括前置技能）。
    ```python
    # core/adaptive_engine.py
    # ... (imports) ...
    def get_all_prerequisites(initial_skill_ids: list) -> set:
        # ... 遞迴查詢所有前置技能 ...
        pass

    def recommend_question(user_id, skill_ids: list):
        # ... 獲取學生在這些 skill_ids 上的能力 ...
        # ... 遍歷 TextbookExample，計算 RS 分數 ...
        # ... 返回分數最高的題目 ...
    ```

2.  **修改 `/get_adaptive_question` 路由到 `core/routes/practice.py`**:
    *   修改路由以接收 `mode` (`single`, `multiple`, `review`) 和 `skill_ids` (逗號分隔字串) 或 `curriculum` 參數。
    *   根據不同的 `mode`，準備好要傳遞給 `recommend_question` 的完整技能 ID 列表（包括呼叫 `get_all_prerequisites` 擴充技能池）。
    *   正確地將推薦題目的 `skill_id` 存入 session (`set_current`)，以供後續 `check_answer` 使用。
    ```python
    # core/routes/practice.py
    # ... (imports) ...
    from core.adaptive_engine import recommend_question, update_student_ability, apply_error_penalty, get_all_prerequisites
    # ...
    @practice_bp.route('/get_adaptive_question', methods=['GET'])
    @login_required
    def get_adaptive_question():
        mode = request.args.get('mode', 'single')
        # ... 根據 mode 邏輯處理 skill_ids_to_recommend ...
        question_template = recommend_question(current_user.id, list(skill_ids_to_recommend))
        # ... 使用 recommended_skill_id 生成題目並存入 session ...
        return jsonify({ /* ... 題目資料 ... */ })
    ```

---

## Phase 4: 前端介面與流程整合

**檔案**: `templates/dashboard.html`, `templates/adaptive_selection.html`, `templates/adaptive_practice.html`

**修改說明**:
擴充了儀表板，增加了多模式自適應練習的入口，並建立了專門的頁面來支援這些模式。

1.  **修改 `templates/dashboard.html`**:
    *   在學程切換區旁，為每個學程新增了「總複習」按鈕，連結到 `/adaptive_practice?mode=review&curriculum=...`。
    *   在冊別列表上方，新增了「自選組合練習」按鈕，連結到 `/adaptive_selection?curriculum=...`。
    *   修改了章節卡片下的「自適應學習」按鈕，使其連結統一為 `/adaptive_practice?mode=single&skill_ids=章節名稱`。
    ```html
    <!-- templates/dashboard.html (部分) -->
    <div style="flex-grow: 1; text-align: center; display: flex; justify-content: center; align-items: center; gap: 5px;">
        {% for c, name in [('junior_high', '國中'), ('general', '普高'), ('vocational', '技高')] %}
        <div style="display: inline-block; border: 1px solid {{ '#007bff' if curriculum == c else '#6c757d' }}; border-radius: 20px; overflow: hidden;">
            <a href="{{ url_for('dashboard', view='curriculum', curriculum=c) }}" ...> {{ name }} </a>
            <a href="{{ url_for('adaptive_practice_page', mode='review', curriculum=c) }}" title="{{ name }}總複習" ...> 總複習 </a>
        </div>
        {% endfor %}
    </div>
    <!-- ... -->
    <a href="{{ url_for('adaptive_selection_page', curriculum=curriculum) }}" class="btn-practice" ...>
        <i class="fa fa-check-square"></i> 自選組合練習
    </a>
    <!-- ... -->
    <a href="{{ url_for('adaptive_practice_page', mode='single', skill_ids=ch) }}" class="btn-practice" ...> 單元練習 </a>
    ```

2.  **新增 `templates/adaptive_selection.html`**:
    *   此頁面允許使用者在選擇學程後，勾選多個章節進行組合練習。
    *   JavaScript 會收集勾選的章節，並導向 `/adaptive_practice?mode=multiple&skill_ids=...`。
    ```html
    <!-- templates/adaptive_selection.html -->
    <!-- ... (HTML 結構與 CSS) ... -->
    <div class="chapter-grid" id="chapter-list">
        {% for chapter in chapters %}
        <label class="chapter-label">
            <input type="checkbox" name="chapter" value="{{ chapter }}">
            {{ chapter }}
        </label>
        {% endfor %}
    </div>
    <button id="start-button">...</button>
    <script>
        // ... JavaScript 處理勾選章節並導向 adaptive_practice 頁面 ...
    </script>
    ```

3.  **修改 `templates/adaptive_practice.html`**:
    *   移除了靜態的 `unit-id-storage` 輸入框。
    *   JavaScript 現在會在頁面載入時，從 URL 參數中讀取 `mode`, `skill_ids`, `curriculum`。
    *   `loadNextQuestion` 函式根據這些參數動態建構 `/get_adaptive_question` 的 API 請求 URL。
    *   `checkAnswer` 函式在提交答案時，使用從後端接收到的**當前題目實際 skill_id** (`currentSkillId`)，而不是整個練習模式的 ID。
    ```html
    <!-- templates/adaptive_practice.html (部分 JavaScript) -->
    <script>
        // ...
        const MODE = "{{ mode }}";
        const SKILL_IDS = "{{ skill_ids }}";
        const CURRICULUM = "{{ curriculum }}";
        let currentSkillId = null; // [V2] 新增：儲存當前題目的技能ID

        async function loadNextQuestion() {
            // ... 根據 MODE, SKILL_IDS, CURRICULUM 組合 apiUrl ...
            const response = await fetch(apiUrl);
            // ...
            currentSkillId = data.skill_id; // [V2] 儲存當前題目的技能ID
            // ...
        }

        async function checkAnswer() {
            // ...
            body: JSON.stringify({
                // ...
                skill_id: currentSkillId, // [V2] 使用當前題目的 skill_id
                // ...
            })
            // ...
        }
    </script>
    ```

---

## Phase 5: LLM 錯誤分析整合

**檔案**: `core/ai_analyzer.py`, `core/adaptive_engine.py`, `core/routes/practice.py`

**修改說明**:
整合了 AI 錯誤診斷功能，當學生答錯時，AI 會分析錯誤類型並對能力值施加精準懲罰。

1.  **新增 `diagnose_error` 函式到 `core/ai_analyzer.py`**:
    *   此函式接收題目、正確答案和學生答案，向 Gemini LLM 發送請求，判斷錯誤是「觀念錯誤」還是「計算錯誤」，並返回結果。
    ```python
    # core/ai_analyzer.py
    # ... (imports) ...
    def diagnose_error(question_text, correct_answer, student_answer):
        # ... 構造 Prompt 呼叫 Gemini ...
        # ... 解析 JSON 回傳 error_type ...
        return error_type
    ```

2.  **新增 `apply_error_penalty` 函式到 `core/adaptive_engine.py`**:
    *   此函式根據診斷出的 `error_type`，對學生的 `concept_u` (觀念能力) 或 `calculation_c` (計算熟練度) 應用懲罰（扣分）。
    ```python
    # core/adaptive_engine.py
    # ... (imports) ...
    def apply_error_penalty(user_id, skill_id, question_id, error_type):
        # ... 獲取學生能力和題目難度 H ...
        # ... 計算 penalty，根據 error_type 扣除 U 或 C ...
        db.session.commit()
    ```

3.  **修改 `check_answer` 路由到 `core/routes/practice.py`**:
    *   在 `check_answer` 路由中，當自適應模式且學生答錯時，會呼叫 `diagnose_error` 獲取錯誤類型，然後呼叫 `apply_error_penalty` 施加懲罰。
    ```python
    # core/routes/practice.py
    # ... (imports) ...
    from core.adaptive_engine import recommend_question, update_student_ability, apply_error_penalty, get_all_prerequisites
    from core.ai_analyzer import diagnose_error
    # ...
    @practice_bp.route('/check_answer', methods=['POST'])
    def check_answer():
        # ...
        is_adaptive_mode = request.json.get('mode') == 'adaptive'
        if is_adaptive_mode:
            # ...
            if not is_correct:
                error_type = diagnose_error(current.get('question_text', ''), current.get('correct_answer', ''), user_ans)
                if error_type != "unknown":
                    apply_error_penalty(user_id=current_user.id, skill_id=skill_id,
                                        question_id=question_id, error_type=error_type)
            # ...
        # ...
    ```

---

這份報告涵蓋了本次自適應學習系統所有新增與修改的內容。
