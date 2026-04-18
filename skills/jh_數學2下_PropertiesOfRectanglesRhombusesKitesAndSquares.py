# ==============================================================================
# ID: jh_數學2下_PropertiesOfRectanglesRhombusesKitesAndSquares
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 61.20s | RAG: 5 examples
# Created At: 2026-01-29 16:30:22
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
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

# --- 4. Answer Checker (V18.15 Robust Boolean & Coordinate Checker) ---
def check(user_answer, correct_answer):
    import re, math
    
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}

    # Cleaning function
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Remove LaTeX and special chars
        return re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', s) 

    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    # [Expanded Vocabulary]
    yes_group = ["是", "yes", "true", "1", "o", "right", "正確", "對", "correct"]
    no_group = ["否", "no", "false", "0", "x", "wrong", "錯誤", "錯", "不正確", "不一定"]
    
    # 1. Boolean Check
    if c_str in yes_group:
        is_correct = u_str in yes_group
        return {"correct": is_correct, "result": "正確！" if is_correct else "答案錯誤"}
    if c_str in no_group:
        is_correct = u_str in no_group
        return {"correct": is_correct, "result": "正確！" if is_correct else "答案錯誤"}

    # 2. Coordinate / Numeric Sequence Check (V13.6 Logic)
    try:
        # Check if answer is a sequence like "-3, 2"
        user_parts = [float(p) for p in re.split(r'[,，\s]+', re.sub(r'[()D]', '', u_str)) if p]
        correct_parts = [float(p) for p in re.split(r'[,，\s]+', re.sub(r'[()D]', '', c_str)) if p]
        
        if len(user_parts) == len(correct_parts) and len(user_parts) > 0:
            all_match = True
            for u, c in zip(user_parts, correct_parts):
                if not math.isclose(u, c, abs_tol=1e-5):
                    all_match = False
                    break
            if all_match: return {"correct": True, "result": "正確！"}
    except:
        pass

    # 3. Fallback String Check
    if clean(u_str) == clean(c_str): 
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}



import base64
from io import BytesIO
from datetime import datetime
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# V10.2 Coordinate Hardening Spec: _generate_coordinate_value()
def _generate_coordinate_value(min_val, max_val, is_fraction_allowed=True, denominator_range=(2, 4)):
    """
    Generates a coordinate value, potentially a fraction.
    Returns (float_val, (int_part, num, den, is_neg)).
    """
    is_neg = random.choice([True, False])
    int_part = random.randint(0, max_val - 1) # Ensure magnitude is within range
    
    if is_fraction_allowed and random.random() < 0.3: # ~30% chance for fraction
        denominator = random.randint(denominator_range[0], denominator_range[1])
        numerator = random.randint(1, denominator - 1) # V13.1 禁絕假分數
        
        float_val = int_part + numerator / denominator
        if is_neg:
            float_val = -float_val
            
        # Adjust int_part for negative fractions for display consistency
        display_int_part = int_part
        if is_neg and float_val != 0:
             display_int_part = int_part if int_part == 0 else int_part + 1 # -1 1/2 should display as -1 and 1/2
             if float_val < 0:
                 display_int_part = abs(int(float_val)) if int(float_val) == float_val else abs(int(float_val)) + 1 # Correct for negative mixed representation
        
        return float_val, (display_int_part if not is_neg else -display_int_part, numerator, denominator, is_neg)
    else:
        float_val = int_part
        if is_neg:
            float_val = -float_val
        return float_val, (int_part if not is_neg else -int_part, 0, 0, is_neg)

def _format_coordinate(coord_data):
    """
    Formats coordinate data (int_part, num, den, is_neg) into a string.
    V13.0 & V13.5: Ensure integer coordinates are formatted as integers.
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    if num == 0:
        return str(int(float_val)) # V13.0 & V13.5: Ensure integer format
    
    # Handle negative mixed fractions for display
    if is_neg:
        if int_part == 0: # Pure negative fraction like -1/2
            return r"-\frac{{{num}}}{{{den}}}".replace("{num}", str(num)).replace("{den}", str(den))
        else: # Negative mixed fraction like -1 1/2
            return r"-{int_part}\frac{{{num}}}{{{den}}}".replace("{int_part}", str(abs(int_part))).replace("{num}", str(num)).replace("{den}", str(den))
    else: # Positive mixed or pure fraction
        if int_part == 0:
            return r"\frac{{{num}}}{{{den}}}".replace("{num}", str(num)).replace("{den}", str(den))
        else:
            return r"{int_part}\frac{{{num}}}{{{den}}}".replace("{int_part}", str(int_part)).replace("{num}", str(num)).replace("{den}", str(den))

def _draw_coordinate_plane(points_with_labels, x_range=(-10, 10), y_range=(-10, 10), grid_interval=1):
    """
    Draws a coordinate plane with specified points.
    V10.2 Pure Style, V13.0, V13.5, V13.6, V17.1 Hardening.
    points_with_labels: list of (x, y, label) tuples.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.set_aspect('equal') # V10.2
    ax.grid(True, linestyle='--', alpha=0.6)

    # Set symmetric and wide limits (V13.5)
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # Draw major ticks and labels (V17.1 Critical Rule)
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, grid_interval))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, grid_interval))
    
    # Draw axes with arrows (V13.6 API Hardened Spec)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    
    # Use ax.plot for arrows (V13.6 API Hardened Spec)
    ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8)
    ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8)

    # Label origin (V10.2)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')
    
    # V13.5 標籤隔離: ax.text 只能標註點名稱
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='blue', markersize=6)
        ax.text(x + 0.3, y + 0.3, label, color='black', fontsize=12, ha='left', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')) # V10.2白色光暈

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# V13.6 Exact Check Logic
def _check_numeric_sequence(user_answer, correct_answer_str):
    """
    Robust check logic for numeric sequences.
    V13.5: Strictly numeric sequence comparison.
    """
    # V18.8, V18.9: Local imports
    import re
    
    # V1.2.2: Input Sanitization using Regex
    # Remove LaTeX, variable prefixes, spaces, and common separators
    user_sanitized = re.sub(r'[\\$}{=\[\]a-zA-Z\s,;:]', '', str(user_answer))
    correct_sanitized = re.sub(r'[\\$}{=\[\]a-zA-Z\s,;:]', '', str(correct_answer_str))

    # Split by common delimiters or assume contiguous numbers if no delimiter
    user_parts = [part for part in re.split(r'[/,\s]', user_sanitized) if part]
    correct_parts = [part for part in re.split(r'[/,\s]', correct_sanitized) if part]

    if not user_parts or not correct_parts:
        return False

    # Attempt to convert to numbers (float for flexibility)
    try:
        user_nums = [float(eval(part)) for part in user_parts] # Use eval for fractions like '1/2'
        correct_nums = [float(eval(part)) for part in correct_parts]
    except (ValueError, SyntaxError):
        return False

    # Compare sequences
    if len(user_nums) != len(correct_nums):
        return False

    # V1.2.2: Support for equivalent mathematical formats (e.g., 1/2 = 0.5)
    # Use a small tolerance for float comparison
    tolerance = 1e-6
    for u, c in zip(user_nums, correct_nums):
        if abs(u - c) > tolerance:
            return False
    return True


def generate(level=1):
    # V18.8, V18.9: Local imports
    
    
    import base64
    from io import BytesIO
    from datetime import datetime
    import re
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np # For np.arange in _draw_coordinate_plane

    problem_type = random.choice([
        "rectangle_properties",
        "rhombus_properties",
        "kite_properties",
        "square_properties",
        "coordinate_rectangle_identification",
        "coordinate_rhombus_properties",
        "conditional_identification"
    ])

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = ""
    answer_display = "" # For V1.2.2 answer display

    # --- Problem Type 1: 長方形性質計算 (Maps to hypothetical Example 1, 2) ---
    if problem_type == "rectangle_properties":
        
        pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10), (9, 12, 15)]
        a_val, b_val, c_val = random.choice(pythagorean_triples)
        
        scale = random.randint(1, 3)
        a_val *= scale
        b_val *= scale
        c_val *= scale

        sub_type = random.choice(["find_side", "find_diagonal_part"])

        if sub_type == "find_side":
            if random.random() < 0.5: # Ask for side b
                question_text = r"長方形 ABCD 中，已知 $\overline{{AB}} = {a_val}$ 公分，對角線 $\overline{{AC}} = {c_val}$ 公分，則 $\overline{{BC}}$ 的長度是多少公分？".replace("{a_val}", str(a_val)).replace("{c_val}", str(c_val))
                correct_answer = str(b_val)
                solution_text = r"在長方形 ABCD 中，$\triangle ABC$ 為直角三角形。根據畢氏定理，$\overline{{AB}}^2 + \overline{{BC}}^2 = \overline{{AC}}^2$。所以 ${a_val}^2 + \overline{{BC}}^2 = {c_val}^2$，$ {a_val_sq} + \overline{{BC}}^2 = {c_val_sq}$。$\overline{{BC}}^2 = {c_val_sq} - {a_val_sq} = {b_val_sq}$。因此 $\overline{{BC}} = {b_val}$ 公分。".replace("{a_val}", str(a_val)).replace("{c_val}", str(c_val)).replace("{a_val_sq}", str(a_val**2)).replace("{c_val_sq}", str(c_val**2)).replace("{b_val_sq}", str(b_val**2)).replace("{b_val}", str(b_val))
                answer_display = r"${b_val}$ 公分".replace("{b_val}", str(b_val))
            else: # Ask for side a
                question_text = r"長方形 ABCD 中，已知 $\overline{{BC}} = {b_val}$ 公分，對角線 $\overline{{AC}} = {c_val}$ 公分，則 $\overline{{AB}}$ 的長度是多少公分？".replace("{b_val}", str(b_val)).replace("{c_val}", str(c_val))
                correct_answer = str(a_val)
                solution_text = r"在長方形 ABCD 中，$\triangle ABC$ 為直角三角形。根據畢氏定理，$\overline{{AB}}^2 + \overline{{BC}}^2 = \overline{{AC}}^2$。所以 $\overline{{AB}}^2 + {b_val}^2 = {c_val}^2$。$\overline{{AB}}^2 + {b_val_sq} = {c_val_sq}$。$\overline{{AB}}^2 = {c_val_sq} - {b_val_sq} = {a_val_sq}$。因此 $\overline{{AB}} = {a_val}$ 公分。".replace("{b_val}", str(b_val)).replace("{c_val}", str(c_val)).replace("{b_val_sq}", str(b_val**2)).replace("{c_val_sq}", str(c_val**2)).replace("{a_val_sq}", str(a_val**2)).replace("{a_val}", str(a_val))
                answer_display = r"${a_val}$ 公分".replace("{a_val}", str(a_val))

        elif sub_type == "find_diagonal_part":
            side1 = random.randint(6, 15)
            side2 = random.randint(6, 15)
            while side1 == side2: 
                side2 = random.randint(6, 15)
            
            diagonal_length = math.sqrt(side1**2 + side2**2)
            half_diagonal = diagonal_length / 2

            question_text = r"長方形 ABCD 中，已知 $\overline{{AB}} = {side1}$ 公分，$\overline{{BC}} = {side2}$ 公分。若對角線 $\overline{{AC}}$ 與 $\overline{{BD}}$ 交於 O 點，則 $\overline{{AO}}$ 的長度是多少公分？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{side1}", str(side1)).replace("{side2}", str(side2))
            correct_answer = str(round(half_diagonal, 1)) 
            
            if half_diagonal == int(half_diagonal):
                sol_diag = str(int(diagonal_length))
                sol_half_diag = str(int(half_diagonal))
            else:
                sol_diag = r"\sqrt{{{val}}}".replace("{val}", str(side1**2 + side2**2))
                sol_half_diag = r"\frac{{\sqrt{{{val}}}}}{{2}}".replace("{val}", str(side1**2 + side2**2))
                
            solution_text = r"在長方形 ABCD 中，$\triangle ABC$ 為直角三角形。根據畢氏定理，$\overline{{AC}}^2 = \overline{{AB}}^2 + \overline{{BC}}^2 = {side1_sq} + {side2_sq} = {sum_sq}$。所以 $\overline{{AC}} = {sol_diag}$ 公分。長方形的對角線互相平分且等長，因此 $\overline{{AO}} = \frac{{1}}{{2}}\overline{{AC}} = {sol_half_diag}$ 公分。答案四捨五入至小數點後一位為 ${rounded_half_diag}$ 公分。".replace("{side1_sq}", str(side1**2)).replace("{side2_sq}", str(side2**2)).replace("{sum_sq}", str(side1**2 + side2**2)).replace("{sol_diag}", sol_diag).replace("{sol_half_diag}", sol_half_diag).replace("{rounded_half_diag}", str(round(half_diagonal, 1)))
            answer_display = r"${rounded_half_diag}$ 公分".replace("{rounded_half_diag}", str(round(half_diagonal, 1)))


    # --- Problem Type 2: 菱形性質計算 (Maps to hypothetical Example 3, 4, 5) ---
    elif problem_type == "rhombus_properties":
        
        half_diag1 = random.randint(3, 8)
        half_diag2 = random.randint(3, 8)
        
        while half_diag1 == half_diag2: 
            half_diag2 = random.randint(3, 8)

        side_length_sq = half_diag1**2 + half_diag2**2
        side_length = math.sqrt(side_length_sq)

        sub_type = random.choice(["find_side", "find_angle", "find_diagonal_sum_special_angle"])

        if sub_type == "find_side":
            diag1_len = half_diag1 * 2
            diag2_len = half_diag2 * 2
            question_text = r"菱形 ABCD 中，已知兩對角線長度分別為 ${diag1_len}$ 公分和 ${diag2_len}$ 公分。求菱形的邊長是多少公分？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{diag1_len}", str(diag1_len)).replace("{diag2_len}", str(diag2_len))
            correct_answer = str(round(side_length, 1))
            
            if side_length == int(side_length):
                sol_side = str(int(side_length))
            else:
                sol_side = r"\sqrt{{{val}}}".replace("{val}", str(side_length_sq))
                
            solution_text = r"菱形的對角線互相垂直平分。因此，形成四個直角三角形，其兩股長分別為對角線長度的一半，即 ${half_diag1}$ 公分和 ${half_diag2}$ 公分。菱形的邊長為這些直角三角形的斜邊。根據畢氏定理，邊長$^2 = {half_diag1_sq} + {half_diag2_sq} = {sum_sq}$。所以邊長為 ${sol_side}$ 公分。答案四捨五入至小數點後一位為 ${rounded_side}$ 公分。".replace("{half_diag1}", str(half_diag1)).replace("{half_diag2}", str(half_diag2)).replace("{half_diag1_sq}", str(half_diag1**2)).replace("{half_diag2_sq}", str(half_diag2**2)).replace("{sum_sq}", str(side_length_sq)).replace("{sol_side}", sol_side).replace("{rounded_side}", str(round(side_length, 1)))
            answer_display = r"${rounded_side}$ 公分".replace("{rounded_side}", str(round(side_length, 1)))

        elif sub_type == "find_angle":
            angle_A = random.randint(40, 80) 
            angle_B = 180 - angle_A
            
            question_text = r"菱形 ABCD 中，已知 $\angle A = {angle_A}°$。求 $\angle B$ 的度數是多少？".replace("{angle_A}", str(angle_A))
            correct_answer = str(angle_B)
            solution_text = r"菱形是平行四邊形的一種，其鄰角互補。因此，$\angle B = 180° - \angle A = 180° - {angle_A}° = {angle_B}°$。".replace("{angle_A}", str(angle_A)).replace("{angle_B}", str(angle_B))
            answer_display = r"${angle_B}°$".replace("{angle_B}", str(angle_B))

        elif sub_type == "find_diagonal_sum_special_angle":
            # Mimic Ex 5: Rhombus ABCD, angle BAO=30, AB=12. Find angle ABO and sum of diagonals.
            side_length_ab = random.randint(8, 15) 
            
            angle_abo = 60 
            
            bo_len_val = side_length_ab / 2
            ao_len_val = side_length_ab * math.sqrt(3) / 2
            
            bd_len_val = 2 * bo_len_val
            ac_len_val = 2 * ao_len_val
            
            sum_diagonals_float = round(bd_len_val + ac_len_val, 1)
            
            question_text = r"如右圖，菱形 ABCD 中，$\angle BAO = 30°$，$\overline{{AB}} = {side_length_ab}$。試回答下列問題：⑴ $\angle ABO$ 是幾度？⑵ 此菱形兩對角線長之和為多少？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{side_length_ab}", str(side_length_ab))
            
            correct_answer = f"{angle_abo}, {sum_diagonals_float}" 
            
            solution_text = r"⑴ 在菱形 ABCD 中，對角線互相垂直，所以 $\triangle AOB$ 是直角三角形，$\angle AOB = 90°$。已知 $\angle BAO = 30°$，因此 $\angle ABO = 180° - 90° - 30° = 60°$。\n⑵ 在直角 $\triangle AOB$ 中，$\overline{{AB}} = {side_length_ab}$。根據 30-60-90 直角三角形的邊長比例，$\overline{{BO}} = \overline{{AB}} \times \sin(30°) = {side_length_ab} \times \frac{{1}}{{2}} = {bo_len_val_int}$。$\overline{{AO}} = \overline{{AB}} \times \cos(30°) = {side_length_ab} \times \frac{{\sqrt{{3}}}}{{2}} = {ao_len_val_no_sqrt}\sqrt{{3}}$ (其中 ${ao_len_val_no_sqrt} = {side_length_ab_half}$)。菱形的對角線互相平分，所以 $\overline{{BD}} = 2\overline{{BO}} = 2 \times {bo_len_val_int} = {bd_len_val_int}$。$\overline{{AC}} = 2\overline{{AO}} = 2 \times {ao_len_val_no_sqrt}\sqrt{{3}} = {ac_len_val_no_sqrt}\sqrt{{3}}$。因此，兩對角線長之和為 $\overline{{AC}} + \overline{{BD}} = {ac_len_val_no_sqrt}\sqrt{{3}} + {bd_len_val_int}$。".replace("{side_length_ab}", str(side_length_ab)).replace("{bo_len_val_int}", str(int(bo_len_val))).replace("{ao_len_val_no_sqrt}", str(round(side_length_ab/2, 1) if side_length_ab % 2 != 0 else str(side_length_ab//2))).replace("{side_length_ab_half}", str(side_length_ab/2)).replace("{bd_len_val_int}", str(int(bd_len_val))).replace("{ac_len_val_no_sqrt}", str(side_length_ab))
            answer_display = r"⑴ ${angle_abo}°$ ⑵ ${side_length_ab} + {side_length_ab}\sqrt{{3}}$ (約 ${sum_diagonals_float}$)".replace("{angle_abo}", str(angle_abo)).replace("{side_length_ab}", str(side_length_ab)).replace("{sum_diagonals_float}", str(sum_diagonals_float))


    # --- Problem Type 3: 箏形性質計算 (Maps to hypothetical Example 6) ---
    elif problem_type == "kite_properties":
        
        ao_len = random.randint(4, 10)
        co_len = random.randint(2, ao_len - 1) 
        bo_len = random.randint(3, 8)
        
        ab_sq = ao_len**2 + bo_len**2
        bc_sq = co_len**2 + bo_len**2
        
        ab_len = math.sqrt(ab_sq)
        bc_len = math.sqrt(bc_sq)

        sub_type = random.choice(["find_side", "find_angle_diag_perp"])

        if sub_type == "find_side":
            question_text = r"箏形 ABCD 中，$\overline{{AB}} = \overline{{AD}}$，$\overline{{CB}} = \overline{{CD}}$。對角線 $\overline{{AC}}$ 與 $\overline{{BD}}$ 交於 O 點，且 $\overline{{AC}} \perp \overline{{BD}}$。已知 $\overline{{AO}} = {ao_len}$ 公分，$\overline{{BO}} = {bo_len}$ 公分，$\overline{{CO}} = {co_len}$ 公分。求 $\overline{{BC}}$ 的長度是多少公分？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{ao_len}", str(ao_len)).replace("{bo_len}", str(bo_len)).replace("{co_len}", str(co_len))
            correct_answer = str(round(bc_len, 1))
            
            if bc_len == int(bc_len):
                sol_bc = str(int(bc_len))
            else:
                sol_bc = r"\sqrt{{{val}}}".replace("{val}", str(bc_sq))

            solution_text = r"在箏形 ABCD 中，對角線互相垂直，因此 $\triangle BOC$ 是一個直角三角形。根據畢氏定理，$\overline{{BC}}^2 = \overline{{BO}}^2 + \overline{{CO}}^2 = {bo_len_sq} + {co_len_sq} = {bc_sq}$。所以 $\overline{{BC}} = {sol_bc}$ 公分。答案四捨五入至小數點後一位為 ${rounded_bc}$ 公分。".replace("{bo_len_sq}", str(bo_len**2)).replace("{co_len_sq}", str(co_len**2)).replace("{bc_sq}", str(bc_sq)).replace("{sol_bc}", sol_bc).replace("{rounded_bc}", str(round(bc_len, 1)))
            answer_display = r"${rounded_bc}$ 公分".replace("{rounded_bc}", str(round(bc_len, 1)))

        elif sub_type == "find_angle_diag_perp":
            question_text = r"一個箏形 ABCD，其對角線 $\overline{{AC}}$ 與 $\overline{{BD}}$ 交於 O 點。請問 $\angle AOB$ 的度數是多少？"
            correct_answer = "90"
            solution_text = r"箏形的對角線互相垂直，因此 $\angle AOB = 90°$。"
            answer_display = r"${90}°$"

    # --- Problem Type 4: 正方形性質計算 (Maps to hypothetical Example 5) ---
    elif problem_type == "square_properties":
        
        side = random.randint(5, 12)
        diagonal = side * math.sqrt(2)

        sub_type = random.choice(["find_diagonal", "find_angle_diag"])

        if sub_type == "find_diagonal":
            question_text = r"正方形 ABCD 的邊長為 ${side}$ 公分。求其對角線 $\overline{{AC}}$ 的長度是多少公分？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{side}", str(side))
            correct_answer = str(round(diagonal, 1))
            
            solution_text = r"在正方形 ABCD 中，$\triangle ABC$ 為直角三角形。根據畢氏定理，$\overline{{AC}}^2 = \overline{{AB}}^2 + \overline{{BC}}^2 = {side_sq} + {side_sq} = 2 \times {side_sq} = {two_side_sq}$。所以 $\overline{{AC}} = \sqrt{{{two_side_sq}}} = {side}\sqrt{{2}}$ 公分。答案四捨五入至小數點後一位為 ${rounded_diag}$ 公分。".replace("{side_sq}", str(side**2)).replace("{two_side_sq}", str(2 * side**2)).replace("{side}", str(side)).replace("{rounded_diag}", str(round(diagonal, 1)))
            answer_display = r"${side}\sqrt{{2}}$ 公分 (約 ${rounded_diag}$ 公分)".replace("{side}", str(side)).replace("{rounded_diag}", str(round(diagonal, 1)))

        elif sub_type == "find_angle_diag":
            question_text = r"正方形 ABCD 中，對角線 $\overline{{AC}}$ 與 $\overline{{BD}}$ 交於 O 點。求 $\angle AOB$ 的度數是多少？"
            correct_answer = "90"
            solution_text = r"正方形的對角線互相垂直平分，因此 $\angle AOB = 90°$。"
            answer_display = r"${90}°$"

    # --- Problem Type 5: 座標幾何 - 長方形判斷與性質 (Maps to hypothetical Example 7) ---
    elif problem_type == "coordinate_rectangle_identification":
        
        x_a = random.randint(-5, 5)
        y_a = random.randint(-5, 5)
        
        side_len_x = random.randint(3, 6)
        side_len_y = random.randint(3, 6)
        
        dir_x = random.choice([-1, 1])
        dir_y = random.choice([-1, 1])

        x_b = x_a + side_len_x * dir_x
        y_b = y_a
        x_c = x_a + side_len_x * dir_x
        y_c = y_a + side_len_y * dir_y
        x_d = x_a
        y_d = y_a + side_len_y * dir_y

        points_for_drawing = [
            (x_a, y_a, 'A'), (x_b, y_b, 'B'), (x_c, y_c, 'C'), (x_d, y_d, 'D')
        ]
        
        all_x = [p[0] for p in points_for_drawing]
        all_y = [p[1] for p in points_for_drawing]
        draw_x_range = (min(all_x) - 2, max(all_x) + 2)
        draw_y_range = (min(all_y) - 2, max(all_y) + 2)
        
        # Ensure ranges are symmetric
        max_abs_x = max(abs(draw_x_range[0]), abs(draw_x_range[1]))
        max_abs_y = max(abs(draw_y_range[0]), abs(draw_y_range[1]))
        draw_x_range = (-max_abs_x, max_abs_x)
        draw_y_range = (-max_abs_y, max_abs_y)

        image_base64 = _draw_coordinate_plane(points_for_drawing, x_range=draw_x_range, y_range=draw_y_range)

        sub_type = random.choice(["find_missing_vertex", "calculate_diagonal_length"])

        if sub_type == "find_missing_vertex":
            question_text = r"已知長方形 ABCD 的三個頂點座標為 A({xa}, {ya})、B({xb}, {yb})、C({xc}, {yc})。求 D 點的座標。".replace("{xa}", str(x_a)).replace("{ya}", str(y_a)).replace("{xb}", str(x_b)).replace("{yb}", str(y_b)).replace("{xc}", str(x_c)).replace("{yc}", str(y_c))
            correct_answer = f"{x_d}, {y_d}" 
            solution_text = r"在長方形 ABCD 中，對邊平行且等長。由於 AB 平行於 x 軸 (或 y 軸)，BC 平行於 y 軸 (或 x 軸)，因此 D 點的 x 座標與 A 點相同，y 座標與 C 點相同。故 D 點座標為 ({xd}, {yd})。".replace("{xd}", str(x_d)).replace("{yd}", str(y_d))
            answer_display = r"D({xd}, {yd})".replace("{xd}", str(x_d)).replace("{yd}", str(y_d))

        elif sub_type == "calculate_diagonal_length":
            diagonal_sq = (x_c - x_a)**2 + (y_c - y_a)**2
            diagonal_len = math.sqrt(diagonal_sq)
            
            question_text = r"已知長方形 ABCD 的四個頂點座標為 A({xa}, {ya})、B({xb}, {yb})、C({xc}, {yc})、D({xd}, {yd})。求其對角線 $\overline{{AC}}$ 的長度是多少？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{xa}", str(x_a)).replace("{ya}", str(y_a)).replace("{xb}", str(x_b)).replace("{yb}", str(y_b)).replace("{xc}", str(x_c)).replace("{yc}", str(y_c)).replace("{xd}", str(x_d)).replace("{yd}", str(y_d))
            correct_answer = str(round(diagonal_len, 1))
            
            if diagonal_len == int(diagonal_len):
                sol_diag = str(int(diagonal_len))
            else:
                sol_diag = r"\sqrt{{{val}}}".replace("{val}", str(diagonal_sq))
                
            solution_text = r"在座標平面上，兩點間距離公式為 $\sqrt{{(x_2-x_1)^2 + (y_2-y_1)^2}}$。對角線 $\overline{{AC}}$ 的長度為 $\sqrt{{({xc}-{xa})^2 + ({yc}-{ya})^2}} = \sqrt{{({xc_minus_xa})^2 + ({yc_minus_ya})^2}} = \sqrt{{{diagonal_sq}}} = {sol_diag}$。答案四捨五入至小數點後一位為 ${rounded_diag}$。".replace("{xc}", str(x_c)).replace("{xa}", str(x_a)).replace("{yc}", str(y_c)).replace("{ya}", str(y_a)).replace("{xc_minus_xa}", str(x_c-x_a)).replace("{yc_minus_ya}", str(y_c-y_a)).replace("{diagonal_sq}", str(diagonal_sq)).replace("{sol_diag}", sol_diag).replace("{rounded_diag}", str(round(diagonal_len, 1)))
            answer_display = r"${rounded_diag}$".replace("{rounded_diag}", str(round(diagonal_len, 1)))


    # --- Problem Type 6: 座標幾何 - 菱形性質應用 (Maps to hypothetical Example 8) ---
    elif problem_type == "coordinate_rhombus_properties":
        
        o_x = random.randint(-5, 5)
        o_y = random.randint(-5, 5)
        
        half_d1 = random.randint(2, 5)
        half_d2 = random.randint(2, 5)
        while half_d1 == half_d2:
            half_d2 = random.randint(2, 5)
            
        A_coord = (o_x - half_d1, o_y)
        B_coord = (o_x, o_y + half_d2)
        C_coord = (o_x + half_d1, o_y)
        D_coord = (o_x, o_y - half_d2)

        points_for_drawing = [
            (A_coord[0], A_coord[1], 'A'),
            (B_coord[0], B_coord[1], 'B'),
            (C_coord[0], C_coord[1], 'C'),
            (D_coord[0], D_coord[1], 'D')
        ]
        
        all_x = [p[0] for p in points_for_drawing]
        all_y = [p[1] for p in points_for_drawing]
        draw_x_range = (min(all_x) - 2, max(all_x) + 2)
        draw_y_range = (min(all_y) - 2, max(all_y) + 2)
        
        max_abs_x = max(abs(draw_x_range[0]), abs(draw_x_range[1]))
        max_abs_y = max(abs(draw_y_range[0]), abs(draw_y_range[1]))
        draw_x_range = (-max_abs_x, max_abs_x)
        draw_y_range = (-max_abs_y, max_abs_y)

        image_base64 = _draw_coordinate_plane(points_for_drawing, x_range=draw_x_range, y_range=draw_y_range)

        sub_type = random.choice(["find_diagonal_intersection", "calculate_side_length"])

        if sub_type == "find_diagonal_intersection":
            question_text = r"已知菱形 ABCD 的頂點座標為 A({ax}, {ay})、B({bx}, {by})、C({cx}, {cy})、D({dx}, {dy})。求其兩對角線的交點 O 的座標。".replace("{ax}", str(A_coord[0])).replace("{ay}", str(A_coord[1])).replace("{bx}", str(B_coord[0])).replace("{by}", str(B_coord[1])).replace("{cx}", str(C_coord[0])).replace("{cy}", str(C_coord[1])).replace("{dx}", str(D_coord[0])).replace("{dy}", str(D_coord[1]))
            correct_answer = f"{o_x}, {o_y}"
            solution_text = r"菱形的對角線互相平分，因此對角線的交點 O 是兩對角線的中點。例如，O 是 $\overline{{AC}}$ 的中點。利用中點公式，O 點的 x 座標為 $({ax} + {cx}) / 2 = ({ox_minus_d1} + {ox_plus_d1}) / 2 = {ox}$，y 座標為 $({ay} + {cy}) / 2 = ({oy} + {oy}) / 2 = {oy}$。故 O 點座標為 ({ox}, {oy})。".replace("{ax}", str(A_coord[0])).replace("{ay}", str(A_coord[1])).replace("{cx}", str(C_coord[0])).replace("{cy}", str(C_coord[1])).replace("{ox_minus_d1}", str(o_x - half_d1)).replace("{ox_plus_d1}", str(o_x + half_d1)).replace("{ox}", str(o_x)).replace("{oy}", str(o_y))
            answer_display = r"O({ox}, {oy})".replace("{ox}", str(o_x)).replace("{oy}", str(o_y))

        elif sub_type == "calculate_side_length":
            side_len_sq = half_d1**2 + half_d2**2
            side_len = math.sqrt(side_len_sq)
            
            question_text = r"已知菱形 ABCD 的兩對角線交點為 O({ox}, {oy})，且其中一個頂點 A 的座標為 ({ax}, {ay})，另一個頂點 B 的座標為 ({bx}, {by})。求菱形邊長 $\overline{{AB}}$ 的長度是多少？(請以最簡根式或四捨五入至小數點後一位作答)".replace("{ox}", str(o_x)).replace("{oy}", str(o_y)).replace("{ax}", str(A_coord[0])).replace("{ay}", str(A_coord[1])).replace("{bx}", str(B_coord[0])).replace("{by}", str(B_coord[1]))
            correct_answer = str(round(side_len, 1))

            if side_len == int(side_len):
                sol_side = str(int(side_len))
            else:
                sol_side = r"\sqrt{{{val}}}".replace("{val}", str(side_len_sq))

            solution_text = r"菱形的對角線互相垂直平分，因此 $\triangle AOB$ 為直角三角形。$\overline{{AO}}$ 長度為 $\sqrt{{({ax_minus_ox})^2 + ({ay_minus_oy})^2}} = \sqrt{{({half_d1_sq}) + 0^2}} = {half_d1_val}$。$\overline{{BO}}$ 長度為 $\sqrt{{({bx_minus_ox})^2 + ({by_minus_oy})^2}} = \sqrt{{0^2 + ({half_d2_sq})}} = {half_d2_val}$。根據畢氏定理，$\overline{{AB}}^2 = \overline{{AO}}^2 + \overline{{BO}}^2 = {half_d1_sq} + {half_d2_sq} = {side_len_sq}$。所以 $\overline{{AB}} = {sol_side}$。答案四捨五入至小數點後一位為 ${rounded_side}$。".replace("{ax_minus_ox}", str(A_coord[0]-o_x)).replace("{ay_minus_oy}", str(A_coord[1]-o_y)).replace("{half_d1_val}", str(half_d1)).replace("{bx_minus_ox}", str(B_coord[0]-o_x)).replace("{by_minus_oy}", str(B_coord[1]-o_y)).replace("{half_d2_val}", str(half_d2)).replace("{half_d1_sq}", str(half_d1**2)).replace("{half_d2_sq}", str(half_d2**2)).replace("{side_len_sq}", str(side_len_sq)).replace("{sol_side}", sol_side).replace("{rounded_side}", str(round(side_len, 1)))
            answer_display = r"${rounded_side}$".replace("{rounded_side}", str(round(side_len, 1)))

    # --- Problem Type 7: 條件判斷題 (Maps to hypothetical Example 9) ---
    elif problem_type == "conditional_identification":
        
        condition_type = random.choice(["rectangle_from_parallelogram", "rhombus_from_parallelogram", "square_from_parallelogram"])

        if condition_type == "rectangle_from_parallelogram":
            choice_q = random.choice(["angle", "diagonal"])
            if choice_q == "angle":
                question_text = "判斷題：一個平行四邊形，若其中一個內角是直角，它必定是一個長方形。此敘述是否正確？"
                correct_answer = "是"
                solution_text = "長方形的定義是四個內角都是直角的四邊形。由於平行四邊形的鄰角互補，對角相等，如果一個內角是直角，則所有內角都會是直角，因此它必定是長方形。"
            else:
                question_text = "判斷題：一個平行四邊形，若其兩條對角線等長，它必定是一個長方形。此敘述是否正確？"
                correct_answer = "是"
                solution_text = "平行四邊形的對角線互相平分。如果對角線等長，則平分後的小段也等長，這會導致四個由對角線和邊組成的三角形皆為等腰三角形。在平行四邊形中，對角線等長是其為長方形的充分條件。"
            answer_display = correct_answer 

        elif condition_type == "rhombus_from_parallelogram":
            choice_q = random.choice(["adjacent_sides", "diagonals_perp"])
            if choice_q == "adjacent_sides":
                question_text = "判斷題：一個平行四邊形，若其一組鄰邊等長，它必定是一個菱形。此敘述是否正確？"
                correct_answer = "是"
                solution_text = "菱形的定義是四邊等長的四邊形。由於平行四邊形的對邊等長，如果一組鄰邊等長，則根據對邊等長的性質，所有四邊都會等長，因此它必定是菱形。"
            else:
                question_text = "判斷題：一個平行四邊形，若其兩條對角線互相垂直，它必定是一個菱形。此敘述是否正確？"
                correct_answer = "是"
                solution_text = "在平行四邊形中，如果對角線互相垂直，則透過證明由對角線和邊組成的四個直角三角形全等，可以推導出四邊等長，因此它必定是菱形。"
            answer_display = correct_answer

        elif condition_type == "square_from_parallelogram":
            question_text = "判斷題：一個平行四邊形，若其對角線互相垂直且等長，它必定是一個正方形。此敘述是否正確？"
            correct_answer = "是"
            solution_text = "若平行四邊形對角線垂直，則為菱形（四邊等長）；若對角線等長，則為長方形（四角皆直角）。同時滿足這兩個條件，即為四邊等長且四角皆直角，因此它必定是一個正方形。"
            answer_display = correct_answer

    created_at = datetime.now().isoformat()
    version = "1.0" 

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text,  
        "answer_display": answer_display, 
        "image_base64": image_base64,
        "created_at": created_at,
        "version": version,
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
