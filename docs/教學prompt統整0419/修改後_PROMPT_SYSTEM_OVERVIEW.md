# 1. 文件目的
本文件旨在整理 Mathproject 專案中 AI 助教 Prompt 系統的最終設計、各元件之間的資料流（Data Flow），以及近期修補作業的總結。這份文件可作為開發交接、後續維護，以及向教師與專業評審展示 AI 架構嚴謹性的基準文件。

# 2. Prompt 系統設計原則
為了確保 AI 助教在各個不同環節中皆能表現出一致且高教育價值的行為，本系統採取了以下切分與設計原則：
- **為什麼 prompt 需要分角色**：學生可能在前端做不同的操作（一般聊天、尋求解題提示、要求觀念解釋、提交白板手寫過程 等）。單一且龐大的 Prompt 難以應付所有邊界狀況，透過分工（Tutor, Hint, Concept, Diagnosis）能讓 LLM 專注單一任務，提升回答穩定度。
- **為什麼不能所有 prompt 都拿答案**：AI 助教的核心任務是「引導（Scaffolding）」而非「解答」。避免 AI 拿到標準答案後，因模型參數過小而發生「直接把答案唸出來」的洩題事故，多數的 Tutor / Concept prompt 不會主動獲取標準答案。
- **為什麼小模型（Qwen 8B）與 Gemini Flash 需要共用一套偏精簡的 prompt**：為支援「Runtime AI」配置，系統能自由切換地端（Local Edge）與雲端模型。精簡且指引明確的 Prompt 有助於小參數量模型能遵循指令，同時在大模型上也能保持高效不偏移。
- **分層機制與 Guardrail**：將行為準則（Guardrail）與教學主體（Tutor）分開，確保無論對話如何偏移，核心的「不可直接評價對錯、不可給出最終答案」安全邊界總能在最終階段強制注入系統提示中。

# 3. Prompt 總覽表

| Prompt key | Category / type | 核心定位 | required_variables | 使用頁面 | 使用 API / 程式位置 | 輸入來源 | 輸出用途 | 是否建議使用正確答案 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| `chat_guardrail_prompt` | system | 強制安全護欄（不可給答案/評價對錯） | （無） | Practice / Adaptive | `core/ai_analyzer.py` -> `build_chat_prompt` | 系統內建附加 | 定義 AI 絕對不可觸碰的底線 | 否 |
| `chat_tutor_prompt` | tutor | 一般性對話引導助教 | `user_answer`, `context`, `prereq_text` | Practice / Adaptive | `core/ai_analyzer.py` -> `build_chat_prompt` | 聊天框 (提問) + 題目狀態 | 作為蘇格拉底式反問或回應 | 理論上可，但現以盲測為主 |
| `rag_tutor_prompt` | tutor | 基於知識庫檢索的知識引導 | `query`, `ch_name`, `family_name_block`, `subskill_text`, `route_label` | 對話框 (觸發RAG) | `core/rag_engine.py` -> `rag_chat` | 前端提問 + RAG 檢索文檔 | 提供對應課綱章節的精確知識提醒 | 否 |
| `tutor_hint_prompt` | tutor | 給出下一步微小提示 | `question` | Practice / Adaptive | `core/advanced_rag_engine.py` | 前端提問 | 提供鹰架式輔助，不外洩答案 | 適合內部比對，但不外洩 |
| `concept_prompt` | concept | 特定數學名詞/觀念解析 | `concept`, `grade` | Concept 卡片 | `core/ai_analyzer.py` 等 | 前端特定名詞點擊 | 解釋觀念與迷思概念 | 否 |
| `mistake_prompt` | diagnosis | 錯題診斷與錯誤原因歸納 | `question`, `student_answer`, `correct_answer` | 後台邏輯 / 錯題本 | `core/ai_analyzer.py` -> `analyze_student_mistake` | 批改邏輯送出錯題資料 | 分析出 Concept / Careless 等盲點 | **是**（必須有答案） |
| `handwriting_feedback_prompt` | tutor | 白板批改 second-stage 主流程回饋 prompt | `question`, `student_expression`, `expected_answer`, `status`, `family_description_zh`, `error_mechanism`, `main_issue` | 白板畫布 | `core/routes/analysis.py` -> `_handwriting_feedback_second_prompt()` | 前端截圖傳回的圖片 + 題目描述 | 確認手寫計算步驟並指出具體錯誤步驟 | ✅ 是（使用 `expected_answer`，僅供內部比對） |

# 4. 題目、學生答案、正確答案的資料流

## Generator 層（題目生成）
- `question_text`：存放數學題目的字串（e.g., 化簡：x + 2x）。
- `correct_answer`：存放演算法得出的標準解答。
- `answer`：在 `_wrap_payload` 中，這裡的 `answer` 被設定為等同 `correct_answer`。
- **結論**：Generator 層沒有負責「學生作答」，這裡的 `answer` 指的是正確解答。

## 前端層（Practice / Adaptive 網頁狀態）
- 題目保留在 DOM 元素中，或存在 `currentContext` / `question`。
- **`window.currentExpectedAnswer`**：這是前端在載入新題目時，保留下來的 `correct_answer`，用以比對對錯以及傳給特定批改 API。
- **`answerInput` vs `chatInput` vs `recognized_expression`**：
  - `answerInput.value`：送至 `/check_answer` 比對對錯，欄位名為 `answer`。
  - `chatInput.value`：送至 `/chat_ai` 聊天，欄位名為 `question`。
  - `recognized_expression`：由白板上傳圖片後，經過 Vision OCR 解析出來的算式字串。

## 後端 / API / Prompt 層傳遞現況
- **正確答案 (`correct_answer`) 的傳遞狀況**：
  - `/analyze_handwriting` API **有**收到 `expected_answer`，並已經成功流入 second-stage prompt。
  - `/chat_ai` API 已經成功接收到 `expected_answer` (前端已於 fetch 補上)。
- **AI Prompt 實際吃到的狀況**：
  - `handwriting_feedback_prompt`：不再只是後台孤兒設定，而是實際接回主流程的正式 prompt！目前真正的主流程位於 `core/routes/analysis.py` 的 `_handwriting_feedback_second_prompt()`，它已正式接回 Prompt Registry，並保留 hard-coded fallback。`expected_answer` 等 second-stage 變數（包含來自 OCR 解析出的 `student_expression`）皆已成功參與 render 流程。
  - 註記：舊的 `core/ai_analyzer.py -> analyze()` 已經被徹底隔離不再是主流程。

# 5. 近期修補與結論

1. **PPO 載入邏輯修補**
   - **問題**：原系統依賴 `joblib` 硬食舊版模型，常出現載入錯誤與環境不容。
   - **修改**：全面改用 `stable-baselines3` 原生的 `load()` 方式。
   - **結果**：完全捨棄 `joblib`，避免模型結構改版導致的系統崩潰。

2. **Advanced RAG 啟動與 dependency 檢查修補**
   - **問題**：生產環境常因缺漏套件導致系統啟動失敗或 fallback 到 naive 模式。
   - **修改**：在相關引擎中加入防呆與 fallback 路由提醒。
   - **結果**：讓 RAG 流程能安穩啟動，即使缺少 `chromadb` 也不會引發系統 500 錯誤。

3. **Prompt DB 接管問題與 Admin 後台 prompt update 400 修補**
   - **問題**：Admin 頁面儲存 Prompt 會出現 400 錯誤，且 `rag_tutor_prompt` 不在 DB 中。
   - **修改**：修補 `admin.py` 中的 `/admin/ai_prompt_settings/prompt/update`，加入嚴謹的 JSON Payload 抓取、缺值則 Create 等邏輯，並掛載完整的 `[admin debug]` Log；更新 Migrate 腳本確保 DB 有 `rag_tutor_prompt` 欄位。
   - **結果**：管理者現可於前端順利修改存放於 DB 的 Prompt 架構並動態生效。

4. **route_label 注入與 family_name_block 教學化格式**
   - **問題**：RAG Prompt 中直接塞入冷硬的 `jh_數學1上_xxx` 程式碼常數，影響模型回答口吻。
   - **修改**：於 `rag_engine.py` 加入過濾器將 family 代號轉換為可讀的指令項目，並將搜尋路徑以 `route_label` 變數注入。
   - **結果**：讓 Prompt 指令更像人說話，RAG 也能依據 Fast/Advanced Path 適應回答語氣。

5. **updated_at 顯示時區修補**
   - **修改**：在 Admin 頁面由 UTC 直接轉譯至 Asia/Taipei 處理，避免時區錯亂。

6. **Prompt 與實際 data contract 對齊的結論**
   - **結論**：我們確認了前述缺答案的斷層已修補完成，`chat_ai` 現能從前端收下並轉拋答對預期結果予提示。而白板手寫架構亦將孤兒的 `handwriting_feedback_prompt` 接回了真正的主流程。

7. **白板批改 second-stage prompt 接管說明**
   - **問題**：白板批改第二階段回饋 prompt 原本是 hard-coded 字串，後台無法管理，造成 Prompt Registry 對白板教學最後一哩路失效。
   - **根因**：`_handwriting_feedback_second_prompt()` 未接入 DB Prompt Registry，且舊版 `handwriting_feedback_prompt` 已成孤兒 prompt。
   - **修改**：
     - 更新 `default_templates.py` 的 `handwriting_feedback_prompt`
     - 將 second-stage 主流程改為優先透過 `compose_prompt(...)` 讀取 registry / DB prompt
     - 保留 hard-coded fallback
     - 保留 JSON 格式需求作為 extra block
     - 將 required_variables 對齊 second-stage 真實變數
   - **結果**：
     - 後台修改 `handwriting_feedback_prompt` 後，已可直接影響白板批改第二階段回覆
     - `expected_answer` 已真正流入 prompt
     - second-stage prompt 已納入統一 Prompt 系統管理
     - fallback 保留，系統不會因 prompt render 失敗而崩潰

8. **白板批改 second-stage 全面接管（解除攔截）**
   - **問題**：先前即使已接通 second-stage prompt，但在多數 `partially_correct` / `incorrect` 狀況下仍吃不到請求，最終 reply 仍是舊的 generic rule-based 文案。
   - **根因**：在 `core/routes/analysis.py -> analyze_handwriting()` 流程中，存在 `elif _handwriting_issue_is_clear(analysis_result):` 的攔截分支。
   - **修改**：移除該攔截分支，讓 `hw_status in ("unknown", "correct")` 確保放行快速通道後，所有 `partially_correct` / `incorrect` 皆統一無條件進入 `_handwriting_feedback_second_prompt()`。
   - **結果**：`handwriting_feedback_prompt` 已真正接管白板 second-stage 教學回饋；舊的 generic rule-based 回覆不再攔截主要錯誤情境；後台修改 prompt 已能直接且穩定影響部分正確與錯誤作答的教學回覆。

# 6. 目前建議採用的預設 prompts

此區塊以目前專案 `core/prompts/default_templates.py` 內定義的主流為準。

### chat_guardrail_prompt
- **required_variables**: （無）
- **最終建議內容**:
  ```text
  [CRITICAL RULES]
  1. 你是引導式學習助教，任務是引導思考，不可直接評價對錯。
  2. 嚴禁說出「你錯了/你對了/有道理/不對」這類直接判定。
  3. 嚴禁給出最終答案或完整算式。
  4. 回覆請控制在精簡的長度，給出一個概念與一個小問題即可。
  ```
- **設計理由**: 獨立作為系統安全邊界，掛在任何對話提示底層，防止模型幻覺或洩題。

### chat_tutor_prompt
- **required_variables**: `user_answer`, `context`, `prereq_text`
- **最終建議內容**:
  ```text
  你是台灣國中的「引導式學習助教」。
  你的任務是引導思考，而不是直接給答案。
  請根據學生的問題 {user_answer} 與題目背景 {context}，給予一步提示或反問。
  ```
- **設計理由**: 以蘇格拉底教學法為基礎的對話本體。注意：系統以 `{user_answer}` 來承載「使用者的對話內容」。

### rag_tutor_prompt
- **required_variables**: `query`, `ch_name`, `family_name_block`, `subskill_text`, `route_label`
- **最終建議內容**:
  ```text
  你是一位台灣國中數學助教。
  請用繁體中文回答，語氣簡短，讓國中生看得懂。
  只能提示，不要直接給完整答案。

  學生問題：
  {query}

  [目前檢索路徑：{route_label}]
  目前對應技能：
  {ch_name} {family_name_block}

  重點子技能：
  {subskill_text}

  請輸出：
  1. 先提醒一個最重要的觀念
  2. 再給一個小提示
  3. 最後給一個下一步方向
  ```
- **設計理由**: 指示明確，結合知識庫提供的教學點，讓回答不脫離課本綱要。

### tutor_hint_prompt
- **required_variables**: `question`
- **最終建議內容**:
  ```text
  Given the student question: {question}, provide one concise hint first without revealing the final answer.
  ```
- **設計理由**: 當學生要求提示（非對話）時，使用英文指示更容易壓制大模型不要廢話（視語言設定可改）。

### concept_prompt
- **required_variables**: `concept`, `grade`
- **最終建議內容**:
  ```text
  Explain the concept '{concept}' for grade {grade} students with one example and one common misconception.
  ```
- **設計理由**: 標準化給名詞解釋的操作模式，強制生成一例與一共通信念迷思。

### mistake_prompt
- **required_variables**: `question`, `student_answer`, `correct_answer`
- **最終建議內容**:
  ```text
  Analyze the student mistake from question: {question}, answer: {student_answer}, expected: {correct_answer}. Return mistake type, reason, and one correction step.
  ```
- **設計理由**: 標準的錯誤分析格式，此 Prompt **一定**要有標準答案。

### handwriting_feedback_prompt
- **required_variables**: `question`, `student_expression`, `expected_answer`, `status`, `family_description_zh`, `error_mechanism`, `main_issue`
- **最終建議內容**:
  ```text
  你是一位專業的國中數學老師，正在分析學生的手寫解題結果。

  【題目】
  {question}

  【學生作答】
  {student_expression}

  【標準答案（僅供內部比對，不可直接照抄給學生）】
  {expected_answer}

  【第一階段判定】
  {status}

  【本題重點】
  {family_description_zh}

  【可能錯誤機制】
  {error_mechanism}

  【已知核心問題】
  {main_issue}

  任務：
  請根據以上資訊，對學生目前的作答狀況做教學式回饋，幫助學生知道自己錯在哪裡，以及下一步應該怎麼修正。

  重要規則：
  - 可以判斷正確、錯誤或部分正確，但不要只給結論
  - 不可直接把標準答案完整講給學生
  - 不可完整重建整題解法
  - 要優先指出最關鍵的錯誤步驟或觀念
  - 若學生方向大致正確，請指出還需要檢查的地方
  - 若資訊不足，請誠實說明無法完全判斷，不要亂猜

  請嚴格依照以下格式回答：

  【整體判斷】
  用一句話說明學生目前是正確、部分正確，或是哪裡明顯有問題。

  【錯誤定位】
  指出最可能出錯的步驟、觀念或運算轉換。

  【修正方向】
  用1到2句話告訴學生下一步應該檢查什麼，但不要直接給完整答案。

  【補充提醒】
  補充一個常見錯誤、觀念提醒，或檢查重點。若沒有可省略。

  請使用繁體中文，語氣保持具體、精簡、教學導向。
  ```
- **設計理由**: 這支 prompt 現在是白板批改主流程正式使用版本，由 Prompt Registry/DB 同步管理。使用答案做內部比對，但不直接暴露答案給學生；結構化輸出便於第二階段教學回饋，並將嚴格的 JSON 控制器轉為背景 extra_block，避免污染教學敘述。

# 7. 哪些 prompt 可以使用答案，哪些不應該

| Prompt 種類 | 是否應該使用 `correct_answer` | 原因分析 |
|:---|:---|:---|
| **chat_tutor_prompt** | 理論上適合，但目前程式未串接 | 作為內部比對確認自己沒有引導錯誤有助益，但有微小機率外洩給學生，需嚴格搭配 Guardrail。目前現況為盲測。 |
| **rag_tutor_prompt** | **否** | 此機制重在知識點補充，直接拿答案意義不大，反而偏離重拾基礎的目的。 |
| **tutor_hint_prompt** | 適合，但嚴禁外洩 | 提供關鍵步驟的算式鷹架，有答案能確保方向正確。 |
| **concept_prompt** | **否** | 單純的觀念名詞維基百科，不涉入答題狀態。 |
| **mistake_prompt** | **必須使用** | 必須同時擁有 `student_answer` + `correct_answer` 才能評量何處算錯。 |
| **handwriting_feedback_prompt**| **✅ 已正式使用** | 已正式使用 `expected_answer` 作為內部比對依據，並已接回主流程，能有效讓助教確認正確計算再進行錯誤標示。 |
| **chat_guardrail_prompt** | **否** | 安全防呆機制不需要答案。 |

# 8. 現況風險與後續建議

- **命名不一致風險：** 整個 API 前後端的 `question` / `user_answer` / `query` / `answer` 使用混亂。例如前端的 `question` 代表使用者的聊天文字，傳到 Prompt 卻叫做 `{user_answer}`；容易讓開發者誤以為 `{user_answer}` 裝的是學生算式的結果。
- **Handwriting Pipeline 持續追蹤與 Legacy 遺留物：** 白板批改主流程已完美接回系統，但仍需持續驗證 prompt render 與 fallback 的發動行為；另外舊版的 `core/ai_analyzer.py -> analyze()` 屬於 legacy / orphan path，目前需在此註記並放置不管，若未來要進一步整潔化，可考慮將 legacy path 明確標記為 deprecated。
- **`family_name_block` 再進化：** 雖然經過教學化格式修補，但 fallback 時的字串依然存在系統特性的機器感，建議擴充 DB 對應更口語的章節表。
- **多台電腦與多環境切換的同步率：** 目前系統有 DB 版本也有原碼中 fallback 版本，多地開發時可能因 SQLite 不同步導致結果差異。

# 9. 建議後續維護策略
- **Prompt as Config**：將核心 Prompt 定位為設定檔，不應隨意硬編碼（Hardcode）散落於各組件。
- **YAML 作為 Git 同步基準**：建議未來引進一套 YAML 讀寫機制，讓預設的 Default Prompt 能接受版控管理，並且在部署時強制打平進系統。
- **DB 作為 Runtime Override**：當系統管理員於後台進行更動時，透過 DB 的內容凌駕（Override） YAML。
- **匯入 / 匯出**：建議實現一份腳本，能把線上 DB 調校好的最佳成果備份為 JSON/YAML，以防環境毀損。
- **Prompt Versioning**：若要做 A/B Testing，可以在 DB 表單內擴充 `version_tag` 與 `is_active`。
