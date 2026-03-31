# ==============================================================================
# ID: jh_數學1上_PowerOfNumbers
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 30.30s | RAG: 5 examples
# Created At: 2026-01-14 19:07:10
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
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
    if n <= 1: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    if n <= 3: return {'correct': True, 'result': '正確！'}
    if n % 2 == 0 or n % 3 == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
        i += 6
    return {'correct': True, 'result': '正確！'}
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
import base64 # For image_base64, will be an empty string if no image

# Helper function to safely format LaTeX strings
def _latex_safe_format(template_str, replacements):
    """
    Safely formats a string template with replacements, strictly using .replace()
    to avoid f-string or % formatting issues with LaTeX commands.

    Args:
        template_str (str): The string template, with placeholders like "{key}".
                            Must be a raw string (r"...") if it contains backslashes.
        replacements (dict): A dictionary where keys are placeholder names (e.g., "key")
                             and values are the data to insert. Values will be
                             converted to string before replacement.

    Returns:
        str: The formatted string.
    """
    formatted_str = template_str
    for key, value in replacements.items():
        # Ensure value is string before replacement to prevent type errors
        formatted_str = formatted_str.replace("{" + str(key) + "}", str(value))
    return formatted_str


def generate(level=1):
    """
    Generates a math problem for the 'Power of Numbers' skill.

    Args:
        level (int): Difficulty level (currently not used for variation, always 1).

    Returns:
        dict: A dictionary containing problem details:
              - question_text (str): The problem statement in LaTeX format.
              - correct_answer (str): The machine-readable correct answer.
              - answer (str): The display-ready correct answer (e.g., LaTeX formatted).
              - image_base64 (str): Base64 encoded image (empty for this skill).
              - created_at (str): ISO formatted datetime of creation.
              - version (str): Version of the problem generator.
    """
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""  # Machine-readable string for checking
    answer_display = ""  # LaTeX formatted answer for display
    image_base64 = ""    # No images for this skill

    if problem_type == 1:  # 題型變體 1: 直接計算 (Direct Calculation)
        sub_type = random.choice([1, 2, 3, 4])
        
        if sub_type == 1:  # 正數底數、正數指數
            base = random.randint(2, 5)
            exponent = random.randint(2, 4)
            ans_val = base ** exponent
            
            question_template = r"計算 $ {base}^{exponent} $ 的值。"
            question_text = _latex_safe_format(question_template, {"base": base, "exponent": exponent})
            correct_answer = str(ans_val)
            answer_display = str(ans_val)

        elif sub_type == 2:  # 負數底數或負號運算
            choice = random.choice([1, 2])
            base_val = random.randint(2, 5)
            exponent_val = random.randint(2, 4)
            
            if choice == 1:  # $(-a)^b$
                ans_val = (-base_val) ** exponent_val
                question_template = r"計算 $ ({base})^{exponent} $ 的值。"
                question_text = _latex_safe_format(question_template, {"base": -base_val, "exponent": exponent_val})
                correct_answer = str(ans_val)
                answer_display = str(ans_val)
            else:  # $-a^b$
                ans_val = -(base_val ** exponent_val)
                question_template = r"計算 $ -{base}^{exponent} $ 的值。"
                question_text = _latex_safe_format(question_template, {"base": base_val, "exponent": exponent_val})
                correct_answer = str(ans_val)
                answer_display = str(ans_val)

        elif sub_type == 3:  # 分數底數
            numerator = random.randint(1, 4)
            denominator = random.randint(numerator + 1, 6) # denominator > numerator to ensure proper fraction
            
            # Simplify fraction
            common_divisor = math.gcd(numerator, denominator)
            numerator //= common_divisor
            denominator //= common_divisor
            
            exponent = random.randint(2, 3)
            ans_numerator = numerator ** exponent
            ans_denominator = denominator ** exponent
            
            question_template = r"計算 $ \left(\frac{{{num}}}{{{den}}}\right)^{{{exp}}} $ 的值。"
            question_text = _latex_safe_format(question_template, {"num": numerator, "den": denominator, "exp": exponent})
            
            if ans_denominator == 1: # Should not happen with proper fraction setup unless numerator was 1 and denominator was 1 which is avoided.
                correct_answer = str(ans_numerator)
                answer_display = str(ans_numerator)
            else:
                correct_answer = f"{ans_numerator}/{ans_denominator}" # Machine-readable fraction format
                answer_display = _latex_safe_format(r"$\frac{{{num}}}{{{den}}}$", {"num": ans_numerator, "den": ans_denominator})

        elif sub_type == 4:  # 混合運算 (例如 $A \times B^C$ 或 $A + B^C$)
            op_choice = random.choice(['multiply', 'add'])
            coeff = random.randint(2, 5)
            base = random.randint(2, 3)
            exponent = random.randint(2, 3)
            
            if op_choice == 'multiply':
                ans_val = coeff * (base ** exponent)
                question_template = r"計算 $ {coeff} \times {base}^{exponent} $ 的值。"
                question_text = _latex_safe_format(question_template, {"coeff": coeff, "base": base, "exponent": exponent})
            else: # 'add'
                add_val = random.randint(1, 10)
                ans_val = add_val + (base ** exponent)
                question_template = r"計算 $ {add_val} + {base}^{exponent} $ 的值。"
                question_text = _latex_safe_format(question_template, {"add_val": add_val, "base": base, "exponent": exponent})
            
            correct_answer = str(ans_val)
            answer_display = str(ans_val)

    elif problem_type == 2:  # 題型變體 2: 逆向求解 / 判斷 (Inverse Solving / Judgment)
        sub_type = random.choice([1, 2])
        
        if sub_type == 1:  # 逆向求解 (已知平方求底數)
            base = random.randint(2, 7)
            exponent = 2 # For K12, typically square
            ans_val = base ** exponent
            
            question_template = r"如果 $ x^{exponent} = {ans_val} $，則 $ x $ 的值可能為何？(請列出所有可能的值，以逗號分隔，例如 $3,-3$)"
            question_text = _latex_safe_format(question_template, {"exponent": exponent, "ans_val": ans_val})
            
            # For x^2 = N, x can be +sqrt(N) or -sqrt(N)
            correct_answer = f"{base},{-base}" # Machine-readable for check function
            answer_display = _latex_safe_format(r"$\pm {base}$", {"base": base})

        elif sub_type == 2:  # 比較次方數大小
            a = random.randint(2, 5)
            b = random.randint(2, 5)
            c = random.randint(2, 5)
            d = random.randint(2, 5)

            # Ensure they are not trivially equal too often or identical expressions
            # This loop tries to get distinct expressions or values for comparison
            attempts = 0
            max_attempts = 100
            while attempts < max_attempts and ((a == c and b == d) or (a**b == c**d and a != c and b != d)):
                 a = random.randint(2, 5)
                 b = random.randint(2, 5)
                 c = random.randint(2, 5)
                 d = random.randint(2, 5)
                 attempts += 1
            
            val1 = a ** b
            val2 = c ** d
            
            if val1 > val2:
                comparison_result = ">"
            elif val1 < val2:
                comparison_result = "<"
            else:
                comparison_result = "="
            
            question_template = r"比較 $ {a}^{b} $ 和 $ {c}^{d} $ 的大小。請填入 $>, <, = $。"
            question_text = _latex_safe_format(question_template, {"a": a, "b": b, "c": c, "d": d})
            correct_answer = comparison_result
            answer_display = comparison_result

    elif problem_type == 3:  # 題型變體 3: 情境應用 (Contextual Application)
        sub_type = random.choice([1]) # Only one sub-type for now
        
        if sub_type == 1:  # 倍數成長情境
            initial_amount = random.randint(2, 10)
            multiplier = random.randint(2, 3) # Doubles or triples
            times = random.randint(2, 4) # Number of repetitions
            
            final_amount = initial_amount * (multiplier ** times)
            
            scenario_template = "某種細菌每小時數量會變成原來的 {multiplier} 倍。如果一開始有 {initial_amount} 個細菌，那麼 {times} 小時後會有多少個細菌？"
            question_text = _latex_safe_format(scenario_template, {
                "initial_amount": initial_amount,
                "multiplier": multiplier,
                "times": times
            })
            correct_answer = str(final_amount)
            answer_display = str(final_amount)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }




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
