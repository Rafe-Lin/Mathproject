# ==============================================================================
# ID: jh_數學1上_CommonDivisorAndGreatestCommonDivisor
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 48.76s | RAG: 5 examples
# Created At: 2026-01-14 19:01:05
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



import base64
from datetime import datetime
import json

# --- 輔助函式 (Helper Functions) ---

def _gcd(a, b):
    """計算兩個正整數的最大公因數 (Greatest Common Divisor)。"""
    # 確保輸入為正整數
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def _lcm(a, b):
    """計算兩個正整數的最小公倍數 (Least Common Multiple)。"""
    if a == 0 or b == 0:
        return 0
    # LCM(a, b) = |a*b| / GCD(a, b)
    return abs(a * b) // _gcd(a, b)

def _get_divisors(n):
    """回傳一個正整數 n 的所有正因數，並由小到大排序。"""
    if n <= 0:
        return []
    divs = set()
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return sorted(list(divs))

def _get_common_divisors(a, b):
    """回傳兩個正整數 a 和 b 的所有正公因數，並由小到大排序。"""
    if a <= 0 or b <= 0:
        return []
    divisors_a = set(_get_divisors(a))
    divisors_b = set(_get_divisors(b))
    return sorted(list(divisors_a.intersection(divisors_b)))

def _gcd_three(a, b, c):
    """計算三個正整數的最大公因數。"""
    return _gcd(_gcd(a, b), c)

def _lcm_three(a, b, c):
    """計算三個正整數的最小公倍數。"""
    return _lcm(_lcm(a, b), c)

# --- 題型生成函式 (Problem Generation Functions - Internal) ---

def _generate_variant_direct_calculation():
    """
    生成直接計算最大公因數、最小公倍數或公因數列表的題目。
    """
    problem_type = random.choice([
        "gcd_two", "lcm_two", "common_divisors_two",
        "gcd_three", "lcm_three"
    ])
    
    question_text = ""
    correct_ans_val = None
    answer_text = ""

    if problem_type == "gcd_two":
        num1 = random.randint(20, 100)
        num2 = random.randint(20, 100)
        # 確保數字不相同、不是倍數關係且最大公因數不為 1，以增加題目挑戰性
        while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or _gcd(num1, num2) == 1:
            num1 = random.randint(20, 100)
            num2 = random.randint(20, 100)
        
        correct_ans_val = _gcd(num1, num2)
        question_text_template = r"請找出 {num1} 和 {num2} 的最大公因數 (GCD)。"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2))
        answer_text = str(correct_ans_val)
        
    elif problem_type == "lcm_two":
        num1 = random.randint(10, 30)
        num2 = random.randint(10, 30)
        # 確保數字不相同、不是倍數關係且最小公倍數不大於 200
        while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or _lcm(num1, num2) > 200:
            num1 = random.randint(10, 30)
            num2 = random.randint(10, 30)
        
        correct_ans_val = _lcm(num1, num2)
        question_text_template = r"請找出 {num1} 和 {num2} 的最小公倍數 (LCM)。"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2))
        answer_text = str(correct_ans_val)

    elif problem_type == "common_divisors_two":
        num1 = random.randint(30, 80)
        num2 = random.randint(30, 80)
        # 確保數字不相同、不是倍數關係且至少有兩個公因數 (1 和另一個數)
        while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or len(_get_common_divisors(num1, num2)) < 2:
            num1 = random.randint(30, 80)
            num2 = random.randint(30, 80)
        
        correct_ans_val = _get_common_divisors(num1, num2) # 列表形式
        
        question_text_template = r"請列出 {num1} 和 {num2} 的所有公因數，並用逗號分隔，由小到大排列。"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2))
        answer_text = ", ".join(map(str, correct_ans_val))
        
    elif problem_type == "gcd_three":
        num1 = random.randint(15, 60)
        num2 = random.randint(15, 60)
        num3 = random.randint(15, 60)
        # 確保三個數字皆不相同且最大公因數不為 1
        while len(set([num1, num2, num3])) < 3 or _gcd_three(num1, num2, num3) == 1:
            num1 = random.randint(15, 60)
            num2 = random.randint(15, 60)
            num3 = random.randint(15, 60)
        
        correct_ans_val = _gcd_three(num1, num2, num3)
        question_text_template = r"請找出 {num1}、{num2} 和 {num3} 的最大公因數 (GCD)。"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2)).replace("{num3}", str(num3))
        answer_text = str(correct_ans_val)
        
    elif problem_type == "lcm_three":
        num1 = random.randint(5, 15)
        num2 = random.randint(5, 15)
        num3 = random.randint(5, 15)
        # 確保三個數字皆不相同且最小公倍數不大於 250
        while len(set([num1, num2, num3])) < 3 or _lcm_three(num1, num2, num3) > 250:
            num1 = random.randint(5, 15)
            num2 = random.randint(5, 15)
            num3 = random.randint(5, 15)
            
        correct_ans_val = _lcm_three(num1, num2, num3)
        question_text_template = r"請找出 {num1}、{num2} 和 {num3} 的最小公倍數 (LCM)。"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2)).replace("{num3}", str(num3))
        answer_text = str(correct_ans_val)

    return question_text, correct_ans_val, answer_text


def _generate_variant_word_problem_gcd():
    """
    生成需要應用最大公因數的應用問題。
    """
    scenario_type = random.choice(["distribute", "tile", "cut"])
    
    question_text = ""
    correct_ans_val = None
    answer_text = ""

    if scenario_type == "distribute":
        items1 = random.randint(30, 120)
        items2 = random.randint(30, 120)
        # 確保最大公因數大於 1，使問題有意義
        while _gcd(items1, items2) == 1:
            items1 = random.randint(30, 120)
            items2 = random.randint(30, 120)
        
        correct_ans_val = _gcd(items1, items2)
        item_name1 = random.choice(["蘋果", "橘子", "鉛筆", "橡皮擦"])
        item_name2 = random.choice(["香蕉", "梨子", "筆記本", "尺子"])
        while item_name1 == item_name2: # 確保物品名稱不同
            item_name2 = random.choice(["香蕉", "梨子", "筆記本", "尺子"])
            
        question_text_template = r"有一籃 {items1} 個{item_name1}和 {items2} 個{item_name2}。如果要把這些物品平均分給一群小朋友，每個小朋友分到的{item_name1}數量相同，{item_name2}數量也相同，請問最多可以分給多少個小朋友？"
        question_text = question_text_template.replace("{items1}", str(items1)).replace("{item_name1}", item_name1).replace("{items2}", str(items2)).replace("{item_name2}", item_name2)
        answer_text = str(correct_ans_val)
        
    elif scenario_type == "tile":
        length = random.randint(50, 150)
        width = random.randint(50, 150)
        # 確保最大公因數大於 1 且長寬不相等
        while _gcd(length, width) == 1 or length == width:
            length = random.randint(50, 150)
            width = random.randint(50, 150)
            
        correct_ans_val = _gcd(length, width)
        question_text_template = r"一塊長方形地磚長 {length} 公分，寬 {width} 公分。如果要用大小相同的正方形瓷磚鋪滿這塊地磚，且不能切割，請問最大的正方形瓷磚邊長是多少公分？"
        question_text = question_text_template.replace("{length}", str(length)).replace("{width}", str(width))
        answer_text = str(correct_ans_val)

    elif scenario_type == "cut":
        rope1 = random.randint(60, 180)
        rope2 = random.randint(60, 180)
        # 確保最大公因數大於 1 且繩長不相等
        while _gcd(rope1, rope2) == 1 or rope1 == rope2:
            rope1 = random.randint(60, 180)
            rope2 = random.randint(60, 180)
            
        correct_ans_val = _gcd(rope1, rope2)
        question_text_template = r"有兩條繩子，長度分別是 {rope1} 公分和 {rope2} 公分。現在要把這兩條繩子剪成等長的小段，且不能有剩餘，請問每小段最長可以是幾公分？"
        question_text = question_text_template.replace("{rope1}", str(rope1)).replace("{rope2}", str(rope2))
        answer_text = str(correct_ans_val)

    return question_text, correct_ans_val, answer_text


def _generate_variant_word_problem_lcm():
    """
    生成需要應用最小公倍數的應用問題。
    """
    scenario_type = random.choice(["meet", "cycle", "square"])
    
    question_text = ""
    correct_ans_val = None
    answer_text = ""

    if scenario_type == "meet":
        interval1 = random.randint(6, 15)
        interval2 = random.randint(6, 15)
        # 確保間隔時間不相同且最小公倍數不大於 100
        while interval1 == interval2 or _lcm(interval1, interval2) > 100:
            interval1 = random.randint(6, 15)
            interval2 = random.randint(6, 15)
        
        correct_ans_val = _lcm(interval1, interval2)
        question_text_template = r"甲公車每 {interval1} 分鐘發一班車，乙公車每 {interval2} 分鐘發一班車。如果兩班公車同時在上午 8:00 發車，請問下次兩班公車會同時發車是幾分鐘後？"
        question_text = question_text_template.replace("{interval1}", str(interval1)).replace("{interval2}", str(interval2))
        answer_text = str(correct_ans_val)
        
    elif scenario_type == "cycle":
        cycle1 = random.randint(4, 10)
        cycle2 = random.randint(4, 10)
        cycle3 = random.randint(4, 10)
        # 確保三個週期不相同且最小公倍數不大於 120
        while len(set([cycle1, cycle2, cycle3])) < 3 or _lcm_three(cycle1, cycle2, cycle3) > 120:
            cycle1 = random.randint(4, 10)
            cycle2 = random.randint(4, 10)
            cycle3 = random.randint(4, 10)
            
        correct_ans_val = _lcm_three(cycle1, cycle2, cycle3)
        question_text_template = r"小明每 {cycle1} 天去圖書館一次，小華每 {cycle2} 天去圖書館一次，小美每 {cycle3} 天去圖書館一次。如果他們三人今天同時去了圖書館，請問最少還要多少天，他們會再次同時去圖書館？"
        question_text = question_text_template.replace("{cycle1}", str(cycle1)).replace("{cycle2}", str(cycle2)).replace("{cycle3}", str(cycle3))
        answer_text = str(correct_ans_val)

    elif scenario_type == "square":
        length = random.randint(4, 12)
        width = random.randint(4, 12)
        # 確保長寬不相等
        while length == width:
            width = random.randint(4, 12)

        correct_ans_val = _lcm(length, width)
        question_text_template = r"用長 {length} 公分、寬 {width} 公分的長方形紙片，拼成一個最小的正方形。請問這個正方形的邊長是多少公分？"
        question_text = question_text_template.replace("{length}", str(length)).replace("{width}", str(width))
        answer_text = str(correct_ans_val)

    return question_text, correct_ans_val, answer_text


# --- 主要函式 (Main Functions) ---

def generate(level=1):
    """
    生成 K12 數學「公因數與最大公因數」技能的題目。
    
    Args:
        level (int): 難度等級 (目前用於區分題型，但未細化難度)。

    Returns:
        dict: 包含題目細節的字典。
    """
    problem_variants = [
        _generate_variant_direct_calculation,
        _generate_variant_word_problem_gcd,
        _generate_variant_word_problem_lcm,
    ]
    
    # 隨機選擇一種題型變體
    question_func = random.choice(problem_variants)
    question_text, correct_ans_val, answer_text = question_func()

    # 處理 correct_answer 欄位的序列化
    if isinstance(correct_ans_val, list):
        # 將列表答案轉換為 JSON 字串，以便 check 函式解析
        correct_answer_for_field = json.dumps(correct_ans_val)
    else:
        # 單一數值答案直接轉換為字串
        correct_answer_for_field = str(correct_ans_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_for_field,
        "answer": answer_text,
        "image_base64": "",  # 目前不生成圖像
        "created_at": datetime.now().isoformat(),
        "version": 1,
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
