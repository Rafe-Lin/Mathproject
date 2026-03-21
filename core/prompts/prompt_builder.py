# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/prompts/prompt_builder.py
# Version: V2.3 (Added BARE_PROMPT_TEMPLATE for realistic user simulation)
# Last Updated: 2026-01-30
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   Prompt 構建引擎 - 負責生成不同 Ablation 模式的 Prompt
#   [Research Edition] 用於消融研究實驗
#
# [Ablation Modes]:
#   1. BARE_PROMPT_TEMPLATE: 模擬一般用戶的 Prompt（Ab1 對照組）
#   2. UNIVERSAL_GEN_CODE_PROMPT: 完整規格書（Ab2/Ab3 實驗組）
#
# [Core Technology]:
#   - Template-based prompt generation
#   - Dynamic prompt assembly based on mode
#
# [Logic Flow]:
#   1. Input: (master_spec, mode, model_name)
#   2. Select Template based on mode
#   3. Inject MASTER_SPEC or Examples
#   4. Return final prompt string
# ==============================================================================

import logging

logger = logging.getLogger(__name__)

# ==============================================================================
# [2026-01-30 新增] Ab1 Bare Prompt Template - 模擬一般用戶
# ==============================================================================
# 設計理念：
# - 模擬「一般老師」會如何跟 AI 下 Prompt
# - 使用自然語言，無工程化指導
# - 給 1-2 個參考例題，讓 AI 自己推理
# - 完全獨立於 UNIVERSAL_GEN_CODE_PROMPT 和 MASTER_SPEC
# ==============================================================================

BARE_PROMPT_TEMPLATE = """【角色設定】
你是一位中學數學老師的「出題助理」。

【任務說明】
請幫我寫一個 Python 程式，用來自動生成數學題目。
★ 題目主題是：「{topic}」（請務必針對此主題出題，不要生成其他類型的題目）
這個程式需要隨機產生數字，每次執行都能變換數值。
請使用跟課本一樣的格式表達數學式子。

【參考例題】
以下是我們想模仿的題目類型（請參考這個邏輯來寫程式）：
{textbook_example}

【程式要求】
1. 請寫成兩個函式：
   - `def generate(level=1, **kwargs)`: 生成題目
   - `def check(user_answer, correct_answer)`: 檢查答案是否正確

2. `generate` 函式要回傳一個字典 (Dictionary)，包含以下欄位（請照抄 key 名稱）：
   - 'question_text': 題目文字
   - 'answer': 空字串 ''
   - 'correct_answer': 正確答案（必須是字串，例如："24" 或 "3x^2+5"；多個答案用逗號分隔）
   - 'mode': 1

3. `check` 函式請回傳一個字典，包含：
   - 'correct': True 或 False
   - 'result': 回傳 '正確' 或 '錯誤'

# --- [教授的科學測試：開放 Sympy 與放寬限制] ---
# (原版限制) 4. 請使用 Python 的 standard library (如 random, math) 即可。
# (原版限制)    - 🔴 重要：不要使用 sympy、numpy 或其他外部套件
4. 允許使用 Python 標準庫（math, random 等）與 sympy 套件來輔助計算與 LaTeX 格式化。

⚠️ 重要：只輸出 Python 程式碼！
- ✅ 正確：直接從 import 開始寫
- ❌ 錯誤：不要加任何說明文字或註解在程式碼之外
- ❌ 錯誤：不要在程式碼後面加「這個程式碼會...」的說明
- ❌ 錯誤：不要在程式碼後面加英文說明（如 "This code defines..."）
- ❌ 錯誤：不要用 ```python 包裹代碼
- ❌ 錯誤：不要加 Example usage 或 `if __name__ == '__main__'`
- ❌ 錯誤：不要加 Explanation/說明段落
- 🔴 CRITICAL：程式碼結束後不可有任何文字（包括空白行後的說明）
"""

# ==============================================================================
# [Fallback] BARE_MINIMAL_PROMPT - 保留作為備用
# ==============================================================================
# 注意：這個已被 BARE_PROMPT_TEMPLATE 取代，但保留以保持向後相容
# ==============================================================================

BARE_MINIMAL_PROMPT = r"""你是 Python 程式設計師。請根據以下 MASTER_SPEC 生成數學題目生成函數。

要求：
1. 實作函數：def generate(level=1, **kwargs)
2. ⚠️ 回傳字典格式（必須同時包含雙鍵）：
   return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
3. 只輸出 Python 代碼，不要有任何說明或 Markdown 標記

🔴 LaTeX 格式鐵律（必須遵守）：
   question_text 格式：
      ✅ 正確："計算 $(-3) + 5$ 的值"（中文在外，數學式用 $ $ 包裹）
      ✅ 正確："求 $2 \times (-4)$ 的結果"
      ❌ 錯誤："$(-3) + 5$"（缺少中文說明）
      ❌ 錯誤："計算$(-3) + 5$的值"（$ $ 與中文直接相連）
   
   answer 格式：
      ✅ 正確："42"（純數字）
      ✅ 正確："\frac{3}{7}"（LaTeX 分數，不含 $ $）
      ❌ 錯誤："答案是 42"（不要加中文說明）

📐 題目字串拼接範例（3步驟標準流程）：
   # 步驟1: 先拼接數學式（不含 $ $）
   math_expr = f"{fmt_num(n1)} {op_latex['+']} {fmt_num(n2)}"
   
   # 步驟2: 組合中文與數學式（手動加 $ $）
   q = f"計算 ${math_expr}$ 的值"  # ⚠️ 使用簡短變量名 q
   
   # 步驟3: 最後呼叫 clean_latex_output()（可選，用於進階清洗）
   q = clean_latex_output(q)
   
   # 步驟4: 格式化答案為純數字字符串
   a = str(answer)  # ⚠️ 使用簡短變量名 a
   
   # ⚠️ 返回格式（必須完全遵守）：
   return {
       'question_text': q,
       'correct_answer': a,
       'answer': a,         # ⚠️ CRITICAL: 必須同時包含此鍵（與 correct_answer 值相同）
       'mode': 1
   }

❌ 常見錯誤（絕對不要這樣寫）：
   # 錯誤1: 在 f-string 內呼叫 clean_latex_output()
   q_str = f"計算 {clean_latex_output(expr)} 的值"  # ❌ 錯誤
   
   # 錯誤2: 字串拼接時用 + 運算符混合函式呼叫
   q_str = f"計算 {clean_latex_output(fmt_num(n1) + op_latex['*'] + fmt_num(n2))} 的值"  # ❌ 錯誤
   
   # 錯誤3: 只返回單一 answer 鍵
   return {'question_text': q, 'answer': a, 'mode': 1}  # ❌ 缺少 'correct_answer'
   
   # 錯誤4: 變量名過長
   question_text = "..."  # ❌ 應使用 q
   answer = "..."         # ❌ 應使用 a

📐 使用以下工具函數（已預先定義）：
   - fmt_num(x): 格式化數字（負數自動加括號）
   - op_latex: 運算符映射字典 {'+': '+', '-': '-', '*': '\\times', '/': '\\div'}
   - clean_latex_output(q_str): 自動清洗 LaTeX 格式（僅用於最後一步）

提示：你可以使用 Python 的 random, math, Fraction 等標準庫。
"""

# ==============================================================================
# 完整的 UNIVERSAL_GEN_CODE_PROMPT（針對 14B 模型優化的鷹架版）
# ==============================================================================

UNIVERSAL_GEN_CODE_PROMPT = """【角色】K12 數學演算法工程師

【任務】
實作 `def generate(level=1, **kwargs)` 函數，根據 MASTER_SPEC 生成數學問題的完整 Python 代碼。
該函數應返回 dict: {{'question_text': str, 'correct_answer': str, 'answer': str, 'mode': 1}}

【參考範例】(請模仿此題型風格生成)
{textbook_example_section}

【預載工具 API 手冊】(環境已實作，請直接調用，無需重新定義)

1. **基礎工具**
   - `fmt_num(n) -> str`: 格式化數字
   - `to_latex(n) -> str`: 轉 LaTeX 格式
   - `clean_latex_output(latex_str) -> str`: LaTeX 格式清洗和包裹 (自動添加 $)


【核心規則】
1. ✅ shuffle + slice 避免無限迴圈
2. ✅ 數學式用 $ 包裹
3. ✅ 答案純結果，不含符號
4. ✅ Data Flow: coeffs -> terms -> 計算 -> plain text
5. ✅ 只輸出代碼

⚠️ **返回格式檢查**
• 必須返回字典 {{'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}}
• correct_answer 必須是字串
• question_text 數學式必須用 $ 包裹
"""


class PromptBuilder:
    """
    Prompt 構建引擎 - 負責生成不同 Ablation 模式的 Prompt
    [V2.4 新增] 上下文感知工具選用系統 (Context-Aware Tool Selection)
    
    支援 3 種 Ablation 模式：
    - Ab1: BARE_MINIMAL_PROMPT (最簡 Prompt)
    - Ab2: UNIVERSAL_GEN_CODE_PROMPT + MASTER_SPEC + 動態工具選擇
    - Ab3: UNIVERSAL_GEN_CODE_PROMPT + MASTER_SPEC + 動態工具選擇 (默認)
    
    [新增功能] 自動感知並選用數學工具：
    - 根據題目關鍵字動態組裝 API 手冊
    - 只給 LLM 看它需要的工具（節省 Token，減少幻覺）
    - 植入決策指令確保工具正確使用
    """
    
    # ==========================================
    # 工具庫手冊定義 (Domain Function Manuals)
    # ==========================================
    
    # [V2.5 新增] 基礎工具手冊 - 所有題型都使用
    MANUAL_BASE = """
### 基礎工具 (全域可用)
- `fmt_num(n) -> str`: 格式化數字，負數會自動加括號 (例: -5 -> "(-5)")。
- `to_latex(n) -> str`: 將數字轉換為 LaTeX 格式 (支援分數、整數、小數)。
- `clean_latex_output(latex_str) -> str`: LaTeX 格式清洗和包裹，自動添加 $ 符號。
"""
    
    MANUAL_INTEGER = """
### 1. 基礎與整數工具 (IntegerOps) - [預設啟用]
- `fmt_num(n)`: 格式化數字，負數會自動加括號 (例: -5 -> "(-5)")。
- `IntegerOps.random_nonzero(min, max)`: 生成非零整數 (避免除以零)。
- `IntegerOps.is_divisible(a, b)`: 檢查整除。
"""
    
    # [V2.5 新增] 多項式專用工具 - 僅在檢測到多項式關鍵字時載入
    MANUAL_POLYNOMIAL = """
### 多項式與微分工具 (CalculusOps - Polynomial Module) - [檢測到多項式/微分關鍵字時啟用]
- `_coeffs_to_terms(coeffs: list) -> list[tuple]`: 將係數列表轉換為 (係數, 次數) 的 terms 清單。
- `_differentiate_poly(terms, order=1) -> list[tuple]`: 對多項式進行符號微分，支援高階導數。
- `_poly_to_latex(terms) -> str`: 將 terms 轉換為 LaTeX 格式字串 (不含 $)。
- `_poly_to_plain(terms) -> str`: 將 terms 轉換為純文字格式。
- `_deriv_symbol_latex(order) -> str`: 生成導數符號 (例: 一階 → f', 二階 → f'')。
- `build_polynomial_text(coeffs) -> str`: 根據係數列表構建多項式文字表示 (例: [2, 0, -3, 1] → "2x^3 - 3x + 1")。

**規則**: 涉及多項式、微分或導函數操作時，必須使用此模組。禁止自行實現多項式運算。
"""

    MANUAL_FRACTION = """
### 2. ✨ 分數工具 (FractionOps) - [檢測到分數相關關鍵字時啟用]
- `FractionOps.create(num, den)`: 建立分數，自動約分。
- `FractionOps.to_latex(frac, mixed=True)`: 輸出 LaTeX (mixed=True 為帶分數格式)。
- `FractionOps.add(a, b)`, `sub`, `mul`, `div`: 分數四則運算。
**規則**: 涉及有理數運算時，必須使用此模組，嚴禁使用 float。
"""

    MANUAL_RADICAL = """
### 3. ✨ 根號與幾何工具 (RadicalOps) - [檢測到根號/幾何關鍵字時啟用]
- `RadicalOps.create(inner)`: 建立根號 sqrt(inner) 並自動化簡 (例: sqrt(12)->2sqrt(3))。
- `RadicalOps.to_latex(expr)`: 輸出標準 LaTeX 根式。
- `RadicalOps.is_perfect_square(n)`: 檢查完全平方數。
**規則**: 涉及無理數或幾何運算(畢氏定理)時，必須使用此模組。
"""
    
    @staticmethod
    def _get_dynamic_api_manual(skill_name: str, skill_desc: str) -> tuple:
        """
        [V2.5 更新] 根據題目關鍵字，動態組裝 API 手冊 (Token 優化版)
        
        核心邏輯：
        - 先載入基礎工具 (MANUAL_BASE) - 所有題型都需要
        - 掃描技能名稱和描述中的關鍵字
        - 根據檢測結果動態載入相應的領域工具手冊
        - 節省 Token，減少 LLM 幻覺
        
        Args:
            skill_name: 技能名稱 (例: "整數的四則運算")
            skill_desc: 技能描述
            
        Returns:
            tuple: (manual_text: str, active_tools: list[str])
                - manual_text: 最終的 API 手冊文字
                - active_tools: 已啟用的工具列表
        """
        # 1. 準備掃描文本 (轉小寫以模糊比對)
        scan_text = (skill_name + " " + skill_desc).lower()
        
        # 2. 預設載入基礎工具和整數工具
        manual_parts = [PromptBuilder.MANUAL_BASE, PromptBuilder.MANUAL_INTEGER]
        active_tools = ["Base", "IntegerOps"]
        
        # 3. 關鍵字快篩 (Keyword Triggering)
        # 注意：優先級順序很重要 - 多項式應該在分數之前檢查
        
        # [V2.5 新增] 多項式與微分偵測 (最先檢查，以免被分數偵測搶走)
        if any(k in scan_text for k in ['多項式', 'poly', '微', '積分', 'integral', '導', '微分', 'diff', 'deriv', '切線', 'tangent', 'f(x)', 'f\'(x)', 'f\'\'(x)', 'derivative']):
            manual_parts.append(PromptBuilder.MANUAL_POLYNOMIAL)
            active_tools.append("CalculusOps")
            logger.info(f"   ✅ 檢測到多項式/微分相關關鍵字，啟用 CalculusOps (Polynomial)")
        
        # 分數偵測 (避免與英文路徑中的 "/" 混淆，只檢查更精確的中文關鍵字)
        if any(k in scan_text for k in ['分', 'frac', 'ratio', '有理', '除法', 'rational', '分之', '分母', '分子']):
            manual_parts.append(PromptBuilder.MANUAL_FRACTION)
            active_tools.append("FractionOps")
            logger.info(f"   ✅ 檢測到分數相關關鍵字，啟用 FractionOps")
            
        # 根號/幾何偵測
        if any(k in scan_text for k in ['根', 'sqrt', 'root', '幾何', 'geo', '畢氏', 'pythag', '開方', 'radical', '直角三角']):
            manual_parts.append(PromptBuilder.MANUAL_RADICAL)
            active_tools.append("RadicalOps")
            logger.info(f"   ✅ 檢測到根號/幾何相關關鍵字，啟用 RadicalOps")
            
        # 4. 組裝最終手冊字串
        header = f"\n【已啟用的數學軍火庫】(Detected Modes: {', '.join(active_tools)})\n"
        manual_text = header + "\n".join(manual_parts)
        
        return manual_text, active_tools
    
    @staticmethod
    def _build_tool_selection_protocol(active_tools: list) -> str:
        """
        [V2.4 新增] 構建工具選用協定 (Domain Tool Selection Protocol)
        
        强制 LLM 根據題目需求選擇正確的工具，避免亂用或重複實現。
        
        Args:
            active_tools: 已啟用的工具列表
            
        Returns:
            str: 協定文字
        """
        protocol = """
## 🔧 Domain Tool Selection Protocol (工具選用協定)
你必須根據題目需求，從上方【已啟用的數學軍火庫】中選擇正確的工具：
"""
        
        if "FractionOps" in active_tools:
            protocol += """1. **FractionOps**: 當題目涉及除法、比率或需要精確小數運算時。\n"""
            
        if "RadicalOps" in active_tools:
            protocol += """2. **RadicalOps**: 當題目涉及開方、距離公式或無理數時。\n"""
            
        if "CalculusOps" in active_tools:
            protocol += """3. **CalculusOps**: 當題目涉及多項式或變化率時。\n"""
            
        protocol += """4. **IntegerOps**: 僅在純整數運算時使用。

**Constraint**: 在生成的 Python Code 中，嚴禁自己實現上述已有的功能 (如 gcd, simplify)，必須呼叫庫函數。
**Critical Rule**: 永遠不要說「我沒有這個工具」- 所有必要的工具都已經為你準備好了。
"""
        return protocol
    
    @staticmethod
    def build(master_spec: str, ablation_id: int = 3, textbook_example: str = "", topic: str = "", skill_id: str = "") -> str:
        """
        構建 Prompt（[V47.13] 新增 Domain 函數庫自動注入）
        [V2.4 新增] 動態工具選用系統
        
        Args:
            master_spec: MASTER_SPEC 字串
            ablation_id: Ablation 模式 ID (1, 2, 3)
            textbook_example: [Ab1 專用] 教科書範例文字
            topic: [Ab1 專用] 題目主題（從 skill_id 提取）
            skill_id: [V47.13 新增] 用於自動識別所需 Domain 函數庫
            
        Returns:
            str: 完整的 Prompt（已自動注入 Domain 標準函數）
        """
        # [V47.13] 自動識別並注入 Domain 函數庫
        domain_injection = ""
        if skill_id:
            try:
                from core.prompts.domain_function_library import get_required_domains, get_domain_helpers_code
                required_domains = get_required_domains(skill_id)
                if required_domains:
                    domain_code = get_domain_helpers_code(required_domains)
                    domain_injection = f"""

### 🔧 標準函數庫（{', '.join(required_domains)}）

{domain_code}

⚠️ 規則：
1. 直接調用上述函數，禁止重新定義
2. 你只需實現 `def generate(level=1, **kwargs)`
3. 答案格式：純多項式逗號分隔，例 "6x-5, 6"（禁止包含 f'(x)= 或換行）
"""
                    logger.info(f"   ✅ Domain 函數庫注入: {required_domains}")
            except Exception as e:
                logger.warning(f"   ⚠️ Domain 函數庫注入失敗: {e}")
        
        if ablation_id == 1:
            # Ab1: 模擬一般用戶的 Prompt + 範例 + 主題
            # 如果沒有提供範例，使用預設範例
            if not textbook_example:
                textbook_example = "範例：計算 3 + 5 = ?"
            if not topic:
                topic = "數學題目"
            
            prompt = BARE_PROMPT_TEMPLATE.format(
                topic=topic,
                textbook_example=textbook_example
            )
            logger.info(f"Prompt Ab1 - BARE_PROMPT_TEMPLATE (自然語言)")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Final Prompt: {len(prompt)} chars")

        elif ablation_id == 2 or ablation_id == 3:
            # Ab2/Ab3: UNIVERSAL Prompt + MASTER_SPEC + Domain Stubs (Stub Mode)
            # ✅ [V47.14 淨化 MASTER_SPEC] 移除會誤導模型的實作步驟
            clean_spec = PromptBuilder._clean_master_spec(master_spec)
            
            # [V2.5 Refactor] 使用 Domain Stubs 取代冗長的 API Manual
            # 1. 獲取所需的 Domain Code Stubs
            domain_injection = ""
            active_tools = ["Base"]  # Base tools are always active
            tool_selection_protocol = ""
            
            if skill_id:
                try:
                    from core.prompts.domain_function_library import get_required_domains, get_domain_helpers_code
                    required_domains = get_required_domains(skill_id)
                    
                    if required_domains:
                        # 轉換 active_tools 用於 Protocol 生成
                        # required_domains 是 ['fractionops', 'integerops'] 格式
                        if 'fractionops' in required_domains: active_tools.append('FractionOps')
                        if 'integerops' in required_domains: active_tools.append('IntegerOps')
                        if 'radicalops' in required_domains: active_tools.append('RadicalOps')
                        if 'calculusops' in required_domains or 'polynomial' in required_domains: active_tools.append('CalculusOps')
                        if 'geometry' in required_domains: active_tools.append('GeometryOps')
                        if 'vector' in required_domains: active_tools.append('VectorOps')
                        if 'probability' in required_domains: active_tools.append('ProbabilityOps')

                        # 獲取 Stubs 代碼
                        domain_stubs = get_domain_helpers_code(required_domains, stub_mode=True)
                        
                        domain_injection = f"""
### 🔧 標準函數庫（API Stubs）
{domain_stubs}

⚠️ 規則：
1. 直接調用上述函數，禁止重新定義
2. 你只需實現 `def generate(level=1, **kwargs)`
3. 答案格式：純多項式逗號分隔，例 "6x-5, 6"（禁止包含 f'(x)= 或換行）
"""
                        logger.info(f"   ✅ Domain Stubs 注入: {required_domains}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Domain Stubs 注入失敗: {e}")

            # 2. 生成工具選用協定
            tool_selection_protocol = PromptBuilder._build_tool_selection_protocol(active_tools)
            
            # [V2.5 新增] 為 UNIVERSAL_GEN_CODE_PROMPT 注入課本例題
            textbook_example_section = ""
            if textbook_example:
                textbook_example_section = f"【課本範例】\n{textbook_example}\n\n參考該風格生成類似題目。"
            else:
                textbook_example_section = "（無特定參考範例，根據 MASTER_SPEC 自由生成）"
            
            # 3. 注入 Manual Base (基礎工具說明)
            # Universal Prompt 裡面已經有一個 placeholder 嗎？
            # 沒，它在 UNIVERSAL_GEN_CODE_PROMPT 本身被包含
            # 其實 UNIVERSAL_GEN_CODE_PROMPT 的 L165-177 已經寫死了「預載工具 API 手冊」
            # 我們需要避免重複。
            # UNIVERSAL_GEN_CODE_PROMPT 的內容是固定的，包含「基礎工具」和「多項式專用工具」(L172-177)
            # 這些是 Legacy 的寫法。
            # 我們應該依賴我們動態生成的 prompt part。
            
            # 對 UNIVERSAL_GEN_CODE_PROMPT 進行格式化
            universal_prompt_with_example = UNIVERSAL_GEN_CODE_PROMPT.format(
                textbook_example_section=textbook_example_section
            )
            
            # 最終組裝
            # universal_prompt + domain_stubs + tool_selection + master_spec
            prompt = universal_prompt_with_example + domain_injection + tool_selection_protocol + f"\n\n### MASTER_SPEC:\n{clean_spec}"
            
            logger.info(f"Prompt Ab{ablation_id} - Optimized Stub Mode")
            logger.info(f"   Universal Prompt: {len(universal_prompt_with_example)} chars")
            logger.info(f"   Domain Injection: {len(domain_injection)} chars")
            logger.info(f"   MASTER_SPEC: {len(clean_spec)} chars")
        
        return prompt
    
    @staticmethod
    def _extract_and_clean_yaml(text: str) -> str:
        """
        從 AI 回覆中提取並清理 YAML 區塊（強力去殼）
        
        處理 AI 可能包含的 Markdown 代碼塊標記（```yaml ... ```）
        
        Args:
            text: 原始文本（可能包含 Markdown 代碼塊）
        
        Returns:
            str: 清理後的 YAML 內容
        """
        import re
        
        # 1. 嘗試用正則表達式抓取 ```yaml ... ``` 中間的內容
        pattern = r"```(?:yaml)?\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            clean_text = match.group(1).strip()
        else:
            # 2. 如果沒找到 code block，可能整段就是 YAML
            # 但要把頭尾的 ``` 去掉（可能只有頭或只有尾）
            clean_text = text.replace("```yaml", "").replace("```", "").strip()
        
        return clean_text
    
    @staticmethod
    def _clean_master_spec(master_spec: str) -> str:
        """
        [V47.14] MASTER_SPEC 淨化器 - 移除會誤導 14B 模型的實作細節
        
        核心邏輯：
        - 保留「做什麼」(entities, constraints, operators, templates.complexity_requirements)
        - 移除「怎麼做」(construction, implementation_checklist, formatting, variables)
        
        原因：14B 模型看到 construction 後會照抄步驟，反而不使用我們提供的 API 工具。
        
        Args:
            master_spec: 原始 MASTER_SPEC 字串
            
        Returns:
            str: 淨化後的 MASTER_SPEC
        """
        try:
            import yaml
            
            # 🔧 [重要] 強力去殼 - 在解析前清理 Markdown 代碼塊標記
            clean_input = PromptBuilder._extract_and_clean_yaml(master_spec)
			
            # [V47.15 Safety Check] 防止將 API 錯誤訊息當作 Spec 解析
            if "Google AI Error" in clean_input or "PERMISSION_DENIED" in clean_input:
                logger.error(f"   🚨 MASTER_SPEC 包含 API 錯誤訊息，攔截並回退到 Safe Mode")
                return "domain: unknown\nentities: []\noperators: []\n# [System Error] Original Spec was an API Error Message"

            spec_dict = yaml.safe_load(clean_input)
            
            # 移除會誤導模型的「實作指引」
            keys_to_remove = ['construction', 'implementation_checklist', 'formatting', 'variables']
            
            # 保留 templates 裡的 name 和 complexity_requirements，但移除內部的實作細節
            if 'templates' in spec_dict:
                for template in spec_dict['templates']:
                    for key in keys_to_remove:
                        if key in template:
                            del template[key]
                            
            # 重新轉回字串
            clean_spec = yaml.dump(spec_dict, allow_unicode=True, sort_keys=False)
            logger.info(f"   ✅ MASTER_SPEC 淨化完成: 移除 {keys_to_remove}")
            return clean_spec
            
        except Exception as e:
            # 如果解析失敗，回退到原始 MASTER_SPEC
            logger.warning(f"   ⚠️ MASTER_SPEC 淨化失敗: {e}，使用原始版本")
            return master_spec
    
    @staticmethod
    def get_skeleton() -> str:
        """
        獲取代碼框架（用於向後兼容）
        
        Returns:
            str: 空字串（CALCULATION_SKELETON 已棄用）
        """
        return ""


# 導出常量（向後兼容）
__all__ = [
    'PromptBuilder',
    'BARE_MINIMAL_PROMPT',
    'UNIVERSAL_GEN_CODE_PROMPT',
]
