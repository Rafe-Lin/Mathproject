# ==============================================================================
# ID: jh_數學2上_ValueOfSquareRootA
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 45.01s | RAG: 5 examples
# Created At: 2026-01-18 15:02:00
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



from datetime import datetime
import re
import json

# --- Helper Functions ---

def _format_latex_value(value):
    """
    描述: 將數值格式化為 LaTeX 友好的字串，確保整數顯示為 5 而非 5.0。
    回傳值: str。
    防洩漏原則: 僅處理題目已知數據，不涉及答案數據。
    """
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    return str(value)

def _get_prime_factors_with_exponents(num):
    """
    描述: 接收一個整數，回傳其質因數分解結果 (字典形式，鍵為質因數，值為次方)。
    回傳值: dict。
    防洩漏原則: 僅處理題目已知數據。
    """
    factors = {}
    d = 2
    temp = num
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def _get_prime_factorization_str(factors):
    """
    描述: 將質因數分解字典格式化為 LaTeX 字串 (例如 2^2 \times 3)。
    回傳值: str。
    防洩漏原則: 僅處理題目已知數據。
    """
    if not factors:
        return "1"
    parts = []
    for p, e in sorted(factors.items()):
        if e == 1:
            parts.append(_format_latex_value(p))
        else:
            parts.append(r"{}^{}".format(_format_latex_value(p), _format_latex_value(e)))
    return r" \times ".join(parts)

# --- Check Logic ---


    """
    閱卷決定論 (Deterministic Grading):
    `check` 函式嚴禁呼叫任何 `random` 模組或重新執行 `generate` 邏輯。
    `check` 函式必須完全依賴傳入的 `correct_answer` 參數作為唯一的真理來源。
    """
    
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean_input(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, ans=
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
        return s

    u = clean_input(user_answer)
    c = clean_input(correct_answer)

    # Helper to parse potential fractions/floats
    def parse_val(val_str):
        if "/" in val_str:
            n, d = map(float, val_str.split("/"))
            return n / d
        return float(val_str)

    # --- Type-specific checks ---
    
    # Type 2: Multiple answers (e.g., "3,4")
    if "," in c:
        try:
            u_parts = sorted([parse_val(p) for p in u.split(",")])
            c_parts = sorted([parse_val(p) for p in c.split(",")])
            if len(u_parts) == len(c_parts) and all(math.isclose(up, cp, rel_tol=1e-5) for up, cp in zip(u_parts, c_parts)):
                return {"correct": True, "result": "正確！"}
        except ValueError: # Catch cases where user input parts are not numbers
            pass 

    # Type 3: Comparison symbols (e.g., "1" for '>', "-1" for '<', "0" for '=')
    comparison_map = {
        ">": "1", "greaterthan": "1", "大于": "1", "大於": "1",
        "<": "-1", "lessthan": "-1", "小于": "-1", "小於": "-1",
        "=": "0", "equal": "0", "equals": "0", "等于": "0", "等於": "0"
    }
    if c in ["1", "-1", "0"]: # Indicates a comparison type question
        mapped_u = comparison_map.get(u, u) # Try to map user input
        if mapped_u == c:
            return {"correct": True, "result": "正確！"}
    
    # 2. 嘗試數值比對 (支援分數與小數) - General for Type 1, 4 and parts of Type 3
    try:
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch cases where user input is not a number
        pass 

    # 3. 降級為字串比對 (Final fallback)
    if u == c: 
        return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": f"答案錯誤。"}

# --- Problem Generation Function ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4]) # Randomly choose problem type

    question_text = ""
    correct_answer = ""
    solution_text = ""
    
    if problem_type == 1:
        # Type 1: 找出平方根 (Finding Square Roots of Perfect Squares)
        # 對應機制: Maps to RAG Example 1, 2 (平方根的基本定義)。
        # 隨機化參數:
        #   生成一個隨機整數 k (例如 random.randint(2, 15))。
        #   被開方數 a 則為 k * k。
        k = random.randint(2, 15)
        a = k * k
        question_text = r"求 $\sqrt{{{a}}}$ 的值。" \
                        .replace("{a}", _format_latex_value(a))
        correct_answer = _format_latex_value(k)
        solution_text = r"由於 ${k_val}^2 = {a_val}$，因此 $\sqrt{{{a_val}}} = {k_val}$。" \
                        .replace("{k_val}", _format_latex_value(k)) \
                        .replace("{a_val}", _format_latex_value(a))

    elif problem_type == 2:
        # Type 2: 估計平方根的範圍 (Estimating Square Root Range)
        # 對應機制: Maps to RAG Example 3, 4 (平方根的估計與範圍判斷)。
        # 隨機化參數:
        #   生成一個隨機整數 k (例如 random.randint(3, 15))。
        #   計算 lower_bound = k * k 和 upper_bound = (k + 1) * (k + 1)。
        #   被開方數 a 則在 (lower_bound + 1, upper_bound - 1) 之間隨機生成，確保 a 不是完美平方數。
        k = random.randint(3, 15)
        lower_bound = k * k
        upper_bound = (k + 1) * (k + 1)
        
        # Ensure a is not a perfect square and is strictly between k^2 and (k+1)^2
        # The range (lower_bound + 1, upper_bound - 1) naturally excludes perfect squares
        # since lower_bound and upper_bound are consecutive perfect squares.
        a_candidates = list(range(lower_bound + 1, upper_bound))
        if not a_candidates: # Fallback for extremely narrow ranges (shouldn't happen with k>=3)
             a = random.randint(lower_bound + 1, upper_bound - 1)
        else:
             a = random.choice(a_candidates)

        question_text = r"$\sqrt{{{a}}}$ 的值介於哪兩個連續整數之間？" \
                        .replace("{a}", _format_latex_value(a))
        correct_answer = "{},{}".format(_format_latex_value(k), _format_latex_value(k + 1))
        solution_text = r"因為 ${k_val}^2 = {lower_bound_val}$ 且 $({k_plus_1_val})^2 = {upper_bound_val}$，" \
                        r"又 ${lower_bound_val} < {a_val} < {upper_bound_val}$，" \
                        r"所以 $\sqrt{{{lower_bound_val}}} < \sqrt{{{a_val}}} < \sqrt{{{upper_bound_val}}}$。" \
                        r"因此 ${k_val} < \sqrt{{{a_val}}} < {k_plus_1_val}$。$\sqrt{{{a_val}}}$ 的值介於 {k_val} 和 {k_plus_1_val} 之間。" \
                        .replace("{k_val}", _format_latex_value(k)) \
                        .replace("{k_plus_1_val}", _format_latex_value(k + 1)) \
                        .replace("{lower_bound_val}", _format_latex_value(lower_bound)) \
                        .replace("{upper_bound_val}", _format_latex_value(upper_bound)) \
                        .replace("{a_val}", _format_latex_value(a))

    elif problem_type == 3:
        # Type 3: 比較平方根的大小 (Comparing Square Roots)
        # 對應機制: Maps to RAG Example 5。
        scenario = random.choice([1, 2]) # 1: sqrt(A) vs B, 2: sqrt(A) vs sqrt(B)
        
        if scenario == 1:
            # 情境 1 (比較 sqrt(A) 與 B)
            # 生成 A = random.randint(4, 200)。
            # 生成 B = random.randint(max(1, int(math.sqrt(A) - 3)), int(math.sqrt(A) + 3))。
            A = random.randint(4, 200)
            sqrt_A_approx = math.sqrt(A)
            B = random.randint(max(1, int(sqrt_A_approx - 3)), int(sqrt_A_approx + 3))
            
            # Determine comparison result
            if A > B*B:
                comparison_symbol = ">"
                correct_answer = "1"
            elif A < B*B:
                comparison_symbol = "<"
                correct_answer = "-1"
            else: # A == B*B
                comparison_symbol = "="
                correct_answer = "0"
            
            question_text = r"比較 $\sqrt{{{A_val}}}$ 與 ${B_val}$ 的大小。（請填入 >、< 或 =）" \
                            .replace("{A_val}", _format_latex_value(A)) \
                            .replace("{B_val}", _format_latex_value(B))
            
            B_squared = B * B
            solution_text = r"比較 $\sqrt{{{A_val}}}$ 與 ${B_val}$ 的大小。我們可以將 ${B_val}$ 寫成平方根的形式：${B_val} = \sqrt{{{B_squared_val}}}$。" \
                            r"因為 $\sqrt{{{A_val}}} {symbol} \sqrt{{{B_squared_val}}}$，所以 $\sqrt{{{A_val}}} {symbol} {B_val}$。" \
                            .replace("{A_val}", _format_latex_value(A)) \
                            .replace("{B_val}", _format_latex_value(B)) \
                            .replace("{B_squared_val}", _format_latex_value(B_squared)) \
                            .replace("{symbol}", comparison_symbol)

        else: # scenario == 2
            # 情境 2 (比較 sqrt(A) 與 sqrt(B))
            # 生成 A = random.randint(2, 100)。
            # 生成 B = random.randint(2, 100)，確保 A != B 以提供有意義的比較。
            A = random.randint(2, 100)
            B = random.randint(2, 100)
            while A == B: # Ensure A and B are different
                B = random.randint(2, 100)
            
            # Determine comparison result
            if A > B:
                comparison_symbol = ">"
                correct_answer = "1"
            elif A < B:
                comparison_symbol = "<"
                correct_answer = "-1"
            else: # A == B, though we ensured A != B, this branch is for completeness
                comparison_symbol = "="
                correct_answer = "0"
            
            question_text = r"比較 $\sqrt{{{A_val}}}$ 與 $\sqrt{{{B_val}}}$ 的大小。（請填入 >、< 或 =）" \
                            .replace("{A_val}", _format_latex_value(A)) \
                            .replace("{B_val}", _format_latex_value(B))
            
            solution_text = r"比較 $\sqrt{{{A_val}}}$ 與 $\sqrt{{{B_val}}}$ 的大小。當被開方數皆為正數時，被開方數越大，其平方根越大。" \
                            r"因為 ${A_val} {symbol} {B_val}$，所以 $\sqrt{{{A_val}}} {symbol} \sqrt{{{B_val}}}$。" \
                            .replace("{A_val}", _format_latex_value(A)) \
                            .replace("{B_val}", _format_latex_value(B)) \
                            .replace("{symbol}", comparison_symbol)

    elif problem_type == 4:
        # Type 4: 根號運算中的整數判斷 (Integer Check within Square Root Operations)
        # 對應機制: Maps to RAG Example 7, 8 (使根號為整數的條件判斷)。
        # 隨機化參數:
        #   生成一個隨機整數 N (例如 random.randint(10, 100))，確保 N 不是一個完美平方數。
        #   計算 N 的質因數分解，找出所有次方為奇數的質因數，將這些質因數相乘即為 k 的最小值。
        
        N = random.randint(10, 100)
        # Ensure N is not a perfect square
        while math.isqrt(N)**2 == N: 
            N = random.randint(10, 100)
        
        factors = _get_prime_factors_with_exponents(N)
        
        k_val = 1
        for p, e in factors.items():
            if e % 2 != 0:
                k_val *= p
        
        # Format prime factorization for solution
        prime_factorization_N_str = _get_prime_factorization_str(factors)
        
        question_text = r"若 $\sqrt{{{N_val} \times k}}$ 為一個正整數，則最小的正整數 $k$ 為多少？" \
                        .replace("{N_val}", _format_latex_value(N))
        correct_answer = _format_latex_value(k_val)
        
        solution_text = r"欲使 $\sqrt{{{N_val} \times k}}$ 為正整數，則 ${N_val} \times k$ 必須為一個完全平方數。" \
                        r"將 ${N_val}$ 進行質因數分解：${N_val} = {prime_factorization_N_str_val}$。" \
                        r"要使 ${N_val} \times k$ 為完全平方數，其每個質因數的次方都必須是偶數。" \
                        r"因此，最小的正整數 $k = {k_val_str}$。" \
                        .replace("{N_val}", _format_latex_value(N)) \
                        .replace("{prime_factorization_N_str_val}", prime_factorization_N_str) \
                        .replace("{k_val_str}", _format_latex_value(k_val))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text, # As per spec, 'answer' field holds solution_text
        "image_base64": None, # No image for this skill
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
