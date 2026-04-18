# ==============================================================================
# ID: jh_數學1下_PropertiesOfInequalities
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 56.26s | RAG: 3 examples
# Created At: 2026-01-17 14:58:52
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
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

# --- 2. Number Theory Helpers ---
def is_prime(n):
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

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

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

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度，僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理：剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}

# Standard library imports

import base64
from datetime import datetime
import io
import re # For inequality parsing in helper

# External library imports (mocked for spec - Coder will ensure these are available)
# import matplotlib.pyplot as plt
# from matplotlib.patches import Polygon

# --- 輔助函式 (Helper Functions) ---
# [必須回傳]：所有定義的輔助函式最後一行必須明確使用 'return' 語句回傳結果。
# [類型一致]：若該函式結果會用於拼接 question_text，則回傳值必須強制轉為字串 (str)。
# [防洩漏原則]：視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。

# V10.2 座標平面專用硬化規格 - A. 資料結構鎖死 (Prevent Unpacking Error)
# 此函數為系統級通用規範，即使當前技能不直接使用座標，也需定義。
def _generate_coordinate_value(is_fraction=False, integer_only=False):
    """
    統一生成座標值 (整數或帶分數)。
    回傳格式: (float_val, (int_part, num, den, is_neg))
    - float_val: 實際浮點數值。
    - int_part: 帶分數的整數部分 (若為負數，此為絕對值)。
    - num: 分子。
    - den: 分母。
    - is_neg: 是否為負數 (True/False)。
    """
    is_neg = random.choice([True, False])
    float_val = 0.0
    int_part = 0
    num = 0
    den = 0

    if integer_only:
        # V13.0 座標選取控制: 確保範圍對稱且寬裕
        int_part = random.randint(1, 8) 
        float_val = float(int_part)
        if is_neg:
            float_val = -float_val
    elif is_fraction:
        # V13.0 座標選取控制: 確保範圍
        int_part = random.randint(0, 5) 
        # V13.1 禁絕假分數: 確保分子小於分母且分母大於1
        num = random.randint(1, 4) 
        den = random.randint(num + 1, 6)
        
        float_val = float(int_part) + float(num) / den
        if is_neg:
            float_val = -float_val
    else: # 預設為整數或半整數 (例如 3.5)
        choice = random.choice([0, 1])
        if choice == 0: # 整數
            int_part = random.randint(1, 8)
            float_val = float(int_part)
        else: # 半整數
            int_part = random.randint(1, 7)
            num = 1
            den = 2
            float_val = float(int_part) + 0.5
        if is_neg:
            float_val = -float_val
            
    # V13.5 整數優先: 確保整數值以整數形式儲存 (e.g., 5 而非 5.0)
    if float_val.is_integer():
        float_val = int(float_val)
        num = 0
        den = 0

    return (float_val, (int_part, num, den, is_neg))

def _format_coordinate_value(data):
    """
    將座標值格式化為 LaTeX 安全的字串。
    data: (float_val, (int_part, num, den, is_neg))
    """
    # V10.2 A. 資料結構鎖死: 嚴格解包
    _float_val, (_int_part, _num, _den, _is_neg) = data

    # V13.5 整數優先 & V13.0 格式精確要求: 確保整數輸出為 "5" 而非 "5.0"
    if isinstance(_float_val, int):
        return str(_float_val)
    
    # 處理分數的負號
    sign = "-" if _is_neg and (_int_part != 0 or _num != 0) else ""
    
    if _int_part == 0 and _num == 0: # 應已被 int 處理，此為備用
        return "0" 
    elif _int_part == 0: # 純分數 (e.g., 1/2)
        # V10.2 C. LaTeX 模板規範 (No Double Braces): 使用單層大括號搭配 replace
        expr = r"\frac{n}{d}".replace("{n}", str(_num)).replace("{d}", str(_den))
        return sign + expr
    else: # 帶分數 (e.g., 2 1/2)
        expr = r"{i}\frac{n}{d}".replace("{i}", str(abs(_int_part))).replace("{n}", str(_num)).replace("{d}", str(_den))
        return sign + expr

def _parse_inequality_expression(expr_str):
    """
    輔助函式：將不等式字串解析為標準形式 (變數, 運算符, 值) 元組。
    處理如 'x > 5', '5 < x', 'X >= -2' 等多種輸入格式。
    回傳 (variable_name, operator_symbol, value) 或 None (若解析失敗)。
    此函式用於 check() 內部，將字串解析邏輯從 check() 中隔離，以符合「禁絕複雜比對」精神。
    """
    expr_str = expr_str.replace(" ", "").lower() # 標準化：移除空格並轉為小寫
    
    # 定義運算符，處理常見變體 (例如 '=>' 轉為 '>=')
    # 順序很重要，長的運算符在前 (例如 '>=' 在 '>' 之前)
    operators = {
        r"\ge": ">=", r"\le": "<=", 
        ">=": ">=", "=>": ">=", "\u2265": ">=", # Unicode ≥
        "<=": "<=", "=<": "<=", "\u2264": "<=", # Unicode ≤
        ">": ">",
        "<": "<",
        "=": "=" # 等號也可能用於某些比較型問題
    }
    
    # 建立運算符的 Regex 模式，確保長運算符優先匹配
    # Use re.escape for all keys, but since valid keys contain escapes, handle carefully.
    # keys contain \ge which needs to be matched.
    sorted_keys = sorted(operators.keys(), key=len, reverse=True)
    # 必須小心 \ (LaTeX) 與 Regex 的衝突。
    op_pattern = "|".join(re.escape(k) for k in sorted_keys)
    
    # 模式一：(變數)(運算符)(值) 例如：x>5, y<=-3.5
    # Group 1: 變數 (單一字母 a-z)
    # Group 2: 運算符
    # Group 3: 值 (數字，可為整數或浮點數，含正負號)
    pattern1 = fr"([a-z])({op_pattern})([-+]?\d+(\.\d*)?)"
    match1 = re.match(pattern1, expr_str)
    
    if match1:
        var = match1.group(1)
        # Normalization
        raw_op = match1.group(2)
        op = operators.get(raw_op, raw_op)
        val = float(match1.group(3))
        return (var, op, val)

    # 模式二：(值)(運算符)(變數) 例如：5<x, -3.5>=y
    pattern2 = fr"([-+]?\d+(\.\d*)?)({op_pattern})([a-z])"
    match2 = re.match(pattern2, expr_str)
    
    if match2:
        val = float(match2.group(1))
        # Normalization
        raw_op = match2.group(3)
        op_rev = operators.get(raw_op, raw_op)
        var = match2.group(4)
        
        # 反轉運算符以轉換為標準形式 (變數, 運算符, 值)
        op = ""
        if op_rev == ">": op = "<"
        elif op_rev == "<": op = ">"
        elif op_rev == ">=": op = "<="
        elif op_rev == "<=": op = ">="
        elif op_rev == "=": op = "="
        else: return None # 理論上不會發生，因為運算符已定義
        
        return (var, op, val)
    
    return None # 解析失敗

# --- 頂層函式 (Top-Level Functions) ---
# [頂層函式]：嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# [自動重載]：確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level=1):
    """
    生成 K12 數學「不等式的運算規則」題目。
    - level: 題目難度等級 (目前未使用，預設為1)。
    """
    # [隨機分流]：使用 random.choice 或 if/elif 邏輯，明確對應到 RAG 中的例題。
    # Added problem_type 6 to specifically map to RAG Ex 3.
    problem_type = random.choice([1, 2, 3, 4, 5, 6]) 
    
    # [數據禁絕常數]：使用 random.randint 生成所有幾何長度、角度與面積。
    # 確保變數 a, b, c 在 K12 合理範圍內。
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    # 確保 c 不為零，以免產生除以零或無意義的乘法
    while c == 0:
        c = random.randint(-10, 10)

    question_text = ""
    correct_answer = ""
    
    # [範例]：Spec 描述如何將 RAG 例題中的數據「動態化」，而不是創造新題型。
    # Helper to convert op to LaTeX (V16.13)
    def op_to_latex(op):
        return op.replace(">=", r"\ge").replace("<=", r"\le")

    if problem_type == 1: # Type 1 (Property: Addition/Subtraction)
        # 例題: 若 $a > b$，則 $a+c \ ? \ b+c$。
        
        initial_op = random.choice([">", "<", ">=", "<="])
        
        # 若為嚴格不等式，確保 a != b，使問題有意義
        if initial_op in [">", "<"]:
            while a == b:
                b = random.randint(-10, 10)
        
        operation = random.choice(["add", "subtract"])
        
        # [V16.15 Parenthesis Protection]
        c_str = f"({c})" if c < 0 else str(c)

        if operation == "add":
            # [排版與 LaTeX 安全]：嚴禁使用 f-string 或 % 格式化。
            question_text_template = r"已知 $a {op} b$，則 $a + {c_val} \ ? \ b + {c_val}$。請填入正確的不等號。"
            question_text = question_text_template.replace("{op}", op_to_latex(initial_op)).replace("{c_val}", c_str)
            final_op = initial_op # 加減法不改變不等號方向
        else: # subtract
            question_text_template = r"已知 $a {op} b$，則 $a - {c_val} \ ? \ b - {c_val}$。請填入正確的不等號。"
            question_text = question_text_template.replace("{op}", op_to_latex(initial_op)).replace("{c_val}", c_str)
            final_op = initial_op # 加減法不改變不等號方向
            
        correct_answer = op_to_latex(final_op) # 答案僅為運算符
        
    elif problem_type == 2: # Type 2 (Property: Multiplication/Division by Positive)
        # 例題: 若 $x > 5$，解 $2x \ ? \ 10$。
        
        x_boundary = random.randint(-10, 10)
        initial_op = random.choice([">", "<", ">=", "<="])
        
        # 生成一個正數乘數/除數 (multiplier > 0)
        multiplier = random.randint(1, 5) # 確保為正數
        
        operation = random.choice(["multiply", "divide"])
        
        if operation == "multiply":
            initial_inequality_str = r"x {op} {val}".replace("{op}", op_to_latex(initial_op)).replace("{val}", str(x_boundary))
            
            question_text_template = r"已知 ${initial_ineq}$，求 ${multiplier_val}x \ ? \ {result_val}$ 的不等式。"
            question_text = question_text_template.replace("{initial_ineq}", initial_inequality_str) \
                                                .replace("{multiplier_val}", str(multiplier)) \
                                                .replace("{result_val}", str(multiplier * x_boundary))
            final_op = initial_op # 正數乘除不改變不等號方向
            answer_val = multiplier * x_boundary
        else: # divide
            # [公式計算]：確保邊界值為乘數的倍數，產生整數答案。
            temp_x_boundary_base = random.randint(-5, 5)
            x_boundary = temp_x_boundary_base * multiplier
            
            initial_inequality_str = r"x {op} {val}".replace("{op}", op_to_latex(initial_op)).replace("{val}", str(x_boundary))
            
            # [V16.14 Fraction Fix] Use \frac instead of /
            question_text_template = r"已知 ${initial_ineq}$，求 $\frac{x}{ {divisor_val} } \ ? \ {result_val}$ 的不等式。"
            question_text = question_text_template.replace("{initial_ineq}", initial_inequality_str) \
                                                .replace("{divisor_val}", str(multiplier)) \
                                                .replace("{result_val}", str(x_boundary // multiplier)) # 整數除法
            final_op = initial_op # 正數乘除不改變不等號方向
            answer_val = x_boundary // multiplier

        # 正確答案格式: "x > 5" (LaTeX Standard)
        correct_answer_template = r"$x {op} {val}$".replace("{op}", op_to_latex(final_op)).replace("{val}", str(answer_val))
        correct_answer = correct_answer_template
        
    elif problem_type == 3: # Type 3 (Property: Multiplication/Division by Negative)
        # 例題: 若 $x > 5$，解 $-2x \ ? \ -10$。不等號方向翻轉。
        
        x_boundary = random.randint(-10, 10)
        initial_op = random.choice([">", "<", ">=", "<="])

        # 生成一個負數乘數/除數 (multiplier < 0)
        multiplier = random.randint(-5, -1) # 確保為負數
        
        operation = random.choice(["multiply", "divide"])
        
        # 判斷翻轉後的不等號
        flipped_op = ""
        if initial_op == ">": flipped_op = "<"
        elif initial_op == "<": flipped_op = ">"
        elif initial_op == ">=": flipped_op = "<="
        elif initial_op == "<=": flipped_op = ">="
        
        if operation == "multiply":
            initial_inequality_str = r"x {op} {val}".replace("{op}", op_to_latex(initial_op)).replace("{val}", str(x_boundary))
            
            question_text_template = r"已知 ${initial_ineq}$，求 ${multiplier_val}x \ ? \ {result_val}$ 的不等式。"
            question_text = question_text_template.replace("{initial_ineq}", initial_inequality_str) \
                                                .replace("{multiplier_val}", str(multiplier)) \
                                                .replace("{result_val}", str(multiplier * x_boundary))
            final_op = flipped_op # 不等號翻轉
            answer_val = multiplier * x_boundary
        else: # divide
            # 確保邊界值為乘數絕對值的倍數，產生整數答案。
            temp_x_boundary_base = random.randint(-5, 5)
            x_boundary = temp_x_boundary_base * abs(multiplier)
            
            initial_inequality_str = r"x {op} {val}".replace("{op}", op_to_latex(initial_op)).replace("{val}", str(x_boundary))
            
            # [V16.14 Fraction Fix] Use \frac instead of /
            question_text_template = r"已知 ${initial_ineq}$，求 $\frac{x}{ {divisor_val} } \ ? \ {result_val}$ 的不等式。"
            question_text = question_text_template.replace("{initial_ineq}", initial_inequality_str) \
                                                .replace("{divisor_val}", str(multiplier)) \
                                                .replace("{result_val}", str(x_boundary // multiplier)) # 整數除法
            final_op = flipped_op # 不等號翻轉
            answer_val = x_boundary // multiplier

        correct_answer_template = r"$x {op} {val}$".replace("{op}", op_to_latex(final_op)).replace("{val}", str(answer_val))
        correct_answer = correct_answer_template

    elif problem_type == 4: # Type 4 (Maps to RAG Ex 1 & 2): Solve Ax + B op C
        # Generate coefficients and constants
        A = random.randint(-5, 5)
        while A == 0: # A cannot be zero
            A = random.randint(-5, 5)
        
        B = random.randint(-10, 10)
        C = random.randint(-10, 10)
        
        initial_op = random.choice([">", "<", ">=", "<="])

        # Solve for x: Ax + B > C  =>  Ax > C - B
        # To ensure integer solution for x, (C - B) must be divisible by A.
        # Adjust C to make (C - B) a multiple of A.
        # Let C_target = B + k*A for some integer k.
        # k can be randomly chosen, ensuring a reasonable solution range.
        k = random.randint(-5, 5)
        C = B + k * A # This ensures (C - B) is a multiple of A.
        
        right_side_after_subtraction = C - B

        boundary_val = right_side_after_subtraction // A

        final_op = initial_op
        if A < 0:
            # Flip operator if A is negative
            if initial_op == ">": final_op = "<"
            elif initial_op == "<": final_op = ">"
            elif initial_op == ">=": final_op = "<="
            elif initial_op == "<=": final_op = ">="
        
        # Format B for display (e.g., +5 or -3). Handle B=0 case.
        B_part = ""
        if B != 0:
            B_sign_display = "+" if B >= 0 else "-"
            B_abs_display = abs(B)
            B_part = r" {B_sign_display} {B_abs_display}".replace("{B_sign_display}", B_sign_display).replace("{B_abs_display}", str(B_abs_display))
        
        # Format A for display (e.g., 1x -> x, -1x -> -x, 2x -> 2x)
        A_part = ""
        if A == 1:
            A_part = "x"
        elif A == -1:
            A_part = "-x"
        else:
            A_part = r"{A_val}x".replace("{A_val}", str(A))

        question_text_template = r"求解不等式 $ {A_part}{B_part} {op} {C_val} $。"
        question_text = question_text_template.replace("{A_part}", A_part) \
                                            .replace("{B_part}", B_part) \
                                            .replace("{op}", op_to_latex(initial_op)) \
                                            .replace("{C_val}", str(C))
        
        correct_answer_template = r"$x {op} {val}$".replace("{op}", op_to_latex(final_op)).replace("{val}", str(boundary_val))
        correct_answer = correct_answer_template

    elif problem_type == 5: # Type 5 (General Property: Comparison of expressions)
        # 例題: 若 $a > b$，則 $a+3 \ ? \ b+3$。或 $-2a \ ? \ -2b$。
        
        initial_op = random.choice([">", "<", ">=", "<="])
        
        # 若為嚴格不等式，確保 a != b
        if initial_op in [">", "<"]:
            while a == b:
                b = random.randint(-10, 10)
        
        question_text_template = r"已知 $a {op_ab} b$，則 $ {expr_a} \ ? \ {expr_b}$。請填入正確的不等號。"
        
        # 選擇對兩邊應用的操作類型
        op_type = random.choice(["add_sub", "mult_pos", "mult_neg"])
        
        if op_type == "add_sub":
            const = random.randint(-10, 10)
            op_sign = "+" if const >= 0 else "-"
            abs_const = abs(const)
            expr_a = r"a {op_sign} {abs_const}".replace("{op_sign}", op_sign).replace("{abs_const}", str(abs_const))
            expr_b = r"b {op_sign} {abs_const}".replace("{op_sign}", op_sign).replace("{abs_const}", str(abs_const))
            final_op = initial_op # 加減法不改變不等號方向
        elif op_type == "mult_pos":
            const = random.randint(1, 5) # 正數乘數
            expr_a = r"{const}a".replace("{const}", str(const))
            expr_b = r"{const}b".replace("{const}", str(const))
            final_op = initial_op # 正數乘除不改變不等號方向
        else: # mult_neg
            const = random.randint(-5, -1) # 負數乘數
            expr_a = r"{const}a".replace("{const}", str(const))
            expr_b = r"{const}b".replace("{const}", str(const))
            # 負數乘除，不等號翻轉
            if initial_op == ">": final_op = "<"
            elif initial_op == "<": final_op = ">"
            elif initial_op == ">=": final_op = "<="
            elif initial_op == "<=": final_op = ">="
            
        question_text = question_text_template.replace("{op_ab}", op_to_latex(initial_op)) \
                                                .replace("{expr_a}", expr_a) \
                                                .replace("{expr_b}", expr_b)
        correct_answer = op_to_latex(final_op) # 答案僅為運算符

    elif problem_type == 6: # Type 6 (Maps to RAG Ex 3): Solve (x - K)/D1 op (-x + K)/D2
        # This type specifically mirrors the structure of RAG Ex 3: (x-5)/3 < (-x+5)/2
        # The general form is (x - K) / D1 op (-x + K) / D2, which simplifies to x op K.
        
        # Generate D1, D2 (positive denominators)
        D1 = random.randint(2, 5)
        D2 = random.randint(2, 5)
        
        # Generate K (the boundary value for x)
        K = random.randint(-8, 8)
        
        initial_op = random.choice([">", "<", ">=", "<="])

        # Construct the left side: (x - K) / D1
        # If K is negative, (x - (-K)) becomes (x + abs(K))
        left_numerator_part = ""
        if K >= 0:
            left_numerator_part = r"x - {K_val}".replace("{K_val}", str(K))
        else:
            left_numerator_part = r"x + {K_val}".replace("{K_val}", str(abs(K)))
        
        left_side = r"\frac{{{num}}}{{{den}}}".replace("{{num}}", left_numerator_part).replace("{{den}}", str(D1))

        # Construct the right side: (-x + K) / D2
        # If K is negative, (-x + (-K)) becomes (-x - abs(K))
        right_numerator_part = ""
        if K >= 0:
            right_numerator_part = r"-x + {K_val}".replace("{K_val}", str(K))
        else:
            right_numerator_part = r"-x - {K_val}".replace("{K_val}", str(abs(K)))

        right_side = r"\frac{{{num}}}{{{den}}}".replace("{{num}}", right_numerator_part).replace("{{den}}", str(D2))
        
        question_text_template = r"解一元一次不等式 $ {left_side} {op} {right_side} $。"
        question_text = question_text_template.replace("{left_side}", left_side) \
                                                .replace("{op}", op_to_latex(initial_op)) \
                                                .replace("{right_side}", right_side)
        
        # The solution is always x op K (since D1+D2 is positive, no flip required)
        final_op = initial_op
        boundary_val = K
        
        correct_answer_template = r"$x {op} {val}$".replace("{op}", op_to_latex(final_op)).replace("{val}", str(boundary_val))
        correct_answer = correct_answer_template

    # [視覺化與輔助函式通用規範]：若無圖形，image_base64 留空。
    image_base64 = ""

    # [數據與欄位]：返回字典必須且僅能包含指定欄位。
    # [時間戳記]：更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 'answer' 字段通常保存原始計算值，此處與 correct_answer 相同。
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    檢查用戶對不等式問題的回答。
    此函數嚴格實作 V13.6 規定的「4-line check logic」，並利用輔助函式處理字串解析，
    以符合「禁絕複雜比對」要求。
    """
    # `correct_answer` 可能是單一運算符 (例如 ">") 或不等式字串 (例如 "x > 5")。

    # 1. 處理答案僅為運算符的情況 (Type 1, Type 5)
    # 1. 處理答案僅為運算符的情況 (Type 1, Type 5)
    # Check if correct_answer is just a LaTeX operator
    if correct_answer in [">", "<", r"\ge", r"\le"]:
        user_ans_norm = user_answer.strip()
        
        # Map user input to standardized operators
        # Allow >=, <=, \ge, \le, unicode, etc.
        op_map = {
            ">=": r"\ge", "=>": r"\ge", r"\ge": r"\ge", "\u2265": r"\ge",
            "<=": r"\le", "=<": r"\le", r"\le": r"\le", "\u2264": r"\le",
            ">": ">", "<": "<"
        }
        user_std = op_map.get(user_ans_norm, user_ans_norm)
        
        if user_std == correct_answer:
            return True
        return False

    # 2. 處理答案為不等式字串的情況 (Type 2, 3, 4, 6)
    # [強制運算]：透過解析將正確答案轉換為標準形式 (變數, 運算符, 值)
    correct_parsed = _parse_inequality_expression(correct_answer)
    if not correct_parsed:
        # 若正確答案本身格式不正確，則返回 False (不應發生，因為 correct_answer 由 generate 產生)
        return False 

    # 將用戶答案解析為標準形式
    user_parsed = _parse_inequality_expression(user_answer)
    if not user_parsed:
        # 若用戶答案格式不正確，則返回 False
        return False

    # 提取組件進行比較
    correct_var, correct_op, correct_val = correct_parsed
    user_var, user_op, user_val = user_parsed

    # 3. 比較各組件以判斷等價性。這是核心邏輯。
    # V13.6 Exact Check Logic:
    # - 變數必須匹配。
    # - 運算符必須匹配 (經 _parse_inequality_expression 規範化後)。
    # - 數值必須在浮點數容忍範圍內匹配。
    # [禁絕複雜比對]：此處為數值比較，而非字串拆解邏輯。
    if correct_var == user_var and correct_op == user_op and abs(correct_val - user_val) < 1e-9:
        return True
    
    # 4. 若任何組件不匹配，則返回 False。
    return False

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
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

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
