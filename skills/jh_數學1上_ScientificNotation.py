# ==============================================================================
# ID: jh_數學1上_ScientificNotation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 33.05s | RAG: 5 examples
# Created At: 2026-01-14 18:44:50
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
import base64 # 依規範必須包含，即使不使用
import re

# --- 輔助函式 (Helper Functions) ---
# 規範：所有輔助函式必須明確使用 'return' 語句回傳結果。
# 規範：若結果用於拼接 question_text，則回傳值必須強制轉為字串 (str)。

def _format_scientific_notation(coefficient, exponent):
    """
    格式化科學記號字串，嚴格遵守 LaTeX 安全排版規範。
    範例：3.45 \times 10^{6}
    規範：凡字串包含 LaTeX 指令，嚴禁使用 f-string 或 % 格式化。
    """
    # 處理係數為 0 的特殊情況
    if math.isclose(coefficient, 0.0, abs_tol=1e-12):
        return "0"

    # 確保係數格式化至合理的位數，並移除尾隨的零和點
    # 內部使用 f-string 格式化係數數值，但最終拼接 LaTeX 字串時仍使用 replace
    if coefficient == int(coefficient):
        coeff_str = str(int(coefficient))
    else:
        # 使用足夠的精度，然後移除尾隨零和點
        coeff_str = f"{coefficient:.10f}".rstrip('0').rstrip('.')
        if coeff_str == "-0": # 處理 -0.0 顯示為 0
            coeff_str = "0"

    # 嚴格執行 LaTeX 模板替換，禁止 f-string 或 % 格式化
    template = r"{coeff} \times 10^{{{exp}}}".replace("{coeff}", coeff_str)
    formatted_string = template.replace("{exp}", str(exponent))
    return formatted_string

def _to_scientific_notation_tuple(number):
    """
    將標準數字轉換為 (係數, 指數) 元組，確保 1 <= |係數| < 10。
    """
    if math.isclose(number, 0.0, abs_tol=1e-12):
        return (0.0, 0) # 0 的科學記號通常直接表示為 0

    is_negative = number < 0
    abs_number = abs(number)
    exponent = 0

    if abs_number >= 10:
        while abs_number >= 10:
            abs_number /= 10
            exponent += 1
    elif abs_number < 1:
        while abs_number < 1 and not math.isclose(abs_number, 0.0, abs_tol=1e-12):
            abs_number *= 10
            exponent -= 1
    
    coefficient = abs_number * (-1 if is_negative else 1)
    
    # 微調以確保係數在 [1, 10) 範圍內，處理浮點數精度問題
    # 例如：如果原始數字是 9.999999999999999，可能被表示為 10.0
    # 或者 0.9999999999999999，可能被表示為 0.999...
    if abs(coefficient) >= 10 and not math.isclose(coefficient, 0.0, abs_tol=1e-12):
        coefficient /= 10
        exponent += 1
    elif abs(coefficient) < 1 and not math.isclose(coefficient, 0.0, abs_tol=1e-12):
        coefficient *= 10
        exponent -= 1
    
    # 再次檢查並確保係數在 [1, 10) 範圍內 (排除 0)
    if not math.isclose(coefficient, 0.0, abs_tol=1e-12):
        while abs(coefficient) >= 10:
            coefficient /= 10
            exponent += 1
        while abs(coefficient) < 1:
            coefficient *= 10
            exponent -= 1

    return (coefficient, exponent)

def _parse_scientific_notation_string(s):
    """
    解析可能是科學記號形式的字串為浮點數值。
    能處理的格式包含： "3.45 \times 10^{6}", "3.45E6", "3.45 * 10^6", "12345", "0.000123"。
    若解析失敗則回傳 None。
    """
    s = s.strip()
    
    # 嘗試直接轉換為浮點數 (處理標準數字和 '3.45e6' 格式)
    try:
        return float(s)
    except ValueError:
        pass

    # 嘗試解析 LaTeX 樣式的科學記號: X \times 10^{Y} 或 X * 10^{Y}
    # 支援係數為負數、小數點，指數為負數。
    latex_pattern = re.compile(
        r"^(-?\d+(?:\.\d+)?)\s*(?:\\times|\*|\cdot)?\s*10\^{(-?\d+)}$"
    )
    # 移除空格以匹配 LaTeX 格式，但保留係數和指數之間的空格彈性
    match = latex_pattern.match(s) 
    if match:
        coeff_str, exp_str = match.groups()
        try:
            coefficient = float(coeff_str)
            exponent = int(exp_str)
            return coefficient * (10**exponent)
        except ValueError:
            pass

    # 嘗試解析簡化版科學記號: X * 10^Y 或 X * 10**Y
    simple_pattern = re.compile(
        r"^(-?\d+(?:\.\d+)?)\s*(?:[\*x]\s*10(?:\^|\*\*)(-?\d+))$"
    )
    match = simple_pattern.match(s)
    if match:
        coeff_str, exp_str = match.groups()
        try:
            coefficient = float(coeff_str)
            exponent = int(exp_str)
            return coefficient * (10**exponent)
        except ValueError:
            pass
            
    return None # 所有解析嘗試都失敗

# --- 頂層函式 (Top-Level Functions) ---
# 規範：嚴禁使用 class 封裝。必須直接定義 generate() 與 check() 於模組最外層。
# 規範：確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level=1):
    """
    根據指定難度等級生成科學記號相關題目。

    Args:
        level (int): 難度等級，預設為 1。

    Returns:
        dict: 包含題目文本、正確答案、答案、圖片 base64、創建時間和版本號的字典。
    """
    question_text = ""
    correct_answer = ""
    answer = "" # 此欄位與 correct_answer 相同，用於顯示給使用者
    image_base64 = None # 科學記號通常不需要圖片，依規範設為 None

    # 規範：generate() 內部必須使用 random.choice 或 if/elif 邏輯，實作至少 3 種不同的題型變體。
    problem_type = random.choice([
        "standard_to_scientific",  # 變體 1: 直接計算 (標準數字轉科學記號)
        "scientific_to_standard",  # 變體 2: 逆向求解 (科學記號轉標準數字)
        "comparison_or_operation"  # 變體 3: 情境應用 (比較大小或運算)
    ])

    if problem_type == "standard_to_scientific":
        # 變體 1: 將標準數字表示成科學記號
        if level == 1:
            num_range_choice = random.choice(["large", "small", "moderate"])
            if num_range_choice == "large":
                num = random.randint(10**3, 10**6) # 例如: 12345, 987654
            elif num_range_choice == "small":
                num = random.uniform(0.001, 0.999) # 例如: 0.00123, 0.987
                num = round(num, random.randint(3, 5)) # 保留一些精度
            else: # moderate, 10-999 或 0.1-0.99
                if random.random() < 0.5:
                    num = random.randint(10, 999)
                else:
                    num = random.uniform(0.1, 0.99)
                    num = round(num, random.randint(2,3))
        else: # 更高難度等級
            num_range_choice = random.choice(["large", "small", "very_large", "very_small"])
            if num_range_choice == "large":
                num = random.randint(10**5, 10**10)
            elif num_range_choice == "small":
                num = random.uniform(10**-10, 10**-5)
                num = round(num, random.randint(8, 12))
            elif num_range_choice == "very_large":
                num = random.randint(10**10, 10**15)
            else: # very_small
                num = random.uniform(10**-15, 10**-10)
                num = round(num, random.randint(12, 16))

        if random.random() < 0.2: # 約 20% 機率生成負數
            num *= -1
        
        # 約 5% 機率生成 0
        if random.random() < 0.05:
            num = 0

        coeff, exp = _to_scientific_notation_tuple(num)
        
        # 格式化數字字串，避免顯示為 -0.0
        num_str = f"{num:f}".rstrip('0').rstrip('.')
        if num_str == "-0": num_str = "0"
        
        # 規範：凡字串包含 LaTeX 指令，嚴禁使用 f-string 或 % 格式化。
        # 必須嚴格執行以下模板：expr = r"x = {a}".replace("{a}", str(ans_val))
        question_template = r"請將數字 ${num_val}$ 表示成科學記號。"
        question_text = question_template.replace("{num_val}", num_str)
        
        correct_answer = _format_scientific_notation(coeff, exp)

    elif problem_type == "scientific_to_standard":
        # 變體 2: 將科學記號表示成一般的數字
        if level == 1:
            coeff = round(random.uniform(1, 9.99), random.randint(0, 2))
            exp = random.randint(-5, 5) # 較小範圍的指數
        else:
            coeff = round(random.uniform(1, 9.99), random.randint(0, 3))
            exp = random.randint(-10, 10) # 較大範圍的指數

        if random.random() < 0.2:
            coeff *= -1
        
        # 約 5% 機率生成 0
        if random.random() < 0.05:
            coeff = 0

        scientific_str = _format_scientific_notation(coeff, exp)
        
        standard_num = coeff * (10**exp)
        # 格式化標準數字字串，避免顯示為 -0.0
        correct_answer = f"{standard_num:f}".rstrip('0').rstrip('.')
        if correct_answer == "-0": correct_answer = "0"

        question_template = r"請將科學記號 ${sci_val}$ 表示成一般的數字。"
        question_text = question_template.replace("{sci_val}", scientific_str)

    else: # problem_type == "comparison_or_operation"
        # 變體 3: 比較大小或簡單運算
        op_type = random.choice(["compare", "multiply", "divide"])

        # 生成兩個科學記號數字
        coeff1 = round(random.uniform(1, 9.99), random.randint(0, 2))
        exp1 = random.randint(-8, 8)
        
        coeff2 = round(random.uniform(1, 9.99), random.randint(0, 2))
        exp2 = random.randint(-8, 8)

        if random.random() < 0.2: coeff1 *= -1
        if random.random() < 0.2: coeff2 *= -1

        # 確保不會生成 0 用於乘除法，除非作為特例處理
        if op_type in ["multiply", "divide"]:
            if math.isclose(coeff1, 0.0, abs_tol=1e-12): coeff1 = round(random.uniform(1, 9.99), random.randint(0,2)) * (-1 if random.random() < 0.5 else 1)
            if math.isclose(coeff2, 0.0, abs_tol=1e-12): coeff2 = round(random.uniform(1, 9.99), random.randint(0,2)) * (-1 if random.random() < 0.5 else 1)
        
        # 允許比較 0
        if op_type == "compare" and random.random() < 0.05: coeff1 = 0
        if op_type == "compare" and random.random() < 0.05: coeff2 = 0

        sci_str1 = _format_scientific_notation(coeff1, exp1)
        sci_str2 = _format_scientific_notation(coeff2, exp2)

        if op_type == "compare":
            # 比較大小
            num1 = coeff1 * (10**exp1)
            num2 = coeff2 * (10**exp2)
            
            question_template = r"請比較 ${val1}$ 和 ${val2}$ 的大小，並填入 $>, <, =$。"
            question_text = question_template.replace("{val1}", sci_str1).replace("{val2}", sci_str2)

            if num1 > num2:
                correct_answer = ">"
            elif num1 < num2:
                correct_answer = "<"
            else:
                correct_answer = "="
        
        elif op_type == "multiply":
            # 乘法運算: (a x 10^b) * (c x 10^d) = (a*c) x 10^(b+d)
            result_val = (coeff1 * (10**exp1)) * (coeff2 * (10**exp2))

            # 將結果正規化為科學記號形式
            final_coeff, final_exp = _to_scientific_notation_tuple(result_val)

            question_template = r"請計算 $(\text{${val1}$}) \times (\text{${val2}$})$，並將結果以科學記號表示。"
            question_text = question_template.replace("{val1}", sci_str1).replace("{val2}", sci_str2)
            
            correct_answer = _format_scientific_notation(final_coeff, final_exp)

        else: # op_type == "divide"
            # 除法運算: (a x 10^b) / (c x 10^d) = (a/c) x 10^(b-d)
            # 確保除數不為零
            if math.isclose(coeff2, 0.0, abs_tol=1e-12): # 再次檢查，避免浮點數誤差導致的 0
                coeff2 = random.uniform(1, 9.99)
                if random.random() < 0.2: coeff2 *= -1
                sci_str2 = _format_scientific_notation(coeff2, exp2)
            
            result_val = (coeff1 * (10**exp1)) / (coeff2 * (10**exp2))

            # 將結果正規化為科學記號形式
            final_coeff, final_exp = _to_scientific_notation_tuple(result_val)

            question_template = r"請計算 $(\text{${val1}$}) \div (\text{${val2}$})$，並將結果以科學記號表示。"
            question_text = question_template.replace("{val1}", sci_str1).replace("{val2}", sci_str2)

            correct_answer = _format_scientific_notation(final_coeff, final_exp)

    # 規範：返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    # 規範：更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    answer = correct_answer # 依規範，答案欄位通常用於顯示，與正確答案一致

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64, # 無圖片，設為 None
        "created_at": datetime.now().isoformat(),
        "version": "9.6"
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
