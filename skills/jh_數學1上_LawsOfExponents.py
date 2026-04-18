# ==============================================================================
# ID: jh_數學1上_LawsOfExponents
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 55.69s | RAG: 5 examples
# Created At: 2026-01-14 19:39:32
# Fix Status: [Repaired]
# Fixes: Regex=7, Logic=0
#==============================================================================


import random
import math
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from fractions import Fraction
from functools import reduce
import ast

# [V10.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. Formatting Helpers (V10.6 No-F-String LaTeX) ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX using .replace() to avoid f-string conflicts.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX (Safe Mode).
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
        
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# Alias
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def is_prime(n):
    """Check primality (Standard Boolean Return)."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True
def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

# --- 3. Fraction Generator ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)
    
def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result

# --- 4. Answer Checker (V10.6 Hardcoded Golden Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    # [V11.0] 暴力清理 LaTeX 冗餘符號 ($, \) 與空格
    u = str(user_answer).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "")
    
    # 強制還原字典格式 (針對商餘題)
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try: import ast; c_raw = ast.literal_eval(c_raw)
        except: pass

    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q, r = str(c_raw.get("quotient", "")), str(c_raw.get("remainder", ""))
        ans_display = r"{q},{r}".replace("{q}", q).replace("{r}", r)
        try:
            u_parts = u.replace("商", "").replace("餘", ",").split(",")
            if int(u_parts[0]) == int(q) and int(u_parts[1]) == int(r):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(c_raw).strip()

    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        import math
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}



from datetime import datetime
import base64
import io

# Placeholder for potential visualization, though not strictly needed for LawsOfExponents
# If a visualization library like matplotlib were allowed and needed, it would be imported here.
# For this skill, image_base64 will likely be empty or a simple placeholder.

# --- Helper Functions (通用輔助函式) ---

def _format_latex_safe(template_str, **kwargs):
    """
    Formats a string, replacing placeholders like {placeholder} with values.
    Ensures that LaTeX commands within the template_str are not broken by f-strings.
    This function is CRITICAL for Regex=0 compliance.
    """
    formatted_str = template_str
    for key, value in kwargs.items():
        placeholder = "{" + str(key) + "}"
        formatted_str = formatted_str.replace(placeholder, str(value))
    return formatted_str

def _render_exponent_str(base_str, exponent):
    """
    [V11.1 Fix] 增加底數偵測，防止 Double Exponent 錯誤。
    Renders a base string and an integer exponent into a LaTeX-safe string.
    """
    # 如果底數本身已經包含次方符號 '^' 或 '{'，則必須用括號包起來
    safe_base = base_str
    if "^" in str(base_str) or "{" in str(base_str):
        safe_base = r"({b})".replace("{b}", str(base_str))

    if exponent == 1:
        return str(base_str) # 指數為 1 不需要括號
    if exponent == 0:
        # For base^0, display as base^0 explicitly
        return _format_latex_safe(r"{base_str}^{0}", base_str=safe_base)
    if exponent < 0:
        # Use {{-exp}} for negative exponents to ensure correct LaTeX rendering
        return _format_latex_safe(r"{base_str}^{{-{exp_val}}}", base_str=safe_base, exp_val=abs(exponent))
    else:
        return _format_latex_safe(r"{base_str}^{{{exp_val}}}", base_str=safe_base, exp_val=exponent)

def _simplify_variable_exponent(var_exponents):
    """
    Simplifies a dictionary of variable exponents into a LaTeX string.
    e.g., {'x': 2, 'y': -1, 'z': 0} -> "x^{2}y^{-1}"
    Note: This helper is provided but not directly used in the current `simplify_with_variables`
    section, as that section specifically handles "positive exponents only" display.
    It's kept for potential general-purpose use.
    Returns: str
    """
    parts = []
    for var, exp in sorted(var_exponents.items()):
        if exp == 0:
            continue # x^0 = 1, usually not displayed unless it's the only term or specifically asked
        parts.append(_render_exponent_str(var, exp))
    return "".join(parts) if parts else "1" # If all exponents are 0, result is 1

# --- Main Functions (主要函式) ---

def generate(level=1):
    """
    Generates a K12 Laws of Exponents problem.
    """
    problem_type = random.choice([
        "direct_calculation",
        "solve_for_unknown_exponent",
        "simplify_with_variables"
    ])

    question_text = ""
    correct_answer = ""
    answer_display = "" # This will be the user-facing answer format
    image_base64 = ""

    if problem_type == "direct_calculation":
        # Type 1: 直接計算 (Direct Calculation)
        # Involves multiple exponent rules: product, quotient, power of a power, zero, negative.
        base = random.randint(2, 5)
        
        # Ensure exponents don't lead to excessively large numbers for K12
        exp1 = random.randint(2, 4)
        exp2 = random.randint(-2, 3)
        exp3 = random.randint(0, 2)

        # Example forms:
        # (base^exp1 * base^exp2) / base^exp3
        # (base^exp1)^exp2 * base^exp3
        # base^exp1 / (base^exp2)^exp3
        
        choice = random.randint(1, 3)
        if choice == 1: # (a^m * a^n) / a^p => a^(m+n-p)
            question_str = _format_latex_safe(
                r"計算：$ {base_val}^{{{exp1_val}}} \times {base_val}^{{{exp2_val}}} \div {base_val}^{{{exp3_val}}} $",
                base_val=base, exp1_val=exp1, exp2_val=exp2, exp3_val=exp3
            )
            result = base**(exp1 + exp2 - exp3)
            correct_answer = str(result)
            answer_display = str(result)
        elif choice == 2: # (a^m)^n * a^p => a^(m*n+p)
            question_str = _format_latex_safe(
                r"計算：$ ({base_val}^{{{exp1_val}}})^{{{exp2_val}}} \times {base_val}^{{{exp3_val}}} $",
                base_val=base, exp1_val=exp1, exp2_val=exp2, exp3_val=exp3
            )
            result = base**(exp1 * exp2 + exp3)
            correct_answer = str(result)
            answer_display = str(result)
        else: # (a^m / a^n)^p => a^((m-n)*p)
            # Ensure m >= n for positive base and integer result in intermediate step, or handle fractions
            exp1 = random.randint(3, 6) # Make exp1 generally larger
            exp2 = random.randint(1, 2)
            # Ensure exp1 - exp2 is not too small or negative
            while exp1 <= exp2:
                exp1 = random.randint(3, 6)
            exp3 = random.randint(1, 2)
            question_str = _format_latex_safe(
                r"計算：$ ({base_val}^{{{exp1_val}}} \div {base_val}^{{{exp2_val}}})^{{{exp3_val}}} $",
                base_val=base, exp1_val=exp1, exp2_val=exp2, exp3_val=exp3
            )
            result = base**((exp1 - exp2) * exp3)
            correct_answer = str(result)
            answer_display = str(result)

        question_text = question_str + r" 請寫出最終的數值答案。"

    elif problem_type == "solve_for_unknown_exponent":
        # Type 2: 逆向求解 (Solving for an Unknown Exponent)
        base = random.choice([2, 3, 5])
        
        # Equation form: base^(Ax+B) = base^C
        # Ax+B = C => Ax = C-B => x = (C-B)/A
        A = random.choice([1, 2, 3]) # Coefficient of x
        B = random.randint(-3, 3) # Constant term
        C = random.randint(2, 4) # Target exponent (Reduced range for pedagogical optimization)
        
        # Ensure x is an integer for K12 by adjusting C
        # Adjust C to make (C - B) divisible by A
        if (C - B) % A != 0:
            C = A * random.randint(1, 4) + B 
            # Re-check C. Ensure C-B is not excessively small or negative for reasonable x.
            while C < B and A > 0: # Avoid negative target exponent if B is large positive, for simpler K12 problems
                 C = A * random.randint(1, 4) + B
            
        target_value = base**C
        
        # Construct exponent expression A*x + B using string concatenation for LaTeX safety (Regex=0)
        exponent_expr_parts = []
        if A != 1:
            exponent_expr_parts.append(str(A) + "x")
        else:
            exponent_expr_parts.append("x")
            
        if B != 0:
            if B > 0:
                exponent_expr_parts.append("+" + str(B))
            else: # B is negative
                exponent_expr_parts.append(str(B)) # str(B) already includes '-'
        
        exponent_expr = "".join(exponent_expr_parts)
        
        question_text = _format_latex_safe(
            r"若 $ {base_val}^{{{exponent_expr_val}}} = {target_val} $，求 $ x $ 的值。",
            base_val=base, exponent_expr_val=exponent_expr, target_val=target_value
        )
        
        x_val = (C - B) // A
        correct_answer = str(x_val)
        answer_display = str(x_val)

    else: # simplify_with_variables
        # Type 3: 情境應用 (Simplification with Variables)
        # Applying exponent rules to expressions with variables.
        # Example: Simplify $(x^a y^b)^c / (x^d y^e)$
        
        variables = random.sample(['x', 'y', 'z'], random.randint(2, 3))
        
        term1_exponents = {v: random.randint(-2, 3) for v in variables}
        term2_exponents = {v: random.randint(-2, 3) for v in variables}
        power_c = random.randint(1, 2) # Power for the first term

        # Construct the expression
        expr_parts = []
        
        # Part 1: (x^a y^b)^c
        inner_expr_parts = []
        for var in variables:
            # Only include variables with non-zero exponents in the inner part for cleaner display
            if term1_exponents[var] != 0:
                inner_expr_parts.append(_render_exponent_str(var, term1_exponents[var]))
        
        # Handle cases where inner_expr_parts might be empty (all exponents are 0 for term1)
        if not inner_expr_parts:
            term1_str = _render_exponent_str("1", power_c) # (1)^c = 1
        elif len(inner_expr_parts) > 1:
            term1_str = _render_exponent_str("(" + "".join(inner_expr_parts) + ")", power_c)
        else: # len == 1
            # 強制加上括號保護，避免 x^{2}^{3} 這種錯誤格式
            inner_content = "".join(inner_expr_parts)
            term1_str = _render_exponent_str(r"({c})".replace("{c}", inner_content), power_c)
            
        expr_parts.append(term1_str)
        
        # Part 2: divided by x^d y^e
        term2_str_parts = []
        for var in variables:
            if term2_exponents[var] != 0:
                term2_str_parts.append(_render_exponent_str(var, term2_exponents[var]))

        if term2_str_parts:
            expr_parts.append(r"\div")
            if len(term2_str_parts) > 1:
                expr_parts.append("(" + "".join(term2_str_parts) + ")")
            else:
                expr_parts.append("".join(term2_str_parts))
        # If term2_str_parts is empty, it means we are dividing by 1, so no division symbol needed.

        question_text = _format_latex_safe(
            r"簡化下列各式，並以正指數表示：$ {expression} $",
            expression=" ".join(expr_parts)
        )

        # Calculate final exponents
        final_exponents = {}
        for var in variables:
            final_exp = (term1_exponents.get(var, 0) * power_c) - term2_exponents.get(var, 0)
            final_exponents[var] = final_exp
        
        # Format correct answer with positive exponents only for display
        numerator_terms = []
        denominator_terms = []

        for var in sorted(final_exponents.keys()):
            exp = final_exponents[var]
            if exp > 0:
                numerator_terms.append(_render_exponent_str(var, exp))
            elif exp < 0:
                # Move to denominator with positive exponent
                denominator_terms.append(_render_exponent_str(var, abs(exp)))
            # If exp == 0, it's 1 and not displayed unless it's the only term

        numerator_str = "".join(numerator_terms) if numerator_terms else "1"
        denominator_str = "".join(denominator_terms) if denominator_terms else "1"

        if numerator_str == "1" and denominator_str == "1":
            correct_answer_str = "1"
        elif denominator_str == "1":
            correct_answer_str = numerator_str
        else:
            correct_answer_str = _format_latex_safe(r"\frac{{{numerator_val}}}{{{denominator_val}}}",
                                                    numerator_val=numerator_str,
                                                    denominator_val=denominator_str)

        correct_answer = correct_answer_str
        answer_display = correct_answer_str
        
    question_text += ""
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # Display format for students
        "image_base64": image_base64,
        "input_mode": "handwriting", # V11.2 Handwriting Mode
        "created_at": datetime.now().isoformat(),
        "version": "1.1" # Version Bump
    }


if __name__ == "__main__":
    print("--- K12 指數律問題生成測試 ---")
    for _ in range(5):
        problem = generate()
        print(f"Question: {problem['question_text']}")
        print(f"Correct Answer (internal): {problem['correct_answer']}")
        print(f"Answer (display): {problem['answer']}")
        print(f"Check 'user_answer={problem['answer']}' against correct: {check(problem['answer'], problem['correct_answer'])}")
        print("-" * 30)

    # Test specific type for LaTeX safety
    print("\n--- LaTeX 安全性測試 (變數簡化) ---")
    problem = generate(level=1)
    while "簡化下列各式" not in problem["question_text"]:
        problem = generate(level=1)
    print(f"Question: {problem['question_text']}")
    print(f"Correct Answer (internal): {problem['correct_answer']}")
    print(f"Answer (display): {problem['answer']}")
    print(f"Check 'user_answer={problem['answer']}' against correct: {check(problem['answer'], problem['correct_answer'])}")
    print("-" * 30)

    # Test edge case for simplification to '1'
    print("\n--- 簡化為 '1' 的測試 (手動模擬) ---")
    # 模擬一個結果為 '1' 的簡化題，例如：(x^2 y^-1)^1 / (x^2 y^-1)
    # 為了測試目的，我們直接構建預期的答案。
    test_correct_answer_str_one = "1"
    print(f"模擬答案為 '1' 的情況: {test_correct_answer_str_one}")
    print(f"檢查 '1' vs '{test_correct_answer_str_one}': {check('1', test_correct_answer_str_one)}")
    print("-" * 30)

    # Test `check` function
    print("\n--- check 函式測試 ---")
    print(f"檢查 '5' vs '5.0': {check('5', '5.0')}") # 預期: 正確！
    print(f"檢查 '5' vs '6': {check('5', '6')}")   # 預期: 答案錯誤...
    print(f"檢查 'x^2y' vs 'x^2y': {check('x^2y', 'x^2y')}") # 預期: 正確！
    print(f"檢查 'x^2y' vs 'x^2z': {check('x^2y', 'x^2z')}") # 預期: 答案錯誤...
    print(f"檢查 '2.000000001' vs '2.0': {check('2.000000001', '2.0')}") # 預期: 正確！
    print(f"檢查 'x^{{2}}y^{{-1}}' vs 'x^{{2}}y^{{-1}}': {check(r'x^{2}y^{-1}', r'x^{2}y^{-1}')}") # 預期: 正確！
    print(f"檢查 'x' vs 'x': {check('x', 'x')}") # 預期: 正確！
    print(f"檢查 '1' vs '1': {check('1', '1')}") # 預期: 正確！
    print(f"檢查 '1/x' vs '\frac{1}{x}': {check('1/x', r'\frac{1}{x}')}") # 預期: 答案錯誤... (嚴格字串比對)
    print("-" * 30)


# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # 2. [V10.3] 解決 r-string 導致的 \n 換行失效問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\']
            if (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers) and "手寫" not in res.get('question_text', ''):
                res['question_text'] += "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
