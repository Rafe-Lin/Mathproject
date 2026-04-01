# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/ai_analyzer.py
功能說明 (Description): 負責與 Google Gemini AI 模型互動，提供圖片分析、手寫辨識、題目技能識別以及從圖片生成測驗等核心 AI 功能。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""此模組負責與 Google Gemini AI 模型進行互動，提供圖片分析、手寫辨識、題目技能識別以及從圖片生成測驗等功能。"""
# core/ai_analyzer.py
import google.generativeai as genai
import base64
import json
import tempfile
import os
import re
from flask import current_app
import PIL.Image
import io
from core.ai_wrapper import get_ai_client

# 初始化 gemini_model 為 None，避免 NameError
gemini_model = None
gemini_chat = None

def clean_and_parse_json(text):
    try:
        # 移除 Markdown 標記
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)
        
        # 尋找最外層的 { }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            
        # 關鍵修復：處理 LaTeX 中常見的雙反斜線與 Unicode
        # 先嘗試直接解析
        return json.loads(text, strict=False)
    except Exception as e:
        try:
            # [Step 2] 嘗試修復截斷的 JSON (Unterminated string/brackets)
            def repair_truncated_json(s):
                s = s.strip()
                # 1. 補齊引號 (假設偶數個引號才是閉合，若奇數個則補一個)
                # 簡單計算 " 的數量 (排除轉義的 \")
                quote_count = len(re.findall(r'(?<!\\)"', s))
                if quote_count % 2 != 0:
                    s += '"'
                
                # 2. 補齊括號
                open_braces = s.count('{')
                close_braces = s.count('}')
                s += '}' * (open_braces - close_braces)
                
                open_brackets = s.count('[')
                close_brackets = s.count(']')
                s += ']' * (open_brackets - close_brackets)
                return s

            fixed_text = repair_truncated_json(text)
            return json.loads(fixed_text, strict=False)
        except:
            try:
                # [Step 3] 若正規 JSON 失敗，嘗試 Python eval (針對 True/False/None)
                import ast
                return ast.literal_eval(text)
            except:
                print(f"JSON 解析終極失敗: {e}")
                return {"reply": text, "follow_up_prompts": []}

def enforce_strict_mode(text):
    if not text: return ""
    import re
    
    # [Step 1] 移除 Markdown 格式
    text = text.replace('**', '')

    # [Step 2] 智慧刪除廢話 (保留句子結構)
    # 我們不直接刪除 "你很棒"，而是用替換的方式
    
    # 刪除純粹的稱讚句 (獨立成句的)
    text = re.sub(r"(^|[，！!。])同學[，！!、]*你很棒[，！!、]*", r"\1", text)
    text = re.sub(r"(^|[，！!。])你已經很棒.*?[，！!]", r"\1", text)
    text = re.sub(r"(^|[，！!。])這一步非常正確[。！!]*", r"\1", text)
    
    # 刪除開場白
    text = re.sub(r"^同學[，！!、]*", "", text)
    text = re.sub(r"^哈囉[，！!、]*", "", text)
    
    # [Step 3] 修復 "地找到了" -> "正確地找到了" 或 "找到了"
    # 如果句子開頭變成 "地..." 或 "的..."，移除該字
    text = text.strip()
    if text.startswith("地") or text.startswith("的"):
        text = text[1:]
        
    # 去除首尾殘留標點
    text = text.strip("，,！!。 ")

    # [Step 4] 終極 LaTeX 保護 (這是修復 Math Input Error 的關鍵)
    # 確保所有反斜線在 JSON 傳輸前都是雙份的
    # 先還原 (避免變成 4 條線)，再統一加倍
    text = text.replace('\\\\\\\\', '\\\\') 
    text = text.replace('\\\\', '\\\\\\\\')
    
    return text


def _looks_like_direct_answer(text):
    if not isinstance(text, str):
        return False

    s = re.sub(r'\s+', ' ', text).strip().lower()
    if not s:
        return False

    answer_markers = [
        '答案是',
        '正確答案',
        '最後答案',
        '所以答案',
        '因此答案',
        '直接算出',
        'you should get',
        'the answer is',
    ]
    if any(marker in s for marker in answer_markers):
        return True

    # Common direct-answer patterns for math tutoring.
    if re.search(r'[=＝]\s*[-+]?\d+(\.\d+)?', s):
        return True
    if re.search(r'^\s*[-+]?\d+(\.\d+)?\s*$', s):
        return True
    if re.search(r'\\frac\{[^{}]+\}\{[^{}]+\}\s*$', s):
        return True

    return False


def _build_guiding_reply(user_question='', question_context=''):
    focus_text = ''
    for raw in (user_question, question_context):
        if isinstance(raw, str) and raw.strip():
            focus_text = raw
            break

    if any(token in focus_text for token in ['分數', '\\frac', '約分', '通分']):
        return '先看分子和分母各能不能再約一次，好嗎？'
    if any(token in focus_text for token in ['根號', '\\sqrt']):
        return '先看根號前後能不能先整理成同一種型態。'
    if any(token in focus_text for token in ['多項式', 'x', 'y', '項']):
        return '先找同類項，再想想哪些項可以先合併。'
    if any(token in focus_text for token in ['減', '-', '加', '+', '乘', '除', '×', '÷']):
        return '先不要急著算完，先確認你現在用的運算符號有沒有看對。'
    return '先別急著看答案，先想想這一步要用哪個規則。'


def sanitize_tutor_reply(reply_text, user_question='', question_context=''):
    if not isinstance(reply_text, str):
        return _build_guiding_reply(user_question, question_context)

    cleaned = re.sub(r'\s+', ' ', reply_text).strip()
    if not cleaned:
        return _build_guiding_reply(user_question, question_context)

    if _looks_like_direct_answer(cleaned):
        return _build_guiding_reply(user_question, question_context)

    if len(cleaned) > 80:
        cleaned = cleaned[:80].rstrip('，。；、 ') + '。'

    return cleaned

# 預設批改 Prompt
DEFAULT_PROMPT =  """
你是資深數學中學老師，講話精準樂於幫助同學思考，語言極度精簡、冷靜、直接。規則：
1. **禁開場白**：禁止「哈囉、你好、很棒」等任何贅詞及任何鼓勵或情緒詞（如「很棒」「加油」「別擔心」「你已經很努力」「這是很好的開始」）。
2. **直擊錯誤**：直接指出算式問題，不要委婉。
3. **字數硬限**：每次回話嚴格限制在 40 字內。
4. **LaTeX 規範**：公式務必使用單個 $ 包裹。
5. **邏輯鏈氣泡**：必須回傳 follow_up_prompts：【觀察】、【聯想】、【執行】。
6. **直接指出錯誤或重點，不委婉。

題目：{context}
此單元的前置基礎技能有：{prereq_text}

請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字、格式條列清楚。

【⚠️ 絕對嚴格的數學輸出規範 ⚠️】：
為了讓網頁能正確顯示數學公式，你必須遵守以下規則，否則學生會看到亂碼：
1. **所有的數學符號與算式**，無論多短，都**必須**用單個錢字號 $ 包裹。
   - ✅ 正確：$x^3 + \\frac{1}{x^3}$
2. **變數與數字**：
   - ✅ 正確：令 $a = x$
3. **禁止巢狀 $**：
   - ✅ 正確：$\\sqrt{3 \\times 5}$
4. **常用符號對照表**：
   - 分數：$\\frac{a}{b}$
   - 次方：$x^2$
   - 根號：$\\sqrt{x}$
   - 乘號：\\times 或 \\cdot

{
  "reply": "用 Markdown 格式寫出具體建議(步驟對錯、遺漏、改進點)。如果計算過程完全正確,reply 內容應為「答對了,計算過程很正確!」。(記住：極致簡練，不超過40字)",
  "is_process_correct": true 或 false,
  "correct": true 或 false,
  "next_question": true 或 false,
  "error_type": "如果答錯,請從以下選擇一個:'計算錯誤'、'觀念錯誤'、'粗心'、'其他'。如果答對則為 null",
  "error_description": "如果答錯,簡短描述錯誤原因(例如:正負號弄反、公式背錯),30字以內。如果答對則為 null",
  "improvement_suggestion": "如果答錯,給學生的具體改進建議,30字以內。如果答對則為 null",
  "follow_up_prompts": [
      "Prompt 1 (【觀察】：引導學生觀察圖形或算式特徵)",
      "Prompt 2 (【聯想】：提示相關公式或策略)",
      "Prompt 3 (【執行】：具體修正步驟或驗算)"
  ]
}

直接輸出 JSON 內容，不要包在 ```json 標記內。"""

# 預設聊天 Prompt
# 預設聊天 Prompt
# ======================================================
# 請將這段程式碼「完全覆蓋」原本的 DEFAULT_CHAT_PROMPT 設定
# ======================================================

DEFAULT_CHAT_PROMPT = """
你是資深數學中學老師，講話精準樂於幫助同學思考，語言極度精簡、冷靜、直接。規則：
1. **禁開場白**：禁止「哈囉、你好、很棒」等任何贅詞及任何鼓勵或情緒詞（如「很棒」「加油」「別擔心」「你已經很努力」「這是很好的開始」）。
2. **直擊錯誤**：直接指出算式問題，不要委婉。
3. **字數硬限**：每次回話嚴格限制在 40 字內。
4. **LaTeX 規範**：公式務必使用單個 $ 包裹。
5. **邏輯鏈氣泡**：必須回傳 follow_up_prompts：【觀察】、【聯想】、【執行】。
6. **直接指出錯誤或重點，不委婉。

【JSON 輸出格式與安全守則】：
你必須輸出符合此 JSON schema 的內容：
{
  "reply": "老師的對話內容精準批改或引導內容 (口語化，40字內，不含標題與情緒，必須包含 LaTeX 格式的數學符號，如 \\sqrt{7})",
  "follow_up_prompts": [
    "問題1 (【觀察】：請根據當前題目提出一個具體觀察點)",
    "問題2 (【聯想】：請連到此題相關觀念或公式)",
    "問題3 (【執行】：請給可立即操作的檢查或修正步驟)"
  ]
}
"""


def _looks_generic_followup_prompt(text):
    """Detect placeholder-like prompts that should be regenerated."""
    if not isinstance(text, str):
        return True
    s = text.strip()
    if not s:
        return True

    generic_markers = [
        '...',
        '這裡的...為什麼',
        '如果我不...，還有別的方法嗎',
        '這題的陷阱是不是在',
        '引導學生觀察圖形或算式特徵',
        '提示相關公式或策略',
        '具體修正步驟或驗算',
        'prompt 1',
        'prompt 2',
        'prompt 3'
    ]
    lowered = s.lower()
    return any(marker in s or marker in lowered for marker in generic_markers)


def _extract_focus_phrase(user_question, question_context, ai_reply):
    """Pick a short context phrase so regenerated prompts are anchored to current turn."""
    candidates = [user_question, question_context, ai_reply]
    for raw in candidates:
        if not isinstance(raw, str):
            continue
        cleaned = re.sub(r'\s+', ' ', raw).strip()
        if not cleaned:
            continue
        cleaned = cleaned.replace('"', '').replace("'", '')
        cleaned = cleaned.replace('$', '')
        return cleaned[:24]
    return '這一題'


def build_dynamic_follow_up_prompts(user_question='', question_context='', ai_reply=''):
    """Generate deterministic, non-placeholder follow-up prompts."""
    focus = _extract_focus_phrase(user_question, question_context, ai_reply)
    return [
        f"問題1 (【觀察】：先看「{focus}」，哪個條件最容易被忽略？)",
        f"問題2 (【聯想】：這題和哪個公式或性質最直接相關？為什麼？)",
        f"問題3 (【執行】：請用 1 步驗算「{focus}」是否成立。)"
    ]


def build_dynamic_follow_up_prompts_variant(user_question='', question_context='', ai_reply='', variant=0):
    """Generate stylistic variants so repeated turns won't show identical prompts."""
    focus = _extract_focus_phrase(user_question, question_context, ai_reply)
    styles = [
        (
            "問題1 (【觀察】：先看「{focus}」，哪個條件最容易被忽略？)",
            "問題2 (【聯想】：這題和哪個公式或性質最直接相關？為什麼？)",
            "問題3 (【執行】：請用 1 步驗算「{focus}」是否成立。)"
        ),
        (
            "問題1 (【觀察】：在「{focus}」裡，哪個數字或符號最關鍵？)",
            "問題2 (【聯想】：把這題對應到一個你熟悉的規則，會是哪一個？)",
            "問題3 (【執行】：先做一個最小步驟，確認「{focus}」方向有沒有反。)"
        ),
        (
            "問題1 (【觀察】：請指出「{focus}」中最容易看錯的地方。)",
            "問題2 (【聯想】：若套用同類型題目的方法，第一個要用的觀念是什麼？)",
            "問題3 (【執行】：寫出一行檢查式，驗證「{focus}」是否合理。)"
        )
    ]
    chosen = styles[variant % len(styles)]
    return [s.format(focus=focus) for s in chosen]


def _prompt_fingerprint(text):
    if not isinstance(text, str):
        return ''
    return re.sub(r'[\s\W_]+', '', text, flags=re.UNICODE).lower()


def diversify_follow_up_prompts(prompts, last_prompts, user_question='', question_context='', ai_reply='', turn_index=0):
    """Avoid cross-turn duplication by rewriting prompts when current equals previous turn."""
    current = normalize_follow_up_prompts(
        prompts,
        user_question=user_question,
        question_context=question_context,
        ai_reply=ai_reply
    )

    if not isinstance(last_prompts, list) or len(last_prompts) == 0:
        return current

    current_fp = [_prompt_fingerprint(p) for p in current]
    last_fp = [_prompt_fingerprint(p) for p in last_prompts[:3]]

    if current_fp == last_fp:
        return build_dynamic_follow_up_prompts_variant(
            user_question=user_question,
            question_context=question_context,
            ai_reply=ai_reply,
            variant=(turn_index + 1)
        )

    return current


def normalize_follow_up_prompts(prompts, user_question='', question_context='', ai_reply=''):
    """Keep valid prompts; regenerate if placeholders/generic text are returned."""
    cleaned = []
    if isinstance(prompts, list):
        for p in prompts[:3]:
            if isinstance(p, str):
                p = p.strip()
                if p and p.lower() != 'none':
                    cleaned.append(p)

    must_regen = len(cleaned) < 3 or all(_looks_generic_followup_prompt(p) for p in cleaned)
    if must_regen:
        return build_dynamic_follow_up_prompts(user_question, question_context, ai_reply)

    labels = ['【觀察】', '【聯想】', '【執行】']
    normalized = []
    for idx, p in enumerate(cleaned[:3]):
        if labels[idx] in p:
            normalized.append(p)
        else:
            normalized.append(f"問題{idx + 1} ({labels[idx]}：{p})")

    # 去重防呆：若三句提示過度相似，改用系統產生的穩定提示
    fps = [_prompt_fingerprint(p) for p in normalized]
    if len(set(fps)) < len(fps):
        return build_dynamic_follow_up_prompts(user_question, question_context, ai_reply)

    return normalized


def _unwrap_nested_reply_payload(reply_text):
    """If reply is a JSON string payload, extract nested reply/prompts safely."""
    if not isinstance(reply_text, str):
        return reply_text, None

    raw = reply_text.strip()
    if not (raw.startswith('{') and 'reply' in raw):
        return reply_text, None

    nested = clean_and_parse_json(raw)
    if not isinstance(nested, dict):
        return _extract_reply_and_prompts_from_jsonish(raw)

    nested_reply = nested.get('reply')
    nested_prompts = nested.get('follow_up_prompts')
    if isinstance(nested_reply, str):
        # clean_and_parse_json 失敗時可能回傳 {"reply": 原字串}，這裡要避免誤判為成功
        if _prompt_fingerprint(nested_reply) == _prompt_fingerprint(raw):
            return _extract_reply_and_prompts_from_jsonish(raw)
        if not isinstance(nested_prompts, list):
            nested_prompts = None
        return nested_reply, nested_prompts

    return _extract_reply_and_prompts_from_jsonish(raw)


def _extract_reply_and_prompts_from_jsonish(text):
    """Best-effort extractor for malformed JSON string payloads in reply."""
    if not isinstance(text, str):
        return text, None

    raw = text.strip()

    # 1) 抓 reply 欄位
    reply = raw
    match = re.search(r'"reply"\s*:\s*"([\s\S]*?)"\s*(,|\})', raw)
    if match:
        escaped = match.group(1)
        try:
            reply = json.loads(f'"{escaped}"')
        except Exception:
            reply = escaped.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

    # 2) 抓 follow_up_prompts 陣列
    prompts = None
    prompts_block = re.search(r'"follow_up_prompts"\s*:\s*\[([\s\S]*?)\]', raw)
    if prompts_block:
        items = re.findall(r'"((?:\\.|[^"])*)"', prompts_block.group(1))
        if items:
            decoded = []
            for it in items[:3]:
                try:
                    decoded.append(json.loads(f'"{it}"'))
                except Exception:
                    decoded.append(it.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\'))
            prompts = decoded

    return reply, prompts

def configure_gemini(api_key, model_name):
    global gemini_model, gemini_chat
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)
    gemini_chat = gemini_model.start_chat(history=[])  # 動態設定！

def diagnose_error(question_text, correct_answer, student_answer, prerequisite_units=None, conversation_history=None):
    """
    [Phase 6] 使用 LLM 診斷學生的錯誤類型並判斷是否與前置單元相關。

    Args:
        question_text (str): 題目內容。
        correct_answer (str): 正確答案。
        student_answer (str): 學生的答案。
        prerequisite_units (list, optional): 前置單元列表，格式 [{"id": "unit_id", "name": "單元名稱"}, ...]
        conversation_history (list, optional): AI 對話歷史，格式 [{"role": "...", "content": "..."}, ...]

    Returns:
        dict: {
            "error_type": "concept" | "calculation" | "careless" | "unknown",
            "related_prerequisite_id": "unit_id" or None,
            "prerequisite_explanation": "說明文字" or None
        }
    """
    try:
        model = get_model()
        
        # 準備前置單元資訊文字（簡化版）
        prereq_list = ""
        if prerequisite_units and len(prerequisite_units) > 0:
            prereq_list = "\n".join([f"- {p['name']} (ID: {p['id']})" for p in prerequisite_units])
        
        # 暫時移除對話歷史以節省 token
        # convo_info = ""
        # if conversation_history and len(conversation_history) > 0:
        #     convo_text = "\n".join([f"[{c['role']}]: {c['content']}" for c in conversation_history[-2:]])
        #     convo_info = f"\n對話: {convo_text}"
        
        prompt = f"""診斷錯誤。

題目: {question_text}
答案: {correct_answer}
學生: {student_answer}

前置單元:
{prereq_list if prereq_list else "無"}

正負號錯誤→推薦「正數與負數」

JSON:
{{
  "error_type": "concept",
  "related_prerequisite_id": "單元ID或null",
  "prerequisite_explanation": "簡短說明或null"
}}
"""
        
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 2000, "temperature": 0.1}
        )
        
        # 檢查 API 回應狀態
        print("=" * 80)
        print("[AI 診斷] API 狀態檢查:")
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            print(f"  - Finish Reason: {candidate.finish_reason}")
            if hasattr(candidate, 'safety_ratings'):
                print(f"  - Safety Ratings: {candidate.safety_ratings}")
        if hasattr(response, 'prompt_feedback'):
            print(f"  - Prompt Feedback: {response.prompt_feedback}")
        print("=" * 80)
        
        # 完整記錄 AI 回應
        print("[AI 診斷] 完整回應:")
        print(response.text)
        print("=" * 80)
        print(f"[AI 診斷] 回應長度: {len(response.text)} 字符")
        
        # 從 markdown 代碼塊中提取 JSON
        response_text = response.text.strip()
        
        # 移除 markdown 代碼塊標記
        if response_text.startswith('```'):
            # 找到第一個 { 和最後一個 }
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
                print(f"[AI 診斷] 提取的 JSON: {response_text}")
        
        # 使用既有的 robust JSON parser
        result = clean_and_parse_json(response_text)
        
        print(f"[AI 診斷] 解析結果: {result}")
        
        # 確保回傳格式正確
        return {
            "error_type": result.get("error_type", "unknown"),
            "related_prerequisite_id": result.get("related_prerequisite_id"),
            "prerequisite_explanation": result.get("prerequisite_explanation")
        }

    except Exception as e:
        current_app.logger.error(f"診斷錯誤類型失敗: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error_type": "unknown",
            "related_prerequisite_id": None,
            "prerequisite_explanation": None
        }

def get_model():
    if gemini_model is None:
        raise RuntimeError("Gemini 尚未初始化！")
    return gemini_model

def get_ai_prompt():
    """
    從資料庫讀取 AI Prompt，若不存在則使用預設值並寫入資料庫
    """
    from models import SystemSetting, db
    
    """
    從資料庫讀取 AI Prompt，若不存在則使用預設值並寫入資料庫
    """
    from models import SystemSetting, db
    
    # DEFAULT_PROMPT 已定義在全域
    
    try:
        # 嘗試從資料庫讀取
        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        
        if setting:
            return setting.value
        else:
            # 資料庫中沒有，寫入預設值
            new_setting = SystemSetting(
                key='ai_analyzer_prompt',
                value=DEFAULT_PROMPT,
                description='AI 分析學生手寫答案時使用的 Prompt 模板。必須保留 {context} 和 {prereq_text} 變數。回傳 JSON 須包含 follow_up_prompts。'
            )
            db.session.add(new_setting)
            db.session.commit()
            return DEFAULT_PROMPT
    except Exception as e:
        # 如果資料庫操作失敗，使用預設值
        print(f"Warning: Failed to read AI prompt from database: {e}")
        return DEFAULT_PROMPT

def analyze(image_data_url, context, api_key, prerequisite_skills=None):
    """
    強制 Gemini 回傳純 JSON，失敗時自動重試一次
    """
    def _call_gemini():
        # 將前置技能列表轉換為文字描述
        prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prerequisite_skills]) if prerequisite_skills else "無"

        # 解碼 Base64 圖片
        _, b64 = image_data_url.split(',', 1)
        img_data = base64.b64decode(b64)

        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name

        try:
            # 上傳到 Gemini
            file = genai.upload_file(path=temp_path)

            # 從資料庫讀取 Prompt 模板
            prompt_template = get_ai_prompt()
            
            # 使用 str.replace() 替換變數（避免 JSON 大括號衝突）
            prompt = prompt_template.replace("{context}", context).replace("{prereq_text}", prereq_text)

            model = get_model()
            resp = model.generate_content(
                [prompt, file],
                generation_config={"max_output_tokens": 4096, "temperature": 0.5}
            )
            raw_text = resp.text.strip()

            # 清理可能的 ```json 標記
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
            # [Fix] Use robust parser
            data = clean_and_parse_json(cleaned)
            
            # [關鍵] 強制注入嚴格模式清洗 (圖片路徑)
            if 'reply' in data:
                data['reply'] = enforce_strict_mode(data['reply'])
                
            return data

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # 最多嘗試 2 次
    for attempt in range(2):
        try:
            return _call_gemini()
        except json.JSONDecodeError as e:
            if attempt == 1:
                return {
                    "reply": f"AI 回應格式錯誤（第 {attempt+1} 次）：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False,
                    "follow_up_prompts": []
                }
            import time; time.sleep(1)  # 重試前延遲
        except Exception as e:
            if attempt == 1:
                return {
                    "reply": f"AI 分析失敗：{str(e)}",
                    "is_process_correct": False,
                    "correct": False,
                    "next_question": False,
                    "follow_up_prompts": []
                }
            import time; time.sleep(1)

    return {
        "reply": "AI 分析失敗，請稍後再試",
        "is_process_correct": False,
        "correct": False,
        "next_question": False,
        "follow_up_prompts": []
    }
    
def identify_skills_from_problem(problem_text):
    """
    Analyzes a math problem's text to identify relevant skills.
    """
    try:
        model = get_model()
        
        # Get the list of available skills from the skills directory
        skills_dir = os.path.join(os.path.dirname(__file__), '..', 'skills')
        skill_files = [f.replace('.py', '') for f in os.listdir(skills_dir) if f.endswith('.py') and f != '__init__.py']
        
        prompt = f"""
        You are an expert math teacher. Your task is to analyze a math problem and identify the key concepts or skills required to solve it.
        I will provide you with a math problem and a list of available skill IDs.

        **Math Problem:**
        "{problem_text}"

        **Available Skills:**
        {', '.join(skill_files)}

        Please identify up to 3 of the most relevant skills from the list that are directly applicable to solving this problem.

        **Instructions:**
        1.  Carefully read the problem to understand what is being asked.
        2.  Review the list of available skills.
        3.  Choose the skill IDs that best match the problem's requirements.
        4.  Return your answer in a JSON format with a single key "skill_ids" containing a list of the chosen skill ID strings.

        **Example Response:**
        {{
          "skill_ids": ["quadratic_equation", "factoring"]
        }}

        Do not include any other text or explanations. Just the JSON object.
        """
        
        resp = chat.send_message(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
        raw_text = resp.text.strip()
        
        # Clean up potential markdown formatting
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
        
        data = json.loads(cleaned)
        
        # Basic validation
        if "skill_ids" in data and isinstance(data["skill_ids"], list):
            return data["skill_ids"]
        else:
            # Log or handle the case where the response is not in the expected format
            return []
            
    except json.JSONDecodeError as e:
        # Log or handle JSON parsing errors
        print(f"AI response JSON decode error: {e}")
        return []
    except Exception as e:
        # Log or handle other exceptions
        print(f"An error occurred in identify_skills_from_problem: {e}")
        return []

def ask_ai_text(user_question):
    try:
        model = get_model()
        prompt = f"""
        你是功文數學 AI 助教，用繁體中文親切回答。
        要求：
        1. 多項式用這種格式：f(x) = x³ - 8x² + 9x + 5
        2. 不要用 $...$ 或 LaTeX
        3. 例題用「範例：」開頭
        4. 步驟用數字 1. 2. 3.
        5. 結尾加鼓勵話，如「加油～」
        
        學生問題：{user_question}
        """
        resp = chat.send_message(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
        return resp.text.strip()
    except Exception as e:
        return f"AI 錯誤：{str(e)}"
    
# core/ai_analyzer.py
def ask_ai_text_with_context(user_question, context=""):
    """
    聊天專用 AI：帶入當前題目 context
    """
    model = get_model()
    
    system_prompt = f"""
    [CRITICAL RULES]
    1. STYLE: Senior Professor. No greeting (Hi, Hello), No praise (Good job, Great), No encouragement (Don't worry, Keep going).
    2. LENGTH: MAX 80 words.
    3. CONTENT: Point out errors directly using questions.
    4. FORMAT: Use single $ for LaTeX. Example: $x^2$.
    5. JSON: Must include 'reply' and 'follow_up_prompts' ([Observe], [Relate], [Execute]).
    
    【當前題目】：
    {context or "（無題目資訊）"}
    
    【學生問題】：
    {user_question}
    
    要求：
    1. 如果有題目，必須參考題目內容
    2. 多項式用 x^3 格式（如 x^3 - 2x^2 + 1）
    3. 例題用「範例：」開頭
    4. 步驟用 1. 2. 3.
    5. 結尾加鼓勵話，如「加油～」
    """
    
    try:
        resp = model.generate_content(
            system_prompt,
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
        return resp.text.strip()
    except Exception as e:
        return f"AI 內部錯誤：{str(e)}"


def generate_quiz_from_image(image_file, description):
    """
    Generates a quiz from an image and a text description using a multimodal AI model.
    """
    try:
        model = get_model()

        # Prepare the image for the API
        img = PIL.Image.open(image_file.stream)

        prompt = f"""
        You are an expert math quiz generator. Your task is to create a quiz based on the provided image and description.

        **Description:**
        "{description}"

        **Instructions:**
        1.  Analyze the image, which contains a math problem or concept.
        2.  Use the user's description to understand what kind of quiz to generate (e.g., number of questions, question type).
        3.  Generate a list of questions. Each question should have a question text, a list of options (if applicable), and the correct answer.
        4.  Return your answer in a JSON format with a single key "questions" containing a list of the question objects.
        5.  The structure for each question object should be: {{"question_text": "...", "options": ["...", "...", "..."], "correct_answer": "..."}}. For free-response questions, the "options" key can be omitted.

        **Example Response:**
        {{
          "questions": [
            {{
              "question_text": "What is the first step to solve the equation in the image?",
              "options": ["Add 5 to both sides", "Subtract 5 from both sides", "Multiply by 2"],
              "correct_answer": "Subtract 5 from both sides"
            }},
            {{
              "question_text": "What is the final value of x?",
              "correct_answer": "x = 3"
            }}
          ]
        }}

        Do not include any other text or explanations. Just the JSON object.
        """

        # Generate content with both the prompt and the image
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()

        # Clean up potential markdown formatting
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)

        data = json.loads(cleaned)

        # Basic validation
        if "questions" in data and isinstance(data["questions"], list):
            return data.get("questions", [])
        else:
            current_app.logger.error("AI response for quiz generation was not in the expected format.")
            return []

    except json.JSONDecodeError as e:
        current_app.logger.error(f"AI response JSON decode error in quiz generation: {e}")
        return []
    except Exception as e:
        current_app.logger.error(f"An error occurred in generate_quiz_from_image: {e}")
        return []


def build_chat_prompt(skill_id, user_question, full_question_context, context, prereq_skills):
    """
    Constructs the full system prompt for the chat AI.
    1. Tries to load specific prompt from SkillInfo.
    2. Falls back to SystemSetting or DEFAULT_CHAT_PROMPT.
    3. Handles variable replacement and strict JSON instruction appending.
    """
    from models import SkillInfo, SystemSetting
    
    from models import SkillInfo, SystemSetting
    
    # DEFAULT_CHAT_PROMPT 已定義在全域

    prompt_template = None

    # [SYSTEM OVERRIDE] 改為「引導式學習助教」，不做評分、不聊天。
    base_instruction = """
[SYSTEM OVERRIDE - GUIDED LEARNING TUTOR]
角色：你是「引導式學習助教」，不是評分器、不是聊天機器人。
語言：一律繁體中文。
任務：只做一件事——引導學生做下一步思考。

禁止：
1) 禁止直接判斷對錯（不可說：你錯了、你對了、有道理、不對）。
2) 禁止認同學生答案的正確性（除非系統已明示正確；本路徑一律視為未知，不做認定）。
3) 禁止提供最終答案或完整解題步驟。
4) 禁止閒聊、鼓勵語堆疊、長篇解說。

輸出風格（固定三段）：
這題的關鍵是：{一個核心概念}

想一下：
{一個引導問題}

👉 試著從這一步開始。

要求：
- 每次只提示一個概念 + 一個問題。
- 內容短、準、可操作；總長盡量精簡。
- 不可出現「你這樣對/錯」、「這部分有道理」等評價語。
"""
    
    # 強制忽略 DB，直接使用 Override 指令
    prompt_template = base_instruction

    # 2. If no skill prompt, try SystemSetting
    if not prompt_template:
        try:
            setting = SystemSetting.query.filter_by(key='chat_ai_prompt').first()
            if setting:
                prompt_template = setting.value
        except Exception:
            pass

    # 3. Use Default if still None
    if not prompt_template:
        prompt_template = DEFAULT_CHAT_PROMPT

    # 4. Construct Context Strings
    prereq_text = ", ".join([f"{p['name']} ({p['id']})" for p in prereq_skills]) if prereq_skills else "無"
    
    enhanced_context = f"當前題目：{full_question_context}"
    if context and context != full_question_context:
        enhanced_context += f"\n詳細資訊：{context}"
    enhanced_context += f"\n\n此單元的前置基礎技能有：{prereq_text}。"

    # 5. Format the template
    try:
        # Check if template expects 'context' or strict format
        # For safety, we try to inject values if placeholders exist, 
        # or just append if it's a simple string.
        # But assuming our templates use {context} and {user_answer}
        full_prompt = prompt_template.format(
            user_answer=user_question,
            correct_answer="（待批改）",
            context=enhanced_context,
            prereq_text=prereq_text
        )
    except Exception:
        # Fallback formatting if template keys mismatch
        full_prompt = f"{prompt_template}\n\n[系統補完]\n題目：{enhanced_context}\n學生問題：{user_question}"

    # 關鍵：無論 template 是否有 placeholders，都強制附上本輪學生問題，避免每輪輸入看起來一樣。
    full_prompt += f"\n\n【本輪學生提問】\n{user_question or '（學生未提供）'}"

    # 6. Prepend Title (Optional, specific to requirement)
    if "【學生當前正在練習的題目】" not in full_prompt:
        full_prompt = f"【學生當前正在練習的題目】\n{full_question_context}\n\n" + full_prompt

    # 7. Priority System Instruction (hard guardrail for edge model)
    ultra_short_prompt = """
[CRITICAL RULES]
1. 你是引導式學習助教，只能引導，不可評價對錯。
2. 不可說「你錯了／你對了／有道理／不對」。
3. 不可提供最終答案或完整解題步驟。
4. 回覆限 2~3 行，且只包含：一個概念提示 + 一個引導問題 + 行動句。
5. 語氣像老師提示，不聊天。
6. JSON 必須含 reply 與 follow_up_prompts。
"""
    
    # Prepend this to ensure it's the first thing logic sees or append heavily
    full_prompt = ultra_short_prompt + "\n\n" + full_prompt

    # 8. Append Rigid JSON Instructions
    full_prompt += """

請嚴格輸出 JSON（不可 Markdown、不可多餘文字）：
{
  "hint_focus": "...",
  "guided_question": "...",
  "micro_step": "...",
  "forbidden": false
}

欄位規範：
- hint_focus：只指出一個核心概念，不超過 18 個中文字。
- guided_question：只能問一個引導問題，不超過 28 個中文字。
- micro_step：只能給一個下一步動作，不超過 22 個中文字。
- forbidden：若你輸出了任何違規內容請設為 true，否則 false。

違規內容（禁止）：
- 你錯了 / 你對了 / 有道理 / 不對 / 很棒 / 沒關係 / 再試試
- 答案是...
- 直接給最後結果或完整解法
- 聊天語氣或陪伴式語氣
"""
    
    return full_prompt

def get_chat_response(prompt, image=None, user_question='', question_context=''):
    global gemini_chat
    if gemini_chat is None and gemini_model is not None:
        gemini_chat = gemini_model.start_chat(history=[])

    # Primary path for Practice AI tutor:
    # use config.py -> MODEL_ROLES['tutor'].
    # Keep the legacy Gemini flow below as fallback for quick rollback.
    try:
        tutor_client = get_ai_client(role='tutor')
        tutor_response = tutor_client.generate_content(
            prompt + " (IMPORTANT: Output ONLY valid JSON. Escape all backslashes.)"
        )
        tutor_raw_text = getattr(tutor_response, 'text', '') or ''
        if tutor_raw_text.strip():
            data = None
            try:
                data = json.loads(tutor_raw_text)
            except json.JSONDecodeError:
                data = clean_and_parse_json(tutor_raw_text)

            if data is not None:
                reply_text = data.get('reply', '')
                nested_prompts = None
                if isinstance(reply_text, str):
                    reply_text, nested_prompts = _unwrap_nested_reply_payload(reply_text)
                    reply_text = reply_text.replace('**', '')
                data['reply'] = sanitize_tutor_reply(
                    enforce_strict_mode(reply_text),
                    user_question=user_question,
                    question_context=question_context,
                )
                prompt_source = nested_prompts if isinstance(nested_prompts, list) else data.get('follow_up_prompts', [])
                data['follow_up_prompts'] = normalize_follow_up_prompts(
                    prompt_source,
                    user_question=user_question,
                    question_context=question_context,
                    ai_reply=data.get('reply', '')
                )
                return data
    except Exception as tutor_exc:
        print(f"[chat_ai] tutor role path failed; fallback to legacy Gemini path: {tutor_exc}")

    """
    取得 Gemini 的回應，並確保回傳格式為 JSON。
    """
    if not gemini_model:
        return {
            "reply": "系統尚未初始化 (API Key 可能無效)。",
            "follow_up_prompts": []
        }

    try:
        # 準備請求內容
        content = [prompt + " (IMPORTANT: Output ONLY valid JSON. Escape all backslashes.)"]
        if image:
            # 確保 image 是 PIL Image 物件或 blob
            # 這裡假設 image 是 PIL Image
            content.append(image)

        # 呼叫 Gemini
        # 注意: ChatSession.send_message 支援列表 [text, image]
        response = gemini_chat.send_message(
            content,
            generation_config=genai.types.GenerationConfig(
                response_mime_type='application/json', # 強制 JSON
                temperature=0.5,
                max_output_tokens=2048, 
            )
        )
        
        raw_text = response.text
        
        # 嘗試解析 (優先使用官方 JSON 模式，失敗則用強力清洗)
        # 統一處理 JSON 解析
        data = None
        try:
            # 優先嘗試標準 JSON 解析
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # 解析失敗則嘗試清洗
            data = clean_and_parse_json(raw_text)

        # [關鍵修復]：如果解析/清洗後還是 None，回傳一個安全預設值
        if data is None:
            print(f"解析失敗，原始回傳: {raw_text}")
            return {
                "reply": "運算發生錯誤，請試著換個方式問問看。", 
                "follow_up_prompts": ["重試"]
            }

        # [強制嚴格模式] 無論來源為何，都必須執行清洗
        reply_text = data.get('reply', '')
        nested_prompts = None

        # 模型偶爾會把整包 JSON 放進 reply 字串，先拆開避免前端顯示原始 JSON
        if isinstance(reply_text, str):
            reply_text, nested_prompts = _unwrap_nested_reply_payload(reply_text)
        
        # 1. 移除 Markdown 粗體語法 (轉為純文字)
        if isinstance(reply_text, str):
            reply_text = reply_text.replace('**', '')
        
        # 2. 呼叫全域嚴格模式清洗 (去廢話 + 保護 LaTeX)
        data['reply'] = sanitize_tutor_reply(
            enforce_strict_mode(reply_text),
            user_question=user_question,
            question_context=question_context,
        )
        
        # 3. 確保 follow_up_prompts 存在
        prompt_source = nested_prompts if isinstance(nested_prompts, list) else data.get('follow_up_prompts', [])
        data['follow_up_prompts'] = normalize_follow_up_prompts(
            prompt_source,
            user_question=user_question,
            question_context=question_context,
            ai_reply=data.get('reply', '')
        )
            
        return data

    except Exception as e:
        print(f"AI 生成錯誤: {e}")
        return {
            "reply": "連線忙碌中，請稍後再試。", 
            "follow_up_prompts": ["重試"]
        }

# 預設弱點分析 Prompt
DEFAULT_WEAKNESS_ANALYSIS_PROMPT = """
你是一位專業的數學教學診斷專家。請根據以下學生的錯題記錄，使用「質性分析」方式推估各單元的熟練度。

{prompt_data}

**分析規則**：
1. **概念錯誤**：代表學生對該單元的核心概念不熟練，應大幅降低熟練度分數 (建議扣 30-50 分)
2. **計算錯誤/粗心**：代表學生概念理解但執行細節有誤，應輕微扣分 (建議扣 5-15 分)
3. **考卷資料權重**：請特別重視「考卷診斷」的結果，若考卷答錯，代表真實考試情境下的弱點，權重應高於平時練習。
4. **信心度與評語**：若 AI 評語包含正向詞彙 (如「掌握良好」、「理解正確」)，或是考卷信心度高且正確，可適度提高熟練度
5. **基準分數**：假設學生初始熟練度為 80 分，根據錯誤情況與考卷表現進行調整

請以 JSON 格式回傳分析結果：
{{
  "mastery_scores": {{
    "單元名稱1": 85,
    "單元名稱2": 60
  }},
  "overall_comment": "整體學習評語 (100 字以內)",
  "recommended_unit": "建議優先加強的單元名稱"
}}

注意：
- 熟練度分數範圍 0-100，分數越高代表越熟練
- 請務必回傳有效的 JSON 格式
- mastery_scores 的 key 必須是上述提供的單元名稱
"""

def analyze_student_weakness(prompt_data):
    """
    Calls Gemini to analyze student weakness based on mistake logs.
    """
    try:
        model = get_model() # Use shared model instance
        
        prompt = DEFAULT_WEAKNESS_ANALYSIS_PROMPT.format(prompt_data=prompt_data)
        
        response = model.generate_content(
            prompt + " (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer. Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\frac instead of \frac).)",
            generation_config={"max_output_tokens": 4096, "temperature": 0.5}
        )
        ai_response_text = response.text.strip()
        
        # Clean JSON
        cleaned = re.sub(r'^```json\s*|\s*```$', '', ai_response_text, flags=re.MULTILINE)
        return json.loads(cleaned)
        
    except Exception as e:
        print(f"Weakness Analysis Error: {e}")
        # == Fallback: Heuristic Analysis when AI fails ==
        # Parse prompt_data assuming the format: "【Skill】\n... 總錯誤次數: N ..."
        fallback_scores = {}
        fallback_recommendation = "所有單元"
        max_errors = -1
        
        try:
            # Simple regex to find skills and errors from the prompt text we just built
            # Format: 【SkillName】... 總錯誤次數: N
            skill_blocks = re.split(r'【(.*?)】', prompt_data)
            
            # loop through 1, 3, 5... which are skill names, and 2, 4, 6... which are contents
            for i in range(1, len(skill_blocks), 2):
                skill_name = skill_blocks[i]
                content = skill_blocks[i+1]
                
                # Default score
                score = 80 
                
                # Check errors
                concept_match = re.search(r'概念錯誤: (\d+)', content)
                calculation_match = re.search(r'計算錯誤: (\d+)', content)
                total_match = re.search(r'總錯誤次數: (\d+)', content)
                
                c_err = int(concept_match.group(1)) if concept_match else 0
                calc_err = int(calculation_match.group(1)) if calculation_match else 0
                total_err = int(total_match.group(1)) if total_match else 0
                
                # Deduct points
                score -= (c_err * 15) + (calc_err * 5)
                score = max(0, min(100, score)) # Clamp 0-100
                
                fallback_scores[skill_name] = score
                
                if total_err > max_errors:
                    max_errors = total_err
                    fallback_recommendation = skill_name
                    
        except Exception as fallback_e:
            print(f"Fallback logic failed: {fallback_e}")
            
        return {
            "mastery_scores": fallback_scores,
            "overall_comment": f"目前無法連線至 AI 伺服器 (錯誤: {str(e)})，系統已根據您的錯誤次數自動計算熟練度。建議您針對錯誤較多的單元進行複習。",
            "recommended_unit": fallback_recommendation
        }

def analyze_question_image(image_file):
    """
    Analyzes an uploaded image to extract the math question and solve it.
    Returns:
        dict: {
            "question_text": "extracted question",
            "correct_answer": "calculated answer",
            "answer_type": "text" (or other types if needed)
        }
    """
    try:
        model = get_model()

        # Prepare the image for the API
        img = PIL.Image.open(image_file.stream)

        prompt = """
        You are an expert math solver.
        1. OCR: Extract the math question text from the image accurately. Use LaTeX for math symbols in the QUESTION TEXT (surrounded by single $).
        2. SOLVE: Solve the problem step-by-step to find the final answer.
        3. TOPIC: Analyze the core mathematical concept of this problem (e.g., 'Polynomial Division', 'Law of Cosines').
        4. OUTPUT: Return a JSON object with:
           - "question_text": The extracted question text. (Use LaTeX for math).
           - "correct_answer": The final result/answer in a STUDENT-FRIENDLY PLAIN TEXT format.
             - Do NOT use LaTeX or '$' in the correct_answer.
             - For fractions, use 'a/b' (e.g., '1/2').
             - For coordinates, use '(x, y)' (e.g., '(3, 5)').
             - For text, return just the text.
             - Keep it simple so a student can type it easily.
           - "answer_type": "text"
           - "predicted_topic": "The predicted mathematical concept."
        
        Example JSON:
        {
          "question_text": "Calculate $1 + 1$",
          "correct_answer": "2",
          "answer_type": "text",
          "predicted_topic": "Arithmetic"
        }
        
        Do not include any other text.
        """

        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()
        
        # Clean JSON
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
        
        # Parse
        data = clean_and_parse_json(cleaned)
        
        if data and "question_text" in data and "correct_answer" in data:
            return data
        else:
            return {"error": "AI could not parse the question."}

    except Exception as e:
        print(f"Error in analyze_question_image: {e}")
        return {"error": f"Analysis failed: {str(e)}"}
