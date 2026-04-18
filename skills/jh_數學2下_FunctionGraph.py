# ==============================================================================
# ID: jh_數學2下_FunctionGraph
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 113.60s | RAG: 5 examples
# Created At: 2026-01-20 19:16:25
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

import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# --- Helper Functions Definition ---

def _generate_coordinate_value(min_val_input=-8, max_val_input=8, allow_fraction=False):
    """
    功能: 生成一個座標軸上的數值，可以是整數或帶有 .5 的分數（如 2.5, -3.5）。
    輸入:
        min_val_input (int): 最小值。
        max_val_input (int): 最大值。
        allow_fraction (bool): 是否允許生成 .5 形式的分數。
    輸出 (V10.2 A): (float_val, (int_part, num, den, is_neg))
    邏輯:
        1. 使用 random.randint(min_val, max_val) 生成一個整數。
        2. 若 allow_fraction 為 True 且 random.choice([True, False]) 為 True，則將數值加上 0.5 * random.choice([-1, 1])。
        3. 判斷數值是否為整數：
            * 若是整數，num=0, den=0, int_part=int(val).
            * 若為 x.5 形式，num=1, den=2, int_part=int(abs(val)).
        4. 返回格式 (float_val, (int_part, num, den, is_neg))。
    數據禁絕常數 (V10): min_val, max_val 必須透過 random.randint 隨機生成，確保座標範圍動態變化。
    教學正確性補正 (V13.1): 若有分數部，確保 numerator < denominator 且 denominator > 1 (在此為 1/2)。
    整數優先 (V13.5): 內部處理時，若 val.is_integer() 則轉換為 int(val)。
    """
    
    val = random.randint(min_val_input, max_val_input)
    
    if allow_fraction and random.choice([True, False]):
        fraction_part = 0.5 * random.choice([-1, 1])
        val = val + fraction_part
    
    # 整數優先 (V13.5): 內部處理時，若 val.is_integer() 則轉換為 int(val)。
    if isinstance(val, float) and val.is_integer():
        val = int(val)

    float_val = float(val)
    is_neg = float_val < 0
    
    if float_val.is_integer():
        int_part = int(abs(float_val))
        num = 0
        den = 0
    else: # 必須是 x.5 形式
        # int_part 應該是帶分數的整數部分, e.g. 2.5 -> 2, -2.5 -> 2, -0.5 -> 0
        int_part = int(abs(float_val))
        num = 1
        den = 2

    return float_val, (int_part, num, den, is_neg)

def _draw_coordinate_plane(points_to_plot, lines_to_plot, x_range, y_range, title, show_grid=True, show_tick_labels=True):
    """
    功能: 繪製座標平面，並可標示點和直線。
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    
    # 視覺一致性 (V10.2 D), ULTRA VISUAL STANDARDS (V11.6): Aspect Ratio
    ax.set_aspect('equal')

    # Hide default spines and set position (Axis Visibility V7)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Set x and y limits
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    # 強制顯示刻度 (Mandatory Axis Ticks V6)
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))
    
    if show_tick_labels:
        # 其他整數刻度標籤 (V17.1, V17.2)
        ax.tick_params(axis='both', which='major', labelsize=10)
        for label in ax.get_xticklabels():
            if label.get_text() == '0':
                label.set_text('') # Remove default '0' label
            else:
                label.set_bbox(dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
        for label in ax.get_yticklabels():
            if label.get_text() == '0':
                label.set_text('') # Remove default '0' label
            else:
                label.set_bbox(dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
        
        # 僅標示原點 '0' (V10.2 D, V13.0)
        ax.text(0, 0, '0', color='black', ha='center', va='top', fontsize=18, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    # 網格線輔助 (Grid Lines V8)
    if show_grid:
        ax.grid(True, linestyle=':', alpha=0.6)

    # 箭頭繪製 (V13.6): 嚴禁使用 arrowprops。
    ax.plot(x_range[1], 0, ">k", clip_on=False, transform=ax.get_yaxis_transform()) # X-axis arrow
    ax.plot(0, y_range[1], "^k", clip_on=False, transform=ax.get_xaxis_transform()) # Y-axis arrow
    # 標註座標軸名稱
    ax.text(x_range[1], 0.1, 'x', ha='right', va='bottom', fontsize=12)
    ax.text(0.1, y_range[1], 'y', ha='left', va='top', fontsize=12)

    # Plot lines
    for line in lines_to_plot:
        if len(line) == 3: # (slope, y_intercept, label)
            m, c, label = line
            x_vals = np.array(x_range)
            y_vals = m * x_vals + c
            ax.plot(x_vals, y_vals, color='blue', linestyle='-', label=label if label else None)
        elif len(line) == 3 and line[1] == 'vertical': # (x_val, 'vertical', label)
            x_val, _, label = line
            ax.axvline(x=x_val, color='blue', linestyle='-', label=label if label else None)

    # Plot points
    for point in points_to_plot:
        x, y, label = point
        ax.plot(x, y, 'ro', markersize=6) # Red circle for points
        if label:
            # Label Halo (ULTRA VISUAL STANDARDS V11.6)
            ax.text(x + 0.3, y + 0.3, label, color='black', fontsize=12, ha='left', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8))

    ax.set_title(title)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

def _generate_equation_string(m, c):
    """
    方程式生成鎖死 (Equation Robustness V1): 嚴禁使用 f-string 組合 `ax + by = c`。
    強制流程：必須分別判定 a, b 的正負與是否為 1，手動組合字串片段後合併。
    """
    parts = []
    parts.append("y = ")
    
    if m == 0:
        parts.append(str(int(c)) if c.is_integer() else str(c))
    else:
        if m == 1:
            parts.append("x")
        elif m == -1:
            parts.append("-x")
        else:
            parts.append(str(int(m)) if m.is_integer() else str(m) + "x")

        if c > 0:
            parts.append(" + " + (str(int(c)) if c.is_integer() else str(c)))
        elif c < 0:
            parts.append(" - " + (str(int(abs(c))) if abs(c).is_integer() else str(abs(c))))
    
    return "".join(parts)

def _parse_equation(eq_str):
    """
    Parses a linear equation string (y=mx+c or y=c) and returns (m, c).
    Returns (None, None) if parsing fails.
    """
    eq_str = eq_str.replace(" ", "").lower()
    
    # Handle y = mx + c form
    match_mx_c = re.match(r'y=(-?\d*\.?\d*)x([+-]\d*\.?\d+)$', eq_str)
    if match_mx_c:
        m_str = match_mx_c.group(1)
        c_str = match_mx_c.group(2)
        if m_str == '-': m_str = '-1'
        if m_str == '': m_str = '1'
        return float(m_str), float(c_str)

    # Handle y = mx form (c=0)
    match_mx = re.match(r'y=(-?\d*\.?\d*)x$', eq_str)
    if match_mx:
        m_str = match_mx.group(1)
        if m_str == '-': m_str = '-1'
        if m_str == '': m_str = '1'
        return float(m_str), 0.0

    # Handle y = c form
    match_c = re.match(r'y=(-?\d*\.?\d+)$', eq_str)
    if match_c:
        return 0.0, float(match_c.group(1))
        
    return None, None

# --- Top-Level Functions Definition ---

def generate(level=1):
    """
    功能: 根據指定的難度等級生成一道函數圖形題目。
    輸出 (V7): 字典，包含 question_text, correct_answer, answer, image_base64, created_at, version。
    隨機分流 (V4): 使用 random.choice 或 if/elif 邏輯選擇以下題型之一。
    """
    problem_type = random.choice([1, 2, 3, 4, 5]) # 5 problem types based on 5 RAG examples
    
    # 動態座標範圍生成 (V10 數據禁絕常數)
    x_range_min = random.randint(-10, -5)
    x_range_max = random.randint(5, 10)
    y_range_min = random.randint(-10, -5)
    y_range_max = random.randint(5, 10)
    x_range_plot = (x_range_min, x_range_max)
    y_range_plot = (y_range_min, y_range_max)

    question_text = ""
    correct_answer = ""
    image_base64 = None
    answer_display = ""

    if problem_type == 1: # STRICT MAPPING: RAG Ex 1: Month/Days Function -> Is a point on the graph?
        # Month-day function data (non-leap year)
        month_days = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        # Pick a random month number
        x_month = random.randint(1, 12)
        y_actual_days = month_days[x_month]
        
        # Randomly decide if the point should be on the graph or not
        is_on_graph = random.choice([True, False])
        
        x_point = x_month
        y_point = y_actual_days
        
        if not is_on_graph:
            # If not on graph, modify y_point (ensure it's still a valid number of days, e.g., >0)
            offset = random.choice([-1, 1, -2, 2]) # Offset by 1 or 2 days
            y_point = y_actual_days + offset
            # Ensure y_point is not equal to any other month's days for the same x_month
            while y_point <= 0 or y_point == y_actual_days:
                offset = random.choice([-1, 1, -2, 2])
                y_point = y_actual_days + offset

        question_text_template = r"已知 y 是 x 的函數，其中 x 代表平年中的月分 (1代表一月, 2代表二月, ...)，y 代表該月分的天數。點 ({x_point}, {y_point}) 是這個函數圖形上的點嗎？ (是/否)"
        question_text = question_text_template.replace("{x_point}", str(x_point)).replace("{y_point}", str(y_point))
        correct_answer = "是" if is_on_graph else "否"
        answer_display = correct_answer
        image_base64 = None # 此題為概念判斷，不需繪圖，避免洩漏答案軌跡。

    elif problem_type == 2: # STRICT MAPPING: RAG Ex 2: Plotting y=mx+c, y=c -> Find X-intercept
        # Ensure m != 0 for x-intercept
        m = 0
        while m == 0:
            m_coord_min = random.randint(-4, -1)
            m_coord_max = random.randint(1, 4)
            m, _ = _generate_coordinate_value(m_coord_min, m_coord_max, allow_fraction=False)
        
        c_coord_min = random.randint(-6, -1)
        c_coord_max = random.randint(1, 6)
        c, _ = _generate_coordinate_value(c_coord_min, c_coord_max, allow_fraction=False)

        # Calculate x-intercept: y=0 => mx+c=0 => x = -c/m
        x_intercept = -c / m
        
        # Ensure x_intercept is integer or 0.5 (Coordinate Precision V9)
        attempts = 0
        while not (x_intercept.is_integer() or (abs(x_intercept * 2) - int(abs(x_intercept * 2))) < 1e-9) and attempts < 10:
            m, _ = _generate_coordinate_value(m_coord_min, m_coord_max, allow_fraction=False)
            if m == 0: continue
            c, _ = _generate_coordinate_value(c_coord_min, c_coord_max, allow_fraction=False)
            x_intercept = -c / m
            attempts += 1
        
        # Fallback if generation fails to produce clean intercept
        if not (x_intercept.is_integer() or (abs(x_intercept * 2) - int(abs(x_intercept * 2))) < 1e-9):
            m = random.choice([-2, -1, 1, 2]) # Use integer m
            c = random.choice([-4, -2, 2, 4]) # Use c that makes integer intercept
            x_intercept = -c / m

        equation_str = _generate_equation_string(m, c)
        
        question_text_template = r"在坐標平面上畫出下列各函數的圖形。請問函數 ${equation}$ 的 $x$ 截距為何？"
        question_text = question_text_template.replace("${equation}$", f"${equation_str}$")
        correct_answer = f"{x_intercept:.1f}" if not x_intercept.is_integer() else str(int(x_intercept))
        answer_display = correct_answer

        image_base64 = _draw_coordinate_plane([], [(m, c, r"$L_1$")], x_range_plot, y_range_plot, title="函數圖形")

    elif problem_type == 3: # STRICT MAPPING: RAG Ex 3: Find equation from two points -> y=ax+b
        # Generate two distinct points (p1x, p1y) and (p2x, p2y)
        # Ensure m and c are integers for simplicity in K12
        m = random.randint(-3, 3)
        c = random.randint(-5, 5)

        # Generate points that lie on this line
        p1x_gen_min = random.randint(-5, -1)
        p1x_gen_max = random.randint(1, 5)
        p1x, _ = _generate_coordinate_value(p1x_gen_min, p1x_gen_max, allow_fraction=False)
        p1y = m * p1x + c
        
        p2x_gen_min = random.randint(-5, -1)
        p2x_gen_max = random.randint(1, 5)
        p2x = p1x
        while p2x == p1x: # Ensure p1x != p2x to avoid vertical line
            p2x, _ = _generate_coordinate_value(p2x_gen_min, p2x_gen_max, allow_fraction=False)
        p2y = m * p2x + c

        # Ensure all coordinates are integers (as per K12 practice for this type)
        p1x = int(p1x)
        p1y = int(p1y)
        p2x = int(p2x)
        p2y = int(p2y)
        
        equation_str = _generate_equation_string(float(m), float(c))

        question_text_template = r"已知函數 $y=ax+b$ 的圖形為通過點 A({p1x}, {p1y}) 和 B({p2x}, {p2y}) 的直線，則此函數為何？請以 $y=mx+c$ 的格式作答。"
        question_text = question_text_template.replace("{p1x}", str(p1x)).replace("{p1y}", str(p1y)) \
                                            .replace("{p2x}", str(p2x)).replace("{p2y}", str(p2y))
        correct_answer = equation_str
        answer_display = correct_answer

        # Image: Show only the two points, NOT the line (V6, V13.5, Zero-Graph Protocol interpretation)
        image_base64 = _draw_coordinate_plane([(p1x, p1y, "A"), (p2x, p2y, "B")], [], x_range_plot, y_range_plot, title="通過兩點的直線")

    elif problem_type == 4: # STRICT MAPPING: RAG Ex 4: Horizontal line y=c from a point -> y=c
        px_gen_min = random.randint(-8, -2)
        px_gen_max = random.randint(2, 8)
        py_gen_min = random.randint(-8, -2)
        py_gen_max = random.randint(2, 8)
        
        px, _ = _generate_coordinate_value(px_gen_min, px_gen_max, allow_fraction=False)
        py, _ = _generate_coordinate_value(py_gen_min, py_gen_max, allow_fraction=False)
        
        # For a line parallel to x-axis, the equation is y = constant, where constant is the y-coordinate of the point.
        c = py
        equation_str = f"y = {int(c)}" if c.is_integer() else f"y = {c:.1f}"

        question_text_template = r"已知函數 $y=ax+b$ 的圖形是平行 x 軸的直線，若圖形通過點 ({px}, {py})，則此函數為何？請以 $y=c$ 的格式作答。"
        question_text = question_text_template.replace("{px}", str(int(px))).replace("{py}", str(int(py)))
        correct_answer = equation_str
        answer_display = correct_answer

        # Image: Show only the point, NOT the line (V6, V13.5, Zero-Graph Protocol interpretation)
        image_base64 = _draw_coordinate_plane([(px, py, "P")], [], x_range_plot, y_range_plot, title="平行 x 軸的直線")

    elif problem_type == 5: # STRICT MAPPING: RAG Ex 5: Word problem (linear function, find x-intercept)
        # Generate two points (d1, c1) and (d2, c2) such that d1 < d2, c1 < c2, and x-intercept is positive (meaningful "free mileage").
        
        # First, define the desired x-intercept (free mileage) and a positive slope
        x_intercept_val = random.randint(10, 30) # Daily free mileage (e.g., 10 to 30 km)
        
        # Generate a slope `m` (cost per km)
        m_val = random.choice([0.5, 1, 1.5, 2]) # Use float or int slopes

        # Calculate y-intercept `b` (cost = m * distance + b). At x-intercept, cost = 0.
        # 0 = m_val * x_intercept_val + b => b = -m_val * x_intercept_val
        b_val = -m_val * x_intercept_val

        # Generate two distances d1 and d2, both greater than x_intercept_val
        d1 = random.randint(x_intercept_val + 5, x_intercept_val + 20)
        d2 = random.randint(d1 + 5, d1 + 20)
        
        # Calculate corresponding costs c1 and c2
        c1 = m_val * d1 + b_val
        c2 = m_val * d2 + b_val
        
        # Ensure costs are positive and round to nearest integer for realism
        c1 = int(round(c1))
        c2 = int(round(c2))
        d1 = int(round(d1))
        d2 = int(round(d2))

        # Re-calculate m and b from the rounded points to ensure consistency
        m_calc = (c2 - c1) / (d2 - d1)
        b_calc = c1 - m_calc * d1
        x_intercept_calc = -b_calc / m_calc
        
        # Ensure the final x_intercept is an integer or x.5
        # If not, regenerate with integer m and c values
        if not (x_intercept_calc.is_integer() or (abs(x_intercept_calc * 2) - int(abs(x_intercept_calc * 2))) < 1e-9):
            x_intercept_val = random.randint(10, 30)
            m_val = random.randint(1, 3) # Force integer slope
            b_val = -m_val * x_intercept_val
            
            d1 = random.randint(x_intercept_val + 5, x_intercept_val + 20)
            c1 = m_val * d1 + b_val
            d2 = random.randint(d1 + 5, d1 + 20)
            c2 = m_val * d2 + b_val
            
            c1 = int(round(c1))
            c2 = int(round(c2))
            d1 = int(round(d1))
            d2 = int(round(d2))
            
            m_calc = (c2 - c1) / (d2 - d1)
            b_calc = c1 - m_calc * d1
            x_intercept_calc = -b_calc / m_calc


        question_text_template = r"某高速公路收費方式為：每日行駛優惠里程數以內不收費，超過部分，費用與行駛距離成線型函數關係。如圖，行駛 {d1} 公里收費 {c1} 元，行駛 {d2} 公里收費 {c2} 元。問每日優惠里程數為多少公里？"
        question_text = question_text_template.replace("{d1}", str(d1)).replace("{c1}", str(c1)) \
                                            .replace("{d2}", str(d2)).replace("{c2}", str(c2))
        
        correct_answer = f"{x_intercept_calc:.1f}" if not x_intercept_calc.is_integer() else str(int(x_intercept_calc))
        answer_display = correct_answer + "公里"

        # Adjust plot ranges to fit the word problem context (distances and costs are positive)
        plot_x_min = min(0, int(x_intercept_calc) - 5)
        plot_x_max = max(d2 + 5, x_range_max)
        plot_y_min = min(0, y_range_min)
        plot_y_max = max(c2 + 5, y_range_max)

        # Image: Show the two points and the line as per "如圖" in RAG Ex 5
        image_base64 = _draw_coordinate_plane(
            [(d1, c1, f"({d1},{c1})"), (d2, c2, f"({d2},{c2})")], # Labels for points
            [(m_calc, b_calc, None)], # Draw the line
            x_range=(plot_x_min, plot_x_max), y_range=(plot_y_min, plot_y_max),
            title="高速公路收費示意圖"
        )

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # For display purposes in UI, not for grading
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "V11.8_reflection_enhanced"
    }

# --- Universal Check Template (SYSTEM GUARDRAILS #2) ---

    """
    功能: 批改學生答案。
    強韌閱卷邏輯 (V2, V13.6):
    1. 輸入清洗 (Input Sanitization)
    2. 數值序列比對 (V12.6, V13.5)
    3. 降級為字串比對
    """
    
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = s.replace("$", "").replace("\\", "") # Remove LaTeX specific chars
        # 移除變數名，如 k=, x=, y=。這裡修改為更通用地移除開頭的字母和等號
        s = re.sub(r'^[a-z]+(\s*=\s*)?', '', s) 
        return s
    
    u_cleaned = clean(user_answer)
    c_cleaned = clean(correct_answer)
    
    # --- 1. 嘗試解析為方程式 (y=mx+c 或 y=c) ---
    u_m, u_c = _parse_equation(u_cleaned)
    c_m, c_c = _parse_equation(c_cleaned)

    if u_m is not None and c_m is not None: # 如果兩者都能解析為方程式格式
        if math.isclose(u_m, c_m, rel_tol=1e-5) and math.isclose(u_c, c_c, rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}

    # --- 2. 嘗試數值比對 (支援分數與小數) ---
    try:
        def parse_val(val_str):
            if isinstance(val_str, (int, float)):
                return float(val_str)
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        if math.isclose(parse_val(u_cleaned), parse_val(c_cleaned), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except ValueError:
        pass # 如果不是簡單的數值，則繼續字串比對

    # --- 3. 降級為字串比對 ---
    if u_cleaned == c_cleaned:
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": f"答案錯誤。"}


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
