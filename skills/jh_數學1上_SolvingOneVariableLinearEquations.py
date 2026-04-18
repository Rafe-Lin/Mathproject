# ==============================================================================
# ID: jh_數學1上_SolvingOneVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 43.35s | RAG: 5 examples
# Created At: 2026-01-14 21:06:38
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
import base64 # Required by spec, even if image_base64 is an empty string for this skill.

# --- Helper Functions (符合通用規範：明確回傳、類型一致、防洩漏原則) ---

def _generate_random_int(min_val, max_val, exclude_zero=False):
    """
    生成指定範圍內的隨機整數，可選擇排除零。
    返回值: int
    """
    num = random.randint(min_val, max_val)
    if exclude_zero and num == 0:
        # 遞迴呼叫直到產生非零數
        return _generate_random_int(min_val, max_val, exclude_zero)
    return num

def _format_variable_term(coeff, var_name='x'):
    """
    格式化變數項 (例如: '3x', '-x', 'x', '' (如果係數為0))。
    返回值: str
    """
    if coeff == 1:
        return var_name
    elif coeff == -1:
        return "-" + var_name
    elif coeff == 0:
        return "" # 係數為0時不顯示變數項
    else:
        return str(coeff) + var_name

def _format_constant_term(const):
    """
    格式化常數項，若為正數則包含 '+' 號 (例如: '+5', '-3', '0')。
    返回值: str
    """
    if const >= 0:
        return "+" + str(const)
    else:
        return str(const) # 負號已包含

# --- 題型變體實作 (符合題型多樣性、排版與 LaTeX 安全規範) ---

# Type 1 (Maps to Example 1, 2): 直接計算 - ax + b = c 或 ax = b
def _generate_type1_direct_calculation():
    """
    生成形如 ax + b = c 或 ax = b 的直接計算題。
    確保解為整數。
    """
    a = _generate_random_int(-10, 10, exclude_zero=True)
    b = _generate_random_int(-15, 15)
    
    # 先生成解，再計算常數項，確保解為整數
    solution_x = _generate_random_int(-10, 10)
    c = a * solution_x + b

    # 構造方程式字串
    equation_parts = []
    equation_parts.append(_format_variable_term(a, 'x'))
    if b != 0:
        equation_parts.append(_format_constant_term(b))
    
    equation_str = "".join(equation_parts) + " = " + str(c)
    
    # 嚴格遵循 LaTeX 安全規範
    question_text_template = r"解方程式: ${equation}$"
    question_text = question_text_template.replace("{equation}", equation_str)

    correct_answer = str(solution_x)
    answer_display = r"x = {ans_val}".replace("{ans_val}", str(solution_x))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display
    }

# Type 2 (Maps to Example 3, 4): 直接計算 - 包含括號或兩邊皆有變數
def _generate_type2_intermediate_calculation():
    """
    生成形如 A(bx + c) = d 或 ax + b = cx + d 的中間難度計算題。
    確保解為整數。
    """
    problem_type_choice = random.choice([1, 2])
    solution_x = _generate_random_int(-10, 10)

    if problem_type_choice == 1: # A(bx + c) = d
        A = _generate_random_int(-5, 5, exclude_zero=True)
        b = _generate_random_int(-5, 5, exclude_zero=True)
        
        # 計算 c 和 d，確保解為整數
        # A(b*solution_x + c) = d
        # 先生成 d，再計算 c，並確保 d 可被 A 整除
        d = _generate_random_int(-20, 20)
        while d % A != 0:
            d = _generate_random_int(-20, 20)
        
        c = d // A - b * solution_x

        equation_str = str(A) + "(" + _format_variable_term(b, 'x')
        if c != 0:
            equation_str += _format_constant_term(c)
        equation_str += ") = " + str(d)

    else: # ax + b = cx + d
        a = _generate_random_int(-7, 7, exclude_zero=True)
        c = _generate_random_int(-7, 7, exclude_zero=True)
        
        # 確保 a != c 以避免 0x = k 或 0x = 0 的特殊情況
        while a == c:
            c = _generate_random_int(-7, 7, exclude_zero=True)
        
        # 計算 b 和 d，確保解為整數
        # (a-c)x = d-b
        # 先生成 b，再計算 d
        b = _generate_random_int(-15, 15)
        d = (a - c) * solution_x + b

        equation_parts_left = []
        equation_parts_left.append(_format_variable_term(a, 'x'))
        if b != 0:
            equation_parts_left.append(_format_constant_term(b))
        
        equation_parts_right = []
        equation_parts_right.append(_format_variable_term(c, 'x'))
        if d != 0:
            equation_parts_right.append(_format_constant_term(d))
        
        equation_str = "".join(equation_parts_left) + " = " + "".join(equation_parts_right)

    # 嚴格遵循 LaTeX 安全規範
    question_text_template = r"解方程式: ${equation}$"
    question_text = question_text_template.replace("{equation}", equation_str)

    correct_answer = str(solution_x)
    answer_display = r"x = {ans_val}".replace("{ans_val}", str(solution_x))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display
    }

# Type 3 (Maps to Example 5, 6): 直接計算 - 包含分數
def _generate_type3_fractional_calculation():
    """
    生成包含分數的計算題，例如 (ax+b)/c = d 或 x/a + b = c。
    確保解為整數。
    """
    problem_type_choice = random.choice([1, 2])
    solution_x = _generate_random_int(-10, 10)

    if problem_type_choice == 1: # (ax+b)/c = d
        a = _generate_random_int(-5, 5, exclude_zero=True)
        c = _generate_random_int(2, 6) # 分母，必須非零
        
        # 計算 d 和 b，確保解為整數
        # (a*solution_x + b) / c = d
        # 先生成 d
        d = _generate_random_int(-10, 10)
        b = c * d - a * solution_x
        
        equation_str_template = r"\frac{{ {numerator} }}{{ {denominator} }} = {rhs}"
        numerator_str = _format_variable_term(a, 'x')
        if b != 0:
            numerator_str += _format_constant_term(b)
        
        equation_str = equation_str_template.replace("{numerator}", numerator_str).replace("{denominator}", str(c)).replace("{rhs}", str(d))

    else: # x/a + b = c
        a = _generate_random_int(2, 6) # x 的分母，必須非零
        
        # 確保 solution_x 是 a 的倍數，以簡化整數解的計算
        solution_x = _generate_random_int(-5, 5, exclude_zero=True) * a
        if solution_x == 0: # 如果 solution_x 意外變成 0，重新生成
             solution_x = _generate_random_int(-5, 5, exclude_zero=True) * a

        # 計算 b 和 c
        # x/a + b = c
        # 先生成 b
        b = _generate_random_int(-10, 10)
        c = solution_x // a + b

        equation_str_template = r"\frac{{x}}{{ {denominator} }} {constant_b} = {rhs}"
        
        constant_b_str = _format_constant_term(b) if b != 0 else "" 
        
        equation_str = equation_str_template.replace("{denominator}", str(a)).replace("{constant_b}", constant_b_str).replace("{rhs}", str(c))
        # 清理若 b 為 0 時可能產生的 "+0"
        equation_str = equation_str.replace(" +0", "")

    # 嚴格遵循 LaTeX 安全規範
    question_text_template = r"解方程式: ${equation}$"
    question_text = question_text_template.replace("{equation}", equation_str)

    correct_answer = str(solution_x)
    answer_display = r"x = {ans_val}".replace("{ans_val}", str(solution_x))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display
    }

# Type 4 (Maps to Example 7, 8): 逆向求解 - 尋找係數
def _generate_type4_inverse_solving():
    """
    生成逆向求解問題：已知 x 的解，求方程式中的某個係數 'm'。
    確保解為整數。
    """
    # x 的解不能為 0，如果 'm' 是 x 的係數
    solution_x_val = _generate_random_int(-8, 8, exclude_zero=True) 

    problem_type_choice = random.choice([1, 2])

    if problem_type_choice == 1: # 已知 x，求 mx + b = c 中的 m
        # 先生成 m_val (答案)
        m_val = _generate_random_int(-10, 10, exclude_zero=True)
        b = _generate_random_int(-15, 15)
        
        # 計算 c，使 mx + b = c 在 x = solution_x_val 時成立
        c = m_val * solution_x_val + b

        equation_str_template = r"mx {constant_b} = {rhs}"
        constant_b_str = _format_constant_term(b) if b != 0 else ""
        
        equation_str = equation_str_template.replace("{constant_b}", constant_b_str).replace("{rhs}", str(c))
        question_text_template = r"若 $x = {solution}$ 是方程式 ${equation}$ 的解，則 $m = ?$".replace("{solution}", str(solution_x_val))
        question_text = question_text_template.replace("{equation}", equation_str)
        
        correct_answer = str(m_val)
        answer_display = r"m = {ans_val}".replace("{ans_val}", str(m_val))

    else: # 已知 x，求 A(x + m) = B 中的 m
        # 先生成 m_val (答案)
        m_val = _generate_random_int(-10, 10)
        A = _generate_random_int(-5, 5, exclude_zero=True)
        
        # 計算 B，使 A(x + m) = B 在 x = solution_x_val, m = m_val 時成立
        B = A * (solution_x_val + m_val)

        equation_str = str(A) + r"(x + m) = " + str(B)
            
        question_text_template = r"若 $x = {solution}$ 是方程式 ${equation}$ 的解，則 $m = ?$".replace("{solution}", str(solution_x_val))
        question_text = question_text_template.replace("{equation}", equation_str)
            
        correct_answer = str(m_val)
        answer_display = r"m = {ans_val}".replace("{ans_val}", str(m_val))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display
    }

# Type 5 (Maps to Example 9, 10): 情境應用 - 應用問題
def _generate_type5_word_problem():
    """
    生成可轉換為一元一次方程式的應用問題 (例如：連續整數問題、年齡問題)。
    確保解為整數。
    """
    problem_type_choice = random.choice([1, 2])

    if problem_type_choice == 1: # 連續整數問題
        first_num = _generate_random_int(10, 50)
        num_consecutive = random.choice([2, 3]) # 兩個或三個連續整數
        
        if num_consecutive == 2:
            # 方程式: x + (x+1) = Sum
            solution_x = first_num
            sum_val = solution_x + (solution_x + 1)
            
            question_text = r"有兩個連續整數，其和為 ${sum_val}$。請問較小的整數為何？".replace("{sum_val}", str(sum_val))
            correct_answer = str(solution_x)
            answer_display = r"較小的整數為 {ans_val}".replace("{ans_val}", str(solution_x))
            
        else: # num_consecutive == 3
            # 方程式: x + (x+1) + (x+2) = Sum
            solution_x = first_num
            sum_val = solution_x + (solution_x + 1) + (solution_x + 2)
            
            question_text = r"有三個連續整數，其和為 ${sum_val}$。請問最小的整數為何？".replace("{sum_val}", str(sum_val))
            correct_answer = str(solution_x)
            answer_display = r"最小的整數為 {ans_val}".replace("{ans_val}", str(solution_x))

    else: # 年齡問題 (簡化版)
        # 爸爸的年齡是小明的 M 倍，他們的年齡和是 S 歲。求小明今年幾歲。
        # 方程式: x + M*x = S => (M+1)x = S.
        
        M = random.choice([2, 3, 4]) # 爸爸的倍數
        solution_x = _generate_random_int(5, 20) # 小明目前的年齡
        
        sum_of_ages = (M + 1) * solution_x
        
        question_text_template = r"爸爸的年齡是小明的 {M_times} 倍，他們的年齡和是 {sum_ages} 歲。請問小明今年幾歲？"
        question_text = question_text_template.replace("{M_times}", str(M)).replace("{sum_ages}", str(sum_of_ages))
        
        correct_answer = str(solution_x)
        answer_display = r"小明今年 {ans_val} 歲".replace("{ans_val}", str(solution_x))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display
    }

# --- 頂層函式 (符合程式結構、自動重載、數據與欄位規範) ---

def generate(level=1):
    """
    生成 K12 數學一元一次方程式的題目。
    根據 level 參數調整題目難度。
    返回值: dict (包含 question_text, correct_answer, answer, image_base64, created_at, version)
    """
    problem_generators = {
        1: _generate_type1_direct_calculation,
        2: _generate_type2_intermediate_calculation,
        3: _generate_type3_fractional_calculation,
        4: _generate_type4_inverse_solving,
        5: _generate_type5_word_problem,
    }

    # 根據難度等級選擇題型
    if level == 1:
        # 基礎題型：直接計算、簡單括號、簡單應用題
        selected_generator = random.choice([
            problem_generators[1],
            problem_generators[2], # 包含 Type 2 的較簡單變體
            problem_generators[5]  # 簡單應用題
        ])
    elif level == 2:
        # 中等難度題型：更複雜的直接計算 (分數、兩邊皆有變數)、逆向求解、中等應用題
        selected_generator = random.choice([
            problem_generators[2],
            problem_generators[3],
            problem_generators[4],
            problem_generators[5] # 應用題可包含更複雜的設定
        ])
    else: # 預設或更高難度等級，包含所有題型
        selected_generator = random.choice(list(problem_generators.values()))

    problem_data = selected_generator()

    # 填充標準欄位
    problem_data["image_base64"] = "" # 此技能不涉及圖像，因此為空字串
    problem_data["created_at"] = datetime.datetime.now().isoformat()
    problem_data["version"] = "1.0" # 初始版本號

    return problem_data

# 根據基礎設施規則 (【絕對禁令】：嚴禁自定義 check() ... 系統會自動注入 V10.6 鎖死版工具庫。)，
# 此處不應定義 check 函式。系統將自動注入其專用版本。

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
