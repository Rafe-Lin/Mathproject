# ==============================================================================
# ID: jh_數學1上_EvaluatingAlgebraicExpressions
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 29.69s | RAG: 3 examples
# Created At: 2026-01-14 20:58:02
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



# --- 輔助函式通用規範 ---
# [必須回傳]：所有定義的輔助函式，最後一行必須明確使用 'return' 語句回傳結果。
# [類型一致]：若該函式結果會用於拼接 question_text，則回傳值必須強制轉為字串 (str)。
# [防洩漏原則]：視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。

def _format_number_for_latex(num):
    """
    格式化數字為 LaTeX 字串，處理整數和分數。
    確保正數在單獨顯示時沒有前導 '+' 號。
    回傳值強制轉為字串。
    """
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # 使用 \frac 進行分數表示
        expr = r"\frac{{num_n}}{{num_d}}".replace("{num_n}", str(num.numerator)).replace("{num_d}", str(num.denominator))
        return expr
    return str(num)

def _get_coeff_str(coeff, var_name, power):
    """
    取得代數項係數的字串表示，處理 1 和 -1 係數。
    例如：(1, 'x', 1) -> 'x', (-1, 'x', 1) -> '-x', (2, 'x', 1) -> '2x'
    回傳值強制轉為字串。
    """
    if coeff == 1 and var_name:
        return var_name + (r"^{" + str(power) + r"}" if power > 1 else "")
    elif coeff == -1 and var_name:
        return "-" + var_name + (r"^{" + str(power) + r"}" if power > 1 else "")
    elif var_name:
        return _format_number_for_latex(coeff) + var_name + (r"^{" + str(power) + r"}" if power > 1 else "")
    else: # 常數項
        return _format_number_for_latex(coeff)

def _build_expression_string_from_parts(terms):
    """
    從 (係數, 變數名, 次方) 元組列表建立 LaTeX 安全的代數式字串。
    假設項已排序 (例如：最高次方在前)。正確處理正負號。
    範例：[(3, 'x', 1), (-5, None, None)] -> "3x - 5"
    範例：[(-1, 'x', 2), (2, 'y', 1), (7, None, None)] -> "-x^2 + 2y + 7"
    回傳值強制轉為字串。
    """
    parts = []
    for i, (coeff, var_name, power) in enumerate(terms):
        if coeff == 0:
            continue

        term_str = _get_coeff_str(abs(coeff), var_name, power)

        if i == 0: # 第一個非零項
            if coeff < 0:
                parts.append(r"-" + term_str)
            else:
                parts.append(term_str)
        else: # 後續項
            if coeff < 0:
                parts.append(r" - " + term_str)
            else:
                parts.append(r" + " + term_str)

    if not parts:
        return "0" # 如果所有係數都為零
    return "".join(parts)

# --- 頂層函式 ---
# [頂層函式]：嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# [自動重載]：確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level=1):
    """
    生成 K12 數學「求代數式的值」題目。
    確保題型多樣性、LaTeX 安全性並符合程式結構規範。
    """
    # [題型多樣性]：generate() 內部必須使用 random.choice 或 if/elif 邏輯，實作至少 3 種不同的題型變體。
    problem_types = [
        "Type 1 (Maps to Example 1): 直接計算簡單線性代數式 (ax+b)。",
        "Type 2 (Maps to Example 2, 4): 直接計算較複雜代數式 (例如：ax^2+b, ax+by+c, 含分數)。",
        "Type 3 (Maps to Example 3, 5): 情境應用題，需代入數值計算 (例如：長方形周長/面積、花費計算)。"
    ]

    chosen_type = random.choice(problem_types)

    question_text_parts = []
    expression_latex = ""
    variable_values_latex = ""
    calculated_answer = None # 儲存計算結果，可以是 int, float, Fraction

    if "Type 1" in chosen_type:
        # 範例：求代數式 $3x+5$ 的值，當 $x=2$ 時。
        a = random.randint(-5, 5)
        while a == 0: # 確保 'a' 不為零，否則會變成常數式
            a = random.randint(-5, 5)
        b = random.randint(-10, 10)
        x_val = random.randint(-5, 5)

        terms = [(a, 'x', 1)]
        if b != 0:
            terms.append((b, None, None))
        expression_latex = _build_expression_string_from_parts(terms)

        var_x_str = _format_number_for_latex(x_val)
        # [排版與 LaTeX 安全]：嚴禁使用 f-string 或 % 格式化。必須嚴格執行 .replace() 模板。
        variable_values_latex = r"當 $x={x_val}$ 時".replace("{x_val}", var_x_str)

        calculated_answer = a * x_val + b

        question_text_template = r"求代數式 ${expr}$ 的值，{vars}。"
        question_text_parts.append(
            question_text_template.replace("{expr}", expression_latex).replace("{vars}", variable_values_latex)
        )

    elif "Type 2" in chosen_type:
        sub_type = random.choice(["quadratic", "two_variables", "fractional"])

        if sub_type == "quadratic":
            # 範例：求代數式 $2x^2 - 3x + 7$ 的值，當 $x=2$ 時。
            a = random.randint(-3, 3)
            while a == 0:
                a = random.randint(-3, 3)
            b = random.randint(-5, 5)
            c = random.randint(-10, 10)
            x_val = random.randint(-4, 4)

            terms = [(a, 'x', 2)]
            if b != 0:
                terms.append((b, 'x', 1))
            if c != 0:
                terms.append((c, None, None))
            expression_latex = _build_expression_string_from_parts(terms)

            var_x_str = _format_number_for_latex(x_val)
            variable_values_latex = r"當 $x={x_val}$ 時".replace("{x_val}", var_x_str)
            calculated_answer = a * (x_val**2) + b * x_val + c

            question_text_template = r"求代數式 ${expr}$ 的值，{vars}。"
            question_text_parts.append(
                question_text_template.replace("{expr}", expression_latex).replace("{vars}", variable_values_latex)
            )

        elif sub_type == "two_variables":
            # 範例：求代數式 $3x - 2y + 5$ 的值，當 $x=2, y=1$ 時。
            a = random.randint(-3, 3)
            while a == 0: a = random.randint(-3, 3)
            b = random.randint(-3, 3)
            while b == 0: b = random.randint(-3, 3)
            c = random.randint(-5, 5)
            x_val = random.randint(-3, 3)
            y_val = random.randint(-3, 3)

            terms = [(a, 'x', 1), (b, 'y', 1)]
            if c != 0:
                terms.append((c, None, None))
            expression_latex = _build_expression_string_from_parts(terms)

            var_x_str = _format_number_for_latex(x_val)
            var_y_str = _format_number_for_latex(y_val)
            variable_values_latex = r"當 $x={x_val}$, $y={y_val}$ 時".replace("{x_val}", var_x_str).replace("{y_val}", var_y_str)
            calculated_answer = a * x_val + b * y_val + c

            question_text_template = r"求代數式 ${expr}$ 的值，{vars}。"
            question_text_parts.append(
                question_text_template.replace("{expr}", expression_latex).replace("{vars}", variable_values_latex)
            )

        elif sub_type == "fractional":
            # 範例：求代數式 $\frac{6}{x} + 2$ 的值，當 $x=-3$ 時。
            a = random.randint(-10, 10)
            while a == 0: a = random.randint(-10, 10)
            b = random.randint(-5, 5)
            x_val = random.choice([x for x in range(-5, 6) if x != 0]) # x 不能為 0

            frac_part_latex = r"\frac{{num_a}}{{x}}".replace("{num_a}", _format_number_for_latex(a))
            if b != 0:
                if b > 0:
                    expression_latex = frac_part_latex + r" + " + _format_number_for_latex(b)
                else:
                    expression_latex = frac_part_latex + r" - " + _format_number_for_latex(abs(b))
            else:
                expression_latex = frac_part_latex

            var_x_str = _format_number_for_latex(x_val)
            variable_values_latex = r"當 $x={x_val}$ 時".replace("{x_val}", var_x_str)

            # 計算答案，使用 Fraction 確保精度
            calculated_answer = Fraction(a, x_val) + Fraction(b)
            # 如果分母為 1，則轉換為整數
            if calculated_answer.denominator == 1:
                calculated_answer = int(calculated_answer)

            question_text_template = r"求代數式 ${expr}$ 的值，{vars}。"
            question_text_parts.append(
                question_text_template.replace("{expr}", expression_latex).replace("{vars}", variable_values_latex)
            )

    elif "Type 3" in chosen_type:
        sub_type = random.choice(["perimeter_area", "cost_calculation"])

        if sub_type == "perimeter_area":
            # 範例：一個長方形的長為 $(2x+1)$ 公分，寬為 $x$ 公分。當 $x=3$ 時，求此長方形的周長。
            x_val = random.randint(2, 8)
            length_coeff = random.randint(1, 3)
            length_const = random.randint(0, 5)
            width_coeff = random.randint(1, 2)
            width_const = random.randint(0, 3)

            # 確保在 x_val 時，長寬都是正數且寬度小於長度
            actual_length = length_coeff * x_val + length_const
            actual_width = width_coeff * x_val + width_const
            # 重新生成直到滿足條件
            while actual_length <= 0 or actual_width <= 0 or actual_width >= actual_length:
                x_val = random.randint(2, 8)
                length_coeff = random.randint(1, 3)
                length_const = random.randint(0, 5)
                width_coeff = random.randint(1, 2)
                width_const = random.randint(0, 3)
                actual_length = length_coeff * x_val + length_const
                actual_width = width_coeff * x_val + width_const

            length_expr_terms = [(length_coeff, 'x', 1)]
            if length_const > 0:
                length_expr_terms.append((length_const, None, None))
            length_latex = _build_expression_string_from_parts(length_expr_terms)

            width_expr_terms = [(width_coeff, 'x', 1)]
            if width_const > 0:
                width_expr_terms.append((width_const, None, None))
            width_latex = _build_expression_string_from_parts(width_expr_terms)

            var_x_str = _format_number_for_latex(x_val)
            variable_values_latex = r"當 $x={x_val}$ 時".replace("{x_val}", var_x_str)

            question_type_choice = random.choice(["perimeter", "area"])
            if question_type_choice == "perimeter":
                question_text_template = r"一個長方形的長為 $({length})$ 公分，寬為 $({width})$ 公分。{vars}，求此長方形的周長。"
                calculated_answer = 2 * (actual_length + actual_width)
            else: # area
                question_text_template = r"一個長方形的長為 $({length})$ 公分，寬為 $({width})$ 公分。{vars}，求此長方形的面積。"
                calculated_answer = actual_length * actual_width

            question_text_parts.append(
                question_text_template
                .replace("{length}", length_latex)
                .replace("{width}", width_latex)
                .replace("{vars}", variable_values_latex)
            )

        elif sub_type == "cost_calculation":
            # 範例：某商店的 A 商品單價為 $20 元，B 商品單價為 $15 元。
            # 小明購買了 $(2x+3)$ 個 A 商品和 $5$ 個 B 商品。當 $x=4$ 時，求小明總共花費多少元？
            item_price_a = random.randint(10, 50)
            item_price_b = random.randint(5, 30)
            num_a_coeff = random.randint(1, 3)
            num_a_const = random.randint(0, 5)
            num_b_const = random.randint(1, 10)
            x_val = random.randint(2, 10)

            qty_a_expr_terms = [(num_a_coeff, 'x', 1)]
            if num_a_const > 0:
                qty_a_expr_terms.append((num_a_const, None, None))
            qty_a_latex = _build_expression_string_from_parts(qty_a_expr_terms)

            actual_qty_a = num_a_coeff * x_val + num_a_const
            actual_qty_b = num_b_const

            calculated_answer = item_price_a * actual_qty_a + item_price_b * actual_qty_b

            var_x_str = _format_number_for_latex(x_val)
            variable_values_latex = r"當 $x={x_val}$ 時".replace("{x_val}", var_x_str)

            question_text_template = (
                r"某商店的 A 商品單價為 ${price_a}$ 元，B 商品單價為 ${price_b}$ 元。 "
                r"小明購買了 $({qty_a_expr})$ 個 A 商品和 ${qty_b}$ 個 B 商品。 "
                r"{vars}，求小明總共花費多少元？"
            )
            question_text_parts.append(
                question_text_template
                .replace("{price_a}", _format_number_for_latex(item_price_a))
                .replace("{price_b}", _format_number_for_latex(item_price_b))
                .replace("{qty_a_expr}", qty_a_latex)
                .replace("{qty_b}", _format_number_for_latex(actual_qty_b))
                .replace("{vars}", variable_values_latex)
            )

    # 最終題目文字
    final_question_text = "".join(question_text_parts)

    # 格式化 calculated_answer 為字串，以符合 correct_answer 的規範
    if isinstance(calculated_answer, Fraction):
        if calculated_answer.denominator == 1:
            correct_answer_str = str(int(calculated_answer))
        else:
            # 使用 \frac 進行分數表示
            correct_answer_str = r"\frac{{num_n}}{{num_d}}".replace("{num_n}", str(calculated_answer.numerator)).replace("{num_d}", str(calculated_answer.denominator))
    else:
        correct_answer_str = str(calculated_answer)

    # [數據與欄位]：返回字典必須且僅能包含指定欄位。
    # [時間戳記]：更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    result = {
        "question_text": final_question_text,
        "correct_answer": correct_answer_str, # 字串化的正確答案，用於 check 函式比較
        "answer": calculated_answer,         # 原始計算結果 (int, float, Fraction)，用於內部記錄或顯示
        "image_base64": None,                # 此技能不涉及圖片，故為 None
        "created_at": datetime.datetime.now().isoformat(),
        "version": "9.6.0",                  # 版本號
    }
    return result

# 根據「絕對禁令：嚴禁自定義 check()」，系統將自動注入 V10.6 鎖死版工具庫，
# 因此此處不定義 check 函式。
# def check(user_answer, correct_answer):
#     """
#     檢查使用者答案是否正確。
#     處理整數、浮點數和分數的比較。
#     """
#     try:
#         # 嘗試將使用者答案解析為 Fraction，可處理 "1/2", "-3", "5" 等格式
#         user_val = Fraction(user_answer)
#         correct_val = Fraction(correct_answer)

#         # 以 Fraction 進行精確比較
#         return user_val == correct_val
#     except ValueError:
#         # 如果 Fraction 解析失敗，嘗試解析為浮點數 (例如："0.5")
#         try:
#             user_val = float(user_answer)
#             correct_val = float(correct_answer)
#             # 使用 math.isclose 比較浮點數以處理精度問題
#             return math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9)
#         except ValueError:
#             # 如果所有解析都失敗，則視為無效格式
#             return False

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
