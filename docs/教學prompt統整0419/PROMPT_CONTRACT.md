# AI Tutor Prompt Contract (參數契約)

本文件定義專案中所有核心 Prompt 的「變數契約（Data Contract）」。
目的在於確保前端、API 路由、AI 分析引擎與 Prompt 渲染層之間的資料遞接擁有**嚴格的一致性**，避免因為參數漏傳導致的 `KeyError` 或是傳了沒用到的髒資料（Silent failure）。

---

### [Prompt] chat_guardrail_prompt
- **key**: `chat_guardrail_prompt`
- **required_variables（最終版）**: （空）
- **render kwargs（實際）**: `user_answer`, `context`, `prereq_text`, `correct_answer`
- **安全變數（可用）**: 原則上不應依賴任何業務變數，建議保持為純規則型 system prompt，不應使用 `user_answer`、`context` 等動態內容。
- **不保證存在的變數（禁止用）**: 白板批改產生之 `status`, `main_issue` 等分析結果。
- **呼叫路徑**: `core/ai_analyzer.py -> build_chat_prompt()`

---

### [Prompt] chat_tutor_prompt
- **key**: `chat_tutor_prompt`
- **required_variables（最終版）**: `user_answer, context, prereq_text, correct_answer`
- **render kwargs（實際）**: `user_answer`, `context`, `prereq_text`, `correct_answer`
- **安全變數（可用）**: `user_answer`, `context`, `prereq_text`, `correct_answer`
- **不保證存在的變數（禁止用）**: 白板特有參數（`student_expression` 等）、進階關鍵詞（`concept`）。
- **呼叫路徑**: `core/ai_analyzer.py -> build_chat_prompt()`

---

### [Prompt] rag_tutor_prompt
- **key**: `rag_tutor_prompt`
- **required_variables（最終版）**: `query, ch_name, family_name_block, subskill_text, route_label`
- **render kwargs（實際）**: `query`, `ch_name`, `family_name_block`, `subskill_text`, `route_label`
- **安全變數（可用）**: 上列五項皆與來源 100% 同步，安全可用。
- **不保證存在的變數（禁止用）**: `correct_answer`, `user_answer`。
- **呼叫路徑**: `core/rag_engine.py -> rag_chat()`

---

### [Prompt] tutor_hint_prompt
- **key**: `tutor_hint_prompt`
- **required_variables（最終版）**: `question, context, prereq_text`
- **render kwargs（實際）**:
  1. (Adv RAG) `question`, `context`, `prereq_text`
  2. (Fallback ask) `question`, `context`, `concept`, `grade`, `student_answer`, `correct_answer`, `prereq_text`
- **安全變數（可用）**: 兩條路徑共有的嚴格交集：`question, context, prereq_text`。
- **不保證存在的變數（禁止用）**: `concept`, `grade`, `student_answer`, `correct_answer`。**注意：DB 設定若使用這些變數，在 Adv RAG 路徑中將引發錯誤，屬於不安全變數。**
- **呼叫路徑**: `core/advanced_rag_engine.py -> _build_adv_rag_prompt()` 及 `core/ai_analyzer.py -> ask_ai_text_with_context()`

---

### [Prompt] concept_prompt
- **key**: `concept_prompt`
- **required_variables（最終版）**: `concept, grade`
- **render kwargs（實際）**: `question`, `context`, `concept`, `grade`, `student_answer`, `correct_answer`, `prereq_text`
- **安全變數（可用）**: `concept`, `grade`
- **補充可用變數**: `question`, `context`（目前呼叫路徑存在，但不建議作為契約依賴）
- **不保證存在的變數（禁止用）**: `student_expression`（OCR分析後產物）。
- **呼叫路徑**: `core/ai_analyzer.py -> ask_ai_text_with_context()`

---

### [Prompt] mistake_prompt
- **key**: `mistake_prompt`
- **required_variables（最終版）**: `question, student_answer, correct_answer`
- **render kwargs（實際）**: `question`, `context`, `concept`, `grade`, `student_answer`, `correct_answer`, `prereq_text`
- **安全變數（可用）**: `question`, `student_answer`, `correct_answer`, `context`
- **不保證存在的變數（禁止用）**: `error_mechanism`, `status` 等來自真實錯題機制的結構分析。
- **呼叫路徑**: `core/ai_analyzer.py -> ask_ai_text_with_context()`
- **備註**: 此 Prompt 屬於診斷型 Prompt，允許且應該使用 `correct_answer` 作為內部比對依據，以提升錯誤分析準確性。

---

### [Prompt] handwriting_feedback_prompt
- **key**: `handwriting_feedback_prompt`
- **required_variables（最終版）**: `question, student_expression, expected_answer, status, family_description_zh, error_mechanism, main_issue`
- **render kwargs（實際）**: `question`, `student_expression`, `expected_answer`, `status`, `family_description_zh`, `error_mechanism`, `main_issue`
- **安全變數（可用）**: 以上皆是，此為全站資料銜接密度最高的 Prompt，精確符合主流程送出的架構。
- **不保證存在的變數（禁止用）**: `user_answer`, `query`
- **呼叫路徑**: `core/routes/analysis.py -> _handwriting_feedback_second_prompt()`
- **備註**: 此 Prompt 已正式接回白板批改 second-stage 主流程，後台修改內容會直接影響手寫作答的教學回饋結果。目前 partially_correct 與 incorrect 已強制進入 second-stage prompt，不再由 rule-based reply 攔截。

---

## 補充原則

1. Prompt 只能使用主流程真實提供的變數，不可依理想設計假設變數存在。
2. 若一支 Prompt 存在多條呼叫路徑，required_variables 必須取所有路徑的安全交集。
3. 答案類變數（correct_answer, expected_answer）僅限特定 Prompt 使用，不可濫用。
4. Generator 層、前端層、OCR 分析層、Prompt render 層的變數語意必須嚴格區分。
