# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/prompt_architect.py
功能說明 (Description): 
    V42.0 Architect (Pure Math Edition)
    專注於分析「純符號計算題」的數學結構，產出 MASTER_SPEC。
    此版本已移除圖形 (Geometry) 與情境 (Scenario) 的干擾，
    指導 Coder 生成精準的數論與運算邏輯。
    
版本資訊 (Version): V42.0
更新日期 (Date): 2026-01-21
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import os
import json
import re
import time
from datetime import datetime
from flask import current_app
from models import db, SkillInfo, SkillGenCodePrompt, TextbookExample
from core.ai_wrapper import get_ai_client

# ==============================================================================
# V42.0 SYSTEM PROMPT (Pure Symbolic Math)
# ==============================================================================
ARCHITECT_SYSTEM_PROMPT = r"""你現在是 K12 數學跨領域「課綱架構師」。
你的任務是分析用戶提供的例題，並以「領域膠囊 (DOMAIN_CAPSULE)」格式產出通用規格，
供工程師實作「統一生成管線」。無論題型是四則運算、方程式、幾何、三角、機率統計或排列組合，
都遵循同一輸出格式。

【核心原則】
- **不鎖題型**：產出格式與轉換邏輯必須「領域無關」，適用於任何數學領域。
- **嚴禁程式碼**：僅輸出「自然語述的結構規格」，NOT Python Code；工程師負責實作。
- **嚴禁 eval**：所有運算必須以「有界、可驗證」的方式敘述，禁止 eval/exec 相關描述。

【產出格式：DOMAIN_CAPSULE】

```
domain: <arithmetic | algebra.linear | algebra.quadratic | geometry.plane | 
         trigonometry | probability | statistics | combinatorics | ...>

entities:
  - 對象名稱: 型別 (型別選項: integer, rational, real, angle, point, vector, 
                                      set, interval, ...)
    constraints: 具體範圍與限制 (例: 非零、互質、正整數、 -180°~180° 等)
    [可選] mutually_exclusive_with: [其他對象名稱]

operators: [可用運算列表]
  - +, -, *, /, sqrt, abs, ^, gcd, lcm, factorial, nCr, nPr, ...
  - 三角: sin, cos, tan, arcsin, ...
  - 幾何: distance, dot, cross, area, ...
  - 其他領域特定運算

constraints:
  - 可計算性: 所有中間值與最終答案都必須「可精確計算」（用 Fraction 或 int）
  - 邊界: 必須明確指定數值範圍與複雜度限制（避免模糊不清）
    * 分數分母範圍: 明確指定 (例: 2~10, 2~20, 1~100 等)
    * 整數範圍: 明確指定 (例: 1~10, -100~100, 1~1000 等)
    * 運算複雜度: 明確指定結果的位數限制 (例: 分子/分母不超過 2 位數)
  - 互斥: 哪些條件不能同時出現
  - 最小複雜度: 必須明確說明題目的最低複雜度要求，防止退化成過簡單的題目

templates: [一個或多個可變模板]
  - name: <清晰的模板名稱>
    
    complexity_requirements: |
      明確說明此模板的複雜度要求，例如：
      - 必須包含的元素數量 (如: 至少 3 個運算數)
      - 必須使用的運算符類型 (如: 必須包含乘法或除法)
      - 必須實現的結構 (如: 必須有括號、必須有負數等)
      
    variables:
      - var_name: 生成規則 (例：從 [範圍 a~b 的整數] 隨機取；需避免 X 值；互質等)
      - ...
    
    construction: |
      <自然語述的計算流程，不寫程式碼>
      第一步：... (數值與來源)
      第二步：... (運算、使用了哪些工具)
      第三步：...
      最終答案：...
      [重要] 不含任何 eval/exec 描述
      
    implementation_checklist: |
      工程師實作時必須確認：
      - [ ] **必須有外層 while True: 迴圈**（def generate 內第一行）
      - [ ] 所有驗證邏輯都在 while True 內（用 continue 或 break 控制重試）
      - [ ] 格式化和 return 都在 while True 外（break 後才執行）
      - [ ] 是否生成了所有必要的變數
      - [ ] 是否實現了所有必要的運算步驟
      - [ ] 是否達到複雜度要求（運算數數量、運算符種類等）
      - [ ] 是否遵守了所有 constraints
    
    formatting:
      question_display: |
        題幹格式化規則（重要！LaTeX 與中文處理）
        
        🔴 **核心原則**：
        - 中文字和文字敘述必須在 LaTeX ($...$) 外面
        - 數學式子必須在 LaTeX ($...$) 裡面
        - 使用 fmt_num() 格式化所有數字（包括係數和變數）
        - 使用 op_latex 字典映射運算符（* → \\times, / → \\div）
        
        **實作模式判斷**：
        
        🟢 **模式 A：使用 Domain 標準函數（推薦）**
        - 當題型涉及多項式、導數、三角函數等，優先使用 Domain 標準函數庫
        - Domain 函數已返回完美 LaTeX（不含 $ 符號）
        - ⚠️ **絕對禁止**對 Domain 函數結果調用 clean_latex_output()
        
        範例（導數題型）：
        1. 使用標準函數格式化：
           poly_latex = _poly_to_latex(terms)  # 返回 "3x^{2} - 5x + 2" (無 $)
           deriv_sym = _deriv_symbol_latex(1)   # 返回 "f'(x)" (無 $)
        
        2. 手動添加 $ 符號組合題目：
           q = f"已知 $f(x) = {poly_latex}$，求 ${deriv_sym}$ 的值。"
           # ✅ 完成！不要再呼叫 clean_latex_output(q)
        
        3. 列舉多個符號時，每個符號獨立包裹 $：
           symbols = ' 與 '.join(f"${_deriv_symbol_latex(n)}$" for n in orders)
           q = f"已知 $f(x) = {poly_latex}$，求 {symbols}。"
           # ✅ 完成！
        
        🟡 **模式 B：簡單運算式（無 Domain 函數）**
        - 當題型是簡單四則運算、不使用標準函數庫時
        - 可以在最後呼叫 clean_latex_output() 一次
        
        範例（簡單運算）：
        1. 構造 LaTeX 式子（不含 $）：
           expr = f"{fmt_num(a)} {op_latex['*']} {fmt_num(b)}"  # "3 \\times 5"
        
        2. 組合題目：
           q = f"計算 {expr} 的值"  # "計算 3 \\times 5 的值"
        
        3. 最後呼叫一次：
           q = clean_latex_output(q)  # "計算 $3 \\times 5$ 的值"
        
        **絕對禁止（會導致佔位符外洩）**：
        - ❌ 對 Domain 函數結果使用 clean_latex_output()
        - ❌ 混合已包裹 $ 和未包裹內容後再 clean_latex_output()
        - ❌ 重複呼叫 clean_latex_output()（會產生多層 $ $）
        - ❌ 先手動添加 $ 符號後又呼叫 clean_latex_output()（會產生 $...$...$）
        - ❌ 將中文包在 $ $ 內（matplotlib 無法渲染中文）
        - ❌ 不用 fmt_num()，直接用 str(a)（無法正確處理負數和分數）
        
      answer_display: |
        答案格式化規則（純數字，不使用 LaTeX）
        - 整數：直接字符串 "42"
        - 分數：Python Fraction 格式 "3/7"
        - 帶分數："整數 分子/分母" 格式 "2 3/7"
        - 禁止使用 LaTeX 格式（如 \\frac{3}{7}）
        - 禁止使用 fmt_num() 作為答案
      
    notes: [可選] 額外說明 (例：為何選這些變數、通常難點在哪)

diversity:
  - 變異點 1: <簡述可變位置與方式>
  - 變異點 2: ...
  - 退化檢查: 如何確保不會產生 trivial 或重複的題目

verifier:
  - 生成後應驗證：<邏輯檢核清單，供工程師實作>
    * 條件 A 是否滿足
    * 計算結果是否有效
    * ...

[可選] cross_domain_tools:
  - 若此題型會用到通用工具（如 clamp_fraction, safe_pow, fmt_interval 等），
    請明確列出工具名稱與用途。
```

【OUTPUT FORMAT RULES (YAML 語法規則)】

🔴 **YAML SYNTAX RULE 【強制規定】**:

Inside YAML, NEVER use the asterisk * for bullet points.

Use hyphens - for lists, or indent with spaces.

❌ Bad Example:
```yaml
constraints:
  * 可計算性: 所有中間值...
  * 邊界: 明確指定數值範圍...
  * range: 1-10
```

✅ Good Example:
```yaml
constraints:
  - 可計算性: 所有中間值...
  - 邊界: 明確指定數值範圍...
  - range: 1-10
```

✅ Alternative (Key-Value Format):
```yaml
constraints:
  computability: 所有中間值...
  boundary: 明確指定數值範圍...
  range: 1-10
```

**重點**：
- YAML lists must use `-` (hyphen) prefixes, NOT `*` (asterisk)
- Asterisk `*` in YAML is reserved for special syntax and will cause parsing errors
- Always use `-` for bullet points in YAML contexts
- If you need to use `*`, escape it or place it inside quotes: `"description with * character"`

【嚴格禁令 (Negative Constraints)】
- ❌ **嚴禁字串算式或 eval/exec/safe_eval 敘述**：任何運算都必須用「Python 直接運算」描述。
  - ❌ 錯誤: "使用 safe_eval 計算結果"
  - ✅ 正確: "使用 Python 運算符直接計算: result = (a + b) * c"
- ❌ **嚴禁直接寫 Python Code**：規格是「自然語述」，工程師自己實作。
- ❌ **嚴禁繪圖、視覺、Matplotlib**：題目可涉及幾何，但別要求繪圖生成。
- ❌ **嚴禁應用題、物理情境、單位轉換等實世界敘事**：純數學題。
- ❌ **嚴禁在 YAML 中使用 * 作為條列符號**：使用 `-` 取代（見上方 YAML SYNTAX RULE）。

【工程師實作結構要求】
在自然語述規格完成後，工程師必須按照以下結構實作 generate() 函數：

```python
def generate(level=1, **kwargs):
    while True:  # ⚠️ CRITICAL: 外層 while True 是必須的！用於整個物件再生
        # === 步驟 1: 變數生成（按照 MASTER_SPEC） ===
        <根據規格生成變數>
        
        # === 步驟 2: 運算與驗證 ===
        <執行必要的運算>
        
        # === 步驟 3: 驗證與重試控制 ===
        if <不符合要求>:
            continue  # 重新生成整個物件
        
        if <符合所有要求>:
            break  # 跳出迴圈，進入格式化
    
    # === 步驟 4: 格式化（必須在 while True 外層！） ===
    q = <格式化題目>
    a = <格式化答案>
    
    # === 步驟 5: 回傳標準格式 ===
    return {'question_text': q, 'correct_answer': a, 'answer': a, 'mode': 1}
```

**結構檢查清單（提交前必確認）**：
✅ 必須有外層 `while True:`（def generate 內第一行）
✅ 所有驗證邏輯都在 while True 內
✅ 格式化和 return 都在 while True 外
✅ 有 continue 語句時，確保在 while True 內
✅ 不可在內層有 while True（只有外層一個）

【輸出範例（僅示意）】
⚠️ **重要**：以下範例必須包含明確的複雜度要求和實現檢查清單

```
domain: arithmetic

entities:
  - n1: rational
    constraints: 
      - value_range: -20~20
      - denominator_range: 2~10
      - 非零
  - n2: rational
    constraints:
      - value_range: -20~20  
      - denominator_range: 2~10
      - 非零
  - n3: rational
    constraints:
      - value_range: -20~20
      - denominator_range: 2~10
      - 非零
  - op1: operator ('+', '-', '*', '/') 
  - op2: operator ('+', '-', '*', '/')

constraints:
  - 可計算性: 所有中間值與最終答案都必須「可精確計算」（用 Fraction 或 int）
  - 邊界:
    - 分數分母範圍: 2~10
    - 整數範圍: -20~20
    - 運算複雜度: 分子/分母不超過 2 位數
  - 互斥: 不可全為整數（必須至少有一個分數）
  - 最小複雜度: 必須至少 3 個運算數，必須至少包含一個乘法或除法

templates:
  - name: chain_of_operations
    
    complexity_requirements: |
      - 必須生成 3 個運算數 (n1, n2, n3)
      - 必須生成 2 個運算符 (op1, op2)
      - 至少一個運算符必須是乘法 (*) 或除法 (/)
      - 必須實現括號結構變化（none/left_group/right_group）
      - 至少一個運算數必須是分數形式
      
    variables:
      - bracket_type: 隨機選 (none | left_group | right_group)
      - 確保 op1 和 op2 中至少有一個是 * 或 /
    
    construction: |
      1. 隨機生成 n1, n2, n3（遵守非零約束和分母範圍 2~10）
      2. 隨機選 op1, op2，確保至少有一個是 * 或 /
      3. 隨機選 bracket_type
      4. 依 bracket_type 使用 Python 運算符直接計算：
         
         ✅ 正確方式（直接用 Python 運算符）：
         ```
         if bracket_type == 'left_group':
             temp = n1 + n2  # 或 n1 - n2, n1 * n2, n1 / n2
             result = temp * n3  # 根據 op2
         elif bracket_type == 'right_group':
             temp = n2 + n3
             result = n1 * temp
         else:
             # 遵循數學優先級
             result = n1 + n2 * n3  # 或其他組合
         ```
         
         ❌ 禁止方式（字符串評估）：
         ```
         ❌ result = eval(f"{n1} {op1} {n2}")
         ❌ result = safe_eval(f"{n1} {op1} {n2}")
         ❌ expr = f"{n1} + {n2}"; result = eval(expr)
         ```
         
         重點：所有運算都必須用 if-elif 判斷運算符，然後用 Python 的 +, -, *, / 直接計算
         
      5. 化簡到最簡分數形式（Fraction 自動處理）
      
    implementation_checklist: |
      工程師實作時必須確認：
      - [ ] 是否生成了 3 個運算數（不可只有 2 個）
      - [ ] 是否生成了 2 個運算符
      - [ ] 是否至少有一個乘法或除法運算符
      - [ ] 是否實現了括號結構邏輯
      - [ ] 是否至少有一個分數（不可全為整數）
    
    formatting:
      question_display: |
        純數學式，無中文敘述：
        1. 使用 fmt_num() 格式化每個運算數
        2. 使用 op_latex 字典映射運算符（+ - * /）
        3. 根據 bracket_type 添加括號
        4. 使用 clean_latex_output() 包裝（自動加 $ $）
        
        ⚠️ **重要：避免重複插入運算符的常見錯誤**
        
        ✅ **正確方式（推薦）**：
        如果你先組裝了包含運算符的列表，**直接使用索引**：
        ```
        # q_parts 結構：[num1, op1, num2, op2, num3]
        #                [0]   [1]  [2]   [3]  [4]
        q_parts = []
        for i in range(num_operators):
            q_parts.append(fmt_num(operands[i]))
            q_parts.append(op_latex[operators[i]])
        q_parts.append(fmt_num(operands[-1]))
        
        # 組裝時直接用索引，不要再從 operators 取
        if bracket_type == 'left_group':
            q = f"({q_parts[0]} {q_parts[1]} {q_parts[2]}) {q_parts[3]} {q_parts[4]}"
        ```
        
        ❌ **錯誤方式（會產生重複運算符）**：
        ```
        # q_parts 已包含運算符，但又從 operators 取，導致重複
        q = f"({q_parts[0]} {op_latex[operators[0]]} {q_parts[1]}) ..."
        #                    ↑ 重複了！           ↑ 這已經是運算符
        # 結果：$num1 \times \times num2$ ❌
        ```
        
        ✅ **替代方式（不預先組裝）**：
        ```
        # 直接在 f-string 中組裝
        if bracket_type == 'left_group':
            q = f"({fmt_num(n1)} {op_latex[op1]} {fmt_num(n2)}) {op_latex[op2]} {fmt_num(n3)}"
        q = clean_latex_output(q)  # 自動變成 $...$
        ```
        
      answer_display: |
        純數字格式（方便文本框比對）：
        - 整數：str(result) → "42"
        - 分數：str(result) → "3/7"（Python Fraction 自動格式化）
        - 帶分數：f"{whole} {num}/{den}" → "2 3/7"
        
        禁止：
        - 使用 LaTeX 格式（如 \\frac{3}{7}）
        - 使用 fmt_num(result)（會產生 LaTeX）
```

【最終輸出要求】
1. 一個清晰、完整的 DOMAIN_CAPSULE
2. 使用上述格式，但勿機械性複製範例
3. 確保「不鎖題型」原則：任何工程師遵循此規格，用「統一生成管線」都能實作
"""

# ==============================================================================
# AUXILIARY FUNCTION DESIGN GUIDELINES
# ==============================================================================
AUXILIARY_FUNCTION_PROMPT = r"""你是 K12 數學教案設計專家。

當設計「輔助函數」章節時，請注意：

1. **系統已預載工具**：
   - `fmt_num(num)`: 格式化數字為 LaTeX（自動處理括號，**不含外層 $**）
   - `to_latex(num)`: 轉換分數為 LaTeX（**不含外層 $**）
   - `clean_latex_output(q_str)`: 清洗題目字串並在最外層**自動加一對 $ 符號**（你不要再自己加）
   - `Fraction(num, den)`: Python 內建分數類別；小數請用 `Fraction(str(decimal_value))` 避免浮點誤差
   - `random.randint()`, `random.choice()`: 隨機數生成
   - `check()`: 驗證答案的數論工具
   - `op_latex`: **全域已定義的運算子映射表** `{'+': '+', '-': '-', '*': '\\times', '/': '\\div'}`
     - ✅ 直接使用: `f"{fmt_num(n1)} {op_latex[op]} {fmt_num(n2)}"`
     - ❌ **嚴禁重新定義**: 不要在 generate() 內部再寫 `op_latex = {...}`

2. **嚴禁事項 [V47 強制規定]**：
   - ❌ **嚴禁 eval/exec/safe_eval/字串算式**：所有數學結果必須用 Python 直接計算（`+`, `-`, `*`, `/`），不要建構字符串表達式再評估
     - ❌ 錯誤: `result = safe_eval(f'{a} + {b}')`
     - ✅ 正確: `result = a + b`
   - ❌ **嚴禁 import 任何模組**：預載工具已包含所有必要依賴（random, Fraction 等）
   - ❌ **嚴禁重新定義系統工具**：不可重新定義或覆蓋 `fmt_num`, `to_latex`, `clean_latex_output`, `check` 等

3. **輔助函數設計原則**：
   - ✅ 可以設計**領域專用**的輔助函數（例如 `_generate_chain_operation()`，用 `_` 前綴表示私有）
   - ❌ 不要重新設計格式化函式（例如 `ToLaTeX`, `FormatNumber`）
   - ❌ 不要重新設計隨機數生成器（例如 `GenerateInteger`）

4. **正確寫法範例**：
   ```
   **輔助函數**:
   - `_build_expression(terms, ops)`: 組合多項式表達式
   - `_validate_result(value)`: 檢查結果是否符合範圍
   
   **使用系統工具**:
   - 格式化數字：直接使用 `fmt_num(value)`
   - 生成隨機整數：直接使用 `random.randint(a, b)`
   - 生成分數：直接使用 `Fraction(num, den)`
   - 小數轉分數：使用 `Fraction(str(0.5))` 而非 `Fraction(0.5)`
   - 清洗題目字串：使用 `q = clean_latex_output(q)` **僅呼叫一次**
   ```

5. **錯誤示範（禁止）**：
   ```
   ❌ `ToLaTeX(value)`: 將數字轉為 LaTeX（這會誘導 AI 自己實作）
   ❌ `GenerateInteger(range)`: 生成隨機整數（應直接用 random.randint）
   ❌ `FormatFraction(num, den)`: 格式化分數（應直接用 to_latex(Fraction(num, den))）
   ❌ `calc_str = "1/2 + 3/4"; result = eval(calc_str)`: 字串評估（禁止！應直接用 Fraction(1,2) + Fraction(3,4)）
   ❌ `q = clean_latex_output(q); q = clean_latex_output(q)`: 重複呼叫（僅需一次）
   ```
"""

# ==============================================================================
# Pure Orchestrator Scaffold for jh_數學2上_FourOperationsOfRadicals
# (Edge AI Orchestrator V4 — DomainFunctionHelper, p0–p6 pattern IDs)
#
# Change log:
#   V1  DomainFunctionHelper with 11 granular p*_* pattern IDs.
#       (First implementation — later overridden by V2.)
#   V2  RadicalLogicEngine with 4 consolidated IDs: SimpleAdd | Multiply |
#       Rationalize | Combo.  ZERO math logic in generated code.
#   V3  Selective context loading on top of V2: P4_COMBO → slim spec (~40%
#       token reduction via brace-depth OCR detector).
#   V4  Full revert to DomainFunctionHelper + p0–p6 IDs (Pure Orchestrator).
#       Removes all V2 naming (SimpleAdd/Multiply/Rationalize/Combo) and all
#       RadicalLogicEngine references.  Selective loading retained and updated
#       to target p6_combo instead of "Combo".
# ==============================================================================

_RADICAL_ORCHESTRATOR_SKILL_ID = "jh_數學2上_FourOperationsOfRadicals"

# ---------------------------------------------------------------------------
# Shared building blocks (referenced by both full and slim spec builders)
# ---------------------------------------------------------------------------

_V4_HEADER = """/no_think
【絕對禁止輸出 thinking 或任何非 code 內容】
【Edge AI Orchestrator V4 — 根式四則運算 Pure Orchestrator】
【引擎：core/domain_functions.py :: DomainFunctionHelper】
"""

_V4_ARCH_NOTE = """
════════════════════════════════════════════
架構說明（Pure Orchestrator Mode）
════════════════════════════════════════════
模型職責：pattern_id（11 選 1）+ difficulty（3 選 1）+ term_count（觀察原題項數）。
所有根式計算、化簡、有理化、步驟 → DomainFunctionHelper 決定性完成。
禁止自行撰寫任何根式數學邏輯。
"""

_V4_DIFFICULTY_GUIDE = """
════════════════════════════════════════════
difficulty 設定指南
════════════════════════════════════════════
  easy  → p0, p1（2 項）, p2a, p3b
  mid   → p1（3 項）, p2b, p3a, p4, p5a
  hard  → p1（4 項）, p2c, p5b, p6_combo
"""

# Prohibitions reference df (DomainFunctionHelper) not engine/RLE
_V4_PROHIBITIONS = """
════════════════════════════════════════════
硬性禁令（違反即觸發 Healer 重試，計 0 分）
════════════════════════════════════════════
1. 嚴禁 import math / sympy / numpy
2. 嚴禁 math.sqrt / ** / float() / pow()
3. 嚴禁解析 LaTeX 字串取數值
4. 嚴禁自行定義任何根式計算函數
5. 嚴禁修改或重寫 df.get_safe_vars_for_pattern 以下的任何 scaffold
6. 嚴禁呼叫 RadicalLogicEngine（已棄用）
7. pattern_id 必須完全符合 Pattern Catalogue 中的值（含下劃線後綴）
8. difficulty 必須是：easy / mid / hard 之一
9. 嚴禁寫 import df 或 from X import df — df 已由系統注入全域範圍，
   它是一個物件實例，不是模組，永遠不需要 import
10. 嚴禁重寫 from core.domain_functions import DomainFunctionHelper —
    系統已在執行前注入，重複宣告會導致 NameError
11. 嚴禁輸出 def generate 或 def check 函式定義 — scaffold 已由系統提供
"""

_V4_PATTERN_TABLE = r"""
════════════════════════════════════════════
Pattern Catalogue（按優先順序匹配）
════════════════════════════════════════════
p5b_conjugate_rad  | √p/(b√q±c)      共軛有理化，分子為根式
p5a_conjugate_int  | 1/(b√q±c)       共軛有理化，分子為整數 1
p2c_mult_binomial  | (a√r+b)(c√s+d)  雙括號多項×多項展開
p2b_mult_distrib   | k√r×(a√s±b√t)  單項×多項，分配律展開
p2f_int_mult_rad   | k₁ × k₂√r      純整數與根式相乘 (允許負數括號)
p2g_rad_mult_frac  | k√r × (a/b)    純根式與分數相乘
p2h_frac_mult_rad  | (a/b) × k√r    純分數與根式相乘
p2a_mult_direct    | k₁√r₁ × k₂√r₂  兩根式直接相乘（無括號）
p4_frac_mult       | (a/b)×(√r/c)    分數×含根式的分數
p3a_div_expr       | (a√r±b√s)÷√d   表達式除單一根式
p3b_div_simple     | a/√b            純分數形式，分母有理化
p6_combo           | 多步驟混合       加減＋有理化等複合題型
p1_add_sub         | k₁√r₁ ± k₂√r₂  純根式加減，化簡後合併同類項
p0_simplify        | √r              單一根式化簡

⚠ p5b 優先於 p5a；p2c 優先於 p2b；p2f 優先於 p2b（整數×根式）；p2a 不是 p2b（無括號！）
⚠ 如遇無法辨識，預設 p1_add_sub，difficulty="mid"
"""

_V4_API_SIGNATURES = """
════════════════════════════════════════════
DomainFunctionHelper API（僅此 3 個必要方法）
════════════════════════════════════════════
df.get_safe_vars_for_pattern(pattern_id, difficulty, term_count=term_count) → dict
df.solve_problem_pattern(pattern_id, vars, difficulty) → (str, List[str])
df.format_question_LaTeX(pattern_id, vars)             → str
"""

# ===========================================================================
# Scaffold preamble / tail — EXPORTED for use by live_show.py
#
# The live_show route PRE-INJECTS these around the model's 2-line output so
# the model never needs to write import statements or function definitions.
#
# Full execution flow:
#   1. RADICAL_V4_SCAFFOLD_PREFIX  (injected BEFORE model output)
#   2. model outputs:  pattern_id = "..."  +  difficulty = "..."
#   3. RADICAL_V4_SCAFFOLD_SUFFIX  (injected AFTER model output)
# ===========================================================================

RADICAL_V4_SCAFFOLD_PREFIX = (
    "from core.domain_functions import DomainFunctionHelper\n"
    "df = DomainFunctionHelper()\n"
    "\n"
    "def generate(level=1, **kwargs):\n"
    "    # [Pre-injected by Architect — model provided decisions below]\n"
)

RADICAL_V4_SCAFFOLD_SUFFIX = (
    "    # [Auto-appended scaffold — deterministic, DO NOT output]\n"
    "    _req_rs = locals().get('required_radical_style')\n"
    "    _retry_rs = bool(locals().get('_radical_style_retry', False))\n"
    "    _base_rs = locals().get('radical_style', 'mixed')\n"
    "    if _req_rs == 'simple_radical':\n"
    "        _gen_style = 'simplified'\n"
    "    else:\n"
    "        _gen_style = _base_rs\n"
    "    vars = df.get_safe_vars_for_pattern(\n"
    "        pattern_id, difficulty, term_count=term_count,\n"
    "        style=_gen_style, style_profile=_req_rs, style_retry_pass=_retry_rs,\n"
    "    )\n"
    "    ans, sol = df.solve_problem_pattern(pattern_id, vars, difficulty)\n"
    "    question_text = df.format_question_LaTeX(pattern_id, vars)\n"
    "\n"
    "    return {\n"
    "        'question_text': question_text,\n"
    "        'answer': '',\n"
    "        'correct_answer': ans,\n"
    "        'solution_steps': sol,\n"
    "        'mode': 1,\n"
    "        '_o1_healed': False\n"
    "    }\n"
    "\n"
    "def check(user_answer, correct_answer):\n"
    "    correct = str(user_answer).strip() == str(correct_answer).strip()\n"
    "    return {'correct': correct, 'result': '正確' if correct else '錯誤'}\n"
)

# ---------------------------------------------------------------------------
# Code section shown inside the spec (model sees what's pre-injected +
# exactly which 2 lines it must output — nothing else)
# ---------------------------------------------------------------------------
_V4_CODE_SCAFFOLD_FULL = (
    "\n════════════════════════════════════════════\n"
    "【系統已注入以下 Scaffold，你的輸出只有 ↓↑ 之間的三行】\n"
    "════════════════════════════════════════════\n"
    "# [Pre-injected by Architect — DO NOT RE-OUTPUT]\n"
    "# from core.domain_functions import DomainFunctionHelper\n"
    "# df = DomainFunctionHelper()   ← df 是物件，非模組，禁止 import df\n"
    "#\n"
    "# def generate(level=1, **kwargs):\n"
    "#\n"
    "# ↓ 你只輸出以下三行（縮排 4 個空格）↓\n"
    "    pattern_id = \"p1_add_sub\"  # ← 從 Pattern Catalogue 選擇\n"
    "    difficulty  = \"mid\"         # ← easy / mid / hard\n"
    "    term_count = 2             # ← 觀察原題，填寫根式的總項數（如 2 或 3）\n"
    "# ↑ 你的輸出到這裡結束 ↑\n"
    "#\n"
    "# [Auto-appended after your output — DO NOT OUTPUT]\n"
    "# vars = df.get_safe_vars_for_pattern(pattern_id, difficulty, term_count=term_count)\n"
    "# ans, sol = df.solve_problem_pattern(pattern_id, vars, difficulty)\n"
    "# question_text = df.format_question_LaTeX(pattern_id, vars)\n"
    "# return { 'question_text': ..., 'correct_answer': ans, ... }\n"
    "#\n"
    "# def check(user_answer, correct_answer): ...\n"
    "\n"
    "════════════════════════════════════════════\n"
    "你的輸出應為（僅此三行，不加任何其他 code）：\n"
    "════════════════════════════════════════════\n"
    "    pattern_id = \"<從上方 Catalogue 選一個 p-ID>\"\n"
    "    difficulty  = \"<easy|mid|hard>\"\n"
    "    term_count = <觀察原題中根式的總項數，填整數>\n"
)

_V4_CODE_SCAFFOLD_P6_COMBO = (
    "\n════════════════════════════════════════════\n"
    "【pattern_id 已鎖定為 p6_combo，你只輸出 difficulty 一行】\n"
    "════════════════════════════════════════════\n"
    "# [Pre-injected — DO NOT RE-OUTPUT]\n"
    "# from core.domain_functions import DomainFunctionHelper\n"
    "# df = DomainFunctionHelper()   ← df 是物件，非模組，禁止 import df\n"
    "# def generate(level=1, **kwargs):\n"
    "#     pattern_id = \"p6_combo\"  # locked\n"
    "#\n"
    "# ↓ 你只輸出以下一行 ↓\n"
    "    difficulty  = \"hard\"  # ← easy / mid / hard\n"
    "# ↑ 你的輸出到這裡結束 ↑\n"
    "\n"
    "════════════════════════════════════════════\n"
    "你的輸出應為（僅此一行）：\n"
    "════════════════════════════════════════════\n"
    "    difficulty  = \"<easy|mid|hard>\"\n"
)

# ===========================================================================
# Full spec — model must identify the pattern itself from OCR
# ===========================================================================

def _build_full_spec(ocr_example: str = "") -> str:
    """
    Full context spec for ambiguous or first-pass OCR input.
    Includes the complete 11-pattern catalogue and difficulty guide.
    Model fills both pattern_id and difficulty.
    """
    parts = [
        _V4_HEADER,
        _V4_ARCH_NOTE,
        _V4_PATTERN_TABLE,
        _V4_DIFFICULTY_GUIDE,
        _V4_CODE_SCAFFOLD_FULL,
        _V4_API_SIGNATURES,
        _V4_PROHIBITIONS,
    ]
    spec = "\n".join(parts)
    if ocr_example:
        spec += (
            "\n════════════════════════════════════════\n"
            "參考 OCR 語義（本次輸入，僅供辨識 pattern_id 用）\n"
            "════════════════════════════════════════\n"
            f"{ocr_example}\n"
        )
    return spec


# ===========================================================================
# p6_combo slim spec — pattern pre-confirmed as "p6_combo"
#
# Strips vs full spec:
#   ✂ Full 11-pattern catalogue  → replaced by 2-line lock confirmation
#   ✂ Difficulty-to-pattern mapping table
#   ✂ vars-structure docs        → not needed (df generates internally)
#
# Retained:
#   ✓ Architecture note (1-liner)
#   ✓ "pattern_id = p6_combo locked" statement
#   ✓ difficulty guide (3 lines)
#   ✓ Code scaffold with p6_combo pre-filled
#   ✓ 3 API signatures
#   ✓ Prohibitions
#   ✓ OCR snippet (if provided)
#
# Token reduction vs full spec: ~40%.
# ===========================================================================

_V4_P6_COMBO_LOCK = """
════════════════════════════════
p6_combo 已確認（OCR 語義鎖定）
════════════════════════════════
pattern_id = "p6_combo"  ← 已鎖定，禁止更改
組合方式：(p2b_mult_distrib | p3b_div_simple | p5a_conjugate_int) + p1_add_sub
vars 由 df.get_safe_vars_for_pattern 完全自動生成，模型無需構造任何變數。
"""

def _build_p6_combo_slim_spec(ocr_example: str = "") -> str:
    """
    Minimal context spec for p6_combo (multi-step combination problems).

    The model already knows pattern_id = "p6_combo", so we strip:
      - 11-pattern recognition table
      - difficulty-to-pattern mapping
      - vars-structure documentation
    and retain only the minimum operational instructions.
    """
    parts = [
        _V4_HEADER,
        "所有計算由 DomainFunctionHelper 完成。模型只需確認 difficulty。\n",
        _V4_P6_COMBO_LOCK,
        _V4_DIFFICULTY_GUIDE,
        _V4_CODE_SCAFFOLD_P6_COMBO,
        _V4_API_SIGNATURES,
        _V4_PROHIBITIONS,
    ]
    spec = "\n".join(parts)
    if ocr_example:
        spec += (
            "\n════════════════════════════════\n"
            "OCR 語義（已確認 p6_combo）\n"
            "════════════════════════════════\n"
            f"{ocr_example}\n"
        )
    return spec


# ===========================================================================
# OCR pattern detector  (text → p-ID string or None)
#
# Decision rules (priority order):
#
#   p6_combo    — expression contains BOTH (fraction-with-radical-denom OR
#                 multiply-bracket) AND a top-level add/subtract of another
#                 radical term; OR an explicit multi-step phrase.
#
#   p5b / p5a   — √.../(...) conjugate forms (distinguished by numerator)
#
#   p2c / p2b   — double-bracket or single-item-×-bracket
#
#   p2a         — bare × between radicals
#
#   p3b / p3a   — fraction or ÷ with radical denominator
#
#   p1_add_sub  — radical add/subtract without fraction or multiplication
#
#   p0_simplify — single isolated radical
#
# The detector is conservative: returns None on ambiguous input so the caller
# falls back to the full spec.
# ===========================================================================

def _has_toplevel_addsub_rad(text: str) -> bool:
    """
    Return True iff a '+' or '-' binary operator appears at brace/paren
    depth-0 AND a radical token (\\sqrt or √) exists anywhere in text.

    Depth-tracking prevents operators inside fraction denominators or
    multiplication brackets from triggering a false Combo classification:
      \\frac{1}{\\sqrt{3}-\\sqrt{2}}     → '-' at depth 1  → False
      2\\sqrt{3}\\times(\\sqrt{12}-1)    → '-' at depth 1  → False
      \\frac{3}{\\sqrt{5}-1} + 2\\sqrt{5} → '+' at depth 0 → True
      2\\sqrt{12} - \\sqrt{27}           → '-' at depth 0  → True
    """
    if r"\sqrt" not in text and "√" not in text:
        return False

    depth = 0
    prev_nonspace = ""
    for ch in text:
        if ch in "{(":
            depth += 1
        elif ch in "})":
            depth = max(0, depth - 1)
        elif ch in "+-" and depth == 0:
            if prev_nonspace in "})" or (prev_nonspace and prev_nonspace[-1].isalnum()):
                return True
        if ch.strip():
            prev_nonspace = ch
    return False


import re as _re

# Compiled pattern for p3b_div_simple: \frac{a}{\sqrt{b}} where the
# denominator is EXACTLY a plain radical with no ± terms.
# Matches e.g. \frac{5}{\sqrt{3}}, \dfrac{2}{\sqrt{7}}.
# Does NOT match \frac{1}{\sqrt{3}-\sqrt{2}} because the denominator brace
# contains more than just \sqrt{digits}.
_RE_P3B_SIMPLE_FRAC = _re.compile(
    r"(?:\\dfrac|\\frac)\{[^{}]*\}\{\\sqrt\{\d+\}\}"
)


def _detect_pattern_from_ocr(ocr_text: str) -> str | None:
    """
    Analyse OCR text and return the most likely pattern_id, or None if
    the signal is insufficient (caller falls back to full spec).

    Returns one of the p-ID strings used by DomainFunctionHelper, or None.
    Priority order mirrors the Pattern Catalogue in SKILL.md.
    """
    if not ocr_text:
        return None

    text = str(ocr_text)

    # ---- signal primitives ------------------------------------------------
    # Fraction whose denominator starts with a radical (broad catch-all)
    has_frac_rad_denom = any(k in text for k in [
        r"\frac{1}{\sqrt", r"\frac{\sqrt",
        r"\dfrac{1}{\sqrt", r"\dfrac{\sqrt",
        r"\frac{", r"\dfrac{",
    ])
    # p3b: fraction with a PURE radical denominator (no ± in denominator)
    has_simple_rad_frac = bool(_RE_P3B_SIMPLE_FRAC.search(text))
    # Radical in numerator → conjugate with radical numerator (p5b)
    has_sqrt_numerator  = r"\frac{\sqrt" in text or r"\dfrac{\sqrt" in text
    # Explicit multiplication with bracket → distributive (p2b/p2c)
    has_times_bracket   = any(k in text for k in [
        r"\times(", r"\times \left(",
        r"×(",      r"× \left(",
    ])
    # Bare multiplication (no bracket) → p2a
    has_times_bare = any(k in text for k in [
        r"\times\sqrt", r"\times \sqrt",
        r"×\sqrt",      r"× \sqrt",
        r"\times",      r"×",
    ])
    # Division by radical → p3a / p3b
    has_div_rad = any(k in text for k in [
        r"\div\sqrt", r"÷\sqrt", r"/\sqrt",
    ])
    # Double-bracket → p2c
    has_double_bracket = any(k in text for k in [
        r")(\sqrt", r")×(", r") \times (",
    ])
    # Depth-0 add/subtract of a radical term (binary operator check)
    has_toplevel_rad = _has_toplevel_addsub_rad(text)
    # Any radical add/subtract (includes depth > 0; for SimpleAdd fallback)
    has_any_rad_addsub = (
        (r"\sqrt" in text or "√" in text)
        and any(k in text for k in ["+", "-", r"\pm"])
    )
    # Explicit multi-step phrases
    has_multi_step = any(k in text for k in [
        "多步", "先計算", "再加", "再減", "combined", "multi-step",
    ])

    # ---- p6_combo: two distinct top-level operations ----------------------
    combo_a = has_frac_rad_denom and has_toplevel_rad and not has_simple_rad_frac
    combo_b = has_times_bracket  and has_toplevel_rad
    combo_c = has_multi_step
    if combo_a or combo_b or combo_c:
        return "p6_combo"

    # ---- p5b: conjugate with radical numerator ----------------------------
    if has_sqrt_numerator:
        return "p5b_conjugate_rad"

    # ---- p3b: simple a/√b fraction (no ± in denominator) -----------------
    # Must be checked BEFORE the generic conjugate (p5a) check because p3b is
    # a specialisation of "frac with radical denominator".
    if has_simple_rad_frac:
        return "p3b_div_simple"

    # ---- p5a: conjugate with integer numerator (denominator has ±) --------
    if has_frac_rad_denom:
        return "p5a_conjugate_int"

    # ---- multiplication patterns (p2c, p2b, p2a) -------------------------
    if has_double_bracket:
        return "p2c_mult_binomial"
    if has_times_bracket:
        return "p2b_mult_distrib"
    if has_times_bare:
        return "p2a_mult_direct"

    # ---- division by a radical without fraction notation (p3a) -----------
    if has_div_rad and has_any_rad_addsub:
        return "p3a_div_expr"
    if has_div_rad:
        return "p3b_div_simple"

    # ---- addition / subtraction fallback (p1_add_sub) --------------------
    if has_any_rad_addsub:
        return "p1_add_sub"

    return None   # insufficient signal → caller uses full spec


# ===========================================================================
# Public entry point for the scaffold builder
# ===========================================================================

#: Patterns that have a dedicated slim spec to reduce context window usage.
_SPEC_BUILDERS = {
    "p6_combo": _build_p6_combo_slim_spec,
    # Extend here when slim specs for other patterns are ready.
}


def _get_radical_orchestrator_spec(skill_id: str, ocr_example: str = "") -> str:
    """
    Selective context loader for jh_數學2上_FourOperationsOfRadicals (V4).

    Algorithm:
      1. Run OCR-semantic pattern detector on ocr_example.
      2. If a high-confidence pattern is identified AND a slim spec exists for
         that pattern, inject the trimmed spec (lower token cost for 8B model).
      3. Otherwise fall back to the full spec (all 11 patterns + difficulty map).
    """
    detected = _detect_pattern_from_ocr(ocr_example)
    builder  = _SPEC_BUILDERS.get(detected)
    if builder is not None:
        return builder(ocr_example)
    return _build_full_spec(ocr_example)


# Backward-compat alias used by generate_v15_spec and external callers.
RADICAL_ORCHESTRATOR_MASTER_SPEC = _build_full_spec()


# ==============================================================================
# Core Generation Logic
# ==============================================================================

def generate_v15_spec(skill_id, model_tag="local_14b", architect_model=None):
    """
    [V42.0 Spec Generator]
    讀取例題 -> 呼叫 AI 架構師 -> 存入資料庫 (MASTER_SPEC)

    [Pure Orchestrator Override — V4]
    For jh_數學2上_FourOperationsOfRadicals, bypasses the LLM architect and
    injects a pre-written Pure Orchestrator spec (DomainFunctionHelper API)
    directly.  The spec instructs Qwen-VL-8B to select one of 11 granular
    pattern IDs (p0_simplify … p6_combo) and a difficulty level, delegating
    ALL radical computation to DomainFunctionHelper.  When OCR semantics
    strongly indicate p6_combo (multi-step), a slim context spec is injected
    instead to minimise context-window usage on the 8B model.
    """
    try:
        # ----------------------------------------------------------------
        # [Neuro-Symbolic Override] jh_數學2上_FourOperationsOfRadicals
        #
        # This branch generates a LIGHTWEIGHT prompt that:
        #   ✅ ASKS FOR:  pattern_id (11 choices) + difficulty (3 choices)
        #   ❌ EXCLUDES:  isomorphic constraints, bracket counting,
        #                 operator-sequence matching, number-count checks,
        #                 decimal-style guards, and all integer/fraction
        #                 V42.0 spec sections — none are relevant to radicals.
        #
        # All other skills fall through to the standard V42.0 LLM-architect
        # flow below.  This branch is isolated: changes here cannot leak
        # integer/fraction constraints into the radical prompt, and vice versa.
        # ----------------------------------------------------------------
        if skill_id == _RADICAL_ORCHESTRATOR_SKILL_ID:
            ocr_example = ""
            try:
                example = TextbookExample.query.filter_by(skill_id=skill_id).limit(1).first()
                if example:
                    ocr_example = f"Question: {example.problem_text.strip()}"
            except Exception:
                pass

            spec_content = _get_radical_orchestrator_spec(skill_id, ocr_example)

            # Safety guard: ensure no integer/fraction complexity-mirror keywords
            # leaked into the spec (would confuse the model about bracket counting).
            _forbidden_in_radical_spec = (
                "isomorphic", "bracket_count", "abs_count",
                "operator_sequence", "number_count",
            )
            for _kw in _forbidden_in_radical_spec:
                if _kw in spec_content:
                    import warnings
                    warnings.warn(
                        f"[prompt_architect] Radical spec contains forbidden "
                        f"integer-guard keyword {_kw!r} — please audit "
                        f"_get_radical_orchestrator_spec().",
                        stacklevel=2,
                    )

            new_prompt_entry = SkillGenCodePrompt(
                skill_id=skill_id,
                prompt_content=spec_content,
                prompt_type="MASTER_SPEC",
                system_prompt="[Neuro-Symbolic Orchestrator V2 — RadicalLogicEngine, no LLM math]",
                user_prompt_template=f"skill_id={skill_id}",
                model_tag="orchestrator_v2",
                created_at=datetime.now()
            )
            db.session.add(new_prompt_entry)
            db.session.commit()
            return {
                'success': True,
                'spec': spec_content,
                'prompt_id': new_prompt_entry.id,
                'orchestrator_mode': True,
                'engine': 'RadicalLogicEngine',
            }

        # ----------------------------------------------------------------
        # Standard flow for all other skills
        # ----------------------------------------------------------------

        # 1. 抓取 1 個範例 (避免過多 Context 干擾)
        skill = SkillInfo.query.filter_by(skill_id=skill_id).first()
        example = TextbookExample.query.filter_by(skill_id=skill_id).limit(1).first()
        
        if not example:
            return {'success': False, 'message': "No example found for this skill."}

        # 簡單清理例題文字，移除不必要的 HTML 或雜訊
        problem_clean = example.problem_text.strip()
        solution_clean = example.detailed_solution.strip()
        example_text = f"Question: {problem_clean}\nSolution: {solution_clean}"

        # 2. 構建 User Prompt
        user_prompt = f"""
當前技能 ID: {skill_id}
技能名稱: {skill.skill_ch_name}

參考例題：
{example_text}

任務：
請根據上述例題，撰寫一份 MASTER_SPEC，指導工程師生成同類型的「純計算題」。
重點：確保數值隨機但邏輯嚴謹（如整除、正負號處理）。
"""
        
        full_prompt = ARCHITECT_SYSTEM_PROMPT + "\n\n" + user_prompt

        # 3. 呼叫架構師 
        # (這裡建議使用邏輯能力較強的模型，如 Gemini Pro 或 Flash)
        client = get_ai_client(role='architect') 
        response = client.generate_content(full_prompt)
        spec_content = response.text

        # 4. 存檔 (永遠覆蓋 MASTER_SPEC，確保 Coder 讀到最新指令)
        new_prompt_entry = SkillGenCodePrompt(
            skill_id=skill_id,
            prompt_content=spec_content,
            prompt_type="MASTER_SPEC",
            system_prompt=ARCHITECT_SYSTEM_PROMPT, 
            user_prompt_template=user_prompt,
            model_tag=model_tag,
            created_at=datetime.now()
        )
        db.session.add(new_prompt_entry)
        db.session.commit()

        # [旺宏科學獎] 回傳 prompt_id 供實驗記錄使用
        return {'success': True, 'spec': spec_content, 'prompt_id': new_prompt_entry.id}

    except Exception as e:
        print(f"❌ Architect Error: {str(e)}")
        # 回傳錯誤訊息但不中斷程式，讓上層處理
        return {'success': False, 'message': str(e)}

def infer_model_tag(model_name):
    """
    [Legacy Support] 根據模型名稱自動判斷分級。
    """
    name = model_name.lower()
    if any(x in name for x in ['gemini', 'gpt', 'claude']): return 'cloud_pro'
    if '70b' in name or '32b' in name or '14b' in name: return 'local_14b'
    if 'phi' in name or '7b' in name or '8b' in name: return 'edge_7b'
    return 'local_14b'

# Alias for backward compatibility
generate_v9_spec = generate_v15_spec