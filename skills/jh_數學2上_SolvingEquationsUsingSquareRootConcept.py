# ==============================================================================
# ID: jh_數學2上_SolvingEquationsUsingSquareRootConcept
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 59.90s | RAG: 4 examples
# Created At: 2026-01-19 12:03:49
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


import re
from datetime import datetime


# 輔助函式 (Helper Functions)
# 必須回傳結果，若用於拼接 question_text 需強制轉為字串。
# 嚴禁將「答案數據」傳入繪圖函式 (本技能無繪圖)。

def _generate_perfect_square(min_base=2, max_base=10):
    """
    生成一個隨機的完全平方數。
    Args:
        min_base (int): 基礎數字的最小值。
        max_base (int): 基礎數字的最大值。
    Returns:
        int: 完全平方數。
    """
    base = random.randint(min_base, max_base)
    return base * base

def _generate_non_perfect_square(min_val=5, max_val=50):
    """
    生成一個隨機的正整數，但不是完全平方數。
    Args:
        min_val (int): 數字的最小值。
        max_val (int): 數字的最大值。
    Returns:
        int: 非完全平方數。
    """
    while True:
        num = random.randint(min_val, max_val)
        # Ensure it's positive and not a perfect square
        if num > 0 and int(math.sqrt(num))**2 != num:
            return num

def _generate_integer_coefficient(min_val=2, max_val=5):
    """
    生成一個用於係數的非零整數。
    Args:
        min_val (int): 整數的最小值。
        max_val (int): 整數的最大值。
    Returns:
        int: 非零整數。
    """
    return random.randint(min_val, max_val)

def _generate_integer_constant(min_val=-5, max_val=5, exclude_zero=False):
    """
    生成一個用於常數項的整數。
    Args:
        min_val (int): 整數的最小值。
        max_val (int): 整數的最大值。
        exclude_zero (bool): 是否排除 0。
    Returns:
        int: 整數。
    """
    val = random.randint(min_val, max_val)
    if exclude_zero and val == 0:
        return _generate_integer_constant(min_val, max_val, exclude_zero)
    return val

def _format_rounded_solution(val, decimal_places=2):
    """
    將浮點數格式化為指定小數點位數的字串。
    Args:
        val (float): 浮點數。
        decimal_places (int): 小數點位數。
    Returns:
        str: 格式化後的字串。
    """
    return f"{val:.{decimal_places}f}"

def _get_simplified_sqrt_form_str(n):
    """
    返回簡化後的平方根 LaTeX 字串表示，例如 '2\\sqrt{3}' 或 '5'。
    Args:
        n (int): 欲開根號的數字。
    Returns:
        str: 簡化平方根的 LaTeX 字串。
    """
    if n < 0:
        return r"\text{無實數解}" # In this problem design, n should always be non-negative
    if n == 0:
        return "0"
    
    # Check if n is a perfect square
    sqrt_n_int = int(math.sqrt(n))
    if sqrt_n_int * sqrt_n_int == n:
        return str(sqrt_n_int)
    
    coeff = 1
    radicand = n
    
    # Find largest perfect square factor
    for i in range(2, int(math.sqrt(n)) + 1):
        while radicand % (i*i) == 0:
            coeff *= i
            radicand //= (i*i)
            
    if coeff == 1:
        return r"\sqrt{" + str(radicand) + "}"
    else:
        return str(coeff) + r"\sqrt{" + str(radicand) + "}"

# 頂層函式：generate 與 check
# 嚴禁使用 class 封裝。必須直接定義於模組最外層。
# 確保代碼不依賴全域狀態。

def generate(level=1):
    """
    生成一個利用平方根概念解一元二次方程式的題目。
    Args:
        level (int): 難度等級 (目前未使用)。
    Returns:
        dict: 包含題目、正確答案、詳解和圖片的字典。
    """
    problem_type = random.choice([1, 2, 3, 4, 5, 6]) # 隨機選擇題型，對應 RAG 範例

    question_text = ""
    correct_answer_raw = []
    solution_text_latex = ""
    
    decimal_places = 2 # 預設無理數解四捨五入到小數點後 2 位

    if problem_type == 1: # Maps to Example 1: x^2 = k
        is_perfect_square = random.choice([True, False])
        if is_perfect_square:
            k = _generate_perfect_square(min_base=2, max_base=10) # k = 4 to 100
            sol1 = math.sqrt(k)
            sol2 = -math.sqrt(k)
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            solution_text_latex = r"x^2 = " + str(k) + r" \\ x = \pm \sqrt{" + str(k) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k)
            question_text = r"解方程式 $x^2 = " + str(k) + "$。"
        else:
            k = _generate_non_perfect_square(min_val=5, max_val=50) # k = 5 to 50, 非完全平方數
            sol1 = math.sqrt(k)
            sol2 = -math.sqrt(k)
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            solution_text_latex = r"x^2 = " + str(k) + r" \\ x = \pm \sqrt{" + str(k) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k) + r" \approx \pm " + _format_rounded_solution(sol1, decimal_places)
            question_text = r"解方程式 $x^2 = " + str(k) + "$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    elif problem_type == 2: # Maps to Example 2: (x+a)^2 = k
        a = _generate_integer_constant(min_val=-5, max_val=5, exclude_zero=True)
        is_perfect_square = random.choice([True, False])
        
        op_a = "+" if a > 0 else "" # For formatting (x+a) or (x-a)
        
        if is_perfect_square:
            k = _generate_perfect_square(min_base=2, max_base=10)
            sqrt_k = int(math.sqrt(k))
            sol1 = -a + sqrt_k
            sol2 = -a - sqrt_k
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            solution_text_latex = r"(x " + op_a + str(a) + r")^2 = " + str(k) + r" \\ x " + op_a + str(a) + r" = \pm \sqrt{" + str(k) + r"} \\ x " + op_a + str(a) + r" = \pm " + _get_simplified_sqrt_form_str(k) + r" \\ x = " + ("-" if a > 0 else "+") + str(abs(a)) + r" \pm " + _get_simplified_sqrt_form_str(k)
            question_text = r"解方程式 $(x " + op_a + str(a) + r")^2 = " + str(k) + "$。"
        else:
            k = _generate_non_perfect_square(min_val=5, max_val=50)
            sqrt_k = math.sqrt(k)
            sol1 = -a + sqrt_k
            sol2 = -a - sqrt_k
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            solution_text_latex = r"(x " + op_a + str(a) + r")^2 = " + str(k) + r" \\ x " + op_a + str(a) + r" = \pm \sqrt{" + str(k) + r"} \\ x " + op_a + str(a) + r" = \pm " + _get_simplified_sqrt_form_str(k) + r" \\ x = " + ("-" if a > 0 else "+") + str(abs(a)) + r" \pm " + _get_simplified_sqrt_form_str(k) + r" \approx " + _format_rounded_solution(sol1, decimal_places) + r", " + _format_rounded_solution(sol2, decimal_places)
            question_text = r"解方程式 $(x " + op_a + str(a) + r")^2 = " + str(k) + "$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    elif problem_type == 3: # Maps to Example 3: ax^2 = k
        a = _generate_integer_coefficient(min_val=2, max_val=5)
        is_perfect_square = random.choice([True, False])
        
        if is_perfect_square:
            # 確保 k/a 是完全平方數
            base_k_over_a = random.randint(2, 7)
            k_over_a = base_k_over_a * base_k_over_a
            k = a * k_over_a
            sol1 = math.sqrt(k_over_a)
            sol2 = -math.sqrt(k_over_a)
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            solution_text_latex = str(a) + r"x^2 = " + str(k) + r" \\ x^2 = \frac{" + str(k) + r"}{" + str(a) + r"} \\ x^2 = " + str(k_over_a) + r" \\ x = \pm \sqrt{" + str(k_over_a) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k_over_a)
            question_text = r"解方程式 $" + str(a) + r"x^2 = " + str(k) + "$。"
        else:
            # 確保 k/a 是非完全平方數
            k_over_a = _generate_non_perfect_square(min_val=5, max_val=50)
            k = a * k_over_a
            sol1 = math.sqrt(k_over_a)
            sol2 = -math.sqrt(k_over_a)
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            solution_text_latex = str(a) + r"x^2 = " + str(k) + r" \\ x^2 = \frac{" + str(k) + r"}{" + str(a) + r"} \\ x^2 = " + str(k_over_a) + r" \\ x = \pm \sqrt{" + str(k_over_a) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k_over_a) + r" \approx \pm " + _format_rounded_solution(sol1, decimal_places)
            question_text = r"解方程式 $" + str(a) + r"x^2 = " + str(k) + "$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    elif problem_type == 4: # Maps to Example 4: a(x+b)^2 = k
        a = _generate_integer_coefficient(min_val=2, max_val=5)
        b = _generate_integer_constant(min_val=-5, max_val=5, exclude_zero=True)
        is_perfect_square = random.choice([True, False])

        op_b = "+" if b > 0 else "" # For formatting (x+b) or (x-b)
        
        if is_perfect_square:
            # 確保 k/a 是完全平方數
            base_k_over_a = random.randint(2, 7)
            k_over_a = base_k_over_a * base_k_over_a
            k = a * k_over_a
            sqrt_k_over_a = int(math.sqrt(k_over_a))
            sol1 = -b + sqrt_k_over_a
            sol2 = -b - sqrt_k_over_a
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            solution_text_latex = str(a) + r"(x " + op_b + str(b) + r")^2 = " + str(k) + r" \\ (x " + op_b + str(b) + r")^2 = \frac{" + str(k) + r"}{" + str(a) + r"} \\ (x " + op_b + str(b) + r")^2 = " + str(k_over_a) + r" \\ x " + op_b + str(b) + r" = \pm \sqrt{" + str(k_over_a) + r"} \\ x " + op_b + str(b) + r" = \pm " + _get_simplified_sqrt_form_str(k_over_a) + r" \\ x = " + ("-" if b > 0 else "+") + str(abs(b)) + r" \pm " + _get_simplified_sqrt_form_str(k_over_a)
            question_text = r"解方程式 $" + str(a) + r"(x " + op_b + str(b) + r")^2 = " + str(k) + "$。"
        else:
            # 確保 k/a 是非完全平方數
            k_over_a = _generate_non_perfect_square(min_val=5, max_val=50)
            k = a * k_over_a
            sqrt_k_over_a = math.sqrt(k_over_a)
            sol1 = -b + sqrt_k_over_a
            sol2 = -b - sqrt_k_over_a
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            solution_text_latex = str(a) + r"(x " + op_b + str(b) + r")^2 = " + str(k) + r" \\ (x " + op_b + str(b) + r")^2 = \frac{" + str(k) + r"}{" + str(a) + r"} \\ (x " + op_b + str(b) + r")^2 = " + str(k_over_a) + r" \\ x " + op_b + str(b) + r" = \pm \sqrt{" + str(k_over_a) + r"} \\ x " + op_b + str(b) + r" = \pm " + _get_simplified_sqrt_form_str(k_over_a) + r" \\ x = " + ("-" if b > 0 else "+") + str(abs(b)) + r" \pm " + _get_simplified_sqrt_form_str(k_over_a) + r" \approx " + _format_rounded_solution(sol1, decimal_places) + r", " + _format_rounded_solution(sol2, decimal_places)
            question_text = r"解方程式 $" + str(a) + r"(x " + op_b + str(b) + r")^2 = " + str(k) + "$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    elif problem_type == 5: # Maps to Example 5: ax^2 + c = 0
        a = _generate_integer_coefficient(min_val=2, max_val=5)
        is_perfect_square = random.choice([True, False])
        
        if is_perfect_square:
            # 確保 -c/a 是完全平方數
            k_val = _generate_perfect_square(min_base=2, max_base=10)
            c = -a * k_val # c will be negative
            sol1 = math.sqrt(k_val)
            sol2 = -math.sqrt(k_val)
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            op_c = "+" if c > 0 else "" # For formatting +c or -c
            solution_text_latex = str(a) + r"x^2 " + op_c + str(c) + r" = 0 \\ " + str(a) + r"x^2 = " + str(-c) + r" \\ x^2 = \frac{" + str(-c) + r"}{" + str(a) + r"} \\ x^2 = " + str(k_val) + r" \\ x = \pm \sqrt{" + str(k_val) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k_val)
            question_text = r"解方程式 $" + str(a) + r"x^2 " + op_c + str(c) + r" = 0$。"
        else:
            # 確保 -c/a 是非完全平方數
            k_val = _generate_non_perfect_square(min_val=5, max_val=50)
            c = -a * k_val # c will be negative
            sol1 = math.sqrt(k_val)
            sol2 = -math.sqrt(k_val)
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            op_c = "+" if c > 0 else ""
            solution_text_latex = str(a) + r"x^2 " + op_c + str(c) + r" = 0 \\ " + str(a) + r"x^2 = " + str(-c) + r" \\ x^2 = \frac{" + str(-c) + r"}{" + str(a) + r"} \\ x^2 = " + str(k_val) + r" \\ x = \pm \sqrt{" + str(k_val) + r"} \\ x = \pm " + _get_simplified_sqrt_form_str(k_val) + r" \approx \pm " + _format_rounded_solution(sol1, decimal_places)
            question_text = r"解方程式 $" + str(a) + r"x^2 " + op_c + str(c) + r" = 0$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    elif problem_type == 6: # Maps to Example 6: (x+a)^2 + c = 0
        a = _generate_integer_constant(min_val=-5, max_val=5, exclude_zero=True)
        is_perfect_square = random.choice([True, False])

        op_a = "+" if a > 0 else "" # For formatting (x+a) or (x-a)
        
        if is_perfect_square:
            # 確保 -c 是完全平方數
            k_val = _generate_perfect_square(min_base=2, max_base=10)
            c = -k_val # c will be negative
            sqrt_k_val = int(math.sqrt(k_val))
            sol1 = -a + sqrt_k_val
            sol2 = -a - sqrt_k_val
            correct_answer_raw = [str(int(sol1)), str(int(sol2))]
            op_c = "+" if c > 0 else ""
            solution_text_latex = r"(x " + op_a + str(a) + r")^2 " + op_c + str(c) + r" = 0 \\ (x " + op_a + str(a) + r")^2 = " + str(-c) + r" \\ x " + op_a + str(a) + r" = \pm \sqrt{" + str(-c) + r"} \\ x " + op_a + str(a) + r" = \pm " + _get_simplified_sqrt_form_str(-c) + r" \\ x = " + ("-" if a > 0 else "+") + str(abs(a)) + r" \pm " + _get_simplified_sqrt_form_str(-c)
            question_text = r"解方程式 $(x " + op_a + str(a) + r")^2 " + op_c + str(c) + r" = 0$。"
        else:
            # 確保 -c 是非完全平方數
            k_val = _generate_non_perfect_square(min_val=5, max_val=50)
            c = -k_val # c will be negative
            sqrt_k_val = math.sqrt(k_val)
            sol1 = -a + sqrt_k_val
            sol2 = -a - sqrt_k_val
            correct_answer_raw = [_format_rounded_solution(sol1, decimal_places), _format_rounded_solution(sol2, decimal_places)]
            op_c = "+" if c > 0 else ""
            solution_text_latex = r"(x " + op_a + str(a) + r")^2 " + op_c + str(c) + r" = 0 \\ (x " + op_a + str(a) + r")^2 = " + str(-c) + r" \\ x " + op_a + str(a) + r" = \pm \sqrt{" + str(-c) + r"} \\ x " + op_a + str(a) + r" = \pm " + _get_simplified_sqrt_form_str(-c) + r" \\ x = " + ("-" if a > 0 else "+") + str(abs(a)) + r" \pm " + _get_simplified_sqrt_form_str(-c) + r" \approx " + _format_rounded_solution(sol1, decimal_places) + r", " + _format_rounded_solution(sol2, decimal_places)
            question_text = r"解方程式 $(x " + op_a + str(a) + r")^2 " + op_c + str(c) + r" = 0$。(答案請四捨五入到小數點後第 " + str(decimal_places) + " 位)"

    # 將答案進行數值排序，確保 check() 比較時順序一致
    try:
        correct_answer_parsed = sorted([float(s) for s in correct_answer_raw])
        correct_answer_str = ", ".join([str(s) for s in correct_answer_parsed])
    except ValueError: # 避免非數值情況 (理論上本設計不會發生，但作為防禦性程式碼)
        correct_answer_str = ", ".join(correct_answer_raw)

    final_solution_text = "解題步驟：\n" + solution_text_latex + "\n因此，x 的解為 " + correct_answer_str + "。"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,  # 純數據 (Raw Data)
        "answer": final_solution_text,         # 詳解文字
        "image_base64": None,                  # 無圖形
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    批改使用者答案。
    Args:
        user_answer (str): 使用者輸入的答案。
        correct_answer (str): `generate` 函式產生的正確答案 (純數據)。
    Returns:
        bool: 答案是否正確。
    """
    # 閱卷邏輯 (Robust Check Logic)
    # 1. 輸入清洗 (Input Sanitization)
    #    使用 Regex 移除 LaTeX 符號、變數前綴、所有空白字元。
    def clean_answer_string(s):
        s = str(s).strip().lower()
        # 移除常見的 LaTeX 符號和括號
        s = re.sub(r'[\$\{\}\\]', '', s)
        # 移除變數前綴，如 x=, y=, k=, ans:
        s = re.sub(r'^(x|y|k|ans):?\s*', '', s)
        # 移除所有空白字元
        s = re.sub(r'\s+', '', s)
        # 將常見的答案分隔符或符號轉換為逗號
        s = s.replace("或", ",").replace("±", ",").replace("+-", ",").replace("-+", ",")
        return s
    
    user_answer_cleaned = clean_answer_string(user_answer)
    correct_answer_cleaned = clean_answer_string(correct_answer)

    # 2. 數值序列比對
    #    將答案分割、轉換為浮點數並排序，然後進行數值比較。
    user_parts = [part.strip() for part in user_answer_cleaned.split(',') if part.strip()]
    correct_parts = [part.strip() for part in correct_answer_cleaned.split(',') if part.strip()]

    if len(user_parts) != len(correct_parts):
        return False # 答案數量不一致

    try:
        user_nums = sorted([float(part) for part in user_parts])
        correct_nums = sorted([float(part) for part in correct_parts])
    except ValueError:
        return False # 無法轉換為浮點數，表示輸入格式錯誤

    # 3. 支援多種數學格式的等價性 (透過浮點數比較與容錯處理)
    #    使用 math.isclose 處理浮點數精度問題。
    tolerance = 1e-5 # 容錯範圍，適用於浮點數精度和四捨五入的答案
    for u, c in zip(user_nums, correct_nums):
        if not math.isclose(u, c, rel_tol=tolerance, abs_tol=tolerance):
            return False
    
    return True


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
