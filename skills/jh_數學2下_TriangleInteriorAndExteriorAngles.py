# ==============================================================================
# ID: jh_數學2下_TriangleInteriorAndExteriorAngles
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 81.92s | RAG: 5 examples
# Created At: 2026-01-21 17:54:08
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



import base64
import io
from datetime import datetime
import re
import matplotlib.pyplot as plt
import numpy as np

# --- Helper Functions ---

def _generate_angle(min_val, max_val):
    """Generates a random integer angle."""
    return random.randint(min_val, max_val)

def _draw_triangle_angle_diagram(angle_A_label=None, angle_B_label=None, angle_C_label=None, exterior_angle_label=None, specific_setup=None, highlight_angle=None):
    """
    Draws a generic triangle with angles labeled.
    This function does NOT use a coordinate plane for the triangle itself.
    It simply illustrates the angles.
    Labels can be numeric strings (e.g., "60") or algebraic expressions (e.g., "$x+10$").
    """
    fig, ax = plt.subplots(figsize=(5, 4), dpi=300) # Added dpi=300 as per ULTRA VISUAL STANDARDS
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3)
    ax.axis('off') # Turn off axes for a schematic diagram

    # Define common points for a generic triangle (A is top, B is bottom-left, C is bottom-right)
    points_A = np.array([1.5, 2.5]) 
    points_B = np.array([0, 0])    
    points_C = np.array([3, 0])    

    # Vertex labels
    label_A_text = 'A'
    label_B_text = 'B'
    label_C_text = 'C'
    label_D_text = 'D' # For Type 5

    if specific_setup == 'type5_interior_line':
        # For triangle ABC with D on BC, find angle ADC
        # A is top, B is left, C is right
        
        # Calculate D on BC
        d_x = points_B[0] + (points_C[0] - points_B[0]) * random.uniform(0.3, 0.7)
        points_D = np.array([d_x, points_B[1]]) # D is on BC (same y-coordinate as B and C)

        # Draw triangle ABC
        ax.plot([points_A[0], points_B[0], points_C[0], points_A[0]], 
                [points_A[1], points_B[1], points_C[1], points_A[1]], 'k-')
        # Draw line segment AD
        ax.plot([points_A[0], points_D[0]], [points_A[1], points_D[1]], 'k-')

        # Add vertex labels with white halos
        ax.text(points_A[0], points_A[1]+0.1, label_A_text, fontsize=12, ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
        ax.text(points_B[0]-0.1, points_B[1]-0.1, label_B_text, fontsize=12, ha='right', va='top', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
        ax.text(points_C[0]+0.1, points_C[1]-0.1, label_C_text, fontsize=12, ha='left', va='top', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
        ax.text(points_D[0], points_D[1]-0.1, label_D_text, fontsize=12, ha='center', va='top', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))

        # Angle B (at points_B)
        if angle_B_label is not None:
            label_text = r"$\angle B = " + angle_B_label + r"^\circ$" if "$" not in angle_B_label else r"$\angle B = " + angle_B_label + r"$"
            ax.text(points_B[0]+0.2, points_B[1]+0.1, label_text, fontsize=10, ha='left', va='bottom', color='blue', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        
        # Angle BAD (at points_A, between AB and AD)
        # Calculate approximate position for BAD label
        vec_AB = points_B - points_A
        vec_AD = points_D - points_A
        
        # Normalize vectors and sum for a bisector-like direction for label placement
        vec_AB_norm = vec_AB / np.linalg.norm(vec_AB)
        vec_AD_norm = vec_AD / np.linalg.norm(vec_AD)
        
        label_pos_offset = (vec_AB_norm + vec_AD_norm) * 0.25 # Offset from A
        label_pos = points_A + label_pos_offset
        
        if angle_A_label is not None: # Here angle_A_label represents angle BAD
            label_text = r"$\angle BAD = " + angle_A_label + r"^\circ$" if "$" not in angle_A_label else r"$\angle BAD = " + angle_A_label + r"$"
            ax.text(label_pos[0], label_pos[1], label_text, fontsize=10, ha='center', va='center', color='blue', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))

        # Highlight angle ADC (exterior angle for triangle ABD at D)
        if highlight_angle == 'ADC':
            ax.text(points_D[0]+0.3, points_D[1]+0.1, r"$\angle ADC = ?$", fontsize=10, ha='left', va='bottom', color='purple', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))

    else: # Generic triangle drawing for Types 1, 3, 4, and Type 2 (interior angles for exterior angle calc)
        # Draw triangle using B, C, A as bottom-left, bottom-right, top
        ax.plot([points_B[0], points_C[0], points_A[0], points_B[0]], 
                [points_B[1], points_C[1], points_A[1], points_B[1]], 'k-')

        # Add vertex labels with white halos
        ax.text(points_B[0]-0.1, points_B[1]-0.1, label_B_text, fontsize=12, ha='right', va='top', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
        ax.text(points_C[0]+0.1, points_C[1]-0.1, label_C_text, fontsize=12, ha='left', va='top', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
        ax.text(points_A[0], points_A[1]+0.1, label_A_text, fontsize=12, ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))

        # Add angle labels (A is top, B is bottom-left, C is bottom-right)
        # Positions are heuristic for a generic triangle
        if angle_A_label is not None:
            label_text = r"$\angle A = " + angle_A_label + r"^\circ$" if "$" not in angle_A_label else r"$\angle A = " + angle_A_label + r"$"
            ax.text(points_A[0], points_A[1]-0.2, label_text, fontsize=10, ha='center', va='top', color='blue', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        if angle_B_label is not None:
            label_text = r"$\angle B = " + angle_B_label + r"^\circ$" if "$" not in angle_B_label else r"$\angle B = " + angle_B_label + r"$"
            ax.text(points_B[0]+0.3, points_B[1]+0.2, label_text, fontsize=10, ha='left', va='bottom', color='blue', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        if angle_C_label is not None:
            label_text = r"$\angle C = " + angle_C_label + r"^\circ$" if "$" not in angle_C_label else r"$\angle C = " + angle_C_label + r"$"
            ax.text(points_C[0]-0.3, points_C[1]+0.2, label_text, fontsize=10, ha='right', va='bottom', color='blue', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        
        # Exterior angle C (extends from C to the right)
        if exterior_angle_label is not None:
            # Extend BC (from B to C and beyond)
            vec_BC = points_C - points_B
            p_D_ext = points_C + vec_BC * 0.5 # Extend from C towards right
            ax.plot([points_C[0], p_D_ext[0]], [points_C[1], p_D_ext[1]], 'k--') # Draw extension line

            label_text = r"$\angle ACD = " + exterior_angle_label + r"^\circ$" if "$" not in exterior_angle_label else r"$\angle ACD = " + exterior_angle_label + r"$"
            ax.text(points_C[0] + 0.3, points_C[1] + 0.1, label_text, fontsize=10, ha='left', va='bottom', color='red', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))

        # Highlight specific angle if requested
        if highlight_angle == 'A':
            ax.text(points_A[0], points_A[1]-0.2, r"$\angle A = ?$", fontsize=10, ha='center', va='top', color='purple', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        elif highlight_angle == 'B':
            ax.text(points_B[0]+0.3, points_B[1]+0.2, r"$\angle B = ?$", fontsize=10, ha='left', va='bottom', color='purple', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        elif highlight_angle == 'C':
            ax.text(points_C[0]-0.3, points_C[1]+0.2, r"$\angle C = ?$", fontsize=10, ha='right', va='bottom', color='purple', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))
        elif highlight_angle == 'exterior_C':
            # Extend BC (from B to C and beyond)
            vec_BC = points_C - points_B
            p_D_ext = points_C + vec_BC * 0.5 # Extend from C towards right
            ax.plot([points_C[0], p_D_ext[0]], [points_C[1], p_D_ext[1]], 'k--') # Draw extension line
            ax.text(points_C[0] + 0.3, points_C[1] + 0.1, r"Exterior $\angle C = ?$", fontsize=10, ha='left', va='bottom', color='purple', bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7))

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300) # Added dpi=300
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# --- Main Functions ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5])
    question_text = ""
    correct_answer = ""
    image_base64 = None

    if problem_type == 1: # Type 1 (Maps to Example 1): Basic Interior Angle Sum
        angle_A = _generate_angle(30, 80)
        angle_B = _generate_angle(30, 180 - angle_A - 30) # Ensure angle_C > 0
        angle_C = 180 - angle_A - angle_B
        
        find_angle = random.choice(['A', 'B', 'C'])
        
        if find_angle == 'A':
            question_text = r"在 $\triangle ABC$ 中，若 $\angle B = {b}^\circ$ 且 $\angle C = {c}^\circ$，則 $\angle A = ?$".replace("{b}", str(angle_B)).replace("{c}", str(angle_C))
            correct_answer = str(angle_A)
            image_base64 = _draw_triangle_angle_diagram(angle_B_label=str(angle_B), angle_C_label=str(angle_C), highlight_angle='A')
        elif find_angle == 'B':
            question_text = r"在 $\triangle ABC$ 中，若 $\angle A = {a}^\circ$ 且 $\angle C = {c}^\circ$，則 $\angle B = ?$".replace("{a}", str(angle_A)).replace("{c}", str(angle_C))
            correct_answer = str(angle_B)
            image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(angle_A), angle_C_label=str(angle_C), highlight_angle='B')
        else: # find_angle == 'C'
            question_text = r"在 $\triangle ABC$ 中，若 $\angle A = {a}^\circ$ 且 $\angle B = {b}^\circ$，則 $\angle C = ?$".replace("{a}", str(angle_A)).replace("{b}", str(angle_B))
            correct_answer = str(angle_C)
            image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(angle_A), angle_B_label=str(angle_B), highlight_angle='C')

    elif problem_type == 2: # Type 2 (Maps to Example 2): Basic Exterior Angle Property
        angle_A = _generate_angle(30, 80)
        angle_B = _generate_angle(30, 180 - angle_A - 30)
        exterior_angle_C = angle_A + angle_B

        find_what = random.choice(['exterior_C', 'angle_A', 'angle_B'])

        if find_what == 'exterior_C':
            question_text = r"在 $\triangle ABC$ 中，若 $\angle A = {a}^\circ$ 且 $\angle B = {b}^\circ$，則 $\angle C$ 的外角為多少度？".replace("{a}", str(angle_A)).replace("{b}", str(angle_B))
            correct_answer = str(exterior_angle_C)
            image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(angle_A), angle_B_label=str(angle_B), highlight_angle='exterior_C')
        elif find_what == 'angle_A':
            question_text = r"在 $\triangle ABC$ 中，若 $\angle B = {b}^\circ$ 且 $\angle C$ 的外角為 ${ext_C}^\circ$，則 $\angle A = ?$".replace("{b}", str(angle_B)).replace("{ext_C}", str(exterior_angle_C))
            correct_answer = str(angle_A)
            image_base64 = _draw_triangle_angle_diagram(angle_B_label=str(angle_B), exterior_angle_label=str(exterior_angle_C), highlight_angle='A')
        else: # find_what == 'angle_B'
            question_text = r"在 $\triangle ABC$ 中，若 $\angle A = {a}^\circ$ 且 $\angle C$ 的外角為 ${ext_C}^\circ$，則 $\angle B = ?$".replace("{a}", str(angle_A)).replace("{ext_C}", str(exterior_angle_C))
            correct_answer = str(angle_B)
            image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(angle_A), exterior_angle_label=str(exterior_angle_C), highlight_angle='B')

    elif problem_type == 3: # Type 3 (Maps to Example 3): Exterior Angles with Algebra (following RAG Ex 3 strictly)
        # RAG Ex 3: 有一個三角形，它的一組外角度數為 $2x°$、$3x°$、$4x°$，則此三角形的最大內角為多少度？
        
        # Coefficients for exterior angles: a*x, b*x, c*x
        # Sum of exterior angles is 360. So, (a+b+c) * x = 360.
        
        valid_coeffs_found = False
        attempts = 0
        a_coeff, b_coeff, c_coeff = 0, 0, 0
        x_val = 0
        ext_angle1, ext_angle2, ext_angle3 = 0, 0, 0
        int_angle1, int_angle2, int_angle3 = 0, 0, 0

        while not valid_coeffs_found and attempts < 100:
            a_coeff = random.randint(1, 5)
            b_coeff = random.randint(1, 5)
            c_coeff = random.randint(1, 5)
            sum_coeffs = a_coeff + b_coeff + c_coeff
            
            if sum_coeffs > 0 and 360 % sum_coeffs == 0:
                x_val = 360 // sum_coeffs
                
                # Calculate exterior angles
                ext_angle1 = a_coeff * x_val
                ext_angle2 = b_coeff * x_val
                ext_angle3 = c_coeff * x_val
                
                # Calculate interior angles
                int_angle1 = 180 - ext_angle1
                int_angle2 = 180 - ext_angle2
                int_angle3 = 180 - ext_angle3
                
                # Ensure all exterior angles are between 10 and 170 (inclusive) to have valid interior angles.
                # And interior angles must be positive.
                if (10 <= ext_angle1 <= 170 and 10 <= ext_angle2 <= 170 and 10 <= ext_angle3 <= 170) and \
                   (int_angle1 > 0 and int_angle2 > 0 and int_angle3 > 0):
                    valid_coeffs_found = True
                    break
            attempts += 1
        
        if not valid_coeffs_found: # Fallback to RAG Ex 3 values if random generation fails
            a_coeff, b_coeff, c_coeff = 2, 3, 4 
            x_val = 40
            ext_angle1, ext_angle2, ext_angle3 = 80, 120, 160
            int_angle1, int_angle2, int_angle3 = 100, 60, 20

        exterior_angle_expr1 = r"${a}x^\circ$".replace("{a}", str(a_coeff))
        exterior_angle_expr2 = r"${b}x^\circ$".replace("{b}", str(b_coeff))
        exterior_angle_expr3 = r"${c}x^\circ$".replace("{c}", str(c_coeff))

        question_text = r"有一個三角形，它的一組外角度數分別為 ${e1}$、${e2}$、${e3}$。請問此三角形的最大內角為多少度？".replace("{e1}", exterior_angle_expr1).replace("{e2}", exterior_angle_expr2).replace("{e3}", exterior_angle_expr3)
        
        max_interior_angle = max(int_angle1, int_angle2, int_angle3)
        correct_answer = str(max_interior_angle)
        
        # For drawing, display the actual interior angles as the question asks for the max interior angle.
        image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(int_angle1), angle_B_label=str(int_angle2), angle_C_label=str(int_angle3))

    elif problem_type == 4: # Type 4 (Maps to Example 4): Combined with Isosceles Triangle Properties
        isosceles_type = random.choice(['base_given_vertex_find', 'vertex_given_base_find'])

        if isosceles_type == 'base_given_vertex_find':
            base_angle = 0
            vertex_angle = 0
            while True: # Ensure vertex angle is positive
                base_angle = _generate_angle(30, 80)
                vertex_angle = 180 - 2 * base_angle
                if vertex_angle > 0:
                    break

            question_text = r"在等腰三角形 $\triangle ABC$ 中，已知 $AB=AC$。若 $\angle B = {b}^\circ$，則 $\angle A = ?$".replace("{b}", str(base_angle))
            correct_answer = str(vertex_angle)
            # For isosceles AB=AC, angle B and angle C are base angles. Angle A is vertex angle.
            image_base64 = _draw_triangle_angle_diagram(angle_B_label=str(base_angle), angle_C_label=str(base_angle), highlight_angle='A')

        else: # vertex_given_base_find
            base_angle = 0
            vertex_angle = 0
            while True: # Ensure base angles are positive and integer
                vertex_angle = _generate_angle(20, 140)
                if (180 - vertex_angle) % 2 == 0: 
                    base_angle = (180 - vertex_angle) // 2
                    if base_angle > 0:
                        break

            question_text = r"在等腰三角形 $\triangle ABC$ 中，已知 $AB=AC$。若 $\angle A = {a}^\circ$，則 $\angle B = ?$".replace("{a}", str(vertex_angle))
            correct_answer = str(base_angle)
            image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(vertex_angle), highlight_angle='B')

    elif problem_type == 5: # Type 5 (Maps to Example 5): Multi-step problem (following ARCHITECT'S SPECIFICATION's numerical interpretation)
        # RAG Ex 5 is a proof, but the spec's description implies a numerical problem for this skill.
        # Following spec: "在 $\triangle ABC$ 中，點 $D$ 在 $BC$ 上，求 $\angle ADC$ 若已知 $\angle B$ 和 $\angle BAD$。"
        angle_B = _generate_angle(40, 70)
        angle_BAD = _generate_angle(20, 40)
        
        # This is a direct application of the exterior angle theorem to triangle ABD:
        # Exterior angle ADC = sum of non-adjacent interior angles (angle B + angle BAD)
        angle_ADC = angle_B + angle_BAD

        question_text = r"如圖所示，在 $\triangle ABC$ 中，點 $D$ 在 $BC$ 上。若 $\angle B = {b}^\circ$ 且 $\angle BAD = {bad}^\circ$，則 $\angle ADC = ?$".replace("{b}", str(angle_B)).replace("{bad}", str(angle_BAD))
        correct_answer = str(angle_ADC)
        
        image_base64 = _draw_triangle_angle_diagram(angle_A_label=str(angle_BAD), angle_B_label=str(angle_B), highlight_angle='ADC', specific_setup='type5_interior_line')

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", 
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # CRITICAL RULE: Input Sanitization using Regex
    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        # Using math.isclose for robust float comparison with a small tolerance
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return True
    except ValueError: # Catch conversion errors if user_answer is not a valid number
        pass
        
    # 3. 降級為字串比對 (for cases where direct numeric comparison fails or isn't applicable)
    if u == c: return True
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
