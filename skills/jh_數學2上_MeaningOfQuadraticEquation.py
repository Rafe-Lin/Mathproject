# ==============================================================================
# ID: jh_數學2上_MeaningOfQuadraticEquation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 61.42s | RAG: 3 examples
# Created At: 2026-01-19 11:26:44
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

# K12 數學 AI 首席系統架構師 Spec (V11.8 鏡射增強版)

# --- 輔助函式設計 (Helper Functions) ---

def _format_term(coeff, var, power, is_first_term):
    """
    功能: 將單一多項式項 (e.g., $3x^2$, $-x$, $5$) 格式化為 LaTeX 字串。
    參數:
        coeff (int): 係數。
        var (str): 變數名稱 (e.g., `'x'`)。
        power (int): 變數的次方 (e.g., `0` for constant, `1` for linear, `2` for quadratic, `3` for cubic)。
        is_first_term (bool): 布林值，指示該項是否為多項式中的首項，用於控制開頭的 `+` 號。
    回傳: `str`，表示單項的 LaTeX 字串 (e.g., `"3x^2"`, `"-x"`, `"+5"`)。
    規範:
        係數為 `0` 則回傳空字串。
        係數為 `1` 或 `-1` 時，不顯示數字 `1` (e.g., `x^2`, `-x`)。
        首項為正數時，不顯示 `+` 號；非首項為正數時，顯示 `+` 號。
        所有項為負數時，顯示 `-` 號。
    """
    if coeff == 0:
        return ""

    term_str = ""
    abs_coeff = abs(coeff)

    if power == 0:
        term_str = str(abs_coeff)
    elif power == 1:
        term_str = var if abs_coeff == 1 else f"{abs_coeff}{var}"
    elif power == 2:
        term_str = f"{var}^2" if abs_coeff == 1 else f"{abs_coeff}{var}^2"
    elif power == 3:
        term_str = f"{var}^3" if abs_coeff == 1 else f"{abs_coeff}{var}^3"
    else: # 支援更高次方數，儘管當前技能點可能用不到
        term_str = f"{var}^{power}" if abs_coeff == 1 else f"{abs_coeff}{var}^{power}"

    if coeff > 0:
        return f"+{term_str}" if not is_first_term else term_str
    else: # coeff < 0
        return f"-{term_str}"

def _format_polynomial(a_x2, b_x1, c_x0, var='x'):
    """
    功能: 將標準二次多項式 $a_x2 x^2 + b_x1 x + c_x0$ 格式化為 LaTeX 字串。
    參數:
        a_x2, b_x1, c_x0 (int): 分別為 $x^2, x, 1$ 的係數。
        var (str): 變數名稱，預設為 `'x'`。
    回傳: `str`，表示多項式的 LaTeX 字串 (e.g., `"2x^2-3x+1"`)。
    規範: 內部呼叫 `_format_term` 處理各項，確保排版正確。
    """
    parts = []
    
    # x^2 term
    term_x2 = _format_term(a_x2, var, 2, is_first_term=True)
    if term_x2:
        parts.append(term_x2)

    # x term
    term_x = _format_term(b_x1, var, 1, is_first_term=not bool(parts))
    if term_x:
        parts.append(term_x)

    # Constant term
    term_c = _format_term(c_x0, var, 0, is_first_term=not bool(parts))
    if term_c:
        parts.append(term_c)
    
    return "".join(parts) if parts else "0"

def _format_general_polynomial(coeffs, var='x'):
    """
    功能: 將一個一般多項式（由係數字典表示）格式化為 LaTeX 字串。
    參數:
        coeffs (dict): 鍵為次方數，值為係數的字典 (e.g., `{3: 1, 2: -2, 0: 5}` 代表 $x^3 - 2x^2 + 5$)。
        var (str): 變數名稱，預設為 `'x'`。
    回傳: `str`，表示多項式的 LaTeX 字串。
    規範: 內部呼叫 `_format_term`，並依照次方數遞減順序組合各項。
    """
    sorted_powers = sorted(coeffs.keys(), reverse=True)
    parts = []
    
    for power in sorted_powers:
        coeff = coeffs[power]
        term = _format_term(coeff, var, power, is_first_term=not bool(parts))
        if term:
            parts.append(term)
            
    return "".join(parts) if parts else "0"

def _generate_coefficients():
    """
    功能: 生成用於一元二次方程式的係數 $a, b, c$。
    回傳: `tuple`，包含 `(a, b, c)` 三個整數。
    規範:
        `a` 必須是非零整數 (範圍 `[-5, -1] U [1, 5]`)。
        `b` 和 `c` 可以為零 (範圍 `[-10, 10]`)。
        嚴禁硬編碼任何係數，必須使用 `random.randint` 生成。
    """
    a = 0
    while a == 0:
        a = random.randint(-5, 5) # 確保 'a' 不為零
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    return a, b, c

# --- generate(level=1) 函式設計 ---

def generate(level=1):
    """
    根據技能點 `jh_數學2上_MeaningOfQuadraticEquation` 生成數學題目。
    """
    problem_type = random.choice([1, 2, 3, 4]) # 隨機選擇題型
    
    question_text = ""
    correct_answer = ""
    image_base64 = None # 本技能不涉及圖形

    if problem_type == 1: # Type 1 (Maps to Example 1): 判斷方程式是否為一元二次方程式
        eq_type = random.choice(['quadratic', 'linear', 'cubic', 'not_polynomial_rational', 'looks_quadratic_but_linear'])
        
        if eq_type == 'quadratic':
            a, b, c = _generate_coefficients()
            equation_str = _format_polynomial(a, b, c)
            question_text = r"判斷下列式子是否為一元二次方程式？是的打「○」，不是的打「×」。(  ) $"+ equation_str + r" = 0$"
            correct_answer = "1" # '1' 代表「○」(是)
        elif eq_type == 'linear':
            a_lin = 0
            while a_lin == 0: a_lin = random.randint(-10, 10)
            b_const = random.randint(-10, 10)
            equation_str = _format_polynomial(0, a_lin, b_const)
            question_text = r"判斷下列式子是否為一元二次方程式？是的打「○」，不是的打「×」。(  ) $"+ equation_str + r" = 0$"
            correct_answer = "0" # '0' 代表「×」(不是)
        elif eq_type == 'cubic':
            a_cube = 0
            while a_cube == 0: a_cube = random.randint(-3, 3)
            a_sq = random.randint(-5, 5)
            b_lin = random.randint(-10, 10)
            c_const = random.randint(-10, 10)
            coeffs = {3: a_cube, 2: a_sq, 1: b_lin, 0: c_const}
            equation_str = _format_general_polynomial(coeffs)
            question_text = r"判斷下列式子是否為一元二次方程式？是的打「○」，不是的打「×」。(  ) $"+ equation_str + r" = 0$"
            correct_answer = "0" # '0' 代表「×」(不是)
        elif eq_type == 'not_polynomial_rational':
            coeff_num = random.randint(1, 5)
            coeff_den = random.randint(1, 5)
            const = random.randint(-5, 5)
            equation_str = r"{n}x + \frac{{{d}}}{{x}} = {c}".replace("{n}", str(coeff_num)).replace("{d}", str(coeff_den)).replace("{c}", str(const))
            question_text = r"判斷下列式子是否為一元二次方程式？是的打「○」，不是的打「×」。(  ) $" + equation_str + r"$"
            correct_answer = "0" # '0' 代表「×」(不是)
        elif eq_type == 'looks_quadratic_but_linear':
            A = 0
            while A == 0: A = random.randint(-5, 5) # 確保簡化後 x 項係數不為零
            B = random.randint(-10, 10)
            
            # 方程式形式: x(x+A) - x^2 = B  => x^2 + Ax - x^2 = B => Ax = B (一元一次)
            lhs_inner_str = f"x{_format_term(A, 'x', 0, is_first_term=False)}" # (x+A) or (x-A)
            lhs_expanded_part = f"x({lhs_inner_str})"
            
            rhs_const_str = _format_term(B, 'x', 0, is_first_term=True)
            
            equation_str = lhs_expanded_part + r" - x^2 = " + rhs_const_str
            question_text = r"判斷下列式子是否為一元二次方程式？是的打「○」，不是的打「×」。(  ) $" + equation_str + r"$"
            correct_answer = "0" # '0' 代表「×」(不是)

    elif problem_type == 2: # Type 2 (Maps to Example 2): 找出使方程式不是一元二次方程式的變數值
        # 方程式形式: (k_expr)x^2 + bx + c = 0
        # 若不是一元二次方程式，則 x^2 項係數為 0。
        
        # 設定 k 的目標值，使得 x^2 係數為 0
        k_val_to_make_it_not_quadratic = random.randint(-7, 7)
        
        # 根據 k 的目標值，構造 x^2 項的係數表達式，例如 (k-3) 或 (k+5)
        k_expr_in_parentheses = r"k"
        if k_val_to_make_it_not_quadratic > 0:
            k_expr_in_parentheses = r"(k - {val})".replace("{val}", str(k_val_to_make_it_not_quadratic))
        elif k_val_to_make_it_not_quadratic < 0:
            k_expr_in_parentheses = r"(k + {val})".replace("{val}", str(abs(k_val_to_make_it_not_quadratic)))

        # 生成其他項的係數
        b_coeff = random.randint(-10, 10)
        c_coeff = random.randint(-10, 10)
        
        x2_part = f"{k_expr_in_parentheses}x^2"
        
        # 使用 _format_term 處理 b_coeff 和 c_coeff，確保符號和 '1' 係數的正確顯示
        x_term_str = _format_term(b_coeff, 'x', 1, is_first_term=False)
        c_term_str = _format_term(c_coeff, 'x', 0, is_first_term=False)

        equation_latex = x2_part
        if x_term_str:
            equation_latex += x_term_str
        if c_term_str:
            equation_latex += c_term_str
            
        question_text = r"若方程式 $" + equation_latex + r" = 0$ 不是一元二次方程式，則 $k$ 的值為何？"
        correct_answer = str(k_val_to_make_it_not_quadratic)

    elif problem_type == 3: # Type 3 (Maps to Example 3): 識別標準形式方程式的係數 a, b, c
        a, b, c = _generate_coefficients()
        equation_str = _format_polynomial(a, b, c)
        question_text = r"將方程式 $" + equation_str + r" = 0$ 寫成 $ax^2+bx+c=0$ 的形式，其中 $a, b, c$ 分別為何？"
        correct_answer = f"{a},{b},{c}"

    elif problem_type == 4: # Type 4 (Maps to Example 4): 化簡方程式並識別係數 a, b, c
        sub_type = random.choice(['distribute', 'product_of_binomials'])
        
        if sub_type == 'distribute':
            # 題目形式: Ax(Bx + C) = Dx^2 + Ex + F
            # 化簡後: (AB)x^2 + (AC)x = Dx^2 + Ex + F
            # 整理成標準式: (AB - D)x^2 + (AC - E)x - F = 0
            
            A = random.randint(1, 5) # A > 0 簡化格式
            B = random.randint(1, 5) # B > 0 簡化格式
            C = random.randint(-5, 5)
            D = random.randint(-5, 5)
            E = random.randint(-10, 10)
            F = random.randint(-10, 10)
            
            # 確保化簡後仍為一元二次方程式 (x^2 係數不為 0)
            while A * B - D == 0: D = random.randint(-5, 5) 
            
            lhs_inner_poly = _format_polynomial(0, B, C) # 格式化 Bx + C
            lhs = f"{A}x({lhs_inner_poly})" # 組合 Ax(Bx + C)
            
            rhs = _format_polynomial(D, E, F) # 格式化 Dx^2 + Ex + F
            
            equation_str = lhs + r" = " + rhs
            
            target_a = A * B - D
            target_b = A * C - E
            target_c = -F
            
            question_text = r"將方程式 $" + equation_str + r"$ 整理成 $ax^2+bx+c=0$ 的形式，其中 $a, b, c$ 分別為何？"
            correct_answer = f"{target_a},{target_b},{target_c}"
            
        elif sub_type == 'product_of_binomials':
            # 題目形式: (x + A)(x + B) = C
            # 化簡後: x^2 + (A+B)x + AB = C
            # 整理成標準式: x^2 + (A+B)x + (AB - C) = 0
            
            A_term_val = random.randint(-5, 5)
            B_term_val = random.randint(-5, 5)
            C_const = random.randint(-10, 10)
            
            # 格式化 (x + A_term_val)
            term1_A_str = ""
            if A_term_val > 0: term1_A_str = f"+{A_term_val}"
            elif A_term_val < 0: term1_A_str = f"-{abs(A_term_val)}"
            term1 = f"(x{term1_A_str})"
            
            # 格式化 (x + B_term_val)
            term2_B_str = ""
            if B_term_val > 0: term2_B_str = f"+{B_term_val}"
            elif B_term_val < 0: term2_B_str = f"-{abs(B_term_val)}"
            term2 = f"(x{term2_B_str})"
            
            rhs_const_str = _format_term(C_const, 'x', 0, is_first_term=True)
            equation_str = term1 + term2 + r" = " + rhs_const_str
            
            target_a = 1 
            target_b = A_term_val + B_term_val
            target_c = A_term_val * B_term_val - C_const
            
            question_text = r"將方程式 $" + equation_str + r"$ 整理成 $ax^2+bx+c=0$ 的形式，其中 $a, b, c$ 分別為何？"
            correct_answer = f"{target_a},{target_b},{target_c}"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 內部使用，correct_answer 為批改用純數據
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.2"
    }

# --- check(user_answer, correct_answer) 函式設計 ---


    """
    批改學生答案的函式。
    
    參數:
        user_answer (str): 學生提交的答案。
        correct_answer (str): `generate` 函式生成的正確答案。
        
    回傳:
        bool: 如果答案正確則為 True，否則為 False。
    """
    # 1. 輸入清洗 (Input Sanitization with Regex)
    #    移除 LaTeX 符號 ($), 變數前綴 (x=), 所有空白字元, 及其他非數字/逗號符號
    #    同時移除「○」和「×」符號，因為答案格式統一為 "1" 或 "0"。
    cleaned_user_answer = re.sub(r'[○×\$\s\\\{\}a-zA-Z=,:]+', '', user_answer).strip()
    cleaned_correct_answer = re.sub(r'[○×\$\s\\\{\}a-zA-Z=,:]+', '', correct_answer).strip()

    # 2. 數值序列比對前處理：分割並過濾空字串
    user_parts = [part.strip() for part in cleaned_user_answer.split(',') if part.strip()]
    correct_parts = [part.strip() for part in cleaned_correct_answer.split(',') if part.strip()]

    # 若任一答案為空，則直接判斷為錯
    if not user_parts or not correct_parts:
        return False

    # 3. 數值轉換
    #    嘗試將字串部分轉換為浮點數，以便進行精確比較
    try:
        user_numbers = [float(p) for p in user_parts]
        correct_numbers = [float(p) for p in correct_parts]
    except ValueError:
        return False # 如果轉換失敗 (e.g., 輸入非數字)，則判斷為錯

    # 4. 數值序列比對
    #    比較兩個數字序列的長度，若不同則為錯
    if len(user_numbers) != len(correct_numbers):
        return False
    
    #    逐一比較每個數字，考慮浮點數的精度問題 (使用容忍度 1e-9)
    for u, c in zip(user_numbers, correct_numbers):
        if abs(u - c) >= 1e-9:
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
