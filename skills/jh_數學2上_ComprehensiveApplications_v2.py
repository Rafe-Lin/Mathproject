# ==============================================================================
# ID: jh_數學2上_ComprehensiveApplications_v2
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 92.64s | RAG: 4 examples
# Created At: 2026-01-18 14:57:33
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

# module_name.py


import re
from datetime import datetime

# Helper Functions (輔助函式)
# [CRITICAL RULE: 排版與 LaTeX 安全]
# 函式僅用於產生問題文字，嚴禁接收答案數據。
def _format_latex_expression(base_str, replacements):
    """
    將 LaTeX 模板字串中的佔位符號替換為實際數值。
    嚴禁使用 f-string 或 % 格式化，避免 LaTeX 與 Python 大括號衝突。
    """
    expr = base_str
    for key, value in replacements.items():
        # 對於負數，確保符號與絕對值正確顯示
        # 這裡的 value 可能是已經格式化好的字串 (如 area_poly_str_placeholder)
        if isinstance(value, (int, float)):
            if value < 0:
                expr = expr.replace("{" + key + "}", f"-{abs(value)}")
            else:
                expr = expr.replace("{" + key + "}", str(value))
        else: # Assume it's an already formatted string
            expr = expr.replace("{" + key + "}", str(value))
    return expr

def _format_coefficient_display(coeff):
    """
    格式化多項式係數，處理 1, -1 和其他數值。
    """
    if coeff == 1:
        return ""
    elif coeff == -1:
        return "-"
    else:
        return str(coeff)

def _format_sign_and_abs(value):
    """
    格式化顯示正負號和絕對值，用於 LaTeX。
    例如：5 -> "+ 5", -3 -> "- 3"
    """
    if value >= 0:
        return "+ " + str(abs(value))
    else:
        return "- " + str(abs(value))

def generate(level=1):
    # [CRITICAL RULE: 題型鏡射]
    # 根據 RAG 中的例題類型進行隨機分流，並將數據動態化。
    # 這裡將 RAG 例題 1, 2, 3, 4 嚴格映射為 problem_type 1, 2, 3, 4。
    problem_type = random.choice([1, 2, 3, 4])

    question_text = ""
    correct_answer = ""
    image_base64 = "" # [CRITICAL RULE: 幾何/圖形題的特殊規範]：本題型無圖形，設為空值。

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1): 乘法公式綜合應用 - 展開並化簡多項式
        # Ex 1.1: (x＋2)^2＋(2x＋1) -> K1(ax+b)^2 + K2(cx+d)
        # Ex 1.2: 5(2x＋1)^2-3(x＋1)(x＋3) -> K1(ax+b)^2 - K2(cx+d)(ex+f)
        
        # [CRITICAL RULE: 數據禁絕常數]: 所有數值皆隨機生成。
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 10) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        d = random.randint(1, 10) * random.choice([-1, 1])

        sub_type = random.choice([1, 2]) # 隨機選擇子類型

        if sub_type == 1: # 類型 1.1: K1(ax+b)^2 + K2(cx+d)
            k1 = random.randint(1, 3) * random.choice([-1, 1])
            k2 = random.randint(1, 3) * random.choice([-1, 1])
            
            # (k1*a^2)x^2 + (2*k1*a*b + k2*c)x + (k1*b^2 + k2*d)
            coeff_x2 = k1 * a*a
            coeff_x1 = 2 * k1 * a * b + k2 * c
            coeff_x0 = k1 * b*b + k2 * d

            question_text_template = r"計算下列各式。${k1_display}({a_display}x {b_sign_abs})^2 {k2_sign_abs}{c_display}x {d_sign_abs}$"
            
            question_text = _format_latex_expression(question_text_template, {
                "k1_display": _format_coefficient_display(k1),
                "a_display": _format_coefficient_display(a), "b_sign_abs": _format_sign_and_abs(b),
                "k2_sign_abs": _format_sign_and_abs(k2),
                "c_display": _format_coefficient_display(c), "d_sign_abs": _format_sign_and_abs(d)
            })
            
            correct_answer = f"{coeff_x2},{coeff_x1},{coeff_x0}"

        elif sub_type == 2: # 類型 1.2: K1(ax+b)^2 - K2(cx+d)(ex+f)
            e = random.randint(1, 5) * random.choice([-1, 1])
            f = random.randint(1, 10) * random.choice([-1, 1])
            k1 = random.randint(1, 3) * random.choice([-1, 1])
            k2 = random.randint(1, 3) * random.choice([-1, 1])

            # k1*(a^2 x^2 + 2ab x + b^2) - k2*(ce x^2 + (cf+de) x + df)
            # (k1*a^2 - k2*c*e)x^2 + (2*k1*a*b - k2*(c*f+d*e))x + (k1*b^2 - k2*d*f)
            coeff_x2 = k1 * a*a - k2 * c * e
            coeff_x1 = 2 * k1 * a * b - k2 * (c * f + d * e)
            coeff_x0 = k1 * b*b - k2 * d * f

            question_text_template = r"計算下列各式。${k1_display}({a_display}x {b_sign_abs})^2 {k2_sign_abs_op}({c_display}x {d_sign_abs})({e_display}x {f_sign_abs})$"
            
            question_text = _format_latex_expression(question_text_template, {
                "k1_display": _format_coefficient_display(k1),
                "a_display": _format_coefficient_display(a), "b_sign_abs": _format_sign_and_abs(b),
                "k2_sign_abs_op": _format_sign_and_abs(-k2), # -k2 for the subtraction operator
                "c_display": _format_coefficient_display(c), "d_sign_abs": _format_sign_and_abs(d),
                "e_display": _format_coefficient_display(e), "f_sign_abs": _format_sign_and_abs(f)
            })
            
            correct_answer = f"{coeff_x2},{coeff_x1},{coeff_x0}"

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 2): 多項式展開化簡 (含常數項或多個乘積)
        # Ex 2.1: 1-5(x-2)^2＋2(x-1) -> K0 - K1(ax+b)^2 + K2(cx+d)
        # Ex 2.2: (x＋1)(x＋2)-(x＋3)(x＋4) -> (ax+b)(cx+d) - (ex+f)(gx+h)
        
        # [CRITICAL RULE: 數據禁絕常數]: 所有數值皆隨機生成。
        
        sub_type = random.choice([1, 2])

        if sub_type == 1: # 類型 2.1: K0 - K1(ax+b)^2 + K2(cx+d)
            k0 = random.randint(1, 15) * random.choice([-1, 1]) # Constant term
            k1 = random.randint(1, 5) * random.choice([-1, 1])
            k2 = random.randint(1, 5) * random.choice([-1, 1])
            a = random.randint(1, 3) * random.choice([-1, 1])
            b = random.randint(1, 7) * random.choice([-1, 1])
            c = random.randint(1, 3) * random.choice([-1, 1])
            d = random.randint(1, 7) * random.choice([-1, 1])

            # k0 - k1*(a^2 x^2 + 2ab x + b^2) + k2*(cx+d)
            # (-k1*a^2)x^2 + (-2*k1*a*b + k2*c)x + (k0 - k1*b^2 + k2*d)
            coeff_x2 = -k1 * a*a
            coeff_x1 = -2 * k1 * a * b + k2 * c
            coeff_x0 = k0 - k1 * b*b + k2 * d

            question_text_template = r"計算下列各式。${k0_val_display} {k1_sign_abs_op}{k1_coeff_display}({a_display}x {b_sign_abs})^2 {k2_sign_abs_op2}{k2_coeff_display}({c_display}x {d_sign_abs})$"
            
            question_text = _format_latex_expression(question_text_template, {
                "k0_val_display": str(k0),
                "k1_sign_abs_op": _format_sign_and_abs(-k1), # For the minus sign before k1 term
                "k1_coeff_display": _format_coefficient_display(abs(k1)), # display abs(k1) as sign is handled by k1_sign_abs
                "a_display": _format_coefficient_display(a), "b_sign_abs": _format_sign_and_abs(b),
                "k2_sign_abs_op2": _format_sign_and_abs(k2),
                "k2_coeff_display": _format_coefficient_display(abs(k2)), # display abs(k2)
                "c_display": _format_coefficient_display(c), "d_sign_abs": _format_sign_and_abs(d)
            })
            
            correct_answer = f"{coeff_x2},{coeff_x1},{coeff_x0}"

        elif sub_type == 2: # 類型 2.2: (ax+b)(cx+d) - (ex+f)(gx+h)
            a = random.randint(1, 3) * random.choice([-1, 1])
            b = random.randint(1, 7) * random.choice([-1, 1])
            c = random.randint(1, 3) * random.choice([-1, 1])
            d = random.randint(1, 7) * random.choice([-1, 1])
            e = random.randint(1, 3) * random.choice([-1, 1])
            f = random.randint(1, 7) * random.choice([-1, 1])
            g = random.randint(1, 3) * random.choice([-1, 1])
            h = random.randint(1, 7) * random.choice([-1, 1])

            # (ac x^2 + (ad+bc) x + bd) - (eg x^2 + (eh+fg) x + fh)
            # (ac - eg)x^2 + (ad+bc - (eh+fg))x + (bd - fh)
            coeff_x2 = a*c - e*g
            coeff_x1 = (a*d + b*c) - (e*h + f*g)
            coeff_x0 = b*d - f*h
            
            attempts = 0
            while coeff_x2 == 0 and coeff_x1 == 0 and attempts < 10: # Ensure not trivial (e.g., constant result)
                a = random.randint(1, 3) * random.choice([-1, 1])
                b = random.randint(1, 7) * random.choice([-1, 1])
                c = random.randint(1, 3) * random.choice([-1, 1])
                d = random.randint(1, 7) * random.choice([-1, 1])
                e = random.randint(1, 3) * random.choice([-1, 1])
                f = random.randint(1, 7) * random.choice([-1, 1])
                g = random.randint(1, 3) * random.choice([-1, 1])
                h = random.randint(1, 7) * random.choice([-1, 1])
                coeff_x2 = a*c - e*g
                coeff_x1 = (a*d + b*c) - (e*h + f*g)
                coeff_x0 = b*d - f*h
                attempts += 1

            question_text_template = r"計算下列各式。$({a_display}x {b_sign_abs})({c_display}x {d_sign_abs}) - ({e_display}x {f_sign_abs})({g_display}x {h_sign_abs})$"
            
            question_text = _format_latex_expression(question_text_template, {
                "a_display": _format_coefficient_display(a), "b_sign_abs": _format_sign_and_abs(b),
                "c_display": _format_coefficient_display(c), "d_sign_abs": _format_sign_and_abs(d),
                "e_display": _format_coefficient_display(e), "f_sign_abs": _format_sign_and_abs(f),
                "g_display": _format_coefficient_display(g), "h_sign_abs": _format_sign_and_abs(h)
            })
            
            correct_answer = f"{coeff_x2},{coeff_x1},{coeff_x0}"

    elif problem_type == 3:
        # Type 3 (Maps to RAG Ex 3): 幾何應用 - 複合長方形的周長與面積
        # "大長方形的長為 2x＋5、寬為 x＋4，小長方形的長為 2x＋1、寬為 x-1。試以 x 的多項式表示橘色部分的周長與面積。"
        # Model: Orange Area = Large Area - Small Area, Orange Perimeter = Large Perimeter + Small Perimeter (assuming cut-out)
        
        # [CRITICAL RULE: 數據禁絕常數]: 所有數值皆隨機生成。
        
        # Large rect: L1 = k1*x + b1, W1 = k2*x + d1
        # Small rect: L2 = k1*x + b2, W2 = k2*x + d2 (using same x coeffs for alignment with RAG Ex 3)
        k1 = random.randint(1, 3)
        k2 = random.randint(1, 2)
        
        b1 = random.randint(5, 12)
        d1 = random.randint(4, 10)
        
        b2 = random.randint(-2, b1-3) # Ensure b2 < b1, can be negative (e.g., x-1)
        d2 = random.randint(-2, d1-3) # Ensure d2 < d1, can be negative
        
        # Ensure length and width are distinct for large rectangle for more general case
        if k1 == k2 and b1 == d1: # Make them different if they coincidentally become square
            b1 += 1
        
        # Perimeter: P = 2 * (L1 + W1) + 2 * (L2 + W2)
        # P = 4 * (k1+k2)x + 2*(b1+d1+b2+d2)
        coeff_P_x1 = 4 * (k1 + k2)
        coeff_P_x0 = 2 * (b1 + d1 + b2 + d2)

        # Area: A = L1*W1 - L2*W2
        # A = (k1d1+k2b1 - (k1d2+k2b2))x + (b1d1 - b2d2) (x^2 terms cancel out as in RAG Ex 3)
        coeff_A_x1 = (k1*d1 + k2*b1) - (k1*d2 + k2*b2)
        coeff_A_x0 = b1*d1 - b2*d2
        
        attempts = 0
        while coeff_A_x1 == 0 and attempts < 5: # Re-generate if Area is constant (RAG Ex 3 area is linear)
            k1 = random.randint(1, 3)
            k2 = random.randint(1, 2)
            b1 = random.randint(5, 12)
            d1 = random.randint(4, 10)
            b2 = random.randint(-2, b1-3)
            d2 = random.randint(-2, d1-3)
            if k1 == k2 and b1 == d1: b1 += 1
            coeff_P_x1 = 4 * (k1 + k2)
            coeff_P_x0 = 2 * (b1 + d1 + b2 + d2)
            coeff_A_x1 = (k1*d1 + k2*b1) - (k1*d2 + k2*b2)
            coeff_A_x0 = b1*d1 - b2*d2
            attempts += 1

        question_text_template = r"右圖中，大長方形的長為 $({k1a_display}x {b1_sign_abs})$、寬為 $({k2a_display}x {d1_sign_abs})$，小長方形的長為 $({k1b_display}x {b2_sign_abs})$、寬為 $({k2b_display}x {d2_sign_abs})$。試以 x 的多項式表示橘色部分的周長與面積。"
        
        question_text = _format_latex_expression(question_text_template, {
            "k1a_display": _format_coefficient_display(k1), "b1_sign_abs": _format_sign_and_abs(b1),
            "k2a_display": _format_coefficient_display(k2), "d1_sign_abs": _format_sign_and_abs(d1),
            "k1b_display": _format_coefficient_display(k1), "b2_sign_abs": _format_sign_and_abs(b2),
            "k2b_display": _format_coefficient_display(k2), "d2_sign_abs": _format_sign_and_abs(d2)
        })
        
        # Answer format: "P_coeff_x1,P_coeff_x0;A_coeff_x1,A_coeff_x0"
        correct_answer = f"{coeff_P_x1},{coeff_P_x0};{coeff_A_x1},{coeff_A_x0}"

    elif problem_type == 4:
        # Type 4 (Maps to RAG Ex 4): 幾何應用 - 梯形的高
        # "上底為 x-3、下底為 3x＋5、面積為 $2x^2$＋5x＋2，試以 x 的多項式表示此溜滑梯的高。"
        # Area = 0.5 * (top + bottom) * height => height = (2 * Area) / (top + bottom)
        
        # [CRITICAL RULE: 數據禁絕常數]: 所有數值皆隨機生成。
        # Generate Height (H1x + H0) and Sum of Bases (S1x + S0) such that 2*Area is divisible by 2.
        
        attempts = 0
        while True:
            h1 = random.randint(1, 3) * random.choice([-1, 1]) # Coeff for height x
            h0 = random.randint(1, 5) * random.choice([-1, 1]) # Const for height
            
            s1 = random.randint(2, 5) # Coeff for sum of bases x (must be >=2 to split into two bases)
            s0 = random.randint(1, 10) * random.choice([-1, 1]) # Const for sum of bases

            # Calculate 2 * Area polynomial coefficients
            _2A_x2 = s1 * h1
            _2A_x1 = s1 * h0 + s0 * h1
            _2A_x0 = s0 * h0
            
            # Check if Area coefficients are integers
            if _2A_x2 % 2 == 0 and _2A_x1 % 2 == 0 and _2A_x0 % 2 == 0:
                break # Found valid coefficients
            
            attempts += 1
            if attempts > 20: # Prevent infinite loop for very rare cases
                # If we can't find integer coefficients easily, adjust range or retry.
                # For this problem, it should almost always find integer coeffs.
                break

        A_x2 = _2A_x2 // 2
        A_x1 = _2A_x1 // 2
        A_x0 = _2A_x0 // 2

        # Split (s1*x + s0) into top (a_top*x + b_top) and bottom (c_bottom*x + d_bottom)
        # Ensure a_top and c_bottom are positive
        a_top = random.randint(1, s1-1) if s1 > 1 else 1
        c_bottom = s1 - a_top
        
        b_top = random.randint(-5, 5)
        d_bottom = s0 - b_top
        
        # Ensure top and bottom are not identical to avoid trivial cases.
        # Also ensure x coefficients are not zero.
        while (a_top == c_bottom and b_top == d_bottom) or (a_top == 0) or (c_bottom == 0):
            a_top = random.randint(1, s1-1) if s1 > 1 else 1
            c_bottom = s1 - a_top
            b_top = random.randint(-5, 5)
            d_bottom = s0 - b_top
        
        # Format Area polynomial string (avoiding f-strings for LaTeX safety)
        area_poly_parts = []
        if A_x2 != 0:
            area_poly_parts.append(_format_coefficient_display(A_x2) + "x^2")
        if A_x1 != 0:
            area_poly_parts.append(_format_sign_and_abs(A_x1) + "x")
        if A_x0 != 0 or len(area_poly_parts) == 0: # Ensure constant term is shown if it's the only term
            area_poly_parts.append(_format_sign_and_abs(A_x0))
        
        area_poly_str = "".join(area_poly_parts).strip()
        if area_poly_str.startswith("+"):
            area_poly_str = area_poly_str[1:].strip()
        if not area_poly_str: # If all parts were zero, just show '0'
            area_poly_str = "0"
        
        question_text_template = r"右圖是大象造型的梯形溜滑梯，若溜滑梯的上底為 $({a_top_display}x {b_top_sign_abs})$、下底為 $({c_bottom_display}x {d_bottom_sign_abs})$、面積為 $ {area_poly_str_placeholder} $，試以 x 的多項式表示此溜滑梯的高。"
        
        question_text = _format_latex_expression(question_text_template, {
            "a_top_display": _format_coefficient_display(a_top), "b_top_sign_abs": _format_sign_and_abs(b_top),
            "c_bottom_display": _format_coefficient_display(c_bottom), "d_bottom_sign_abs": _format_sign_and_abs(d_bottom),
            "area_poly_str_placeholder": area_poly_str
        })
        
        correct_answer = f"{h1},{h0}" # Coefficients for height: h1x + h0

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 預留給使用者輸入
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # [CRITICAL RULE: 強韌閱卷邏輯 (Robust Check Logic)]
    # 1. 輸入清洗 (Input Sanitization)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, ans=
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        return s
    
    sanitized_user_answer = clean(user_answer)
    sanitized_correct_answer = clean(correct_answer)

    # [CRITICAL RULE: V13.5 最終硬化規約]: 嚴禁 if/else 字串拆解，統一使用數字序列比對。
    # 判斷是多項式係數列表 (逗號分隔) 還是多組多項式答案 (分號分隔) 還是單一數值答案
    if ';' in sanitized_correct_answer: # Type 3: Perimeter;Area
        user_sub_answers = sanitized_user_answer.split(';')
        correct_sub_answers = sanitized_correct_answer.split(';')
        
        if len(user_sub_answers) != len(correct_sub_answers):
            return False
        
        all_correct = True
        for u_sub, c_sub in zip(user_sub_answers, correct_sub_answers):
            u_parts = u_sub.split(',')
            c_parts = c_sub.split(',')
            
            if len(u_parts) != len(c_parts):
                all_correct = False
                break
            
            try:
                u_nums = [float(p) for p in u_parts]
                c_nums = [float(p) for p in c_parts]
                if not all(math.isclose(u, c, rel_tol=1e-9, abs_tol=1e-9) for u, c in zip(u_nums, c_nums)):
                    all_correct = False
                    break
            except ValueError:
                all_correct = False
                break
        return all_correct

    elif ',' in sanitized_correct_answer: # 多項式係數答案 (e.g., "A,B,C")
        user_parts = sanitized_user_answer.split(',')
        correct_parts = sanitized_correct_answer.split(',')

        if len(user_parts) != len(correct_parts):
            return False

        try:
            user_nums = [float(p) for p in user_parts]
            correct_nums = [float(p) for p in correct_parts]
            
            # 比較浮點數的等價性
            return all(math.isclose(u, c, rel_tol=1e-9, abs_tol=1e-9) for u, c in zip(user_nums, correct_nums))
        except ValueError:
            return False # 非數字輸入

    else:
        # 單一數值答案 (e.g., "5", "0.5", "1/2")
        try:
            # 支援多種數學格式的等價性 (例如：1/2 = 0.5)
            # 將使用者輸入轉換為浮點數，處理分數格式
            def parse_val(val_str):
                if "/" in val_str:
                    n, d = map(float, val_str.split("/"))
                    return n/d
                return float(val_str)
            
            user_val = parse_val(sanitized_user_answer)
            correct_val = parse_val(sanitized_correct_answer)
            
            return math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9)
        except ValueError:
            return False # 非數字輸入或格式錯誤


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
