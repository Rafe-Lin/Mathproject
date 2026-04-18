# ==============================================================================
# ID: jh_數學1下_SolutionsAndGraphicalRepresentationOfOneVariableLinearInequalities
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 69.93s | RAG: 3 examples
# Created At: 2026-01-17 14:15:38
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
    
    # 數線刻度規範 (V16.11 Ticks)
    # 自動計算刻度
    step = 1
    if x_max - x_min > 20: step = 2
    try:
        start_tick = math.ceil(x_min)
        end_tick = math.floor(x_max)
        ticks = range(int(start_tick), int(end_tick) + 1, step)
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(t) for t in ticks], fontsize=12)
    except:
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



import base64
from datetime import datetime
import io
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import re # For parsing user input in check()

# --- Helper Functions ---

def _generate_coordinate_value(min_val=-8, max_val=8, allow_fraction=False):
    """
    Generates a single float value, and its integer/fraction representation.
    Adapted from V10.2 for generating general numbers (not just coordinates).
    Ensures no improper fractions (V13.1).
    Returns (float_val, (int_part, num, den, is_neg)).
    If integer, num=0, den=0. (V10.2 A, V13.0, V13.1, V13.5)
    """
    
    # V13.5: 整數優先 - 70% chance of integer, 30% chance of fraction if allowed
    if allow_fraction and random.random() < 0.3: # 30% chance of fraction
        # Generate integer part (can be 0) for the whole number part of a mixed fraction
        int_part_abs = random.randint(0, max(0, max_val - 1)) # Absolute integer part
        
        # Generate fraction part, ensuring numerator < denominator and den > 1 (V13.1: 禁絕假分數)
        denominator = random.randint(2, 5) # Denominator > 1
        numerator = random.randint(1, denominator - 1) # Numerator < denominator
        
        val_abs = int_part_abs + numerator / denominator
        
        # Fallback to integer within range if generated fraction value is out of bounds
        if val_abs > max_val or (val_abs < abs(min_val) and min_val < 0):
            val = random.randint(min_val, max_val)
            return (float(val), (int(val), 0, 0, val < 0))

        # Assign sign randomly
        is_neg = random.choice([True, False])
        sign = -1 if is_neg else 1
        val = val_abs * sign
        
        # Determine int_part for the return tuple (this is for mixed fraction representation)
        # For a negative mixed fraction like -1 1/2, int_part is -1.
        # For formatting, we use abs(int_part) and then prepend the sign.
        int_part_for_tuple = int(val) # This correctly captures the signed integer part
        
        return (val, (int_part_for_tuple, numerator, denominator, is_neg))
        
    else: # Integer (V13.5: 整數優先)
        val = random.randint(min_val, max_val)
        int_part = int(val)
        numerator = 0
        denominator = 0
        is_neg = val < 0
        return (float(val), (int_part, numerator, denominator, is_neg))

def _format_number_for_latex(value_data):
    """
    Formats the number data (from _generate_coordinate_value) into a LaTeX string.
    Uses .replace() for LaTeX safety (V5, V10.2 C).
    """
    float_val, (int_part, num, den, is_neg) = value_data

    if num == 0: # Integer
        return str(int(float_val))
    else: # Fraction
        # Handle sign for fractions carefully (V5, V10.2 C)
        sign_str = "-" if is_neg else ""
        
        if int_part == 0: # Pure fraction (e.g., 1/2, -1/2)
            # Use abs(num) to ensure numerator is positive in LaTeX fraction display
            return r"{sign}\frac{n}{d}".replace("{sign}", sign_str).replace("{n}", str(abs(num))).replace("{d}", str(den))
        else: # Mixed fraction (e.g., 1 1/2, -1 1/2)
            # LaTeX for mixed fraction usually shows sign then integer, then fraction.
            # So use abs(int_part) for the integer part of the mixed fraction.
            return r"{sign}{i}\frac{n}{d}".replace("{sign}", sign_str).replace("{i}", str(abs(int_part))).replace("{n}", str(num)).replace("{d}", str(den))

def draw_number_line_solution(critical_value, operator_type, x_min=-10, x_max=10):
    """
    Draws the solution of a one-variable linear inequality on a number line.
    No answer data passed directly (V6).
    (V10.2 B/D, V13.0, V13.1, V13.5, V13.6, V11.6 DPI)
    """
    fig, ax = plt.subplots(figsize=(8, 1))
    ax.set_aspect('auto') # Not 'equal' for 1D, use 'auto' (V10.2 D, V11.6)

    # Set x-axis limits and ticks (V13.0, V13.5)
    ax.set_xlim(x_min, x_max)
    ax.xaxis.set_major_locator(MultipleLocator(1)) # Ticks every 1 unit (V13.0)
    ax.set_ylim(-0.5, 0.5) # Keep a small y-range for the line

    # Hide y-axis and top/right/left spines
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Make the bottom spine (x-axis) visible and thick
    ax.spines['bottom'].set_position('center')
    ax.spines['bottom'].set_linewidth(1.5)

    # Draw number line (black line at y=0)
    ax.axhline(0, color='black', linewidth=1.5)

    # Draw arrows at ends of the number line (V13.6 Arrow Ban)
    ax.plot(x_max, 0, ">k", clip_on=False, markersize=8) # Right arrow
    ax.plot(x_min, 0, "<k", clip_on=False, markersize=8) # Left arrow

    # Label origin '0' (V10.2 D, V13.0 標註權限隔離, V13.1 標籤純淨化, V13.5 標籤隔離, V11.6 Label Halo)
    ax.text(0, -0.3, '0', color='black', ha='center', va='top', fontsize=18, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=1.5, alpha=0.9))

    # Plot the critical value point
    if operator_type in ['>', '<']:
        # Open circle
        ax.plot(critical_value, 0, 'o', markerfacecolor='white', markeredgecolor='blue', markersize=10, zorder=5)
    elif operator_type in ['>=', '<=']:
        # Closed circle
        ax.plot(critical_value, 0, 'o', markerfacecolor='blue', markeredgecolor='blue', markersize=10, zorder=5)

    # Draw the solution line and arrow
    if operator_type in ['>', '>=']:
        ax.plot([critical_value, x_max], [0, 0], color='blue', linewidth=3, zorder=4)
        ax.plot(x_max, 0, ">", color='blue', markersize=8, clip_on=False, zorder=5) # Solution arrow
    elif operator_type in ['<', '<=']:
        ax.plot([x_min, critical_value], [0, 0], color='blue', linewidth=3, zorder=4)
        ax.plot(x_min, 0, "<", color='blue', markersize=8, clip_on=False, zorder=5) # Solution arrow

    # Set x-tick labels to only show numbers (V13.0, V11.6 Label Halo)
    # Filter out 0 to avoid double label, as 0 is already handled by ax.text.
    ticks = []
    for t in range(int(x_min), int(x_max) + 1):
        # Avoid overlap with 0 and critical_value label.
        # Use a small tolerance for critical_value comparison, as it might be float.
        if t != 0 and not math.isclose(t, critical_value, abs_tol=0.4): # If critical_value is like 0.5, avoid 0 and 1
            ticks.append(t)

    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks], bbox=dict(facecolor='white', edgecolor='none', pad=1.5, alpha=0.9))
    
    # Add critical value as a text label below the number line, if it's not an integer tick itself or 0
    # V13.0 標註權限隔離, V13.1 標籤純淨化, V13.5 標籤隔離, V11.6 Label Halo
    # Only label if it's not 0 and not a standard integer tick (to avoid clutter)
    if not math.isclose(critical_value, 0.0, abs_tol=1e-9) and \
       not (critical_value == int(critical_value) and int(critical_value) in ticks):
        
        # Position the label slightly below the line
        label_y_pos = -0.3 # Below the axis
        
        # Format the critical value for the label (e.g., 0.5, -2.0, 3)
        crit_val_label = f"{critical_value:.1f}" if critical_value != int(critical_value) else str(int(critical_value))
        
        ax.text(critical_value, label_y_pos, crit_val_label, 
                color='blue', ha='center', va='top', fontsize=12,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5, alpha=0.9))


    # Convert plot to base64 image (V11.6 Resolution)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300) # DPI set here
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# --- Top-level functions ---

def generate(level=1):
    """
    Generates a K12 math problem about one-variable linear inequalities.
    (V3.1: top-level function, V4.1: random choice, V10.1: random generation)
    """
    # Problem Type Mapping (V9.1)
    # Type 1 (Maps to Example 1): Basic Inequality Solving
    # Type 2 (Maps to Example 2): Inequality with Negative Coefficient
    # Type 3 (Maps to Example 3): Multi-step Inequality Solving
    problem_type = random.choice([1, 2, 3]) 

    question_text = ""
    critical_value = 0.0
    operator_type = random.choice(['>', '<', '>=', '<=']) # Initial operator
    
    # Helper for LaTeX symbol (V16.12 Raw String Fix)
    def op_to_latex(op):
        return op.replace(">=", r"\ge").replace("<=", r"\le")

    # Generate numbers for coefficients and constants (V10.1: 數據禁絕常數)
    # For K12 basic inequalities, use integers for simplicity.
    # Level could be used to enable fractions later.
    
    # a for 'a' coefficient in ax+b
    a_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)
    a = int(a_data[0])
    while a == 0: # Ensure 'a' coefficient is not zero to avoid division by zero or trivial 0=0 cases
        a_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)
        a = int(a_data[0])

    # b for 'b' constant
    b_data = _generate_coordinate_value(min_val=-10, max_val=10, allow_fraction=False)
    b = int(b_data[0])

    # c for 'c' constant
    c_data = _generate_coordinate_value(min_val=-10, max_val=10, allow_fraction=False)
    c = int(c_data[0])
    
    current_op = operator_type # Use current_op to track potential changes for negative coefficients

    if problem_type == 1: # Type 1 (Maps to Example 1): Basic Inequality Solving
        form_choice = random.choice([1, 2, 3])
        
        if form_choice == 1: # x + b op c  => x op c - b
            # Build string for 'b' (V1.0: 方程式生成鎖死 - manual string combination)
            b_term_str = ""
            if b > 0:
                b_term_str = "+ {b_val}".replace("{b_val}", str(b))
            elif b < 0:
                b_term_str = "- {b_val}".replace("{b_val}", str(abs(b)))
            # If b == 0, b_term_str remains empty, resulting in 'x op c'
            
            question_template = r"解不等式 $x{b_term} {op} {c_val}$，並將其解圖示在數線上。"
            question_text = question_template.replace("{b_term}", b_term_str) \
                                             .replace("{op}", op_to_latex(current_op)).replace("{c_val}", str(c))
            critical_value = c - b

        elif form_choice == 2: # x - b op c => x op c + b
            # Ensure b is positive for 'x - b' form to be distinct from 'x + (-b)'
            b_positive = abs(b)
            if b_positive == 0: # If b was initially 0, make it a positive non-zero number
                b_positive = random.randint(1, 10) 
            question_template = r"解不等式 $x - {b_val} {op} {c_val}$，並將其解圖示在數線上。"
            question_text = question_template.replace("{b_val}", str(b_positive)) \
                                             .replace("{op}", op_to_latex(current_op)).replace("{c_val}", str(c))
            critical_value = c + b_positive

        else: # ax op c (ensure a > 0 for Type 1 basic) => x op c / a
            a_positive = abs(a) # Enforce positive 'a'
            # Build string for 'a' coefficient (V1.0: 方程式生成鎖死)
            a_term_str = ""
            if a_positive == 1:
                a_term_str = "x"
            else:
                a_term_str = "{a_val}x".replace("{a_val}", str(a_positive))

            question_template = r"解不等式 ${a_term} {op} {c_val}$，並將其解圖示在數線上。"
            question_text = question_template.replace("{a_term}", a_term_str) \
                                             .replace("{op}", op_to_latex(current_op)).replace("{c_val}", str(c))
            critical_value = c / a_positive
            
    elif problem_type == 2: # Type 2 (Maps to Example 2): Inequality with Negative Coefficient
        # Form: -ax op c (ensure a > 0, so -a is negative) => x flipped_op c / (-a)
        a_positive = abs(a) # Ensure 'a' is positive for -ax form
        
        # Build string for '-a' coefficient (V1.0: 方程式生成鎖死)
        a_term_str = ""
        if a_positive == 1:
            a_term_str = "-x"
        else:
            a_term_str = "-{a_val}x".replace("{a_val}", str(a_positive))

        # Use INITIAL operator for question text
        question_template = r"解不等式 ${a_term} {op} {c_val}$，並將其解圖示在數線上。"
        question_text = question_template.replace("{a_term}", a_term_str) \
                                         .replace("{op}", op_to_latex(current_op)).replace("{c_val}", str(c))
        
        critical_value = c / (-a_positive)
        
        # Flip the operator (V10.1: 公式計算)
        if current_op == '>': current_op = '<'
        elif current_op == '<': current_op = '>'
        elif current_op == '>=': current_op = '<='
        elif current_op == '<=': current_op = '>='

    elif problem_type == 3: # Type 3 (Maps to Example 3): Multi-step Inequality Solving
        d_data = _generate_coordinate_value(min_val=-10, max_val=10, allow_fraction=False)
        d = int(d_data[0])
        
        # For cx+d, we need a coefficient for x, let's call it 'coeff_c' to distinguish from constant 'c'
        coeff_c_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)
        coeff_c = int(coeff_c_data[0])
        
        # Ensure a != coeff_c for a meaningful inequality (V10.1: 公式計算)
        # Prevents 0x > 5 or 0x < 5 cases.
        while a == coeff_c:
            a_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)
            a = int(a_data[0])
            coeff_c_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)
            coeff_c = int(coeff_c_data[0])
        
        # Build string for ax + b (V1.0: 方程式生成鎖死)
        ax_b_parts = []
        if a == 1:
            ax_b_parts.append("x")
        elif a == -1:
            ax_b_parts.append("-x")
        else:
            ax_b_parts.append(str(a) + "x")
        
        if b > 0:
            ax_b_parts.append(" + " + str(b))
        elif b < 0:
            ax_b_parts.append(" - " + str(abs(b)))
        
        ax_b_str = "".join(ax_b_parts)

        # Build string for cx + d (V1.0: 方程式生成鎖死)
        cx_d_parts = []
        if coeff_c == 1:
            cx_d_parts.append("x")
        elif coeff_c == -1:
            cx_d_parts.append("-x")
        else:
            cx_d_parts.append(str(coeff_c) + "x")
        
        if d > 0:
            cx_d_parts.append(" + " + str(d))
        elif d < 0:
            cx_d_parts.append(" - " + str(abs(d)))
        
        cx_d_str = "".join(cx_d_parts)

        question_template = r"解不等式 ${lhs} {op} {rhs}$，並將其解圖示在數線上。"
        question_text = question_template.replace("{lhs}", ax_b_str) \
                                         .replace("{op}", op_to_latex(current_op)) \
                                         .replace("{rhs}", cx_d_str)

        # Solve: (a - coeff_c)x op (d - b)
        coefficient_x_final = a - coeff_c
        constant_term_final = d - b

        if coefficient_x_final > 0:
            critical_value = constant_term_final / coefficient_x_final
            # Operator remains the same
        elif coefficient_x_final < 0:
            critical_value = constant_term_final / coefficient_x_final
            # Flip the operator (V10.1: 公式計算)
            if current_op == '>': current_op = '<'
            elif current_op == '<': current_op = '>'
            elif current_op == '>=': current_op = '<='
            elif current_op == '<=': current_op = '>='
        # coefficient_x_final cannot be 0 due to the while loop ensuring a != coeff_c.

    # Format critical_value for display (V13.0 格式精確要求, V13.5 整數優先)
    if critical_value == int(critical_value):
        critical_value_for_display = str(int(critical_value))
    else:
        critical_value_for_display = f"{critical_value:.2f}" # Format to 2 decimal places if float

    # Construct the correct answer string (V16.11 LaTeX Standard)
    # Canonical form: x op value -> $x \op value$
    correct_answer_str = r"$x {op} {val}$".replace("{op}", op_to_latex(current_op)).replace("{val}", critical_value_for_display)
    
    # Generate image (V16.11 Blank Template)
    # Determine number line range based on critical value
    abs_crit_val = abs(critical_value)
    
    # Calculate a base range.
    range_buffer = 5 
    min_abs_range = 10 
    
    # Determine the maximum absolute extent needed
    max_extent = max(min_abs_range, math.ceil(abs_crit_val) + range_buffer)
    
    # Set symmetric x_min and x_max
    x_min_graph = -max_extent
    x_max_graph = max_extent

    # Use draw_number_line with empty intervals to get a blank number line skeleton
    image_base64 = draw_number_line({}, x_min=x_min_graph, x_max=x_max_graph, intervals=[])

    # Final answer dictionary (V7.1)
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str, 
        "answer": correct_answer_str, 
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer for inequality problems.
    (V16.12 Syntax: Safe Raw Strings & Unicode)
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 預處理：標準化使用者輸入符號
    def normalize_input(s):
        s = str(s).strip()
        # 移除 LaTeX $ 符號 (若有)
        s = s.replace("$", "").replace(" ", "")
        
        # 符號替換 (Tolerant Input)
        # Handle unicode ≥ (\u2265) and ≤ (\u2264)
        s = s.replace("\u2265", r"\ge").replace("=>", r"\ge").replace(">=", r"\ge")
        s = s.replace("\u2264", r"\le").replace("=<", r"\le").replace("<=", r"\le")
        # 處理已有的 LaTeX
        s = s.replace(r"\geq", r"\ge").replace(r"\leq", r"\le")
        return s

    def parse_inequality(s):
        # 統一將 \ge, \le 替換為單一 token
        s = normalize_input(s)
        s = s.replace(r"\ge", "@GE@").replace(r"\le", "@LE@")
        
        # Regex (Group 1: lhs, 2: op, 3: rhs)
        pattern = r"^(.*?)(@GE@|@LE@|>|<)(.*)$"
        match = re.match(pattern, s)
        
        if not match:
            return None, None
            
        lhs, op, rhs = match.groups()
        
        try:
            # 判斷變數 x 的位置
            if "x" in lhs and "x" not in rhs:
                val = float(rhs)
                direction = "normal"
            elif "x" in rhs and "x" not in lhs:
                val = float(lhs)
                direction = "reversed" # 5 < x => x > 5
            else:
                return None, None
        except:
            return None, None

        # map back tokens to standard comparison ops
        op_map = {
            ">": ">", "<": "<",
            "@GE@": ">=", "@LE@": "<="
        }
        std_op = op_map.get(op, op)

        if direction == "reversed":
            if std_op == ">": final_op = "<"
            elif std_op == "<": final_op = ">"
            elif std_op == ">=": final_op = "<="
            elif std_op == "<=": final_op = ">="
            else: final_op = std_op
        else:
            final_op = std_op
            
        return val, final_op

    u_val, u_op = parse_inequality(user_answer)
    c_val, c_op = parse_inequality(correct_answer)
    
    if u_val is None or c_val is None:
         return {"correct": False, "result": "答案格式不符，請確認輸入格式。"}
         
    # 數值比對
    val_match = math.isclose(u_val, c_val, rel_tol=1e-9, abs_tol=1e-9)
    op_match = (u_op == c_op)
    
    if val_match and op_match:
        return {"correct": True, "result": "正確！"}
        
    # Use f-string instead of fr-string to be safe (V16.12 Fix)
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}


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
