# ==============================================================================
# ID: jh_數學1上_FactorsAndMultiples
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 40.85s | RAG: 4 examples
# Created At: 2026-01-14 19:49:47
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



import json
from datetime import datetime
import base64 # 雖然目前沒有視覺化需求，但依規範引入

# --- 輔助函式通用規範 (Generic Helper Functions) ---

def _get_factors(n):
    """
    輔助函式：回傳一個數字 n 的所有因數，並由小到大排序。
    若 n 為非正整數，則回傳空列表。
    """
    if not isinstance(n, int) or n <= 0:
        return []
    factors = set()
    # 只需要檢查到平方根，因為因數總是成對出現
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def _get_multiples_in_range(n, start, end):
    """
    輔助函式：回傳數字 n 在指定範圍 [start, end] 內的所有倍數，並由小到大排序。
    若 n 為非正整數或範圍無效，則回傳空列表。
    """
    if not isinstance(n, int) or n <= 0 or start > end:
        return []
    multiples = []
    
    # 找到第一個大於或等於 start 的 n 的倍數
    # 此計算方式對於正數 start 和 n 而言，能確保 first_multiple >= start 且為 n 的倍數
    first_multiple = ((start + n - 1) // n) * n
    
    # 原始規範中包含此段邏輯，為確保完全符合規範，保留此處。
    # 儘管對於正數範圍，上方的計算通常已足夠。
    if first_multiple < start:
        first_multiple = start if start % n == 0 else (((start // n) + 1) * n)
        
    for i in range(first_multiple, end + 1, n):
        multiples.append(i)
    return sorted(multiples)

def _is_factor(a, b):
    """
    輔助函式：判斷 a 是否為 b 的因數。
    """
    return b % a == 0 if a != 0 else False

def _is_multiple(a, b):
    """
    輔助函式：判斷 a 是否為 b 的倍數。
    """
    return a % b == 0 if b != 0 else False

def _get_gcd(a, b):
    """
    輔助函式：計算兩個數字的最大公因數 (Greatest Common Divisor)。
    """
    return math.gcd(a, b)

def _get_lcm(a, b):
    """
    輔助函式：計算兩個數字的最小公倍數 (Least Common Multiple)。
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

# --- 頂層函式 (Top-level Functions) ---

def generate(level=1):
    """
    生成 K12 數學「因數與倍數」的題目。
    根據 level 調整數字範圍和題目複雜度。
    """
    problem_types = [
        "find_factors",             # 找出所有因數
        "find_multiples_in_range",  # 找出範圍內的倍數
        "identify_relationship",    # 判斷因數/倍數關係
        "word_problem_lcm",         # 應用題：最小公倍數情境
        "word_problem_gcd"          # 應用題：最大公因數情境
    ]
    problem_type = random.choice(problem_types)

    question_text = ""
    correct_answer_raw = ""  # 用於系統檢查的原始答案
    display_answer = ""      # 用於使用者顯示的答案
    image_base64 = None      # 本技能暫無視覺化需求

    if problem_type == "find_factors":
        num = random.randint(24, 120) if level == 1 else random.randint(100, 200)
        factors = _get_factors(num)
        
        # 排版與 LaTeX 安全：嚴格使用 replace 模板
        q_temp = r"找出數字 ${N}$ 的所有因數，並以半形逗號分隔，由小到大排列。"
        question_text = q_temp.replace("{N}", str(num))
        
        correct_answer_raw = json.dumps(factors) # 將列表轉為 JSON 字串儲存
        display_answer = ", ".join(map(str, factors))

    elif problem_type == "find_multiples_in_range":
        num = random.randint(5, 20) if level == 1 else random.randint(15, 30)
        start_range = random.randint(50, 100) if level == 1 else random.randint(100, 200)
        end_range = random.randint(150, 250) if level == 1 else random.randint(250, 400)
        
        # 確保範圍有效且為正數
        if start_range >= end_range:
            temp_start = end_range - random.randint(10,30)
            temp_end = start_range + random.randint(10,30)
            start_range = max(1, temp_start) # 確保起始範圍至少為 1
            end_range = temp_end
            if start_range >= end_range: # 若調整後仍無效，提供一個預設安全範圍
                start_range, end_range = 1, random.randint(50, 100)
                
        multiples = _get_multiples_in_range(num, start_range, end_range)
        
        # 排版與 LaTeX 安全：嚴格使用 replace 模板
        q_temp = r"找出介於 ${S}$ 和 ${E}$ 之間（包含 ${S}$ 和 ${E}$），且是 ${N}$ 的倍數的所有數字，並以半形逗號分隔，由小到大排列。"
        question_text = q_temp.replace("{S}", str(start_range)).replace("{E}", str(end_range)).replace("{N}", str(num))
        
        correct_answer_raw = json.dumps(multiples) # 將列表轉為 JSON 字串儲存
        display_answer = ", ".join(map(str, multiples))

    elif problem_type == "identify_relationship":
        is_true_case = random.choice([True, False])
        if is_true_case:
            # A 是 B 的因數
            a = random.randint(2, 15) if level == 1 else random.randint(5, 25)
            multiplier = random.randint(3, 10) if level == 1 else random.randint(5, 15)
            b = a * multiplier
        else:
            # A 不是 B 的因數
            a = random.randint(2, 15) if level == 1 else random.randint(5, 25)
            b = random.randint(30, 150) if level == 1 else random.randint(100, 300)
            # 確保 b 不是 a 的倍數
            while b % a == 0:
                b = random.randint(30, 150) if level == 1 else random.randint(100, 300)
        
        # 排版與 LaTeX 安全：嚴格使用 replace 模板
        q_temp = r"判斷 ${A}$ 是否為 ${B}$ 的因數？請回答「是」或「否」。"
        question_text = q_temp.replace("{A}", str(a)).replace("{B}", str(b))
        
        correct_answer_raw = "是" if _is_factor(a, b) else "否"
        display_answer = correct_answer_raw

    elif problem_type == "word_problem_lcm":
        num1 = random.randint(4, 15) if level == 1 else random.randint(8, 20)
        num2 = random.randint(4, 15) if level == 1 else random.randint(8, 20)
        while num1 == num2: # 確保兩個數字不同
            num2 = random.randint(4, 15) if level == 1 else random.randint(8, 20)
        
        lcm_val = _get_lcm(num1, num2)
        
        # 排版與 LaTeX 安全：嚴格使用 replace 模板
        q_temp = r"小明每 ${N1}$ 天會去圖書館一次，小華每 ${N2}$ 天會去圖書館一次。如果他們今天同時去了圖書館，請問最快要再過幾天，他們才會再次同時去圖書館？"
        question_text = q_temp.replace("{N1}", str(num1)).replace("{N2}", str(num2))
        
        correct_answer_raw = str(lcm_val)
        display_answer = str(lcm_val)

    elif problem_type == "word_problem_gcd":
        num1 = random.randint(30, 80) if level == 1 else random.randint(60, 150)
        num2 = random.randint(30, 80) if level == 1 else random.randint(60, 150)
        # 確保數字不同且彼此不為倍數關係，以增加題目的普遍性，並確保數字非零
        while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or num1 == 0 or num2 == 0:
            num2 = random.randint(30, 80) if level == 1 else random.randint(60, 150)
        
        gcd_val = _get_gcd(num1, num2)
        
        # 排版與 LaTeX 安全：嚴格使用 replace 模板
        q_temp = r"有 ${N1}$ 顆蘋果和 ${N2}$ 顆橘子，想將它們分裝成數個禮物籃。每個禮物籃裡的蘋果數量要相同，橘子數量也要相同。請問最多可以分裝成幾個禮物籃？"
        question_text = q_temp.replace("{N1}", str(num1)).replace("{N2}", str(num2))
        
        correct_answer_raw = str(gcd_val)
        display_answer = str(gcd_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_raw, # 用於自動檢查的標準格式答案
        "answer": display_answer,             # 用於顯示給使用者的答案
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
