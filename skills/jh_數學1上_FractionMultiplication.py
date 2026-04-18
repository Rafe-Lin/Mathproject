# ==============================================================================
# ID: jh_數學1上_FractionMultiplication
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 70.58s | RAG: 4 examples
# Created At: 2026-01-14 19:05:55
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

import base64
import io

# 頂層函式：生成數學題目
def generate(level=1):
    """
    生成分數乘法運算的題目。
    根據 level 參數（目前未使用，但保留擴展性），隨機選擇題型。
    """
    problem_type = random.choice([1, 2, 3]) # 3 種不同的題型變體

    question_text = ""
    correct_answer_frac = None
    image_base64 = None # 本技能不涉及視覺化，因此不產生圖片

    if problem_type == 1:
        # 題型 1: 直接計算 - 分數乘分數
        # 範例：(2/3) * (1/4)
        num1 = random.randint(1, 10)
        den1 = random.randint(num1 + 1, 15) if num1 < 15 else random.randint(2, 15)
        while math.gcd(num1, den1) != 1 or den1 == 1: # 確保初始分數非整數且已簡化
            num1 = random.randint(1, 10)
            den1 = random.randint(num1 + 1, 15) if num1 < 15 else random.randint(2, 15)
        frac1 = Fraction(num1, den1)

        num2 = random.randint(1, 10)
        den2 = random.randint(num2 + 1, 15) if num2 < 15 else random.randint(2, 15)
        while math.gcd(num2, den2) != 1 or den2 == 1: # 確保初始分數非整數且已簡化
            num2 = random.randint(1, 10)
            den2 = random.randint(num2 + 1, 15) if num2 < 15 else random.randint(2, 15)
        frac2 = Fraction(num2, den2)

        correct_answer_frac = frac1 * frac2
        
        # Inlining _fraction_to_display_string logic for frac1
        _frac_obj_temp_1 = frac1
        if _frac_obj_temp_1.denominator == 1:
            _display_string_temp_1 = str(_frac_obj_temp_1.numerator)
        elif _frac_obj_temp_1.numerator == 0:
            _display_string_temp_1 = "0"
        elif _frac_obj_temp_1.numerator > _frac_obj_temp_1.denominator and _frac_obj_temp_1.numerator % _frac_obj_temp_1.denominator != 0:
            _whole_temp_1 = _frac_obj_temp_1.numerator // _frac_obj_temp_1.denominator
            _remainder_temp_1 = _frac_obj_temp_1.numerator % _frac_obj_temp_1.denominator
            _template_temp_1 = r"{whole}\frac{{num}}{{den}}"
            _display_string_temp_1 = _template_temp_1.replace("{whole}", str(_whole_temp_1))\
                                                     .replace("{num}", str(_remainder_temp_1))\
                                                     .replace("{den}", str(_frac_obj_temp_1.denominator))
        else:
            _template_temp_1 = r"\frac{{num}}{{den}}"
            _display_string_temp_1 = _template_temp_1.replace("{num}", str(_frac_obj_temp_1.numerator))\
                                                     .replace("{den}", str(_frac_obj_temp_1.denominator))

        # Inlining _fraction_to_display_string logic for frac2
        _frac_obj_temp_2 = frac2
        if _frac_obj_temp_2.denominator == 1:
            _display_string_temp_2 = str(_frac_obj_temp_2.numerator)
        elif _frac_obj_temp_2.numerator == 0:
            _display_string_temp_2 = "0"
        elif _frac_obj_temp_2.numerator > _frac_obj_temp_2.denominator and _frac_obj_temp_2.numerator % _frac_obj_temp_2.denominator != 0:
            _whole_temp_2 = _frac_obj_temp_2.numerator // _frac_obj_temp_2.denominator
            _remainder_temp_2 = _frac_obj_temp_2.numerator % _frac_obj_temp_2.denominator
            _template_temp_2 = r"{whole}\frac{{num}}{{den}}"
            _display_string_temp_2 = _template_temp_2.replace("{whole}", str(_whole_temp_2))\
                                                     .replace("{num}", str(_remainder_temp_2))\
                                                     .replace("{den}", str(_frac_obj_temp_2.denominator))
        else:
            _template_temp_2 = r"\frac{{num}}{{den}}"
            _display_string_temp_2 = _template_temp_2.replace("{num}", str(_frac_obj_temp_2.numerator))\
                                                     .replace("{den}", str(_frac_obj_temp_2.denominator))
        
        # 嚴格遵循 LaTeX 安全排版規範：使用 .replace() 替換佔位符
        q_template = r"計算：${f1} \times {f2} = ?$"
        question_text = q_template.replace("{f1}", _display_string_temp_1)\
                                  .replace("{f2}", _display_string_temp_2)

    elif problem_type == 2:
        # 題型 2: 帶分數 / 整數乘分數
        # 細分三種子題型：整數乘分數、帶分數乘分數、帶分數乘整數
        sub_type = random.choice([1, 2, 3])

        if sub_type == 1: # 整數乘分數
            whole_num = random.randint(2, 10)
            num = random.randint(1, whole_num + 5)
            den = random.randint(num + 1, 15) if num < 15 else random.randint(2, 15)
            while math.gcd(num, den) != 1 or den == 1:
                num = random.randint(1, whole_num + 5)
                den = random.randint(num + 1, 15) if num < 15 else random.randint(2, 15)
            frac = Fraction(num, den)
            
            correct_answer_frac = Fraction(whole_num) * frac
            
            # Inlining _fraction_to_display_string logic for frac
            _frac_obj_temp_3 = frac
            if _frac_obj_temp_3.denominator == 1:
                _display_string_temp_3 = str(_frac_obj_temp_3.numerator)
            elif _frac_obj_temp_3.numerator == 0:
                _display_string_temp_3 = "0"
            elif _frac_obj_temp_3.numerator > _frac_obj_temp_3.denominator and _frac_obj_temp_3.numerator % _frac_obj_temp_3.denominator != 0:
                _whole_temp_3 = _frac_obj_temp_3.numerator // _frac_obj_temp_3.denominator
                _remainder_temp_3 = _frac_obj_temp_3.numerator % _frac_obj_temp_3.denominator
                _template_temp_3 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_3 = _template_temp_3.replace("{whole}", str(_whole_temp_3))\
                                                         .replace("{num}", str(_remainder_temp_3))\
                                                         .replace("{den}", str(_frac_obj_temp_3.denominator))
            else:
                _template_temp_3 = r"\frac{{num}}{{den}}"
                _display_string_temp_3 = _template_temp_3.replace("{num}", str(_frac_obj_temp_3.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_3.denominator))
            
            q_template = r"計算：${w} \times {f} = ?$"
            question_text = q_template.replace("{w}", str(whole_num))\
                                      .replace("{f}", _display_string_temp_3)

        elif sub_type == 2: # 帶分數乘分數
            whole_part = random.randint(1, 5)
            num_m = random.randint(1, 5)
            den_m = random.randint(num_m + 1, 10)
            while math.gcd(num_m, den_m) != 1 or den_m == 1:
                num_m = random.randint(1, 5)
                den_m = random.randint(num_m + 1, 10)
            mixed_frac = Fraction(whole_part * den_m + num_m, den_m)

            num_f = random.randint(1, 5)
            den_f = random.randint(num_f + 1, 10)
            while math.gcd(num_f, den_f) != 1 or den_f == 1:
                num_f = random.randint(1, 5)
                den_f = random.randint(num_f + 1, 10)
            frac = Fraction(num_f, den_f)
            
            correct_answer_frac = mixed_frac * frac
            
            # Inlining _fraction_to_display_string logic for mixed_frac
            _frac_obj_temp_4 = mixed_frac
            if _frac_obj_temp_4.denominator == 1:
                _display_string_temp_4 = str(_frac_obj_temp_4.numerator)
            elif _frac_obj_temp_4.numerator == 0:
                _display_string_temp_4 = "0"
            elif _frac_obj_temp_4.numerator > _frac_obj_temp_4.denominator and _frac_obj_temp_4.numerator % _frac_obj_temp_4.denominator != 0:
                _whole_temp_4 = _frac_obj_temp_4.numerator // _frac_obj_temp_4.denominator
                _remainder_temp_4 = _frac_obj_temp_4.numerator % _frac_obj_temp_4.denominator
                _template_temp_4 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_4 = _template_temp_4.replace("{whole}", str(_whole_temp_4))\
                                                         .replace("{num}", str(_remainder_temp_4))\
                                                         .replace("{den}", str(_frac_obj_temp_4.denominator))
            else:
                _template_temp_4 = r"\frac{{num}}{{den}}"
                _display_string_temp_4 = _template_temp_4.replace("{num}", str(_frac_obj_temp_4.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_4.denominator))
            
            # Inlining _fraction_to_display_string logic for frac
            _frac_obj_temp_5 = frac
            if _frac_obj_temp_5.denominator == 1:
                _display_string_temp_5 = str(_frac_obj_temp_5.numerator)
            elif _frac_obj_temp_5.numerator == 0:
                _display_string_temp_5 = "0"
            elif _frac_obj_temp_5.numerator > _frac_obj_temp_5.denominator and _frac_obj_temp_5.numerator % _frac_obj_temp_5.denominator != 0:
                _whole_temp_5 = _frac_obj_temp_5.numerator // _frac_obj_temp_5.denominator
                _remainder_temp_5 = _frac_obj_temp_5.numerator % _frac_obj_temp_5.denominator
                _template_temp_5 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_5 = _template_temp_5.replace("{whole}", str(_whole_temp_5))\
                                                         .replace("{num}", str(_remainder_temp_5))\
                                                         .replace("{den}", str(_frac_obj_temp_5.denominator))
            else:
                _template_temp_5 = r"\frac{{num}}{{den}}"
                _display_string_temp_5 = _template_temp_5.replace("{num}", str(_frac_obj_temp_5.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_5.denominator))

            q_template = r"計算：${mf} \times {f} = ?$"
            question_text = q_template.replace("{mf}", _display_string_temp_4)\
                                      .replace("{f}", _display_string_temp_5)

        elif sub_type == 3: # 帶分數乘整數
            whole_part = random.randint(1, 5)
            num_m = random.randint(1, 5)
            den_m = random.randint(num_m + 1, 10)
            while math.gcd(num_m, den_m) != 1 or den_m == 1:
                num_m = random.randint(1, 5)
                den_m = random.randint(num_m + 1, 10)
            mixed_frac = Fraction(whole_part * den_m + num_m, den_m)

            whole_num = random.randint(2, 10)
            
            correct_answer_frac = mixed_frac * Fraction(whole_num)
            
            # Inlining _fraction_to_display_string logic for mixed_frac
            _frac_obj_temp_6 = mixed_frac
            if _frac_obj_temp_6.denominator == 1:
                _display_string_temp_6 = str(_frac_obj_temp_6.numerator)
            elif _frac_obj_temp_6.numerator == 0:
                _display_string_temp_6 = "0"
            elif _frac_obj_temp_6.numerator > _frac_obj_temp_6.denominator and _frac_obj_temp_6.numerator % _frac_obj_temp_6.denominator != 0:
                _whole_temp_6 = _frac_obj_temp_6.numerator // _frac_obj_temp_6.denominator
                _remainder_temp_6 = _frac_obj_temp_6.numerator % _frac_obj_temp_6.denominator
                _template_temp_6 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_6 = _template_temp_6.replace("{whole}", str(_whole_temp_6))\
                                                         .replace("{num}", str(_remainder_temp_6))\
                                                         .replace("{den}", str(_frac_obj_temp_6.denominator))
            else:
                _template_temp_6 = r"\frac{{num}}{{den}}"
                _display_string_temp_6 = _template_temp_6.replace("{num}", str(_frac_obj_temp_6.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_6.denominator))

            q_template = r"計算：${mf} \times {w} = ?$"
            question_text = q_template.replace("{mf}", _display_string_temp_6)\
                                      .replace("{w}", str(whole_num))

    elif problem_type == 3:
        # 題型 3: 情境應用題 (文字應用題)
        # 範例：一本書有 X 頁，小明讀了其中的 (A/B)。請問小明讀了多少頁？
        
        context_type = random.choice([1, 2])
        
        if context_type == 1: # 書本頁數情境
            total_quantity = random.randint(30, 150) # 總頁數
            num = random.randint(1, 5)
            den = random.randint(num + 1, 10)
            while math.gcd(num, den) != 1 or den == 1:
                num = random.randint(1, 5)
                den = random.randint(num + 1, 10)
            fraction_of_quantity = Fraction(num, den)

            correct_answer_frac = Fraction(total_quantity) * fraction_of_quantity
            
            # Inlining _fraction_to_display_string logic for fraction_of_quantity
            _frac_obj_temp_7 = fraction_of_quantity
            if _frac_obj_temp_7.denominator == 1:
                _display_string_temp_7 = str(_frac_obj_temp_7.numerator)
            elif _frac_obj_temp_7.numerator == 0:
                _display_string_temp_7 = "0"
            elif _frac_obj_temp_7.numerator > _frac_obj_temp_7.denominator and _frac_obj_temp_7.numerator % _frac_obj_temp_7.denominator != 0:
                _whole_temp_7 = _frac_obj_temp_7.numerator // _frac_obj_temp_7.denominator
                _remainder_temp_7 = _frac_obj_temp_7.numerator % _frac_obj_temp_7.denominator
                _template_temp_7 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_7 = _template_temp_7.replace("{whole}", str(_whole_temp_7))\
                                                         .replace("{num}", str(_remainder_temp_7))\
                                                         .replace("{den}", str(_frac_obj_temp_7.denominator))
            else:
                _template_temp_7 = r"\frac{{num}}{{den}}"
                _display_string_temp_7 = _template_temp_7.replace("{num}", str(_frac_obj_temp_7.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_7.denominator))

            q_template = r"一本故事書有 {total} 頁，小明已經讀了其中的 ${frac}$。請問小明讀了多少頁？"
            question_text = q_template.replace("{total}", str(total_quantity))\
                                      .replace("{frac}", _display_string_temp_7)

        elif context_type == 2: # 容器容量情境
            total_quantity = random.randint(5, 20) # 總容量或重量
            unit = random.choice(["公升", "公斤", "公尺"])
            num = random.randint(1, 5)
            den = random.randint(num + 1, 10)
            while math.gcd(num, den) != 1 or den == 1:
                num = random.randint(1, 5)
                den = random.randint(num + 1, 10)
            fraction_of_quantity = Fraction(num, den)

            correct_answer_frac = Fraction(total_quantity) * fraction_of_quantity
            
            # Inlining _fraction_to_display_string logic for fraction_of_quantity
            _frac_obj_temp_8 = fraction_of_quantity
            if _frac_obj_temp_8.denominator == 1:
                _display_string_temp_8 = str(_frac_obj_temp_8.numerator)
            elif _frac_obj_temp_8.numerator == 0:
                _display_string_temp_8 = "0"
            elif _frac_obj_temp_8.numerator > _frac_obj_temp_8.denominator and _frac_obj_temp_8.numerator % _frac_obj_temp_8.denominator != 0:
                _whole_temp_8 = _frac_obj_temp_8.numerator // _frac_obj_temp_8.denominator
                _remainder_temp_8 = _frac_obj_temp_8.numerator % _frac_obj_temp_8.denominator
                _template_temp_8 = r"{whole}\frac{{num}}{{den}}"
                _display_string_temp_8 = _template_temp_8.replace("{whole}", str(_whole_temp_8))\
                                                         .replace("{num}", str(_remainder_temp_8))\
                                                         .replace("{den}", str(_frac_obj_temp_8.denominator))
            else:
                _template_temp_8 = r"\frac{{num}}{{den}}"
                _display_string_temp_8 = _template_temp_8.replace("{num}", str(_frac_obj_temp_8.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_8.denominator))

            q_template = r"一個水桶可以裝 {total} {unit} 的水。現在水桶裝了 ${frac}$ 滿。請問水桶裡有多少 {unit} 的水？"
            question_text = q_template.replace("{total}", str(total_quantity))\
                                      .replace("{unit}", unit)\
                                      .replace("{frac}", _display_string_temp_8)

    # 最終答案格式化
    # 'answer' 欄位為顯示給學生的答案字串 (可能包含帶分數或整數)
    # Inlining _fraction_to_display_string logic for correct_answer_frac for display_answer_str
    _frac_obj_temp_final_display = correct_answer_frac
    if _frac_obj_temp_final_display.denominator == 1:
        display_answer_str = str(_frac_obj_temp_final_display.numerator)
    elif _frac_obj_temp_final_display.numerator == 0:
        display_answer_str = "0"
    elif _frac_obj_temp_final_display.numerator > _frac_obj_temp_final_display.denominator and _frac_obj_temp_final_display.numerator % _frac_obj_temp_final_display.denominator != 0:
        _whole_temp_final_display = _frac_obj_temp_final_display.numerator // _frac_obj_temp_final_display.denominator
        _remainder_temp_final_display = _frac_obj_temp_final_display.numerator % _frac_obj_temp_final_display.denominator
        _template_temp_final_display = r"{whole}\frac{{num}}{{den}}"
        display_answer_str = _template_temp_final_display.replace("{whole}", str(_whole_temp_final_display))\
                                                         .replace("{num}", str(_remainder_temp_final_display))\
                                                         .replace("{den}", str(_frac_obj_temp_final_display.denominator))
    else:
        _template_temp_final_display = r"\frac{{num}}{{den}}"
        display_answer_str = _template_temp_final_display.replace("{num}", str(_frac_obj_temp_final_display.numerator))\
                                                         .replace("{den}", str(_frac_obj_temp_final_display.denominator))
    
    # 'correct_answer' 欄位為標準化、易於程式檢查的答案字串 (例如 "1/2" 或 "3")
    if correct_answer_frac.denominator == 1:
        canonical_correct_answer = str(correct_answer_frac.numerator)
    else:
        canonical_correct_answer = f"{correct_answer_frac.numerator}/{correct_answer_frac.denominator}"

    return {
        "question_text": question_text,
        "correct_answer": canonical_correct_answer,
        "answer": display_answer_str,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": 1
    }

# 頂層函式：檢查使用者答案

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
