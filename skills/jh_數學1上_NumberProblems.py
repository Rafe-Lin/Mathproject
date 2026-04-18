# ==============================================================================
# ID: jh_數學1上_NumberProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 53.76s | RAG: 2 examples
# Created At: 2026-01-14 21:00:22
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
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
def simplify_fraction(n, d):
    """[V11.3 Standard Helper] 強力化簡分數並回傳 (分子, 分母)"""
    common = math.gcd(n, d)
    return n // common, d // common


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
    
    # [V11.1] 科學記號自動比對 (1.23*10^4 vs 1.23e4)
    # 支援 *10^, x10^, e 格式
    if "*" in str(ans_display) or "^" in str(ans_display) or "e" in str(ans_display):
        try:
            # 正規化：將常見乘號與次方符號轉為 E-notation
            norm_ans = str(ans_display).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            norm_user = str(u).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            if math.isclose(float(norm_ans), float(norm_user), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
        except: pass

    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}

# Coder Spec for SKILL: 數字問題 (jh_數學1上_NumberProblems)
# STRATEGY: Create a rich variety of problem types covering all nuances of the examples.


import datetime

import base64
import io
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# --- Global Font Setting (Infrastructure Rule 5) ---
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
matplotlib.rcParams['axes.unicode_minus'] = False # To display minus sign correctly in matplotlib

# --- Helper Functions for Visualization (Generic Helper Rules) ---
def draw_number_line_image(start_val, end_val, label_points=None, highlight_point=None, highlight_label=""):
    """
    Generates a number line image as a base64 string.
    Only takes known data. No answer leakage.
    Returns: str (base64 encoded image)
    """
    if label_points is None:
        label_points = []
    
    fig = Figure(figsize=(8, 1)) # Infrastructure Rule 1: Use Figure
    ax = fig.add_subplot(111)     # Infrastructure Rule 1: Use Figure
    
    ax.set_xlim(start_val - 1, end_val + 1) # Give some padding
    ax.set_ylim(0, 1)
    
    # Hide all spines except bottom
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    # Draw a single line for the number line
    ax.spines['bottom'].set_position('center')
    ax.spines['bottom'].set_linewidth(1.5)
    
    ax.yaxis.set_ticks([]) # Hide y-axis ticks
    
    # Infrastructure Rule 5: Number line ONLY shows origin '0' with fontsize 18.
    custom_ticks = []
    if math.floor(start_val - 1) <= 0 <= math.ceil(end_val + 1): # Check if 0 is within the visible range
        custom_ticks.append(0)
    
    ax.xaxis.set_ticks(custom_ticks)
    ax.tick_params(axis='x', length=6, width=1, colors='black', labelsize=18) # Fontsize 18 for '0'

    # Label specific points (e.g., other known points)
    for point in label_points:
        ax.plot(point, 0, 'o', color='blue', markersize=6)
        # Infrastructure Rule 5: Point labels set to 16+. Assuming numerical labels for label_points
        ax.text(point, 0.2, str(point), ha='center', va='bottom', fontsize=16, color='blue') 

    # Highlight a specific point (e.g., initial position)
    if highlight_point is not None:
        ax.plot(highlight_point, 0, 'o', color='red', markersize=8, zorder=5)
        # Infrastructure Rule 5: Point labels set to 16+.
        ax.text(highlight_point, -0.2, highlight_label, ha='center', va='top', fontsize=16, color='red')

    buf = io.BytesIO()
    # Infrastructure Rule 1: Use FigureCanvasAgg
    FigureCanvasAgg(fig).print_png(buf) 
    fig.clear() # Infrastructure Rule 1: Clear the figure
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64


# --- Problem Type 1 (Maps to Example 1, 2): 方程式求解 (Equation Solving) ---
def _generate_type1():
    """
    Generates a linear equation solving problem (e.g., Ax + B = Cx + D).
    Returns: tuple (question_text, correct_answer_str, numerical_answer, image_base64)
    """
    # Generate coefficients and constants to ensure an integer solution
    x_val = random.randint(-10, 10) # Target integer solution
    
    a = random.randint(1, 5)
    c = random.randint(1, 5)
    while a == c: # Ensure (a-c) != 0 to avoid trivial cases or infinite/no solutions
        c = random.randint(1, 5)
    
    # Calculate b and d such that (a-c)x_val = d-b
    b = random.randint(-15, 15)
    d = (a - c) * x_val + b # d = (a-c)x + b

    # Format question text using '甲數'
    def _format_expression(coeff, const_val):
        parts = []
        if coeff == 1:
            parts.append(r"甲數")
        elif coeff == -1:
            parts.append(r"負甲數")
        else: # coeff is 2, 3, 4, 5, or negative multiples
            parts.append(f"甲數的 {abs(coeff)} 倍")
            if coeff < 0:
                parts.insert(0, r"負") # Prepend "負" for negative multiples

        if const_val > 0:
            parts.append(f"加 {const_val}")
        elif const_val < 0:
            parts.append(f"減 {abs(const_val)}")
        
        # Handle cases like "0" for 0*x + 0 (though coeffs are not 0 here)
        if not parts:
            return "0"
        
        return " ".join(parts)

    lhs_text = _format_expression(a, b)
    rhs_text = _format_expression(c, d)

    question_text_template = r"已知 ${lhs_text}$ 等於 ${rhs_text}$，求甲數是多少？"
    question_text = question_text_template.replace("{lhs_text}", lhs_text) \
                                      .replace("{rhs_text}", rhs_text)
    
    correct_answer_str = str(x_val)
    
    return question_text, correct_answer_str, x_val, "" # No image for this type


# --- Problem Type 2 (Maps to Example 2, 3): 逆向求解 (Reverse Solving - Number Line/Distance) ---
def _generate_type2():
    """
    Generates a reverse solving problem involving a number line (finding a coordinate given distance).
    Returns: tuple (question_text, correct_answer_str, numerical_answer, image_base64)
    """
    p_coord = random.randint(-20, 20)
    distance = random.randint(5, 15)
    direction_choice = random.choice(["right", "left"])

    if direction_choice == "right":
        q_coord = p_coord + distance
        direction_text = r"右側"
    else:
        q_coord = p_coord - distance
        direction_text = r"左側"
    
    # Generate question text using .replace()
    p_coord_str = str(p_coord)
    distance_str = str(distance)
    
    question_text_template = r"數線上有一點 $P$ 表示 ${p_val}$。若點 $Q$ 距離點 $P$ 為 ${dist_val}$ 個單位長，且點 $Q$ 在點 $P$ 的 ${dir_text}$，則點 $Q$ 表示的數為何？"
    question_text = question_text_template.replace("{p_val}", p_coord_str) \
                                      .replace("{dist_val}", distance_str) \
                                      .replace("{dir_text}", direction_text)
    
    correct_answer_str = str(q_coord)
    
    # Generate image: only show P, not Q (the answer) to prevent leakage.
    # The number line range should encompass both P and the potential location of Q.
    min_val = min(p_coord, q_coord) - 5
    max_val = max(p_coord, q_coord) + 5
    image_base64 = draw_number_line_image(min_val, max_val, label_points=[p_coord], highlight_point=p_coord, highlight_label=r"$P$")
    
    return question_text, correct_answer_str, q_coord, image_base64


# --- Problem Type 3 (Maps to Example 1, 3): 情境應用 (Contextual Application - Cumulative Change) ---
def _generate_type3():
    """
    Generates a contextual application problem involving cumulative changes (e.g., temperature, depth, balance).
    Returns: tuple (question_text, correct_answer_str, numerical_answer, image_base64)
    """
    initial_val = random.randint(-100, 100) # Initial value for calculation
    
    change1 = random.randint(10, 50)
    change2 = random.randint(10, 50)
    change3 = random.randint(10, 50)
    
    scenario_choices = [
        "溫度", # Temperature: initial, rise, fall, rise -> final
        "潛水艇深度", # Submarine depth: initial (below sea level is neg), ascend, descend, ascend -> final
        "銀行帳戶", # Bank account: initial, deposit, withdraw, deposit -> final
    ]
    
    scenario = random.choice(scenario_choices)
    
    current_val = initial_val
    actions_list = []
    
    # Construct scenario-specific text and calculate cumulative value
    if scenario == "溫度":
        initial_text = r"某地氣溫原為 ${init_val}^\circ C$。"
        current_val += change1
        actions_list.append(r"上升了 ${ch1_val}^\circ C$")
        current_val -= change2
        actions_list.append(r"下降了 ${ch2_val}^\circ C$")
        current_val += change3
        actions_list.append(r"再上升了 ${ch3_val}^\circ C$")
        final_question = r"請問最終氣溫是多少？"
        
    elif scenario == "潛水艇深度":
        # For text, initial depth is usually given as positive (e.g., "50 公尺處"), but for calculation, it's negative.
        initial_text_display = abs(initial_val) if initial_val != 0 else random.randint(20, 80) # Ensure a positive display value if initial_val was 0
        initial_val_for_calc = -initial_text_display # Actual starting point below sea level
        current_val = initial_val_for_calc
        
        initial_text = r"某潛水艇從海平面下 ${init_val}$ 公尺處。"
        current_val += change1
        actions_list.append(r"先上升 ${ch1_val}$ 公尺")
        current_val -= change2
        actions_list.append(r"再下潛 ${ch2_val}$ 公尺")
        current_val += change3
        actions_list.append(r"最後又上升 ${ch3_val}$ 公尺")
        final_question = r"請問潛水艇最終所在的高度距離海平面多少公尺？"
        
        # Replace initial value in text with its absolute value for "海平面下" context
        initial_text = initial_text.replace("{init_val}", str(initial_text_display))
        
    elif scenario == "銀行帳戶":
        initial_val = abs(initial_val) if initial_val < 0 else initial_val # Account balance usually starts non-negative or we adjust.
        current_val = initial_val
        initial_text = r"小明的銀行帳戶原有 ${init_val}$ 元。"
        current_val += change1
        actions_list.append(r"存入 ${ch1_val}$ 元")
        current_val -= change2
        actions_list.append(r"領出 ${ch2_val}$ 元")
        current_val += change3
        actions_list.append(r"再存入 ${ch3_val}$ 元")
        final_question = r"請問帳戶最終有多少元？"

    ans_val = current_val

    # Construct full question text using .replace()
    # The initial_text might already have {init_val} replaced for submarine scenario.
    if "{init_val}" in initial_text: # Only replace if not already handled by submarine logic
        question_text = initial_text.replace("{init_val}", str(initial_val))
    else:
        question_text = initial_text
        
    question_text += r"，".join(actions_list)
    question_text = question_text.replace("{ch1_val}", str(change1)) \
                                 .replace("{ch2_val}", str(change2)) \
                                 .replace("{ch3_val}", str(change3))
    question_text += r"。" + final_question
    
    correct_answer_str = str(ans_val)
    
    return question_text, correct_answer_str, ans_val, "" # No image for this type


# --- Problem Type 4 (Original Problem Type 1): 直接計算 (Direct Calculation) ---
def _generate_type4():
    """
    Generates a direct calculation problem involving integers and order of operations.
    Returns: tuple (question_text, correct_answer_str, numerical_answer, image_base64)
    """
    # Generate numbers for an expression like A * B - [C / D + E]
    a = random.randint(-10, 10)
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5) # Avoid multiplication by zero if not intended
    
    c = random.randint(-20, 20)
    # Ensure division is exact and by a non-zero number
    d_choices = [x for x in range(-5, 6) if x != 0 and c % x == 0]
    if not d_choices: # Fallback if no exact divisor found, broaden c
        c = random.randint(-30, 30)
        d_choices = [x for x in range(-5, 6) if x != 0 and c % x == 0]
    if not d_choices: d_choices = [1, -1] # Last resort, ensure d is not 0
    d = random.choice(d_choices)
    
    e = random.randint(-10, 10)

    # Calculate correct answer
    ans_val = a * b - (c // d + e)
    
    # Format question_text using .replace() for LaTeX safety and clarity
    # Ensure negative numbers are parenthesized for better LaTeX rendering
    def _format_num_for_latex(num):
        return str(num) if num >= 0 else r"({})".replace("{}", str(num))

    a_str = _format_num_for_latex(a)
    b_str = _format_num_for_latex(b)
    c_str = _format_num_for_latex(c)
    d_str = _format_num_for_latex(d)
    e_str = _format_num_for_latex(e)

    question_text_template = r"計算 $ {a_val} \times {b_val} - [ {c_val} \div {d_val} + {e_val} ] $ "
    question_text = question_text_template.replace("{a_val}", a_str) \
                                      .replace("{b_val}", b_str) \
                                      .replace("{c_val}", c_str) \
                                      .replace("{d_val}", d_str) \
                                      .replace("{e_val}", e_str)
    
    correct_answer_str = str(ans_val)
    
    return question_text, correct_answer_str, ans_val, "" # No image for this type


# --- Main Functions (Top-level, No Class) ---
def generate(level=1):
    """
    Generates a K12 math problem for '數字問題'.
    
    Args:
        level (int): Difficulty level (currently unused, fixed to 1).
        
    Returns:
        dict: A dictionary containing the problem details.
    """
    # Select from all problem types, including the new equation solving type (Type 1)
    # and the original direct calculation type (now Type 4) for variety.
    problem_type_func = random.choice([_generate_type1, _generate_type2, _generate_type3, _generate_type4])
    
    question_text, correct_answer_str, numerical_answer, image_base64 = problem_type_func()
    
    # Final structure hardening: return dictionary with locked fields
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str, # Must be string
        "answer": numerical_answer, # The actual numerical value for internal use/checking
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0.0" # Initial version
    }


# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \\n 問題
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\\n(請在手寫區作答!)"

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
