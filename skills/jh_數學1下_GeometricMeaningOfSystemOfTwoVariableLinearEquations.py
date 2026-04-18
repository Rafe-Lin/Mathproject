# ==============================================================================
# ID: jh_數學1下_GeometricMeaningOfSystemOfTwoVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 104.60s | RAG: 4 examples
# Created At: 2026-01-16 10:25:07
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
from datetime import datetime
import matplotlib.pyplot as plt
import io
import re

# --- 輔助函式 (Helper Functions) ---

def _generate_coordinate_value(min_val=-8, max_val=8, allow_fraction=False):
    """
    [V10.2 A. 資料結構鎖死]：統一回傳固定格式 (float_val, (abs_int_part, num, den, is_neg)).
    [V13.0 座標選取控制]：使用 random.randint(-8, 8) 或其分數形式.
    [V13.1 禁絕假分數]：檢查 numerator < denominator 且 denominator > 1.
    [V13.5 整數優先]：生成後判斷是否為整數並轉換.
    """
    is_neg = random.choice([True, False])
    abs_int_part = random.randint(0, max(0, max_val - 1)) # 確保 abs_int_part 非負

    float_val_raw = float(abs_int_part)
    num = 0
    den = 0

    if allow_fraction and random.random() < 0.4: # 約40%的機率生成分數，增加分數出現頻率
        # [V13.1 禁絕假分數]: numerator < denominator and denominator > 1
        num = random.randint(1, 5) # 較小的分子
        # RAG Ex 1: (2, 8/3) 包含分母為 3 的情況，因此 den 應允許 3。
        # random.randint(num + 1, 6) 允許分母為 2, 3, 4, 5, 6
        den = random.randint(num + 1, 6) 
        
        # 簡化分數
        gcd = math.gcd(num, den)
        num //= gcd
        den //= gcd

        float_val_raw += float(num) / den
    
    float_val = float_val_raw
    if is_neg and float_val != 0:
        float_val = -float_val
    
    # [V13.5 整數優先]:
    if float_val.is_integer():
        float_val = int(float_val)
        num = 0
        den = 0
        abs_int_part = abs(int(float_val)) # 如果是整數，更新 abs_int_part
    else:
        # 如果最終不是整數，則 abs_int_part 應為 float_val 的整數部分絕對值
        abs_int_part = math.floor(abs(float_val)) if float_val != 0 else 0


    # 回傳時，is_neg 應反映最終 float_val 的正負，而非最初的隨機選擇
    return float_val, (abs_int_part, num, den, float_val < 0)

def _format_coordinate_latex(coord_data):
    """
    [V10.2 A. 資料結構鎖死]：格式化函式嚴格執行 int_part, num, den, is_neg = data[1] 的解包方式.
    [V10.2 C. LaTeX 模板規範]：使用單層大括號 {n}, {d} 搭配 .replace.
    """
    float_val, (abs_int_part, num, den, is_neg) = coord_data

    if num == 0: # 整數
        return str(int(float_val)) # [V13.0 格式精確要求]: str(int(val))
    else: # 分數
        sign_str = "-" if is_neg else "" # 根據 is_neg 判斷是否顯示負號
        
        if abs_int_part == 0: # 真分數
            template = r"{sign}\frac{{{n}}}{{{d}}}"
            return template.replace("{sign}", sign_str).replace("{n}", str(num)).replace("{d}", str(den))
        else: # 帶分數
            template = r"{sign}{i}\frac{{{n}}}{{{d}}}"
            return template.replace("{sign}", sign_str).replace("{i}", str(abs_int_part)).replace("{n}", str(num)).replace("{d}", str(den))

def _plot_lines(line_eqs_coeffs, intersection_point=None, point_labels=None, highlight_area=None):
    """
    [V6. 視覺化與輔助函式通用規範]：回傳結果 (str), 類型一致. 防洩漏原則.
    [V10.2 D. 視覺一致性]：ax.set_aspect('equal'), 原點 '0' (18號加粗), 點標籤白色光暈.
    [V13.0 格線對齊]：座標軸範圍對稱整數 (-8 到 8), xticks 間隔 1.
    [V13.5 座標範圍]：座標範圍必須對稱且寬裕 (-8 到 8).
    [V13.6 Arrow Ban]：嚴禁使用 arrowprops. 使用 ax.plot(limit, 0, ">k", clip_on=False) 繪製箭頭.
    [V13.5 標籤隔離]：ax.text 只能標註點名稱.
    [V13.1 標籤純淨化]：ax.text 的內容只能是標籤文字（Label），座標值（Values）只能存在於文字敘述與 correct_answer 中。
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # [V13.0 格線對齊] & [V13.5 座標範圍]
    min_coord, max_coord = -8, 8
    ax.set_xlim(min_coord, max_coord)
    ax.set_ylim(min_coord, max_coord)
    ax.set_xticks(range(min_coord, max_coord + 1))
    ax.set_yticks(range(min_coord, max_coord + 1))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal') # [V10.2 D. 視覺一致性]

    # 繪製座標軸
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # [V13.6 Arrow Ban]: 繪製箭頭
    ax.plot(max_coord, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False) # x軸箭頭
    ax.plot(0, max_coord, "^k", transform=ax.get_xaxis_transform(), clip_on=False) # y軸箭頭

    # [V10.2 D. 視覺一致性]: 標註原點 '0'
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

    # 繪製直線
    x_vals = [min_coord, max_coord]
    colors = ['blue', 'red', 'green', 'purple'] # 直線顏色
    line_labels = ['L1', 'L2', 'L3', 'L4'] # 直線標籤
    
    for i, coeffs in enumerate(line_eqs_coeffs):
        a, b, c = coeffs # 方程式形式: ax + by = c
        
        if b == 0: # 垂直線: ax = c => x = c/a
            x_val = c / a
            ax.axvline(x_val, color=colors[i % len(colors)], linestyle='-', label=f"${line_labels[i]}$")
        elif a == 0: # 水平線: by = c => y = c/b
            y_val = c / b
            ax.axhline(y_val, color=colors[i % len(colors)], linestyle='-', label=f"${line_labels[i]}$")
        else: # 一般直線: y = (-a/b)x + (c/b)
            y_vals = [(-a * x + c) / b for x in x_vals]
            ax.plot(x_vals, y_vals, color=colors[i % len(colors)], linestyle='-', label=f"${line_labels[i]}$")

    # 繪製交點
    if intersection_point:
        point_name = point_labels if point_labels else "P" 
        ax.plot(intersection_point[0], intersection_point[1], 'o', color='black', markersize=8, zorder=5)
        ax.text(intersection_point[0], intersection_point[1], point_name,
                color='black', fontsize=12, ha='left', va='bottom',
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

    # 繪製圍成區域 (如果提供)
    if highlight_area:
        # highlight_area = {'axis': 'x' or 'y', 'x_intercepts': (x1, x2), 'y_intercepts': (y1, y2), 'intersection': (sx, sy)}
        if highlight_area['axis'] == 'x':
            x_vals_area = sorted([highlight_area['x_intercept1'], highlight_area['x_intercept2'], highlight_area['intersection'][0]])
            y_vals_area = [0, 0, highlight_area['intersection'][1]] # y-coords for triangle vertices
            
            # Create a polygon for the triangle. The order of points might need adjustment for correct filling.
            # Points: (x1_intercept, 0), (x2_intercept, 0), (sol_x, sol_y)
            triangle_points = [
                (highlight_area['x_intercept1'], 0),
                (highlight_area['x_intercept2'], 0),
                highlight_area['intersection']
            ]
            ax.fill(*zip(*triangle_points), color='yellow', alpha=0.3, label='Area')

        elif highlight_area['axis'] == 'y':
            x_vals_area = [0, 0, highlight_area['intersection'][0]] # x-coords for triangle vertices
            y_vals_area = sorted([highlight_area['y_intercept1'], highlight_area['y_intercept2'], highlight_area['intersection'][1]])
            
            # Points: (0, y1_intercept), (0, y2_intercept), (sol_x, sol_y)
            triangle_points = [
                (0, highlight_area['y_intercept1']),
                (0, highlight_area['y_intercept2']),
                highlight_area['intersection']
            ]
            ax.fill(*zip(*triangle_points), color='yellow', alpha=0.3, label='Area')


    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # 將圖形轉換為 base64 字串
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=300) # [V11.6 Resolution]
    plt.close(fig)
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    return img_base64

def _get_line_info(a, b, c):
    """輔助函式：獲取直線資訊（斜率、y截距或是否為垂直/水平線）"""
    if b == 0: # 垂直線 x = c/a
        if a == 0: return 'degenerate', None, None # 0x + 0y = c, invalid line unless c=0 (0=0)
        return 'vertical', c/a, None
    elif a == 0: # 水平線 y = c/b
        if b == 0: return 'degenerate', None, None # Should be caught by a==0 and b==0 earlier
        return 'horizontal', None, c/b
    else: # 一般直線 y = (-a/b)x + (c/b)
        slope = -a / b
        y_intercept = c / b
        return 'normal', slope, y_intercept

def _format_equation(a, b, c):
    """
    [系統底層鐵律 1]: 方程式生成鎖死 (Equation Robustness)
    嚴禁使用 f-string 組合 `ax + by = c`。
    【強制流程】：必須分別判定 a, b 的正負與是否為 1，手動組合字串片段後合併。
    """
    terms = []

    # x term
    if a == 1:
        terms.append("x")
    elif a == -1:
        terms.append("-x")
    elif a != 0:
        terms.append(f"{a}x")

    # y term
    if b == 1:
        if terms: terms.append(" + y")
        else: terms.append("y")
    elif b == -1:
        if terms: terms.append(" - y")
        else: terms.append("-y")
    elif b > 0:
        if terms: terms.append(f" + {b}y")
        else: terms.append(f"{b}y")
    elif b < 0:
        if terms: terms.append(f" {b}y") # e.g. "2x -3y"
        else: terms.append(f"{b}y")

    # Combine terms to form the left-hand side of the equation
    equation_lhs = "".join(terms).strip()

    # Handle cases where LHS is empty (e.g., 0x + 0y = c)
    if not equation_lhs:
        equation_lhs = "0"

    return f"{equation_lhs} = {c}"

# --- 頂層函式 (Top-level Functions) ---

def generate(level=1):
    """
    [V3. 頂層函式]：直接定義於模組最外層。
    [V4. 題型鏡射]：使用 random.choice 或 if/elif 邏輯對應 RAG 例題.
    [V7. 數據與欄位]：返回字典包含指定欄位。
    [V10. 數據禁絕常數]：隨機生成所有幾何長度、角度與面積。
    [MANDATORY MIRRORING RULES]: Strict mapping to RAG Ex 1-4.
    """
    # Problem types now strictly map to RAG examples by number.
    problem_type = random.choice([1, 2, 3, 4]) 

    question_text = ""
    correct_answer = ""
    answer_data = {} # Renamed to avoid conflict with `answer` in `check`
    image_base64 = None
    
    sol_x_float = None
    sol_y_float = None
    area = None

    coeffs1 = [0, 0, 0] # a1, b1, c1 for line 1 (a1*x + b1*y = c1)
    coeffs2 = [0, 0, 0] # a2, b2, c2 for line 2 (a2*x + b2*y = c2)

    if problem_type == 1 or problem_type == 2:
        # RAG Ex 1 & 2: Plot lines, find intersection point.
        # Example 1: 4x=3y, x+3y=10 -> (2, 8/3)
        # Example 2: y=-x+6, x+2y=8 -> (4, 2)
        
        while True:
            sol_x_float, sol_x_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=True)
            sol_y_float, sol_y_data = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=True)

            # Ensure intersection is not trivial
            if (sol_x_float == 0 and sol_y_float == 0) or \
               (sol_x_float == 1 and sol_y_float == 1) or \
               (sol_x_float == -1 and sol_y_float == -1):
                continue
            
            # Generate coefficients that pass through (sol_x_float, sol_y_float)
            a1 = random.randint(-3, 3)
            b1 = random.randint(-3, 3)
            c1 = a1 * sol_x_float + b1 * sol_y_float
            
            a2 = random.randint(-3, 3)
            b2 = random.randint(-3, 3)
            c2 = a2 * sol_x_float + b2 * sol_y_float

            # Avoid degenerate equations (0x+0y=c) or (0x+0y=0)
            if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
                continue
            
            info1 = _get_line_info(a1, b1, c1)
            info2 = _get_line_info(a2, b2, c2)

            if info1[0] == 'degenerate' or info2[0] == 'degenerate': continue

            # Ensure lines are not parallel or coincident (must intersect uniquely)
            if (info1[0] == 'vertical' and info2[0] == 'vertical' and info1[1] == info2[1]) or \
               (info1[0] == 'horizontal' and info2[0] == 'horizontal' and info1[2] == info2[2]) or \
               (info1[0] == 'normal' and info2[0] == 'normal' and info1[1] == info2[1]):
                continue
            
            # Ensure intersection point is within reasonable plot range
            min_plot_coord, max_plot_coord = -8, 8
            if not (min_plot_coord <= sol_x_float <= max_plot_coord and min_plot_coord <= sol_y_float <= max_plot_coord):
                continue
            
            break
        
        coeffs1 = [a1, b1, c1]
        coeffs2 = [a2, b2, c2]

        eq1_str = _format_equation(a1, b1, c1)
        eq2_str = _format_equation(a2, b2, c2)

        question_text = r"在坐標平面上分別畫出二元一次方程式 " + eq1_str + r"、" + eq2_str + r" 的圖形，並標記這兩條直線的交點坐標。"
        correct_answer = f"({str(int(sol_x_float)) if sol_x_float.is_integer() else _format_coordinate_latex(sol_x_data)}, " \
                         f"{str(int(sol_y_float)) if sol_y_float.is_integer() else _format_coordinate_latex(sol_y_data)})"
        
        image_base64 = _plot_lines([coeffs1, coeffs2], intersection_point=(sol_x_float, sol_y_float), point_labels="P")
        
        answer_data["x"] = sol_x_float
        answer_data["y"] = sol_y_float

    elif problem_type == 3:
        # RAG Ex 3: Plot lines, find area with x-axis.
        # Example: x-y=1, 2x+3y=12 -> Area 5
        
        while True:
            # Generate intersection point (sol_x, sol_y) such that sol_y is not zero (for triangle height)
            sol_x_float, sol_x_data = _generate_coordinate_value(min_val=-3, max_val=3, allow_fraction=True)
            sol_y_float, sol_y_data = _generate_coordinate_value(min_val=1, max_val=3, allow_fraction=True) # Ensure non-zero height
            if random.random() < 0.5: sol_y_float = -sol_y_float # Can be above or below x-axis

            # Generate two lines passing through (sol_x, sol_y)
            a1 = random.randint(-3, 3)
            b1 = random.randint(-3, 3)
            c1 = a1 * sol_x_float + b1 * sol_y_float
            
            a2 = random.randint(-3, 3)
            b2 = random.randint(-3, 3)
            c2 = a2 * sol_x_float + b2 * sol_y_float

            # Avoid degenerate equations
            if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0): continue
            
            info1 = _get_line_info(a1, b1, c1)
            info2 = _get_line_info(a2, b2, c2)

            if info1[0] == 'degenerate' or info2[0] == 'degenerate': continue

            # Ensure lines are not parallel or coincident
            if (info1[0] == 'vertical' and info2[0] == 'vertical' and info1[1] == info2[1]) or \
               (info1[0] == 'horizontal' and info2[0] == 'horizontal' and info1[2] == info2[2]) or \
               (info1[0] == 'normal' and info2[0] == 'normal' and info1[1] == info2[1]):
                continue
            
            # Ensure both lines have x-intercepts (i.e., not horizontal lines with c!=0)
            if a1 == 0 or a2 == 0: continue # If a=0, it's a horizontal line (y=c/b). If c!=0, it doesn't intersect x-axis.

            # Calculate x-intercepts for area calculation
            x_intercept1 = c1 / a1 # when y=0
            x_intercept2 = c2 / a2 # when y=0

            # Ensure x-intercepts are distinct and reasonably spaced for a visible triangle
            if abs(x_intercept1 - x_intercept2) < 0.5: continue # Too close
            
            # Ensure all points (x_intercept1, 0), (x_intercept2, 0), (sol_x_float, sol_y_float) are within plot range
            min_plot_coord, max_plot_coord = -8, 8
            if not (min_plot_coord <= sol_x_float <= max_plot_coord and min_plot_coord <= sol_y_float <= max_plot_coord and \
                    min_plot_coord <= x_intercept1 <= max_plot_coord and min_plot_coord <= x_intercept2 <= max_plot_coord):
                continue
            
            base = abs(x_intercept1 - x_intercept2)
            height = abs(sol_y_float)
            area = 0.5 * base * height
            
            # Ensure area is a simple number (integer or simple fraction like X.5)
            if not (area * 2).is_integer(): 
                continue # regenerate if not simple
            
            break # Found valid equations

        coeffs1 = [a1, b1, c1]
        coeffs2 = [a2, b2, c2]

        eq1_str = _format_equation(a1, b1, c1)
        eq2_str = _format_equation(a2, b2, c2)

        question_text = r"在坐標平面上畫出二元一次方程式 " + eq1_str + r"、" + eq2_str + r" 的圖形，並求出這兩個二元一次方程式的圖形與 x 軸所圍成的區域面積。"
        correct_answer = str(int(area)) if area.is_integer() else str(area)

        image_base64 = _plot_lines([coeffs1, coeffs2], 
                                   intersection_point=(sol_x_float, sol_y_float), 
                                   point_labels="P",
                                   highlight_area={'axis': 'x', 
                                                   'x_intercept1': x_intercept1, 
                                                   'x_intercept2': x_intercept2, 
                                                   'intersection': (sol_x_float, sol_y_float)})
        answer_data["area"] = area

    elif problem_type == 4:
        # RAG Ex 4: Find area with y-axis.
        # Example: x+y=10, x-y=4 -> Area 49
        
        while True:
            # Generate intersection point (sol_x, sol_y) such that sol_x is not zero (for triangle width)
            sol_x_float, sol_x_data = _generate_coordinate_value(min_val=1, max_val=3, allow_fraction=True) # Ensure non-zero width
            if random.random() < 0.5: sol_x_float = -sol_x_float # Can be left or right of y-axis
            sol_y_float, sol_y_data = _generate_coordinate_value(min_val=-3, max_val=3, allow_fraction=True)

            # Generate two lines passing through (sol_x, sol_y)
            a1 = random.randint(-3, 3)
            b1 = random.randint(-3, 3)
            c1 = a1 * sol_x_float + b1 * sol_y_float
            
            a2 = random.randint(-3, 3)
            b2 = random.randint(-3, 3)
            c2 = a2 * sol_x_float + b2 * sol_y_float

            # Avoid degenerate equations
            if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0): continue
            
            info1 = _get_line_info(a1, b1, c1)
            info2 = _get_line_info(a2, b2, c2)

            if info1[0] == 'degenerate' or info2[0] == 'degenerate': continue

            # Ensure lines are not parallel or coincident
            if (info1[0] == 'vertical' and info2[0] == 'vertical' and info1[1] == info2[1]) or \
               (info1[0] == 'horizontal' and info2[0] == 'horizontal' and info1[2] == info2[2]) or \
               (info1[0] == 'normal' and info2[0] == 'normal' and info1[1] == info2[1]):
                continue
            
            # Ensure both lines have y-intercepts (i.e., not vertical lines with c!=0)
            if b1 == 0 or b2 == 0: continue # If b=0, it's a vertical line (x=c/a). If c!=0, it doesn't intersect y-axis.

            # Calculate y-intercepts for area calculation
            y_intercept1 = c1 / b1 # when x=0
            y_intercept2 = c2 / b2 # when x=0

            # Ensure y-intercepts are distinct and reasonably spaced
            if abs(y_intercept1 - y_intercept2) < 0.5: continue
            
            # Ensure all points (0, y_intercept1), (0, y_intercept2), (sol_x_float, sol_y_float) are within plot range
            min_plot_coord, max_plot_coord = -8, 8
            if not (min_plot_coord <= sol_x_float <= max_plot_coord and min_plot_coord <= sol_y_float <= max_plot_coord and \
                    min_plot_coord <= y_intercept1 <= max_plot_coord and min_plot_coord <= y_intercept2 <= max_plot_coord):
                continue
            
            base = abs(y_intercept1 - y_intercept2)
            height = abs(sol_x_float)
            area = 0.5 * base * height

            if not (area * 2).is_integer():
                continue # regenerate if not simple
            
            break # Found valid equations
        
        coeffs1 = [a1, b1, c1]
        coeffs2 = [a2, b2, c2]

        eq1_str = _format_equation(a1, b1, c1)
        eq2_str = _format_equation(a2, b2, c2)

        question_text = r"求二元一次方程式 " + eq1_str + r"、" + eq2_str + r" 的圖形與 y 軸所圍成的區域面積。"
        correct_answer = str(int(area)) if area.is_integer() else str(area)

        image_base64 = _plot_lines([coeffs1, coeffs2], 
                                   intersection_point=(sol_x_float, sol_y_float), 
                                   point_labels="P",
                                   highlight_area={'axis': 'y', 
                                                   'y_intercept1': y_intercept1, 
                                                   'y_intercept2': y_intercept2, 
                                                   'intersection': (sol_x_float, sol_y_float)})
        answer_data["area"] = area
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_data,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    [V3. 頂層函式]：直接定義於模組最外層。
    [V12.6 結構鎖死]：必須實作「數值序列比對」。
    [V13.5 禁絕複雜比對]：統一要求使用數字序列比對。
    [V13.6 Exact Check Logic]：指示 Coder 必須逐字複製 4-line check logic。
    """
    
    # Helper to parse a single numeric value, handling integers, floats, and simple fractions (e.g., "8/3")
    def _parse_simple_value(s):
        if '/' in s:
            num, den = map(float, s.split('/'))
            return num / den
        return float(s)

    # Helper to parse a single numeric value, handling LaTeX fractions and mixed numbers for `correct_answer`
    def _parse_latex_value(latex_str):
        # Try to match mixed fraction: -I\frac{N}{D} or I\frac{N}{D}
        match_mixed = re.match(r'(-?)(\d+)\\frac{(\d+)}{(\d+)}', latex_str)
        if match_mixed:
            sign = -1 if match_mixed.group(1) == '-' else 1
            integer_part = int(match_mixed.group(2))
            numerator = int(match_mixed.group(3))
            denominator = int(match_mixed.group(4))
            return sign * (integer_part + numerator / denominator)
        
        # Try to match simple fraction: -\frac{N}{D} or \frac{N}{D}
        match_frac = re.match(r'(-?)\\frac{(\d+)}{(\d+)}', latex_str)
        if match_frac:
            sign = -1 if match_frac.group(1) == '-' else 1
            numerator = int(match_frac.group(2))
            denominator = int(match_frac.group(3))
            return sign * (numerator / denominator)
        
        # Try to match integer or float
        return float(latex_str)

    try:
        # 1. Parse correct_answer (can be single area value or coordinate pair)
        parsed_correct_values = []
        if not correct_answer.strip().startswith('('): # It's an area value
            parsed_correct_values.append(_parse_latex_value(correct_answer))
        else: # It's a coordinate pair "(x, y)"
            # Extract x and y parts from (x, y)
            coord_match = re.match(r'\((.*?),\s*(.*?)\)', correct_answer)
            if not coord_match:
                return False # Invalid coordinate format in correct_answer
            x_str, y_str = coord_match.groups()
            parsed_correct_values.append(_parse_latex_value(x_str))
            parsed_correct_values.append(_parse_latex_value(y_str))

        # 2. Parse user_answer (assume cleaned: no '$' or '\', only numbers, '.', '/')
        user_answer_cleaned = user_answer.strip().replace('(', '').replace(')', '')
        # Split by comma, then parse each part
        user_parts = [p.strip() for p in user_answer_cleaned.split(',') if p.strip()]
        
        parsed_user_values = []
        for p in user_parts:
            parsed_user_values.append(_parse_simple_value(p))
        
        # 3. [V12.6 & V13.5]：數值序列比對
        if len(parsed_user_values) != len(parsed_correct_values):
            return False
        
        tolerance = 1e-9 # 浮點數比較容忍度
        for u, c in zip(parsed_user_values, parsed_correct_values):
            if abs(u - c) > tolerance:
                return False
        return True
    except Exception:
        # 如果解析失敗，則答案錯誤
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
