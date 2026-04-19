# Prompt Inventory（盤點日期：2026-04-19）

> 範圍：僅盤點，不修改程式邏輯與 prompt。

## Prompt 清單

| prompt_key_suggested | file_path | function_name | route_or_page | purpose | required_variables | current_source | in_db_now | has_override | student_visible | recommended_target_key |
|---|---|---|---|---|---|---|---|---|---|---|
| ai_analyzer_main_assessment | core/ai_analyzer.py:621 | `get_ai_prompt` / `analyze` | `/analyze_handwriting` 等 | 手寫分析主 Prompt 模板 | `{context}`, `{prereq_text}` | mixed (SystemSetting + `DEFAULT_PROMPT`) | 是 (`system_settings.ai_analyzer_prompt`) | true | false | `ai_analyzer_prompt` |
| chat_tutor_forced_override | core/ai_analyzer.py:968 | `build_chat_prompt` | `/chat_ai`（`index.html`、`adaptive_practice_v2.html`） | 聊天助教 system prompt | `user_answer`, `context`, `prereq_text`, `full_question_context` | hardcode + mixed | DB 有 `chat_ai_prompt` 讀取碼，但被強制覆蓋 | **true (hidden override)** | true | `chat_tutor_prompt` |
| chat_ultra_guardrail_suffix | core/ai_analyzer.py:1057 | `build_chat_prompt` | `/chat_ai` | 強制 JSON/風格護欄 | 無（固定附加） | hardcode | 否 | true | false | `chat_guardrail_prompt` |
| concept_explain_prompt | core/ai_analyzer.py:801 | `ask_ai_text` | 學生助教問答 | 概念解說 | `question/context/concept/grade` | DB-first via `render_prompt` | 是 (`prompt_templates.concept_prompt`) | true (fallback hardcode) | true | `concept_prompt` |
| context_aware_hint_mistake_prompt | core/ai_analyzer.py:839 | `ask_ai_text_with_context` | 學生助教問答 | 依上下文切 `tutor_hint`/`mistake`/`concept` | `question, context, student_answer, correct_answer` | DB-first via registry | 是 (`prompt_templates.*`) | true (fallback/切換邏輯) | true | `tutor_hint_prompt` / `mistake_prompt` |
| diagnose_error_prompt | core/ai_analyzer.py:530 | `diagnose_error` | `exam.py` 上傳後錯因診斷 | 錯誤類型+前置技能建議 | `question_text, correct_answer, student_answer, prereq_list` | hardcode | 否 | false | false | `diagnose_error_prompt` |
| weakness_analysis_prompt | core/ai_analyzer.py:1226 | `analyze_student_weakness` | `/student/analyze_weakness` | 錯題紀錄質性分析 | `prompt_data` | default constant | 否 | false | true | `weakness_analysis_prompt` |
| ocr_quiz_image_prompt | core/ai_analyzer.py:1338 | `analyze_question_image` | 圖片題目解析 | OCR+解題+JSON 結構 | image + 固定輸出 schema | hardcode | 否 | false | false | `ocr_quiz_prompt` |
| adv_rag_tutor_hint | core/advanced_rag_engine.py:324 | `_render_adv_rag_prompt_via_registry` | `/api/adaptive/adv_rag_chat` | Advanced RAG 助教提示 | `query, context_text, prereq_text` | DB-first registry | 是 (`prompt_templates.tutor_hint_prompt`) | true (fallback 到 legacy builder) | true | `tutor_hint_prompt` |
| adv_rag_legacy_fallback_prompt | core/advanced_rag_engine.py:272 | `_build_adv_rag_prompt` | `/api/adaptive/adv_rag_chat` | Registry 失敗時備援 | `query, retrieved_skills, question_text, family_id` | hardcode | 否 | true | true | `adv_rag_fallback_prompt` |
| naive_rag_chat_prompt | core/rag_engine.py:393 | `rag_chat` | `/api/rag_chat`（`index.html`） | Naive RAG 回答生成 | `query, top_skill_id->skill/family/subskills` | hardcode | 否 | false | true | `naive_rag_chat_prompt` |
| exam_image_analyze_prompt | core/exam_analyzer.py:124 | `build_gemini_prompt` | `/upload_exam`（`exam_upload.html`） | 考卷 OCR + 對齊單元 + 錯因 JSON | `flattened_units` | hardcode | 否 | false | 間接可見（回傳結果） | `exam_analyzer_prompt` |
| handwriting_recognition_prompt | core/routes/analysis.py:2560 | `analyze_handwriting` | `/analyze_handwriting` | 白板手寫文字轉錄 JSON | image | hardcode | 否 | false | false | `handwriting_recognition_prompt` |
| handwriting_second_stage_feedback | core/routes/analysis.py:1190 | `_handwriting_feedback_second_prompt` | `/analyze_handwriting` | 第二階段補充回饋 | `analysis_result, question_text/context, prereq_text, family_id` | hardcode | 否 | true (rule-based fallback) | true | `handwriting_feedback_prompt` |
| draw_diagram_extract_equation_prompt | core/routes/practice.py:756 | `draw_diagram` | `/draw_diagram`（`index.html`） | 從題目抽方程給繪圖器 | `question_text` | hardcode | 否 | false | false | `diagram_equation_extraction_prompt` |
| skill_suggested_prompts_db | core/routes/practice.py:913 | `get_suggested_prompts` | `index.html` 初始提示按鈕 | 取技能建議問句 | `skill_id` | DB (`skills_info.suggested_prompt_1~3`) | 是 | false | true | `skill_suggested_prompts` |
| skill_codegen_prompt_store | core/routes/admin.py:763 | `api_get/save_skill_prompt` | Admin Prompt 管理 API | 儲存 codegen system/user prompt | `skill_id, model_tag, system_prompt, user_prompt_template` | DB (`skill_gencode_prompt`) | 是 | true (多版本/多tag) | false | `skill_codegen_prompt` |
| global_prompt_settings_legacy | core/routes/admin.py:1266 | `get/update/reset_ai_prompt_setting` | `/admin/ai_prompt_settings` | 全域 `ai_analyzer_prompt` 設定 | `{context},{prereq_text}` | DB + default constant | 是 (`system_settings`) | true (與新 registry 並存) | false | `ai_analyzer_prompt` |
| prompt_registry_templates | core/prompts/registry.py:7 | `get_prompt_template/render_prompt` | 被 ai_analyzer/adv_rag_engine 間接使用 | PromptTemplate DB-first 渲染 | 依 key | mixed (DB + default_templates) | 是 (`prompt_templates`) | true (DB 覆蓋 default) | 視 key 而定 | `base_prompt/tutor_hint_prompt/concept_prompt/mistake_prompt` |
| codegen_prompt_builder_chain | core/code_generator.py:351 | `_build_prompt` | `/skills/<id>/regenerate` 等後台生成流程 | 生成器 Prompt 組裝 | `db_master_spec, skill_id, ablation_id` | mixed (DB MASTER_SPEC + `PromptBuilder` + golden file) | 是 (`skill_gencode_prompt.prompt_content`) | **true** (golden/file override) | false | `codegen_master_spec_prompt` |
| scaler_file_prompt_chain | core/engine/scaler.py:108 | `_load_skill_prompt` / `generate_custom_problems` | live/custom problem 生成流程 | 載入 `prompt_liveshow.md`/`ab1_bare_prompt.md`/`SKILL.md` + 動態拼接 | `skill_name, input_text, mode` | mixed (file + hardcode) | 否 | **true** (ablation/file fallback) | false | `scaler_liveshow_prompt` |

---

## 指定模板檔補充

- `templates/index.html`：同時存在「初始建議提問（DB）」與「動態 follow_up_prompts（AI 回傳）」兩套提示來源。
- `templates/adaptive_practice_v2.html`：有 3 個硬寫 guide 文案（看核心觀念/提示下一步/提醒易錯點）會送到 `/api/adaptive/adv_rag_chat`。
- `templates/exam_upload.html`：無直接 LLM prompt，真正 prompt 在 `core/exam_analyzer.py`。
- `templates/ai_prompt_settings.html`：頁面文字明示 legacy block 尚未完全納入 Prompt Registry。

---

## 盤點總結

### 1) 找到幾個 prompt 來源

- 盤點到 **21 個 prompt 資產/入口**。
- 歸納為 **8 類來源機制**：
  1. hardcode 字串
  2. module default constant
  3. `system_settings` DB
  4. `prompt_templates` DB（registry）
  5. `skills_info` DB（suggested prompts）
  6. `skill_gencode_prompt` DB
  7. 檔案型 prompt（`prompt_liveshow.md` / `ab1_bare_prompt.md` / `SKILL.md`）
  8. golden prompt 檔案覆蓋

### 2) 最危險的 hardcode / override

1. `build_chat_prompt` 內 **強制忽略 DB**（`prompt_template = base_instruction`），屬 hidden override。  
2. 聊天助教同功能多來源衝突：`ai_analyzer_prompt`（SystemSetting）/ `tutor_hint_prompt`（PromptTemplate）/ `build_chat_prompt` hard override。  
3. codegen/scaler 多層覆蓋鏈：DB MASTER_SPEC + PromptBuilder + golden file + skill 檔案 prompt。  
4. `tutor_hint_prompt` DB 內容已與 default 不同，但各路徑是否一致吃到它不完全透明。

### 3) 優先納入 Prompt Registry 建議

1. `/chat_ai` 主鏈（`build_chat_prompt` 的 base instruction + guardrail）。  
2. 手寫鏈（recognition + second-stage feedback）。  
3. `rag_engine.rag_chat` hardcode prompt。  
4. `exam_analyzer.build_gemini_prompt`。  
5. `practice.draw_diagram` 的 equation extraction prompt。  
6. `diagnose_error` 與 `DEFAULT_WEAKNESS_ANALYSIS_PROMPT`。  
7. codegen/scaler 先做來源標準化與生效優先序註冊。

---

## 附註

- `/api/adaptive/adv_rag_search`、`/api/adaptive/adv_rag_chat` 實作位於 `core/routes/adaptive_api.py`（未在原始指定清單），但因前端 `adaptive_practice_v2.html` 直接呼叫，已納入關聯判讀。
