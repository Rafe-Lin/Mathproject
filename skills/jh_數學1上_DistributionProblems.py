# ==============================================================================
# ID: jh_數學1上_DistributionProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 33.73s | RAG: 2 examples
# Created At: 2026-01-14 20:57:32
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
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


import datetime

import base64

# --- Helper Functions (Generic Helper Rules) ---
# No drawing functions are needed for this skill, as it's primarily text-based arithmetic.
# If visual helpers were implemented, they would follow the 'draw_' prefix,
# return a string (e.g., base64 image data), and only receive 'known data' (not answers).

def _get_random_item_name():
    """Returns a random common item name."""
    items = ["蘋果", "糖果", "鉛筆", "餅乾", "貼紙", "氣球", "彈珠", "果凍"]
    return random.choice(items)

def _format_answer_tuple(quotient, remainder, item_name, type_id):
    """
    Formats the student-facing answer for division problems.
    Args:
        quotient (int): The quotient of the division.
        remainder (int): The remainder of the division.
        item_name (str): The name of the item being distributed.
        type_id (int): Identifier for the problem type to adjust phrasing.
    Returns:
        str: Formatted answer string.
    """
    if type_id == 1: # Direct Distribution
        if remainder == 0:
            return r"每人分到 {q} 個{item}。".replace("{q}", str(quotient)).replace("{item}", item_name)
        else:
            return r"每人分到 {q} 個{item}，剩下 {r} 個。".replace("{q}", str(quotient)).replace("{item}", item_name).replace("{r}", str(remainder))
    elif type_id == 2: # Distribution with Packaging/Grouping
        if remainder == 0:
            return r"可以裝成 {q} 袋。".replace("{q}", str(quotient))
        else:
            return r"可以裝成 {q} 袋，剩下 {r} 個{item}。".replace("{q}", str(quotient)).replace("{r}", str(remainder)).replace("{item}", item_name)
    return "" # Should not happen

def _format_answer_integer(total_items, item_name):
    """
    Formats the student-facing answer for total items.
    Args:
        total_items (int): The calculated total number of items.
        item_name (str): The name of the item.
    Returns:
        str: Formatted answer string.
    """
    return r"原本共有 {total} 個{item}。".replace("{total}", str(total_items)).replace("{item}", item_name)


# --- Core Functions (Structure Hardening) ---

def generate(level=1):
    """
    Generates a K12 math problem on "Distribution Problems".
    Ensures no global state dependency for importlib.reload.
    """
    problem_type = random.choice([1, 2, 3])
    
    question_text = ""
    correct_answer = None
    answer = ""
    image_base64 = None # No image for this problem type
    
    item_name = _get_random_item_name()

    # Problem Type 1: Direct Distribution (Division with Remainder)
    # Maps to Example 1, 5: Basic division with remainder.
    if problem_type == 1:
        # For K12 level 1, keep numbers simple.
        total_items = random.randint(20, 100)
        people = random.randint(2, 9)
        # Ensure people is not too large compared to total_items to avoid trivial quotients
        while total_items // people < 3: # Ensure quotient is at least 3
            total_items = random.randint(20, 100)
            people = random.randint(2, 9)

        quotient = total_items // people
        remainder = total_items % people
        
        # LaTeX Safety: Strict adherence to .replace() for all variable insertions.
        question_template = r"有 {total} 個{item}，要分給 {people} 個人，每人分到幾個？剩下幾個？"
        question_text = question_template.replace("{total}", str(total_items)).replace("{item}", item_name).replace("{people}", str(people))
        
        correct_answer = (quotient, remainder)
        answer = _format_answer_tuple(quotient, remainder, item_name, problem_type)

    # Problem Type 2: Distribution with Packaging/Grouping (Contextual Application)
    # Maps to Example 2, 4: Applying division with specific group sizes.
    elif problem_type == 2:
        total_items = random.randint(30, 120)
        per_group = random.randint(3, 10)
        # Ensure per_group allows for at least a few groups
        while total_items // per_group < 3: # Ensure quotient is at least 3
            total_items = random.randint(30, 120)
            per_group = random.randint(3, 10)

        quotient = total_items // per_group
        remainder = total_items % per_group
        
        # LaTeX Safety: Strict adherence to .replace() for all variable insertions.
        question_template = r"有 {total} 個{item}，每 {per_group} 個裝成一袋。可以裝成幾袋？剩下幾個？"
        question_text = question_template.replace("{total}", str(total_items)).replace("{item}", item_name).replace("{per_group}", str(per_group))
        
        correct_answer = (quotient, remainder)
        answer = _format_answer_tuple(quotient, remainder, item_name, problem_type)

    # Problem Type 3: Reverse Calculation for Total Items (Reverse Solving)
    # Maps to Example 3: Working backward from parts and remainder to find total.
    elif problem_type == 3:
        people = random.randint(3, 8)
        per_person = random.randint(4, 12)
        remainder = random.randint(0, people - 1) # Remainder must be less than divisor (people)
        
        total_items = people * per_person + remainder
        
        # LaTeX Safety: Strict adherence to .replace() for all variable insertions.
        question_template = r"每位小朋友分到 {per_person} 個{item}，剩下 {remainder} 個。如果共有 {people} 位小朋友，請問原本有幾個{item}？"
        question_text = question_template.replace("{per_person}", str(per_person)).replace("{item}", item_name).replace("{remainder}", str(remainder)).replace("{people}", str(people))
        
        correct_answer = total_items
        answer = _format_answer_integer(total_items, item_name)

    # Convert correct_answer to a string for consistency in the output dictionary,
    # especially important for potential future complex types like matrices.
    # For tuples, stringify as "(q, r)"; for integers, stringify directly.
    if isinstance(correct_answer, tuple):
        correct_answer_str = r"({q},{r})".replace("{q}", str(correct_answer[0])).replace("{r}", str(correct_answer[1]))
    else:
        correct_answer_str = str(correct_answer)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str, # Stringified for consistency
        "answer": answer, # Student-facing formatted answer
        "image_base64": image_base64, # No image for this problem type
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0",
    }

# The `check` function is explicitly forbidden to be defined by the infrastructure rules.
# The system will automatically inject its own `check()` function (V10.6 locked version).
# Therefore, the `check` function provided in the technical specification
# and any example usage block calling it must be removed for the final submission.

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
