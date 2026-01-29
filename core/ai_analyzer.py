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
            # 如果失敗，嘗試修復可能被截斷或轉義錯誤的字串
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
    "問題1 (【觀察】：引導學生觀察圖形或算式特徵)",
    "問題2 (【聯想】：提示相關公式或策略)",
    "問題3 (【執行】：具體修正步驟或驗算)"
  ]
}
"""

def configure_gemini(api_key, model_name):
    global gemini_model, gemini_chat
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name)
    gemini_chat = gemini_model.start_chat(history=[])  # 動態設定！

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
            data = json.loads(cleaned)
            
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

    # [SYSTEM OVERRIDE] 強制設定，覆蓋任何資料庫傳來的軟性指令
    # 我們不讀取 skill.gemini_prompt，以免舊的暖男指令汙染
    base_instruction = """
[SYSTEM OVERRIDE]
ROLE: Strict Math Professor.
TONE: Cold, Direct, Concise.
FORBIDDEN: "同學", "你好", "很棒", "加油", "別擔心", "不過", "試試看".
LENGTH: Max 80 words.
TASK: 
1. Identify the error in 1 sentence.
2. Ask 1 leading question.
3. Output standard JSON with "follow_up_prompts".
LATEX: Use single backslash e.g. $x^2$.
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

    # 6. Prepend Title (Optional, specific to requirement)
    if "【學生當前正在練習的題目】" not in full_prompt:
        full_prompt = f"【學生當前正在練習的題目】\n{full_question_context}\n\n" + full_prompt

    # 7. Priority System Instruction (Override any fluff)
    ultra_short_prompt = """
    [CRITICAL RULES]
    1. STYLE: Senior Professor. No greeting (Hi, Hello), No praise (Good job, Great), No encouragement (Don't worry, Keep going).
    2. LENGTH: MAX 80 words.
    3. CONTENT: Point out errors directly using questions.
    4. FORMAT: Use single $ for LaTeX. Example: $x^2$.
    5. JSON: Must include 'reply' and 'follow_up_prompts' ([Observe], [Relate], [Execute]).
    """
    
    # Prepend this to ensure it's the first thing logic sees or append heavily
    full_prompt = ultra_short_prompt + "\n\n" + full_prompt

    # 8. Append Rigid JSON Instructions
    full_prompt += """
    
    # We need to guide the student further using Socratic method.
    請**嚴格按照以下 JSON 格式回覆**，不要加入任何過多文字。
    
    {
      "reply": "用繁體中文回答學生的問題。如果學生答錯，給予引導；如果答對，給予鼓勵。**請完全口語化，不要使用「思考：」、「步驟：」等標題**。每次回話不超過 40 字。",
      "follow_up_prompts": [
          "問題1 (【觀察】：老師，這裡的...為什麼...？)",
          "問題2 (【聯想】：如果我不...，還有別的方法嗎？)",
          "問題3 (【執行】：這題的陷阱是不是在...？)"
      ]
    }
    direct output JSON. No Markdown.
    請確保 `reply` 欄位只包含對學生的直接回應。
    
    【重要】：若內容過長，請優先保證 JSON 結構的完整性 (結尾必須有 } )，可適度縮減 reply 內容。
    【重要】：所有數學符號的反斜線必須跳脫，例如 \\sqrt{}, \\frac{}。
    """
    
    return full_prompt

def get_chat_response(prompt, image=None):
    global gemini_chat
    if gemini_chat is None and gemini_model is not None:
        gemini_chat = gemini_model.start_chat(history=[])

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
        
        # 1. 移除 Markdown 粗體語法 (轉為純文字)
        if isinstance(reply_text, str):
            reply_text = reply_text.replace('**', '')
        
        # 2. 呼叫全域嚴格模式清洗 (去廢話 + 保護 LaTeX)
        data['reply'] = enforce_strict_mode(reply_text)
        
        # 3. 確保 follow_up_prompts 存在
        if 'follow_up_prompts' not in data:
            data['follow_up_prompts'] = []
            
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
