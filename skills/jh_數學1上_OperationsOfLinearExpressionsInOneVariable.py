# ==============================================================================
# ID: jh_數學1上_OperationsOfLinearExpressionsInOneVariable
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 79.12s | RAG: 5 examples
# Created At: 2026-01-14 21:01:41
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

import re # For _parse_linear_expression

# --- 輔助函式區塊 ---

def _format_linear_expression(coef_x, const_term):
    """
    將係數和常數項格式化為標準的一元一次式字串。
    例如: (1, 0) -> "x", (5, 3) -> "5x + 3", (-1, -2) -> "-x - 2", (0, 7) -> "7"
    """
    parts = []
    
    # 處理變數項 (x term)
    if coef_x == 1:
        parts.append(r"x")
    elif coef_x == -1:
        parts.append(r"-x")
    elif coef_x != 0:
        parts.append(r"{coef}x".replace("{coef}", str(coef_x)))

    # 處理常數項 (constant term)
    if const_term > 0:
        if parts: # 如果有變數項，則常數項前加 '+'
            parts.append(r"+ {const}".replace("{const}", str(const_term)))
        else: # 如果沒有變數項，直接顯示常數項
            parts.append(str(const_term))
    elif const_term < 0:
        # 如果常數項為負，則前加 '-' (絕對值)
        parts.append(r"- {const}".replace("{const}", str(abs(const_term))))

    if not parts:
        return r"0" # 如果所有項都為零，則表達式為 "0"
    return "".join(parts).strip()

def _parse_linear_expression(expr_str):
    """
    解析一元一次式字串為 (係數, 常數項) 的元組。
    處理格式如 "5x+3", "-x-2", "7", "4x", "3+5x" 等。
    """
    expr_str = expr_str.replace(" ", "").replace("--", "+") # 移除空白，處理雙負號
    
    coef_x = 0
    const_term = 0
    
    # 匹配 x 項 (例如 'x', '-x', '2x', '-2x', '+x' 等)
    x_match = re.search(r"([+-]?\d*)x", expr_str)
    if x_match:
        coef_str = x_match.group(1)
        if coef_str == "+": coef_x = 1
        elif coef_str == "-": coef_x = -1
        elif coef_str == "": coef_x = 1 # 例如 "x"
        else: coef_x = int(coef_str)
        expr_str = expr_str.replace(x_match.group(0), "") # 從字串中移除已解析的 x 項
    
    # 匹配常數項
    # 處理可能剩餘的常數項，現在字串中應該只剩下數字和可能的正負號
    if expr_str:
        # 確保剩餘字串是有效的整數形式
        if re.fullmatch(r"[+-]?\d+", expr_str):
            try:
                const_term = int(expr_str)
            except ValueError:
                pass # 如果解析失敗，表示格式不符，不更新 const_term
            
    return (coef_x, const_term)


# --- 題型生成函式區塊 ---

def _generate_type_1_direct_calculation(level):
    """
    生成直接計算/化簡題。
    Type 1 (對應教科書基礎運算與分配律)
    """
    sub_type = random.choice([1, 2, 3]) # 1:基本加減, 2:分配律, 3:分數運算

    coef_x_ans, const_term_ans = 0, 0
    question_latex = ""

    if sub_type == 1: # 基本加減: ax + b + cx + d
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        d = random.randint(1, 10) * random.choice([-1, 1])
        
        coef_x_ans = a + c
        const_term_ans = b + d
        
        # 建構題目 LaTeX 部分
        expr_parts = []
        
        # 第一個變數項 (ax)
        if a == 1: expr_parts.append(r"x")
        elif a == -1: expr_parts.append(r"-x")
        else: expr_parts.append(r"{a}x".replace("{a}", str(a)))
        
        # 第一個常數項 (b)
        if b > 0: expr_parts.append(r"+ {b}".replace("{b}", str(b)))
        elif b < 0: expr_parts.append(r"- {b}".replace("{b}", str(abs(b))))
        
        # 第二個變數項 (cx) - 總是帶運算符號
        if c > 0: expr_parts.append(r"+ {c}x".replace("{c}", str(c)))
        elif c == 1: expr_parts.append(r"+ x")
        elif c == -1: expr_parts.append(r"- x")
        elif c < 0: expr_parts.append(r"- {c_abs}x".replace("{c_abs}", str(abs(c))))
        
        # 第二個常數項 (d) - 總是帶運算符號
        if d > 0: expr_parts.append(r"+ {d}".replace("{d}", str(d)))
        elif d < 0: expr_parts.append(r"- {d}".replace("{d}", str(abs(d))))

        question_latex_template = r"化簡 ${expr}$。"
        question_latex = question_latex_template.replace("{expr}", "".join(expr_parts).strip())


    elif sub_type == 2: # 分配律: a(bx + c) + d(ex + f) 或 a(bx + c) - d(ex + f)
        op_between_terms = random.choice(["+", "-"]) # 兩個主要項之間的運算符號
        
        a = random.randint(2, 4) * random.choice([-1, 1])
        b = random.randint(1, 3) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        
        d_val = random.randint(2, 4) # 第二個項的乘數的絕對值
        
        e = random.randint(1, 3) * random.choice([-1, 1])
        f = random.randint(1, 10) * random.choice([-1, 1])

        # 根據運算符號計算答案
        if op_between_terms == "+":
            coef_x_ans = a * b + d_val * e
            const_term_ans = a * c + d_val * f
        else: # op_between_terms == "-"
            coef_x_ans = a * b - d_val * e
            const_term_ans = a * c - d_val * f
        
        # 建構第一個項的 LaTeX: a(bx + c)
        term1_inner_c_latex = r"+ {c_abs}".replace("{c_abs}", str(abs(c))) if c > 0 else (r"- {c_abs}".replace("{c_abs}", str(abs(c))) if c < 0 else "")
        term1_bx_latex = r"x" if b == 1 else (r"-x" if b == -1 else r"{b}x".replace("{b}", str(b)))
        term1_latex = r"{a}({bx}{c_term})".replace("{a}", str(a)) \
                                        .replace("{bx}", term1_bx_latex) \
                                        .replace("{c_term}", term1_inner_c_latex)
        
        # 建構第二個項的 LaTeX: d_val(ex + f)
        term2_inner_f_latex = r"+ {f_abs}".replace("{f_abs}", str(abs(f))) if f > 0 else (r"- {f_abs}".replace("{f_abs}", str(abs(f))) if f < 0 else "")
        term2_ex_latex = r"x" if e == 1 else (r"-x" if e == -1 else r"{e}x".replace("{e}", str(e)))
        term2_latex = r"{op} {d_val}({ex}{f_term})".replace("{op}", op_between_terms) \
                                                    .replace("{d_val}", str(d_val)) \
                                                    .replace("{ex}", term2_ex_latex) \
                                                    .replace("{f_term}", term2_inner_f_latex)
        
        question_latex_template = r"化簡 ${term1} {term2}$。"
        question_latex = question_latex_template.replace("{term1}", term1_latex) \
                                          .replace("{term2}", term2_latex)


    elif sub_type == 3: # 分數運算: (ax + b)/c + (dx + e)/f
        # 為了簡化 K12 題型並確保 _format_linear_expression 適用，
        # 我們確保係數和常數項最終能化簡為整數。
        
        # 循環直到生成能化簡為整數係數的題目
        while True:
            c_denom = random.choice([2, 3, 4, 5])
            f_denom = random.choice([2, 3, 4, 5])
            while c_denom == f_denom: # 確保分母不同以增加變化
                f_denom = random.choice([2, 3, 4, 5])

            a_num = random.randint(1, 5) * random.choice([-1, 1])
            b_num = random.randint(1, 10) * random.choice([-1, 1])
            d_num = random.randint(1, 5) * random.choice([-1, 1])
            e_num = random.randint(1, 10) * random.choice([-1, 1])
            
            op = random.choice(["+", "-"]) # 分數間的運算符號

            common_denominator = c_denom * f_denom // math.gcd(c_denom, f_denom)
            
            if op == "+":
                coef_x_numerator = a_num * (common_denominator // c_denom) + d_num * (common_denominator // f_denom)
                const_term_numerator = b_num * (common_denominator // c_denom) + e_num * (common_denominator // f_denom)
            else: # op == "-"
                coef_x_numerator = a_num * (common_denominator // c_denom) - d_num * (common_denominator // f_denom)
                const_term_numerator = b_num * (common_denominator // c_denom) - e_num * (common_denominator // f_denom)

            # 檢查結果是否能化簡為整數係數
            if common_denominator != 0 and \
               coef_x_numerator % common_denominator == 0 and \
               const_term_numerator % common_denominator == 0:
                
                coef_x_ans = coef_x_numerator // common_denominator
                const_term_ans = const_term_numerator // common_denominator
                break # 找到有效數字，退出循環
            # 如果不能整除，重新生成數字

        # 建構第一個分數的 LaTeX
        term1_b_sign = "+" if b_num >= 0 else "-"
        term1_b_val = str(abs(b_num)) if b_num != 0 else ""
        term1_numerator_content = r"{a}x {b_sign} {b_abs}".replace("{a}", str(a_num)) \
                                                        .replace("{b_sign}", term1_b_sign) \
                                                        .replace("{b_abs}", term1_b_val)
        if b_num == 0: # 如果常數項為0，則只顯示變數項
            term1_numerator_content = r"{a}x".replace("{a}", str(a_num))
            if a_num == 1: term1_numerator_content = r"x"
            if a_num == -1: term1_numerator_content = r"-x"

        expr1_latex = r"\frac{{{numerator}}}{{{denominator}}}".replace("{numerator}", term1_numerator_content) \
                                                               .replace("{denominator}", str(c_denom))
        
        # 建構第二個分數的 LaTeX
        term2_e_sign = "+" if e_num >= 0 else "-"
        term2_e_val = str(abs(e_num)) if e_num != 0 else ""
        term2_numerator_content = r"{d}x {e_sign} {e_abs}".replace("{d}", str(d_num)) \
                                                        .replace("{e_sign}", term2_e_sign) \
                                                        .replace("{e_abs}", term2_e_val)
        if e_num == 0: # 如果常數項為0，則只顯示變數項
            term2_numerator_content = r"{d}x".replace("{d}", str(d_num))
            if d_num == 1: term2_numerator_content = r"x"
            if d_num == -1: term2_numerator_content = r"-x"

        expr2_latex = r"{op} \frac{{{numerator}}}{{{denominator}}}".replace("{op}", op) \
                                                                    .replace("{numerator}", term2_numerator_content) \
                                                                    .replace("{denominator}", str(f_denom))

        question_latex_template = r"化簡 ${expr1} {expr2}$。"
        question_latex = question_latex_template.replace("{expr1}", expr1_latex) \
                                          .replace("{expr2}", expr2_latex)

    correct_answer_str = _format_linear_expression(coef_x_ans, const_term_ans)
    
    return {
        "question_text": question_latex,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str # 顯示給學生的答案
    }

def _generate_type_2_contextual_application(level):
    """
    生成情境應用題。
    Type 2 (對應教科書文字敘述轉列式與應用)
    """
    scenario_type = random.choice([1, 2]) # 1:簡單翻譯, 2:基礎應用題

    coef_x_ans, const_term_ans = 0, 0
    question_text = ""

    if scenario_type == 1: # 簡單翻譯
        num = random.randint(2, 5)
        offset = random.randint(1, 10)
        op_type = random.choice(["倍多", "倍少"])
        
        if op_type == "倍多":
            coef_x_ans = num
            const_term_ans = offset
            question_text_template = r"請用 $x$ 表示：「$x$ 的 {num} 倍多 {offset}」。"
            question_text = question_text_template.replace("{num}", str(num)).replace("{offset}", str(offset))
        else: # 倍少
            coef_x_ans = num
            const_term_ans = -offset
            question_text_template = r"請用 $x$ 表示：「$x$ 的 {num} 倍少 {offset}」。"
            question_text = question_text_template.replace("{num}", str(num)).replace("{offset}", str(offset))

    elif scenario_type == 2: # 基礎應用題
        problem_choice = random.choice([1, 2])
        if problem_choice == 1: # 長方形周長
            length_offset = random.randint(1, 5)
            op_sign = random.choice(["+", "-"])
            
            if op_sign == "+":
                # 長是 (x + length_offset)，寬是 x
                # 周長 = 2 * (長 + 寬) = 2 * (x + length_offset + x) = 2 * (2x + length_offset) = 4x + 2*length_offset
                coef_x_ans = 4
                const_term_ans = 2 * length_offset
                question_text_template = r"一個長方形的長是 $(x + {offset})$ 公分，寬是 $x$ 公分。請問它的周長是多少公分？(請用 $x$ 表示並化簡)"
                question_text = question_text_template.replace("{offset}", str(length_offset))
            else: # op_sign == "-"
                # 長是 (x - length_offset)，寬是 x
                # 周長 = 2 * (x - length_offset + x) = 2 * (2x - length_offset) = 4x - 2*length_offset
                coef_x_ans = 4
                const_term_ans = -2 * length_offset
                question_text_template = r"一個長方形的長是 $(x - {offset})$ 公分，寬是 $x$ 公分。請問它的周長是多少公分？(請用 $x$ 表示並化簡)"
                question_text = question_text_template.replace("{offset}", str(length_offset))

        else: # 錢的問題
            multiple = random.randint(2, 3)
            extra = random.randint(5, 20)
            op_type = random.choice(["多", "少"])
            
            if op_type == "多":
                coef_x_ans = multiple
                const_term_ans = extra
                question_text_template = r"小明有 $x$ 元，小華的錢比小明的 {multiple} 倍多 {extra} 元。請問小華有多少元？(請用 $x$ 表示並化簡)"
                question_text = question_text_template.replace("{multiple}", str(multiple)).replace("{extra}", str(extra))
            else: # op_type == "少"
                coef_x_ans = multiple
                const_term_ans = -extra
                question_text_template = r"小明有 $x$ 元，小華的錢比小明的 {multiple} 倍少 {extra} 元。請問小華有多少元？(請用 $x$ 表示並化簡)"
                question_text = question_text_template.replace("{multiple}", str(multiple)).replace("{extra}", str(extra))

    correct_answer_str = _format_linear_expression(coef_x_ans, const_term_ans)
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str
    }

def _generate_type_3_evaluation_substitution(level):
    """
    生成代入求值題。
    Type 3 (對應教科書已知變數值代入求值)
    """
    sub_type = random.choice([1, 2]) # 1:基本代入, 2:複雜代入

    x_val = random.randint(-5, 5)
    result_val = 0
    question_latex = ""

    if sub_type == 1: # 基本代入: ax + b
        a = random.randint(2, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])
        
        result_val = a * x_val + b
        
        # 建構表達式 ax + b 的 LaTeX
        expr_parts = []
        if a == 1: expr_parts.append(r"x")
        elif a == -1: expr_parts.append(r"-x")
        else: expr_parts.append(r"{a}x".replace("{a}", str(a)))
        
        if b > 0: expr_parts.append(r"+ {b}".replace("{b}", str(b)))
        elif b < 0: expr_parts.append(r"- {b}".replace("{b}", str(abs(b))))
        
        expr_latex = "".join(expr_parts).strip()
        
        question_latex_template = r"若 $x = {x_val}$，求 ${expr}$ 的值。"
        question_latex = question_latex_template.replace("{x_val}", str(x_val)) \
                                          .replace("{expr}", expr_latex)

    elif sub_type == 2: # 複雜代入: a(bx + c) + d
        a = random.randint(2, 4) * random.choice([-1, 1])
        b = random.randint(1, 3) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        d = random.randint(1, 10) * random.choice([-1, 1])
        
        result_val = a * (b * x_val + c) + d
        
        # 建構表達式 a(bx + c) + d 的 LaTeX
        term_inner_c_latex = r"+ {c_abs}".replace("{c_abs}", str(abs(c))) if c > 0 else (r"- {c_abs}".replace("{c_abs}", str(abs(c))) if c < 0 else "")
        term_bx_latex = r"x" if b == 1 else (r"-x" if b == -1 else r"{b}x".replace("{b}", str(b)))
        
        expr_latex_parts = []
        expr_latex_parts.append(r"{a}({bx}{c_term})".replace("{a}", str(a)) \
                                                    .replace("{bx}", term_bx_latex) \
                                                    .replace("{c_term}", term_inner_c_latex))
        
        if d > 0: expr_latex_parts.append(r"+ {d}".replace("{d}", str(d)))
        elif d < 0: expr_latex_parts.append(r"- {d}".replace("{d}", str(abs(d))))
        
        expr_latex = "".join(expr_latex_parts).strip()
        
        question_latex_template = r"若 $x = {x_val}$，求 ${expr}$ 的值。"
        question_latex = question_latex_template.replace("{x_val}", str(x_val)) \
                                          .replace("{expr}", expr_latex)

    correct_answer_str = str(result_val)
    
    return {
        "question_text": question_latex,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str
    }

# --- 核心函式區塊 ---

def generate(level=1):
    """
    根據給定難度生成一元一次式運算題目。
    """
    problem_generators = [
        _generate_type_1_direct_calculation,
        _generate_type_2_contextual_application,
        _generate_type_3_evaluation_substitution,
    ]
    
    selected_generator = random.choice(problem_generators)
    problem_data = selected_generator(level)

    # 補充通用欄位
    problem_data["image_base64"] = "" # 此技能不預期有複雜視覺化，故為空字串
    problem_data["created_at"] = datetime.datetime.now()
    problem_data["version"] = 1 # 題目版本號，從 1 開始遞增

    return problem_data



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
