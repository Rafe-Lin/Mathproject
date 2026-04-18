import os
import re
import sys
import importlib
import json
import ast  # 新增：用於語法檢查
from flask import current_app
from core.ai_analyzer import get_model
from models import db, SkillInfo, TextbookExample

TEMPLATE_PATH = 'skills/Example_Program.py'

def fix_code_syntax(code_str, error_msg=""):
    """
    [新增功能] 自動修復常見的 AI 生成語法錯誤
    """
    fixed_code = code_str

    # 1. 修復 f-string 中的 LaTeX 單獨大括號 (f-string: single '}}' is not allowed)
    latex_patterns = [r'sqrt', r'frac', r'text', r'angle', r'overline', r'degree', r'mathbf', r'mathrm']
    
    for pat in latex_patterns:
        fixed_code = re.sub(rf'\\{pat}\{{', rf'\\{pat}{{{{', fixed_code)

    # 簡單暴力修法：針對特定錯誤直接全域替換常見 LaTeX 結構
    if "single '}'" in error_msg or "single '{'" in error_msg:
        fixed_code = re.sub(r'\\frac\{', r'\\frac{{', fixed_code)
        fixed_code = re.sub(r'\}\{', r'}}{{', fixed_code)
        fixed_code = re.sub(r'(\d|\w)\}(?=\"|\')', r'\1}}', fixed_code)

    # 2. 修復缺漏的括號
    if "expected '('" in error_msg:
        fixed_code = re.sub(r'print\s+"(.*)"', r'print("\1")', fixed_code)
        fixed_code = re.sub(r'print\s+(.*)', r'print(\1)', fixed_code)

    return fixed_code

def validate_python_code(code_str):
    """
    [新增功能] 驗證 Python 程式碼語法是否正確
    """
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, f"{e.msg} (Line {e.lineno})"

def auto_generate_skill_code(skill_id, queue=None):
    """
    自動為指定的 skill_id 生成 Python 出題程式碼。
    [強化版] 包含語法預檢查與自動修復機制，並強制限制僅使用標準函式庫。
    """
    message = f"正在為技能 '{skill_id}' 自動生成程式碼..."
    current_app.logger.info(message)
    if queue: queue.put(f"INFO: {message}")

    # 1. 讀取範本
    template_path = os.path.join(current_app.root_path, TEMPLATE_PATH)
    template_code = ""
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_code = f.read()

    # 2. 讀取例題
    examples = TextbookExample.query.filter_by(skill_id=skill_id).all()
    examples_text = "\n".join([
        f"--- 例題 ---\n題目: {ex.problem_text}\n答案: {ex.correct_answer}\n詳解: {ex.detailed_solution}\n" 
        for ex in examples
    ])

    skill = SkillInfo.query.get(skill_id)
    topic_description = skill.description if skill else skill_id
    input_type = skill.input_type if skill else "text"

    # 3. 構建 Prompt
    prompt = """
    You are a Python expert specializing in educational software for math learning.
    Your task is to write a Python script for a specific math skill.

    Target Skill ID: {skill_id}
    Topic Description: {topic_description}
    Input Type: {input_type} (If 'graph', use matplotlib to generate an image)

    --- REFERENCE EXAMPLES (How this skill is taught) ---
    {examples_text}

    --- CODE TEMPLATE (You MUST follow this structure) ---
    {template_code}

    --- REQUIREMENTS ---
    1. **Functionality**:
       - Implement `generate()`: Return a dict with `question_text`, `answer`, `correct_answer`.
       - Implement `check(user_answer, correct_answer)`: Return dict with `correct` (bool) and `result` (feedback string).
       - The code must be robust, handling random number generation to create unique problems each time.

    2. **Input Types**:
       - If Input Type is 'text': The question is text-only.
       - If Input Type is 'graph': The `generate` function MUST create a matplotlib figure, save it to `static/generated_plots/{skill_id}_<uuid>.png`, and include `<img src="...">` in `question_text`.

    3. **Output Format**:
       - Return ONLY the raw Python code.
       - Do NOT wrap in markdown code blocks (```python ... ```).
       - Do NOT include explanations outside the code.


    【CRITICAL PYTHON SYNTAX RULES (Strict Enforcement)】
    1. **Function Signature - MANDATORY**: 
       - The main entry function MUST be defined EXACTLY as: 
         `def generate(level=1):`
       - ❌ WRONG: `def generate():` (Will cause TypeError when called with level parameter)
       - ✅ CORRECT: `def generate(level=1):`

    2. **f-string Escaping - MANDATORY DOUBLE BRACES**: 
       - When using f-strings (f"..."), you MUST use **DOUBLE CURLY BRACES** `{{{{}}}}` for any LaTeX syntax or literal braces.
       - ❌ WRONG: f"Ans: $x^{{2}}$" (Causes SyntaxError)
       - ✅ CORRECT: f"Ans: $x^{{{{2}}}}$" (Renders as $x^{{2}}$)

    3. **Raw Strings for LaTeX**:
       - For LaTeX commands, ALWAYS use raw strings (r"...") to avoid escape issues.
       - ✅ CORRECT: r"\angle A", r"\frac{{{{1}}}}{{{{2}}}}"

    4. **Clean Output**: 
       - Output ONLY valid Python code starting with `import ...`. 
       - Do NOT wrap in markdown fences (```python), no explanatory text.

    5. **LaTeX in f-strings - DETAILED EXAMPLES**: 
       - **CRITICAL**: When using f-strings (f"..."), you MUST use **DOUBLE CURLY BRACES** `{{{{}}}}` for ANY LaTeX syntax intended to be printed literally.
       - **This is NOT optional** - Single braces in f-strings will cause: `SyntaxError: f-string: single '}}}}' is not allowed`
       - ❌ WRONG: f"Area is $x^{{2}}$"  (Python raises SyntaxError: f-string: single '}}}}')
       - ✅ CORRECT: f"Area is $x^{{{{2}}}}$"  (Double braces for exponent)
       - ❌ WRONG: f"Solve $\frac{{a}}{{b}}$"  (Still wrong - needs 4 braces total)
       - ✅ CORRECT: f"Solve $\frac{{{{{{{{a}}}}}}}}{{{{{{{{b}}}}}}}}$"  (6 braces for fraction with variables)
       - **Common patterns**:
         * Exponents: f"$x^{{{{2}}}}$" NOT f"$x^{{2}}$"
         * Subscripts: f"$a_{{{{1}}}}$" NOT f"$a_{{1}}$"
         * Fractions: f"$\frac{{{{1}}}}{{{{2}}}}$" NOT f"$\frac{{1}}{{2}}$"
       - ✅ ALTERNATIVE: Use regular strings when no variables needed: "Area is $x^{{{{2}}}}$" (If not using f-string)


    6. **Escape Sequences**:
       - For LaTeX backslashes (e.g., \frac, \circ, \triangle), you MUST use **Python Raw Strings (r"...")** OR **Double Backslashes (\\)**.
       - ❌ WRONG: "\frac{{1}}{{2}}", "\circ" (Python raises SyntaxWarning/Error)
       - ✅ CORRECT: r"\frac{{{{1}}}}{{{{2}}}}", r"\circ"
       - ✅ CORRECT: "\\frac{{{{1}}}}{{{{2}}}}", "\\circ"

    7. **No Full-width Characters**:
       - Do NOT use full-width symbols (？, ：, ，, ＋) in variable names, logic flow, or math calculations. They are ONLY allowed inside display strings (question_text).
       - ❌ WRONG: if x ？ 0: (Python raises SyntaxError: invalid character)
       - ✅ CORRECT: if x > 0:

    [SYNTAX GUARDRAILS]
    8. Template Markers:
       - NEVER include template markers like ${{{{ or }}}} inside the final Python code.
       - WRONG: "score": ${{{{"unit": "分"}}}}
       - CORRECT: "score": {{{{"unit": "分"}}}}

    8. CRITICAL LATEX COMMAND ESCAPING:
       - All LaTeX commands (e.g., \\angle, \\begin, \\frac, \\overline, \\circ) MUST be written with a double backslash (\\\\) inside Python strings and f-strings.
       - The final generated code MUST contain: "\\\\angle", "\\\\begin", "\\\\overline", "\\\\frac", and "\\\\circ".
       - WRONG (Causes Math Input Error): $\\angle ABC$ 或 $\\overline{{{{AB}}}}$
       - CORRECT (Required): $\\\\angle ABC$ 或 $\\\\overline{{{{AB}}}}$

    9. F-STRING & LATEX INTERACTION (THE "NO DOUBLE $" RULE):
       - When writing Python f-strings involving math, enclose the **entire mathematical expression** in `$` delimiters.
       - **CRITICAL**: DO NOT put `$` signs directly inside the curly braces `{{{{}}}}` or immediately next to them if the variable is already within a `$...$` block.
       - **CORRECT (Grouped)**: f"${{{{a}}}}：{{{{b}}}} = {{{{c}}}}：x$"   (Result: $3：4 = 9：x$ -> Valid)
       - **WRONG (Isolated)**:   f"${{{{a}}}}：${{{{b}}}} = ${{{{c}}}}：x$"  (Result: $3：$4 = $9：x$ -> Syntax Error)
       - **WRONG (Redundant)**:  f"${{{{a}}}}$" when intended to be part of a larger equation.
       
    10. NO NEWLINES INSIDE LATEX (The "Red \\n" Rule):
       - **NEVER** put a newline character `\\n` inside the LaTeX delimiters `$...$`.
       - If you need a line break, use `<br>` and place it **OUTSIDE** the math block.
       - **WRONG**: f"Solve: $\\n x^2 = 1$"  (Causes rendering error)
       - **CORRECT**: f"Solve:<br>$x^2 = 1$"

    11. RANDOM RANGE SAFETY (CRITICAL for Stability):
       - Check `start <= stop` before calling `random.randint(start, stop)`.
       - Avoid `ValueError: empty range for randrange()`.

    12. NO EXTERNAL LIBRARIES (Standard Library Only):
       - **DO NOT** import `sympy`, `numpy`, `pandas`, or `scipy`.
       - Use ONLY Python standard libraries: `random`, `math`, `fractions`, `re`, `collections`.
       - If you need polynomial expansion or simplification, implement simple string formatting logic manually (e.g., for `(ax+b)(cx+d)`, calculate coefficients `ac`, `ad+bc`, `bd` yourself).

    Now, generate the Python code for '{skill_id}'.
    """.format(
        skill_id=skill_id,
        topic_description=topic_description,
        input_type=input_type,
        examples_text=examples_text,
        template_code=template_code
    )

    # 4. 呼叫 AI 模型
    try:
        model = get_model()
        response = model.generate_content(prompt)
        generated_code = response.text

        # 5. 清理 Markdown
        if generated_code.startswith("```python"): generated_code = generated_code.replace("```python", "", 1)
        if generated_code.startswith("```"): generated_code = generated_code.replace("```", "", 1)
        if generated_code.endswith("```"): generated_code = generated_code.rsplit("```", 1)[0]
        generated_code = generated_code.strip()

        # 6. Regex LaTeX 修復
        latex_commands = ['angle', 'frac', 'sqrt', 'pi', 'times', 'div', 'pm', 'circ', 'triangle', 'overline', 'degree']
        for cmd in latex_commands:
            generated_code = re.sub(rf'(?<!\\)\\{cmd}', rf'\\\\{cmd}', generated_code)

        # 7. 語法驗證與修復
        is_valid, syntax_error = validate_python_code(generated_code)
        if not is_valid:
            if current_app: current_app.logger.warning(f"語法錯誤: {syntax_error}，嘗試修復...")
            generated_code = fix_code_syntax(generated_code, syntax_error)
            
            is_valid_2, syntax_error_2 = validate_python_code(generated_code)
            if not is_valid_2:
                msg = f"自動修復失敗: {syntax_error_2}"
                if current_app: current_app.logger.error(msg)
                return False, msg

        # 8. 寫入檔案
        output_dir = os.path.join(current_app.root_path, 'skills')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{skill_id}.py')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)

        # 9. Reload Module
        if skill:
            skill.input_type = input_type
            db.session.commit()

        try:
            module_name = f"skills.{skill_id}"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
            return True, "Success"

        except Exception as e:
            return False, f"Runtime Error: {str(e)}"

    except Exception as e:
        return False, f"AI Error: {str(e)}"