# ==============================================================================
# ID: jh_數學1上_CommonDivisibilityRules
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 25.99s | RAG: 5 examples
# Created At: 2026-01-14 20:04:38
# Fix Status: [Repaired]
# Fixes: Regex=12, Logic=0
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

import base64 # Required for image_base64, though it will be an empty string for this skill

# --- 輔助函式 (Helper Functions) ---
# 這些函式設計為不依賴全域狀態，並明確回傳結果。
# 函式名稱以底線開頭表示它們是模組內部使用的輔助函式。

def _get_digits(n_str: str) -> list[int]:
    """
    從數字字串中提取所有數字並以整數列表回傳，忽略非數字字元。
    範例: "_123*" -> [1, 2, 3]
    """
    return [int(d) for d in n_str if d.isdigit()]

def _is_divisible_by_2(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 2 整除。
    依據：個位數字是偶數 (0, 2, 4, 6, 8)。
    """
    if not n_str or not n_str[-1].isdigit():
        return False # 若個位數未知，則無法判斷
    return int(n_str[-1]) % 2 == 0

def _is_divisible_by_3(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 3 整除。
    依據：所有位數之和能被 3 整除。
    """
    digits = _get_digits(n_str)
    if not digits: return False
    return sum(digits) % 3 == 0

def _is_divisible_by_4(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 4 整除。
    依據：末兩位數字組成的數能被 4 整除。
    """
    if len(n_str) < 2 or not n_str[-2:].isdigit():
        return False # 若末兩位數未知，則無法判斷
    try:
        return int(n_str[-2:]) % 4 == 0
    except ValueError: # 以防萬一，儘管 isdigit() 檢查應能避免
        return False
def _is_divisible_by_5(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 5 整除。
    依據：個位數字是 0 或 5。
    """
    if not n_str or not n_str[-1].isdigit():
        return False
    return int(n_str[-1]) % 5 == 0

def _is_divisible_by_6(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 6 整除。
    依據：同時能被 2 和 3 整除。
    """
    return _is_divisible_by_2(n_str) and _is_divisible_by_3(n_str)

def _is_divisible_by_9(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 9 整除。
    依據：所有位數之和能被 9 整除。
    """
    digits = _get_digits(n_str)
    if not digits: return False
    return sum(digits) % 9 == 0

def _is_divisible_by_10(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 10 整除。
    依據：個位數字是 0。
    """
    if not n_str or not n_str[-1].isdigit():
        return False
    return int(n_str[-1]) == 0

def _is_divisible_by_11(n_str: str) -> bool:
    """
    判斷一個數字字串是否能被 11 整除。
    依據：奇數位數字之和與偶數位數字之和的差能被 11 整除 (從右邊數起)。
    範例: abcde -> (e + c + a) - (d + b) 能被 11 整除。
    """
    digits = _get_digits(n_str)
    if not digits: return False
    alternating_sum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 0: # 從右邊數起第1, 3, 5...位 (0-indexed: 0, 2, 4...)
            alternating_sum += digit
        else: # 從右邊數起第2, 4, 6...位 (0-indexed: 1, 3, 5...)
            alternating_sum -= digit
    return alternating_sum % 11 == 0

# 將判別函式映射到對應的除數，方便隨機選取和呼叫
DIVISIBILITY_CHECKS = {
    2: _is_divisible_by_2,
    3: _is_divisible_by_3,
    4: _is_divisible_by_4,
    5: _is_divisible_by_5,
    6: _is_divisible_by_6,
    9: _is_divisible_by_9,
    10: _is_divisible_by_10,
    11: _is_divisible_by_11,
}

# --- 頂層函式 (Top-level Functions) ---
# 嚴禁使用 class 封裝，必須直接定義於模組最外層。

def generate(level: int = 1) -> dict:
    """
    根據 K12 數學「常用倍數判別法」生成一道題目。
    根據 level 參數調整題目難度，並確保題型多樣性及排版規範。
    """
    problem_type = random.choice([0, 1, 2]) # 0: 直接判斷, 1: 填空題 (缺失數字), 2: 多重條件/最大最小值
    question_text = ""
    correct_answer = ""
    
    # 可用的除數列表，根據 level 調整難度
    possible_divisors_base = [2, 3, 4, 5, 6, 9, 10]
    if level >= 2:
        possible_divisors_base.append(11) # 等級 2 及以上加入 11 的判別法

    if problem_type == 0: # 題型 0: 直接判斷 (Direct Check)
        num_digits = random.randint(3, 5) # 生成 3 到 5 位數
        num = random.randint(10**(num_digits-1), 10**num_digits - 1)
        
        divisor = random.choice(possible_divisors_base)
        
        is_divisible = DIVISIBILITY_CHECKS[divisor](str(num))
        
        question_text = f"數字 {num} 能被 {divisor} 整除嗎？請回答「是」或「否」。"
        correct_answer = "是" if is_divisible else "否"

    elif problem_type == 1: # 題型 1: 填空題 (Missing Digit)
        num_digits = random.randint(3, 5)
        
        # 確保生成的數字至少有一解
        max_attempts = 50
        found_valid_base_num = False
        divisor = random.choice(possible_divisors_base)
        
        num_list = [] # Will hold the chosen number with one digit to be masked
        missing_idx = -1 # Index of the digit to be masked
        
        for _ in range(max_attempts):
            temp_num_list_base = [str(random.randint(0, 9)) for _ in range(num_digits)]
            # 確保首位不為 0 (除非是單位數)
            if num_digits > 1 and temp_num_list_base[0] == '0':
                temp_num_list_base[0] = str(random.randint(1, 9))
            
            # 隨機選擇一個位置作為缺失數字
            current_missing_idx = random.randint(0, num_digits - 1)
            
            # 嘗試用 0-9 替換，看是否能滿足條件
            candidate_digits_for_mask = []
            for d in range(10):
                test_list = list(temp_num_list_base) # 複製一份
                test_list[current_missing_idx] = str(d)
                # 再次檢查首位不為 0 的規則
                if current_missing_idx == 0 and d == 0 and num_digits > 1:
                    continue
                
                if DIVISIBILITY_CHECKS[divisor]("".join(test_list)):
                    candidate_digits_for_mask.append(str(d))
            
            if candidate_digits_for_mask: # 找到了至少一個解
                num_list = temp_num_list_base
                missing_idx = current_missing_idx
                found_valid_base_num = True
                break
        
        if not found_valid_base_num: # 如果多次嘗試都未能找到有解的數字，則生成一個簡單的題目作為備用
            # 這種情況在設計良好的題庫中不應發生，但為系統健壯性考慮
            num_str_with_star = "1*2"
            divisor = 3
            correct_answer = "2,5,8"
            question_text = f"在數字 {num_str_with_star} 中，用哪個數字替換 `*` 可以使其被 {divisor} 整除？(若有多個答案，請從小到大依序填寫，並用逗號分隔)"
        else:
            # 遮蔽掉一個數字
            num_list[missing_idx] = '*'
            num_str_with_star = "".join(num_list)
            
            # 重新計算所有可能的答案 (因為原始數字可能有多個解)
            possible_answers = []
            for d in range(10):
                temp_num_list = list(num_str_with_star)
                temp_num_list[missing_idx] = str(d)
                
                if missing_idx == 0 and d == 0 and num_digits > 1:
                    continue
                    
                test_num_str = "".join(temp_num_list)
                if DIVISIBILITY_CHECKS[divisor](test_num_str):
                    possible_answers.append(str(d))
            
            possible_answers.sort() # 答案從小到大排序
            correct_answer = ",".join(possible_answers)
            
            question_text = f"在數字 {num_str_with_star} 中，用哪個數字替換 `*` 可以使其被 {divisor} 整除？(若有多個答案，請從小到大依序填寫，並用逗號分隔)"

    else: # problem_type == 2: 題型 2: 多重條件 / 最大最小值
        num_digits = random.randint(3, 4) # 生成 3 或 4 位數
        min_val = 10**(num_digits-1)
        max_val = 10**num_digits - 1
        
        # 選擇 2 或 3 個除數
        num_divisors_to_choose = random.choice([2, 3])
        chosen_divisors = random.sample(possible_divisors_base, num_divisors_to_choose)
        
        find_type = random.choice(["smallest", "largest"]) # 找最小或最大
        
        found_number = None
        if find_type == "smallest":
            for i in range(min_val, max_val + 1):
                is_valid = True
                for d in chosen_divisors:
                    if not DIVISIBILITY_CHECKS[d](str(i)):
                        is_valid = False
                        break
                if is_valid:
                    found_number = i
                    break # 找到最小的就停止
        else: # largest
            for i in range(max_val, min_val - 1, -1):
                is_valid = True
                for d in chosen_divisors:
                    if not DIVISIBILITY_CHECKS[d](str(i)):
                        is_valid = False
                        break
                if is_valid:
                    found_number = i
                    break # 找到最大的就停止
        
        if found_number is None: # 如果在範圍內沒有找到符合條件的數字 (極少發生)
            # 確保至少能有一個題目可以正常生成，即使是作為備用
            # 這裡可以生成一個保證有解的簡單組合
            # 例如，找最小的3位數同時能被2和3整除 (即被6整除)，答案是102
            if find_type == "smallest":
                found_number = 102 # 最小的3位數能被2和3整除
                divisors_text = "2、3"
                question_text = f"找出最小的 3 位數，它同時能被 {divisors_text} 整除。"
                correct_answer = str(found_number)
            else: # largest
                found_number = 996 # 最大的3位數能被2和3整除
                divisors_text = "2、3"
                question_text = f"找出最大的 3 位數，它同時能被 {divisors_text} 整除。"
                correct_answer = str(found_number)
        else:
            correct_answer = str(found_number)
            
            divisors_text = "、".join([str(d) for d in chosen_divisors])
            
            if find_type == "smallest":
                question_text = f"找出最小的 {num_digits} 位數，它同時能被 {divisors_text} 整除。"
            else:
                question_text = f"找出最大的 {num_digits} 位數，它同時能被 {divisors_text} 整除。"

    # 返回符合規範的字典
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 學生通常直接填寫正確答案
        "image_base64": "", # 此技能無需圖片，回傳空字串
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0", # 系統會自動維護版本號，這裡提供初始值
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
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['question_text'] += "\\\n(請在手寫區作答!)"

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
