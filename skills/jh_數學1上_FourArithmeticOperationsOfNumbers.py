# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 84.66s | RAG: 4 examples
# Created At: 2026-01-14 19:03:52
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


import datetime

import base64 # 僅作為佔位符，此技能暫不生成圖像

# --- 輔助函式 (Helper Functions) ---

def _gcd(a, b):
    """計算兩個整數的最大公因數 (Greatest Common Divisor)。"""
    while b:
        a, b = b, a % b
    return a

def _simplify_fraction(n, d):
    """
    簡化分數 (n, d)。確保分母為正，且若分子為 0 則分母為 1。
    回傳 (簡化後的分子, 簡化後的分母)。
    """
    if d == 0:
        raise ZeroDivisionError("分母不能為零。")
    if n == 0:
        return (0, 1)
    common = _gcd(abs(n), abs(d))
    n //= common
    d //= common
    if d < 0: # 確保分母為正
        n = -n
        d = -d
    return (n, d)

def _to_fraction(num):
    """
    將數字轉換為分數形式的元組 (分子, 分母)。
    支援整數、浮點數和已是分數元組的輸入。
    """
    if isinstance(num, tuple) and len(num) == 2:
        return _simplify_fraction(num[0], num[1])
    elif isinstance(num, int):
        return (num, 1)
    elif isinstance(num, float):
        # 將浮點數轉換為分數，精確到小數點後 4 位
        precision = 10**4 
        n = int(round(num * precision))
        d = precision
        return _simplify_fraction(n, d)
    return num # 如果是其他類型，直接回傳

def _add(a, b):
    """執行分數加法。"""
    a_frac = _to_fraction(a)
    b_frac = _to_fraction(b)
    n1, d1 = a_frac
    n2, d2 = b_frac
    new_n = n1 * d2 + n2 * d1
    new_d = d1 * d2
    return _simplify_fraction(new_n, new_d)

def _subtract(a, b):
    """執行分數減法。"""
    a_frac = _to_fraction(a)
    b_frac = _to_fraction(b)
    n1, d1 = a_frac
    n2, d2 = b_frac
    new_n = n1 * d2 - n2 * d1
    new_d = d1 * d2
    return _simplify_fraction(new_n, new_d)

def _multiply(a, b):
    """執行分數乘法。"""
    a_frac = _to_fraction(a)
    b_frac = _to_fraction(b)
    n1, d1 = a_frac
    n2, d2 = b_frac
    new_n = n1 * n2
    new_d = d1 * d2
    return _simplify_fraction(new_n, new_d)

def _divide(a, b):
    """執行分數除法。"""
    a_frac = _to_fraction(a)
    b_frac = _to_fraction(b)
    n1, d1 = a_frac
    n2, d2 = b_frac
    
    if n2 == 0: # Check if numerator of divisor is zero
        raise ZeroDivisionError("除數不能為零。")
    
    new_n = n1 * d2
    new_d = d1 * n2
    return _simplify_fraction(new_n, new_d)

def _format_number_for_latex(num):
    """
    將數字格式化為 LaTeX 安全的字串。
    分數會使用 \frac，整數和浮點數直接轉字串。
    """
    if isinstance(num, tuple) and len(num) == 2: # (numerator, denominator)
        n, d = num
        if d == 1:
            return str(n)
        elif n == 0:
            return "0"
        else:
            # 確保負號在分子
            if d < 0:
                n = -n
                d = -d
            # 嚴格遵守 LaTeX Integrity (Regex=0) 規則
            return r"\frac{{{}}}{{{}}}".replace("{}", str(n), 1).replace("{}", str(d), 1)
    elif isinstance(num, float):
        # 如果是整數的浮點表示，則顯示為整數
        if num == int(num):
            return str(int(num))
        return str(round(num, 4)) # 顯示到小數點後 4 位
    return str(num)

def _convert_result_to_display_and_correct_answer(result):
    """
    將內部計算結果 (可能是分數元組) 轉換為顯示用的 'answer' 字串
    和用於後端驗證的 'correct_answer' 字串。
    'correct_answer' 統一為浮點數的字串表示，以確保比較的一致性。
    """
    if isinstance(result, tuple) and len(result) == 2:
        n, d = result
        if d == 1:
            return str(n), str(float(n)) # correct_answer as float string
        
        decimal_val = n / d
        # 嚴格遵守 LaTeX Integrity (Regex=0) 規則
        fraction_str = r"\frac{{{}}}{{{}}}".replace("{}", str(n), 1).replace("{}", str(d), 1)
        
        # 顯示答案可以是分數，但正確答案統一為浮點數字串
        return fraction_str, str(round(decimal_val, 8)) # 提高精度用於比較
    elif isinstance(result, float):
        return str(round(result, 4)), str(round(result, 8))
    return str(result), str(float(result)) # Ensure correct_answer is float string even for int

def _evaluate_expression_with_precedence(expression_sequence):
    """
    根據標準數學運算順序 (乘除優先於加減) 評估一個由數字和運算符組成的列表。
    如果發生除以零，則拋出 ZeroDivisionError。
    """
    # 第一遍：處理乘法和除法
    temp_parts = []
    i = 0
    while i < len(expression_sequence):
        part = expression_sequence[i]
        if part == '*':
            prev_num = temp_parts.pop()
            next_num = expression_sequence[i+1]
            temp_parts.append(_multiply(prev_num, next_num))
            i += 2
        elif part == '/':
            prev_num = temp_parts.pop()
            next_num = expression_sequence[i+1]
            temp_parts.append(_divide(prev_num, next_num)) # _divide 內部會處理 ZeroDivisionError
            i += 2
        else:
            temp_parts.append(part)
            i += 1

    # 第二遍：處理加法和減法
    if not temp_parts:
        raise ValueError("表達式序列在第一遍處理後為空。")
        
    result = temp_parts[0]
    i = 1
    while i < len(temp_parts):
        op = temp_parts[i]
        num = temp_parts[i+1]
        if op == '+':
            result = _add(result, num)
        elif op == '-':
            result = _subtract(result, num)
        i += 2
    return result

def _generate_simple_arithmetic_expression(level, allow_fractions=False, allow_decimals=False, allow_negative=False):
    """
    根據等級生成一個簡單的四則運算式及其結果，並遵守運算順序。
    回傳 (LaTeX 表達式字串, 結果值)。
    結果值可能是整數、浮點數或分數元組。
    """
    ops = ['+', '-', '*', '/']
    # 對於 K12 數學1上，將項數限制在 2 或 3，以保持可管理性
    num_terms = random.randint(2, min(3, 1 + level)) # 2 或 3 項

    expression_sequence = [] # 儲存原始數字和運算符，用於計算
    expression_latex_parts = [] # 儲存 LaTeX 格式化的數字和運算符，用於顯示

    # 生成第一個數字
    val = random.randint(1, 10 * level)
    if allow_negative and random.random() < 0.3:
        val *= -1
    if allow_decimals and random.random() < 0.4 and val != 0:
        val = round(val + random.uniform(-0.9, 0.9), random.randint(1,2))
    elif allow_fractions and random.random() < 0.4 and val != 0:
        denominator = random.choice([2, 3, 4, 5, 6, 8, 10])
        val = (val, denominator)
    expression_sequence.append(val)
    expression_latex_parts.append(_format_number_for_latex(val))

    for i in range(1, num_terms):
        op = random.choice(ops)
        
        # 生成下一個數字
        num_val = random.randint(1, 10 * level)
        if allow_negative and random.random() < 0.3:
            num_val *= -1
        if allow_decimals and random.random() < 0.4 and num_val != 0:
            num_val = round(num_val + random.uniform(-0.9, 0.9), random.randint(1,2))
        elif allow_fractions and random.random() < 0.4 and num_val != 0:
            denominator = random.choice([2, 3, 4, 5, 6, 8, 10])
            num_val = (num_val, denominator)
        
        # 避免除以零
        if op == '/':
            if (isinstance(num_val, (int, float)) and num_val == 0) or \
               (isinstance(num_val, tuple) and num_val[0] == 0):
                # 重新生成一個非零數字
                num_val = random.randint(1, 10 * level)
                if allow_decimals and random.random() < 0.4:
                    num_val = round(num_val + random.uniform(-0.9, 0.9), random.randint(1,2))
                elif allow_fractions and random.random() < 0.4:
                    denominator = random.choice([2, 3, 4, 5, 6, 8, 10])
                    num_val = (num_val, denominator)

        expression_sequence.append(op)
        expression_sequence.append(num_val)
        
        expression_latex_parts.append(op)
        expression_latex_parts.append(_format_number_for_latex(num_val))

    # 評估表達式並遵守運算符優先順序
    try:
        result_val = _evaluate_expression_with_precedence(expression_sequence)
    except ZeroDivisionError:
        # 如果在評估過程中發生除以零，重新生成
        return _generate_simple_arithmetic_expression(level, allow_fractions, allow_decimals, allow_negative)
    except ValueError: # 捕獲 _evaluate_expression_with_precedence 可能拋出的空序列錯誤
        return _generate_simple_arithmetic_expression(level, allow_fractions, allow_decimals, allow_negative)

    expression_str = " ".join(expression_latex_parts)

    # 可選：為 K12 增加括號以提高清晰度，特別是當加減法後跟乘除法時。
    # 例如：A + B * C 變成 A + (B * C)
    if level >= 2 and num_terms == 3: # 僅限 A op1 B op2 C 類型的表達式
        op1 = expression_sequence[1]
        op2 = expression_sequence[3]
        
        if (op1 in ['+', '-'] and op2 in ['*', '/']):
            # 原始：num1 op1 num2 op2 num3
            # 期望：num1 op1 (num2 op2 num3)
            # 重新構建帶括號的 LaTeX 字串
            num2_latex = expression_latex_parts[2]
            op2_latex = expression_latex_parts[3]
            num3_latex = expression_latex_parts[4]
            
            expression_str = f"{expression_latex_parts[0]} {expression_latex_parts[1]} ({num2_latex} {op2_latex} {num3_latex})"

    return expression_str, result_val


# --- 主要函式 (Main Functions) ---

def generate(level=1):
    """
    生成一個 K12 數學「數的四則運算」題目。
    根據 level 調整題目難度。
    """
    # 確保 level 至少為 1
    level = max(1, level)
    
    problem_type = random.choice(['direct_calculation', 'missing_number', 'word_problem'])
    
    question_text = ""
    correct_answer = ""
    answer_display = "" 
    image_base64 = None

    # 為生成有效問題設置重試機制
    max_retries = 5
    for _ in range(max_retries):
        try:
            if problem_type == 'direct_calculation':
                # 題型變體 1: 直接計算
                allow_fractions = level >= 2
                allow_decimals = level >= 2
                allow_negative = level >= 1

                expression_str, result_val = _generate_simple_arithmetic_expression(
                    level, allow_fractions=allow_fractions, allow_decimals=allow_decimals, allow_negative=allow_negative
                )
                
                # 嚴格遵守 LaTeX 格式化規範
                question_text_template = r"計算：${expr}$"
                question_text = question_text_template.format(expr=expression_str)
                
                answer_display, correct_answer = _convert_result_to_display_and_correct_answer(result_val)
                break # 成功生成，跳出重試循環
            
            elif problem_type == 'missing_number':
                # 題型變體 2: 逆向求解 (尋找未知數 x)
                ops = ['+', '-', '*', '/']
                op1 = random.choice(ops)
                
                # 使用原始數字進行初始生成，然後轉換為分數進行計算
                a_val_raw = random.randint(1, 15 * level)
                x_val_raw = random.randint(1, 15 * level)
                
                # 確保 a_val 不為 0，特別是對於乘法/除法
                if op1 in ['*', '/'] and a_val_raw == 0:
                    a_val_raw = random.randint(1, 15 * level)
                if x_val_raw == 0: # x_val 也不能為 0，特別是作為除數
                    x_val_raw = random.randint(1, 15 * level)

                # 對於除法，如果不是分數/小數題，盡量讓結果「好看」
                if op1 == '/':
                    if random.random() < 0.7: # 大部分情況下，讓 a_val 成為 x_val_raw 的倍數
                        a_val_raw = x_val_raw * random.randint(1, 5) 
                        if a_val_raw == 0: a_val_raw = x_val_raw * random.randint(1,5) # 避免 0 * X = 0
                    # 否則，它可能會產生分數/小數結果
                
                a_val = _to_fraction(a_val_raw)
                x_val = _to_fraction(x_val_raw)

                # 計算 B (等式右側的值)
                b_val = None
                if op1 == '+': b_val = _add(a_val, x_val)
                elif op1 == '-': b_val = _subtract(a_val, x_val)
                elif op1 == '*': b_val = _multiply(a_val, x_val)
                elif op1 == '/': b_val = _divide(a_val, x_val) # _divide 會拋出 ZeroDivisionError

                b_val_display, _ = _convert_result_to_display_and_correct_answer(b_val)

                # 嚴格遵守 LaTeX 格式化規範
                question_text_template = r"如果 ${a} {op} x = {b}$，請問 $x$ 是多少？"
                question_text = question_text_template.format(
                    a=_format_number_for_latex(a_val),
                    op=op1,
                    b=b_val_display
                )
                
                answer_display, correct_answer = _convert_result_to_display_and_correct_answer(x_val)
                break # 成功生成，跳出重試循環

            elif problem_type == 'word_problem':
                # 題型變體 3: 情境應用 (文字題)
                scenario_type = random.choice(['money_calculation', 'distance_time_simple', 'item_sharing_combined'])

                if scenario_type == 'money_calculation':
                    initial_money = random.randint(5, 20) * 100 # 500 到 2000
                    item_price1 = random.randint(10, 50)
                    num_items1 = random.randint(2, 5)
                    item_price2 = random.randint(5, 30)
                    num_items2 = random.randint(1, 3)

                    total_spent = _add(_multiply(item_price1, num_items1), _multiply(item_price2, num_items2))
                    remaining_money = _subtract(initial_money, total_spent)
                    
                    # 確保結果不會是負數 (如果 initial_money 不夠，重新生成)
                    if _to_fraction(remaining_money)[0] < 0:
                        continue # 重試此題型
                    
                    question_text_template = r"小明有 ${initial_money}$ 元。他買了 ${num_items1}$ 支筆，每支 ${item_price1}$ 元；又買了 ${num_items2}$ 個橡皮擦，每個 ${item_price2}$ 元。請問小明還剩下多少元？"
                    question_text = question_text_template.format(
                        initial_money=str(initial_money),
                        num_items1=str(num_items1),
                        item_price1=str(item_price1),
                        num_items2=str(num_items2),
                        item_price2=str(item_price2)
                    )
                    
                    answer_display, correct_answer = _convert_result_to_display_and_correct_answer(remaining_money)
                    break # 成功生成，跳出重試循環
                
                elif scenario_type == 'distance_time_simple':
                    speed = random.randint(10, 50) # 公里/小時
                    time_hours = random.randint(2, 6) # 小時
                    distance = _multiply(speed, time_hours)
                    
                    # 增加一個回程或第二段路程的變體
                    if level >= 2 and random.random() < 0.5:
                        speed2 = random.randint(10, 50)
                        time_hours2 = random.randint(1, 4)
                        distance2 = _multiply(speed2, time_hours2)
                        total_distance = _add(distance, distance2)

                        question_text_template = r"一輛車先以 ${speed1}$ 公里/小時的速度行駛了 ${time1}$ 小時，然後又以 ${speed2}$ 公里/小時的速度行駛了 ${time2}$ 小時。請問這輛車總共行駛了多少公里？"
                        question_text = question_text_template.format(
                            speed1=str(speed),
                            time1=str(time_hours),
                            speed2=str(speed2),
                            time2=str(time_hours2)
                        )
                        answer_display, correct_answer = _convert_result_to_display_and_correct_answer(total_distance)
                    else:
                        question_text_template = r"一輛車以 ${speed}$ 公里/小時的速度行駛了 ${time}$ 小時。請問這輛車總共行駛了多少公里？"
                        question_text = question_text_template.format(
                            speed=str(speed),
                            time=str(time_hours)
                        )
                        answer_display, correct_answer = _convert_result_to_display_and_correct_answer(distance)
                    break # 成功生成，跳出重試循環

                elif scenario_type == 'item_sharing_combined':
                    total_items_initial = random.randint(50, 200)
                    boxes_of_items = random.randint(5, 15)
                    items_per_box = random.randint(5, 15)
                    num_people = random.randint(3, 10)
                    
                    total_items_generated = _add(total_items_initial, _multiply(boxes_of_items, items_per_box))
                    
                    # 確保總數可被均分，結果為整數，更符合 K12 應用題
                    items_for_each_frac = _divide(total_items_generated, num_people)
                    if items_for_each_frac[1] != 1: # 如果不是整數，重新生成
                        continue # 重試此題型
                    
                    items_for_each = items_for_each_frac[0] # 取整數部分

                    question_text_template = r"倉庫裡有 ${total_items_initial}$ 個蘋果，又運來了 ${boxes}$ 箱蘋果，每箱有 ${items_per_box}$ 個。現在要把所有蘋果平均分給 ${people}$ 個人，每個人可以分到多少個蘋果？"
                    question_text = question_text_template.format(
                        total_items_initial=str(total_items_initial),
                        boxes=str(boxes_of_items),
                        items_per_box=str(items_per_box),
                        people=str(num_people)
                    )
                    
                    answer_display, correct_answer = _convert_result_to_display_and_correct_answer(items_for_each)
                    break # 成功生成，跳出重試循環
        
        except ZeroDivisionError:
            # 如果發生除以零，重試不同的問題類型或數字
            problem_type = random.choice(['direct_calculation', 'missing_number', 'word_problem']) # 嘗試不同類型
            continue # 繼續循環以重試
        except Exception: # 捕獲生成過程中可能發生的其他意外錯誤
            problem_type = random.choice(['direct_calculation', 'missing_number', 'word_problem']) # 嘗試不同類型
            continue # 繼續循環以重試
    else: # 如果循環在未成功生成問題的情況下完成，表示達到最大重試次數
        # 作為備用，生成一個非常簡單的問題
        question_text = r"計算：$1 + 1$"
        answer_display = "2"
        correct_answer = "2.0"

    # 返回固定欄位的字典
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, 
        "image_base64": image_base64, # 此技能不生成圖片
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0", 
    }

# 根據基礎設施規則，嚴禁自定義 check() 函式，因此此處不提供。
# 系統將自動注入 V10.6 鎖死版工具庫。

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
