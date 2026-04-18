# ==============================================================================
# ID: jh_數學1上_PowersOfTen
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 52.80s | RAG: 1 examples
# Created At: 2026-01-14 17:13:48
# Fix Status: [Repaired]
# Fixes: Regex=5, Logic=0
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
    u = str(user_answer).strip().replace(" ", "").replace("，", ",")
    
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

# --- Helper Functions (遵循通用規範) ---

def _format_number_with_commas(number):
    """
    格式化數字，加入千位分隔符號。
    若數字為整數型浮點數 (如 100.0)，則顯示為整數 (如 100)。
    """
    if isinstance(number, (int, float)) and number == int(number):
        return f"{int(number):,}"
    # 对于浮点数，默认的 f-string 格式化可能在某些情况下显示科学计数法，
    # 但对于 K12 场景，我们通常希望显示完整的数字。
    # 进一步处理以避免过长的小数部分或不必要的科学记号。
    if isinstance(number, float):
        # 尝试转换为整数，如果可以，则显示为整数
        if number.is_integer():
            return f"{int(number):,}"
        # 对于非整数浮点数，显示为标准浮点数，并移除不必要的尾随零
        # 使用 {:f} 强制非科学记号表示，然后移除尾随零
        formatted_str = f"{number:f}"
        if '.' in formatted_str:
            formatted_str = formatted_str.rstrip('0')
            if formatted_str.endswith('.'):
                formatted_str += '0' # Ensure "123." becomes "123.0"
        return formatted_str
    return f"{number:,}" # 此處 f-string 不包含 LaTeX 指令，故安全。

# --- 主要功能函式 ---

def generate(level=1):
    """
    為 K12 數學「10 的次方」技能生成一道題目。

    Args:
        level (int): 題目難度等級 (目前版本未充分利用，預設為 1)。

    Returns:
        dict: 包含題目文本、正確答案、顯示答案、圖片 (若有) 和時間戳記的字典。
    """
    # 根據題型多樣性，隨機選擇至少 3 種不同的題型變體
    problem_type = random.choice([
        "direct_calculation",           # 直接計算 10^n 或將數字轉為 10^n
        "inverse_solving",              # 逆向求解 n (已知 10^n 求 n)
        "operations_with_powers",       # 10 的次方的乘除運算
        "scientific_notation_conversion" # 科學記號與標準記號的轉換 (情境應用)
    ])

    question_text = ""
    correct_answer = None  # 用於系統檢查的精確答案 (通常為字符串)
    answer_display = ""    # 用於顯示給學生看的答案格式
    image_base64 = None    # 目前此技能不提供圖片

    if problem_type == "direct_calculation":
        # 題型變體 1: 直接計算 10^n 的值，或將數字表示為 10^n
        sub_type = random.choice(["power_to_number", "number_to_power"])
        
        if sub_type == "power_to_number":
            exponent = random.randint(2, 7) # 確保指數在 K12 範圍內
            value = 10 ** exponent
            
            # 使用嚴格的 replace 模板，避免 f-string 導致 LaTeX 衝突
            question_text = r"計算 $10^{{exp}}$ 的值。".replace("{exp}", str(exponent))
            correct_answer = str(value)
            answer_display = _format_number_with_commas(value)
        else: # number_to_power
            exponent = random.randint(2, 7)
            value = 10 ** exponent
            
            question_text = r"將 {num} 表示成 $10^n$ 的形式，其中 $n$ 是一個整數。".replace("{num}", _format_number_with_commas(value))
            correct_answer = str(exponent) # 答案是指數 n
            answer_display = r"$10^{{exp}}$".replace("{exp}", str(exponent))

    elif problem_type == "inverse_solving":
        # 題型變體 2: 逆向求解 (已知 10^n 求 n)
        exponent = random.randint(3, 8)
        value = 10 ** exponent
        
        question_text = r"如果 $10^n = {num}$，那麼 $n$ 的值是多少？".replace("{num}", _format_number_with_commas(value))
        correct_answer = str(exponent)
        answer_display = str(exponent)

    elif problem_type == "operations_with_powers":
        # 題型變體 3: 10 的次方的乘除運算
        op_type = random.choice(["multiply", "divide"])
        
        if op_type == "multiply":
            exp1 = random.randint(2, 6)
            exp2 = random.randint(1, 4)
            result_exp = exp1 + exp2
            question_text = r"計算 $10^{{exp1}} \times 10^{{exp2}}$ 的值。".replace("{exp1}", str(exp1)).replace("{exp2}", str(exp2))
            correct_answer = str(10 ** result_exp)
            answer_display = _format_number_with_commas(10 ** result_exp)
        else: # divide
            # 確保除法結果的指數為非負整數，避免 K12 初學時的負指數
            exp1 = random.randint(3, 7) # 確保 exp1 夠大以進行有意義的除法
            exp2 = random.randint(1, exp1) # exp2 可以等於 exp1，結果為 10^0 = 1
            result_exp = exp1 - exp2
            question_text = r"計算 $10^{{exp1}} \div 10^{{exp2}}$ 的值。".replace("{exp1}", str(exp1)).replace("{exp2}", str(exp2))
            correct_answer = str(10 ** result_exp)
            answer_display = _format_number_with_commas(10 ** result_exp)
        
    elif problem_type == "scientific_notation_conversion":
        # 題型變體 4: 科學記號與標準記號的轉換 (情境應用)
        sub_type = random.choice(["to_scientific", "from_scientific"])
        
        if sub_type == "to_scientific":
            coefficient_int = random.randint(1, 9)
            exponent_magnitude = random.randint(4, 8) # 指數的絕對值
            
            if random.random() < 0.5: # 生成大數字 (正指數)
                original_number = coefficient_int * (10 ** exponent_magnitude)
                correct_answer_n = exponent_magnitude
            else: # 生成小數字 (負指數)
                original_number = coefficient_int * (10 ** -exponent_magnitude)
                correct_answer_n = -exponent_magnitude
            
            # 格式化原始數字用於題目文本，避免其本身顯示為科學記號
            if original_number >= 1:
                num_for_question = _format_number_with_commas(original_number)
            else: # 小數字，如 0.000005
                # 强制显示为浮点数，并移除尾随零
                num_for_question = f"{original_number:f}".rstrip('0')
                if num_for_question.endswith('.'):
                    num_for_question += '0'
                if num_for_question == "-0.": # edge case for negative small numbers
                    num_for_question = "-0.0"

            question_text = r"將 {num} 表示成科學記號 $a \times 10^n$ 的形式，其中 $1 \le a < 10$。".replace("{num}", num_for_question)
            
            correct_answer_a = str(float(coefficient_int)) # 確保 'a' 為浮點數形式，如 "5.0"
            correct_answer = f"{correct_answer_a}e{correct_answer_n}" # 內部以 "aen" 格式儲存以利檢查
            answer_display = r"${a} \times 10^{{n}}$".replace("{a}", correct_answer_a).replace("{n}", str(correct_answer_n))

        else: # from_scientific
            coefficient = random.uniform(1.0, 9.9)
            coefficient = round(coefficient, 1) # 保留一位小數
            exponent = random.randint(-5, 7) # 指數範圍
            
            question_text = r"計算 ${a} \times 10^{{n}}$ 的值。".replace("{a}", str(coefficient)).replace("{n}", str(exponent))
            
            value = coefficient * (10 ** exponent)
            correct_answer = str(value) # 內部以標準數字字符串儲存以利檢查
            
            # 格式化 answer_display
            answer_display = _format_number_with_commas(value)


    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


# [Auto-Injected Patch v10.3.1] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝，並強制使用中文
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # 2. [V10.3 核心修復] 解決 r-string 導致的 \n 換行失效問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            
            # 3. 確保反饋訊息也是中文 (針對 AI 可能寫出的英文進行覆蓋)
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
