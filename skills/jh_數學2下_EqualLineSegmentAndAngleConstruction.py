# ==============================================================================
# ID: jh_數學2下_EqualLineSegmentAndAngleConstruction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 75.33s | RAG: 5 examples
# Created At: 2026-01-22 20:12:44
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
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime
import re

# --- 輔助函式定義 (Helper Functions) ---
# [V10.2 座標平面專用硬化規格] A. 資料結構鎖死: _generate_coordinate_value() 統一回傳固定格式。
# [V13.1 教學正確性補正] 禁絕假分數: 檢查 numerator < denominator 且 denominator > 1。
# [CRITICAL CODING STANDARDS: 座標精度] 座標值僅限整數或 0.5。
def _generate_coordinate_value(is_integer=True, include_zero=True):
    """
    生成一個座標值 (float_val, (int_part, num, den, is_neg))。
    is_integer: 若為 True，則生成整數座標。
    include_zero: 若為 True，則有機會生成 0。
    確保分數部分為真分數 (numerator < denominator) 且僅限 0.5。
    """
    is_neg = random.choice([True, False])
    float_val = 0.0
    int_part = 0
    num = 0
    den = 0

    # Handle zero generation explicitly
    if include_zero and random.random() < 0.1: # ~10% chance for 0
        return (0.0, (0, 0, 0, False))

    int_part_abs = random.randint(0, 7) # 整數部分可為 0, 範圍 [-7.5, 7.5]

    if is_integer: # Only integers
        float_val = float(int_part_abs)
        # If int_part_abs is 0 and include_zero is False, regenerate to ensure non-zero
        if int_part_abs == 0 and not include_zero:
            int_part_abs = random.randint(1, 8)
            float_val = float(int_part_abs)

        if is_neg:
            float_val = -float_val
            int_part = -int_part_abs
        else:
            int_part = int_part_abs
    else: # Allow 0.5 fractional part
        fractional_part_val = 0.0
        if random.choice([True, False]): # 50% chance to have a .5 fractional part
            num = 1
            den = 2
            fractional_part_val = 0.5
        else: # 50% chance to be a pure integer (no fractional part)
            num = 0
            den = 0
            fractional_part_val = 0.0
        
        # If int_part_abs is 0 and fractional_part_val is 0.0, it's 0.0.
        # If include_zero is False, we need to ensure it's not 0.0.
        if int_part_abs == 0 and fractional_part_val == 0.0 and not include_zero:
            int_part_abs = random.randint(1, 7) # Ensure non-zero integer part
            if random.choice([True, False]): # Still allow .5 for this non-zero integer
                num = 1
                den = 2
                fractional_part_val = 0.5

        float_val = float(int_part_abs) + fractional_part_val
        
        if is_neg:
            float_val = -float_val
            int_part = -int_part_abs
            if int_part_abs == 0 and fractional_part_val > 0: # For -0.5, int_part is 0.
                int_part = 0
        else:
            int_part = int_part_abs

    # Ensure -0.0 becomes 0.0
    if float_val == -0.0:
        float_val = 0.0

    return (float_val, (int_part, num, den, is_neg))


# [V10.2 座標平面專用硬化規格] C. LaTeX 模板規範: 嚴禁 {{...}}
def _format_coordinate(coord_data):
    """
    將座標數據格式化為字串 (例如："5", "-2", "1/2", "-3\frac{1}{4}")。
    處理整數和分數部分。
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    
    if float_val == 0.0:
        return "0"
    
    # [V13.5 最終硬化規約] 整數優先: 確保輸出為 (5, 4) 而非 (5.0, 4.0)
    if num == 0 and den == 0: # 它是整數
        return str(int(float_val))
    else: # 它是分數 (帶分數或真分數)
        abs_int_part = abs(int_part)
        sign = "-" if is_neg else ""

        if abs_int_part == 0: # 純分數 (e.g., 1/2, -1/2)
            expr = r"{sign}\frac{{{num}}}{{{den}}}"
            expr = expr.replace("{sign}", sign).replace("{num}", str(num)).replace("{den}", str(den))
            return expr
        else: # 帶分數 (e.g., 3 1/2, -3 1/2)
            expr = r"{sign}{int_part}\frac{{{num}}}{{{den}}}"
            expr = expr.replace("{sign}", sign).replace("{int_part}", str(abs_int_part)).replace("{num}", str(num)).replace("{den}", str(den))
            return expr

# [V13.6 API Hardened Spec] 繪製箭頭規範
# [CRITICAL RULE: Visual Solvability] 確保 x-axis 和 y-axis 有整數刻度標籤
# [V10.2 Pure Style] 視覺一致性: ax.set_aspect('equal'), 原點 '0', 點標籤加白色光暈
def _draw_coordinate_plane(points_with_labels=None, lines=None, max_coord=10):
    """
    繪製坐標平面，包含指定點和標籤。
    確保 X 軸和 Y 軸的主要整數刻度可見。
    """
    if points_with_labels is None:
        points_with_labels = []
    if lines is None:
        lines = []

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300

    ax.set_aspect('equal', adjustable='box') # ULTRA VISUAL STANDARDS: Aspect Ratio: `ax.set_aspect('equal')`
    ax.set_xlim([-max_coord - 1, max_coord + 1]) # Add some padding for arrows and labels
    ax.set_ylim([-max_coord - 1, max_coord + 1])

    # 繪製網格
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5) # 網格線輔助 (Grid Lines)

    # 繪製坐標軸
    ax.axhline(0, color='black', linewidth=1.5, zorder=3)
    ax.axvline(0, color='black', linewidth=1.5, zorder=3)

    # 為坐標軸添加箭頭 (V13.6 API Hardened Spec)
    ax.plot(max_coord + 1, 0, ">k", clip_on=False, markersize=8) # X 軸正向箭頭
    ax.plot(-max_coord - 1, 0, "<k", clip_on=False, markersize=8) # X 軸負向箭頭
    ax.plot(0, max_coord + 1, "^k", clip_on=False, markersize=8) # Y 軸正向箭頭
    ax.plot(0, -max_coord - 1, "vk", clip_on=False, markersize=8) # Y 軸負向箭頭

    # 設定刻度與標籤 (CRITICAL RULE: Visual Solvability, V13.0 格線對齊)
    # 確保刻度為整數間隔，且標籤可見
    major_ticks = range(-max_coord, max_coord + 1, 1) # 每 1 個單位一個刻度
    ax.set_xticks(list(major_ticks)) # 強制顯示刻度 (Mandatory Axis Ticks)
    ax.set_yticks(list(major_ticks)) # 強制顯示刻度 (Mandatory Axis Ticks)

    # 為了清晰度，只標註部分主要刻度 (例如每 2 個單位或 0)
    ax.set_xticklabels([str(t) if t % 2 == 0 or t == 0 else '' for t in major_ticks])
    ax.set_yticklabels([str(t) if t % 2 == 0 or t == 0 else '' for t in major_ticks])

    # 標註原點 '0' (V10.2 Pure Style)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold', zorder=7)

    # 繪製線段
    for line_data in lines:
        xs, ys = zip(*line_data['coords'])
        ax.plot(xs, ys, color=line_data.get('color', 'green'), linestyle=line_data.get('linestyle', '-'), linewidth=line_data.get('linewidth', 2), zorder=4)

    # 繪製點和標籤 (V13.5 最終硬化規約 - 標籤隔離)
    for point_data in points_with_labels:
        x, y, label = point_data['coords'][0], point_data['coords'][1], point_data['label']
        ax.plot(x, y, 'o', color='red', markersize=8, zorder=5) # 將點放在上層
        
        # 添加標籤，帶白色光暈 (V10.2 Pure Style), ULTRA VISUAL STANDARDS: Label Halo
        # ax.text 的內容只能是點的名稱 (Label)，不能包含座標值 (V13.0 標註權限隔離, V13.1 標籤純淨化)
        ax.text(x, y + 0.5, label, color='blue', ha='center', va='bottom',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7),
                fontsize=12, zorder=6) # 標籤也在上層

    # 將圖形轉換為 base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _calculate_distance(p1, p2):
    """計算兩點之間的歐幾里得距離。"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def _calculate_angle_measure(A, B, C):
    """
    計算角 ABC 的度數 (B 為頂點)。
    """
    # 向量 BA
    BA_x = A[0] - B[0]
    BA_y = A[1] - B[1]
    # 向量 BC
    BC_x = C[0] - B[0]
    BC_y = C[1] - B[1]

    dot_product = BA_x * BC_x + BA_y * BC_y
    magnitude_BA = math.sqrt(BA_x**2 + BA_y**2)
    magnitude_BC = math.sqrt(BC_x**2 + BC_y**2)

    if magnitude_BA == 0 or magnitude_BC == 0:
        return 0.0 # 退化情況 (點重合)

    cosine_angle = dot_product / (magnitude_BA * magnitude_BC)
    # 由於浮點數精度問題，確保 cosine_angle 在 [-1, 1] 範圍內
    cosine_angle = max(-1.0, min(cosine_angle, 1.0))
    angle_rad = math.acos(cosine_angle)
    return math.degrees(angle_rad)


# --- 題目生成函式 (Problem Generation Function) ---
# [自動重載] 確保代碼不依賴全域狀態。
# [隨機分流] generate() 內部使用 random.choice 對應 RAG 中的例題類型。
def generate(level=1):
    problem_type = random.choice([1, 2, 3]) # 隨機選擇問題類型 (Type 1, 2, or 3)

    max_coord_val = 8 # 座標範圍必須對稱且寬裕 (V13.5)

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    # [數據禁絕常數] 所有幾何長度、角度與面積必須隨機生成。
    # [座標鎖死] 幾何題必須根據 RAG 圖形定義正確的頂點座標。
    # (此處 RAG 圖形為虛擬概念，實作上為程式隨機生成座標)

    if problem_type == 1:
        # Type 1 (Maps to Example: RAG Ex 1 & 2 - 等線段作圖 - 複製線段長度)
        # 題目: 給定兩點 A, B，作一線段 CD 使其長度等於 AB，問 CD 長度。
        
        # 生成兩個不同的點 A 和 B
        Ax_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Ay_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Bx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        By_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        
        A = (Ax_data[0], Ay_data[0])
        B = (Bx_data[0], By_data[0])

        # 確保 A 和 B 是不同的點
        while A == B:
            Bx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            By_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            B = (Bx_data[0], By_data[0])

        # 計算線段 AB 的長度
        segment_length = _calculate_distance(A, B)

        # 格式化座標字串用於顯示
        Ax_str = _format_coordinate(Ax_data)
        Ay_str = _format_coordinate(Ay_data)
        Bx_str = _format_coordinate(Bx_data)
        By_str = _format_coordinate(By_data)
        
        # [CRITICAL RULE: Answer Data Purity] correct_answer 必須是純數據。
        correct_answer_val = round(segment_length, 2) # 四捨五入至小數點後兩位
        correct_answer = str(correct_answer_val)

        # [排版與 LaTeX 安全] 嚴禁 f-string，使用 .replace()。
        question_template = (
            r"已知坐標平面上有兩點 $A({Ax}, {Ay})$ 和 $B({Bx}, {By})$。"
            r"若使用尺規作圖，作一個線段 $CD$ 使其長度等於線段 $AB$ 的長度，"
            r"則線段 $CD$ 的長度為何？ (答案請四捨五入至小數點後兩位)"
        )
        question_text = question_template.replace("{Ax}", Ax_str).replace("{Ay}", Ay_str)
        question_text = question_text.replace("{Bx}", Bx_str).replace("{By}", By_str)

        # 圖片生成: 顯示點 A, B 和線段 AB
        points_to_draw = [
            {'coords': A, 'label': 'A'},
            {'coords': B, 'label': 'B'}
        ]
        lines_to_draw = [
            {'coords': [A, B], 'color': 'red', 'linestyle': '-', 'linewidth': 2}
        ]
        image_base64 = _draw_coordinate_plane(points_to_draw, lines_to_draw, max_coord=max_coord_val)

    elif problem_type == 2:
        # Type 2 (Maps to Example: RAG Ex 5 - 等角作圖 - 複製角度大小)
        # 題目: 給定三點 A, B, C 形成角 ABC，作一角 DEF 使其大小等於 ABC，問 DEF 度數。

        # 生成三個不同的點 A, B, C 形成角 ABC (B 為頂點)
        # 確保 A, B, C 不共線
        Bx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        By_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        B = (Bx_data[0], By_data[0])

        Ax_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Ay_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        A = (Ax_data[0], Ay_data[0])
        while A == B:
            Ax_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            Ay_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            A = (Ax_data[0], Ay_data[0])

        Cx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Cy_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        C = (Cx_data[0], Cy_data[0])
        
        # 避免 C=B, C=A, 和 A-B-C 共線
        # 共線判斷: 檢查 (Ay-By)*(Cx-Bx) == (Cy-By)*(Ax-Bx)
        # Using a small tolerance for float comparison
        collinear_tolerance = 1e-6
        while C == B or C == A or \
              abs((A[1]-B[1])*(C[0]-B[0]) - (C[1]-B[1])*(A[0]-B[0])) < collinear_tolerance:
            Cx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            Cy_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            C = (Cx_data[0], Cy_data[0])

        # 計算角 ABC 的度數
        angle_measure = _calculate_angle_measure(A, B, C)
        
        # 格式化座標字串用於顯示
        Ax_str = _format_coordinate(Ax_data)
        Ay_str = _format_coordinate(Ay_data)
        Bx_str = _format_coordinate(Bx_data)
        By_str = _format_coordinate(By_data)
        Cx_str = _format_coordinate(Cx_data)
        Cy_str = _format_coordinate(Cy_data)

        # [CRITICAL RULE: Answer Data Purity] correct_answer 必須是純數據。
        correct_answer_val = round(angle_measure, 2) # 四捨五入至小數點後兩位
        correct_answer = str(correct_answer_val)

        # [排版與 LaTeX 安全] 嚴禁 f-string，使用 .replace()。
        question_template = (
            r"已知坐標平面上有三點 $A({Ax}, {Ay})$、$B({Bx}, {By})$ 和 $C({Cx}, {Cy})$。"
            r"若使用尺規作圖，作一個角 $\angle DEF$ 使其大小等於 $\angle ABC$。"
            r"則 $\angle DEF$ 的度數為何？ (答案請四捨五入至小數點後兩位)"
        )
        question_text = question_template.replace("{Ax}", Ax_str).replace("{Ay}", Ay_str)
        question_text = question_text.replace("{Bx}", Bx_str).replace("{By}", By_str)
        question_text = question_text.replace("{Cx}", Cx_str).replace("{Cy}", Cy_str)

        # 圖片生成: 顯示點 A, B, C 和角 ABC
        points_to_draw = [
            {'coords': A, 'label': 'A'},
            {'coords': B, 'label': 'B'},
            {'coords': C, 'label': 'C'}
        ]
        lines_to_draw = [
            {'coords': [A, B], 'color': 'blue', 'linestyle': '-', 'linewidth': 2},
            {'coords': [B, C], 'color': 'blue', 'linestyle': '-', 'linewidth': 2}
        ]
        image_base64 = _draw_coordinate_plane(points_to_draw, lines_to_draw, max_coord=max_coord_val)

    else: # problem_type == 3
        # Type 3 (Maps to Architect's Spec: 垂直平分線作圖 - 尋找中點座標)
        # 題目: 給定兩點 A, B，作其垂直平分線會通過中點 M，問 M 的座標。
        
        # 生成兩個不同的點 A 和 B
        Ax_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Ay_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        Bx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        By_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
        
        A = (Ax_data[0], Ay_data[0])
        B = (Bx_data[0], By_data[0])

        # 確保 A 和 B 是不同的點
        while A == B:
            Bx_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            By_data = _generate_coordinate_value(is_integer=random.choice([True, False]), include_zero=True)
            B = (Bx_data[0], By_data[0])

        # 計算線段 AB 的中點 M
        Mx = (A[0] + B[0]) / 2
        My = (A[1] + B[1]) / 2

        # 格式化座標字串用於顯示
        Ax_str = _format_coordinate(Ax_data)
        Ay_str = _format_coordinate(Ay_data)
        Bx_str = _format_coordinate(Bx_data)
        By_str = _format_coordinate(By_data)
        
        # [CRITICAL RULE: Answer Data Purity] correct_answer 必須是純數據。
        # [V13.5 最終硬化規約] 整數優先: 確保輸出為 (5, 4) 而非 (5.0, 4.0)
        Mx_display = str(int(Mx)) if Mx.is_integer() else str(round(Mx, 2))
        My_display = str(int(My)) if My.is_integer() else str(round(My, 2))
        correct_answer = f"{Mx_display},{My_display}" # [V13.1 答案格式標準化] 座標題答案格式為純數字列表，如 "2, -1"。

        # [排版與 LaTeX 安全] 嚴禁 f-string，使用 .replace()。
        question_template = (
            r"已知坐標平面上有兩點 $A({Ax}, {Ay})$ 和 $B({Bx}, {By})$。"
            r"若使用尺規作圖，可以作出線段 $AB$ 的垂直平分線，該線會通過線段 $AB$ 的中點 $M$。"
            r"請問中點 $M$ 的坐標為何？ (答案請以 'x,y' 格式表示，各數值四捨五入至小數點後兩位)"
        )
        question_text = question_template.replace("{Ax}", Ax_str).replace("{Ay}", Ay_str)
        question_text = question_text.replace("{Bx}", Bx_str).replace("{By}", By_str)

        # 圖片生成: 顯示點 A, B 和線段 AB
        points_to_draw = [
            {'coords': A, 'label': 'A'},
            {'coords': B, 'label': 'B'}
        ]
        lines_to_draw = [
            {'coords': [A, B], 'color': 'red', 'linestyle': '-', 'linewidth': 2}
        ]
        image_base64 = _draw_coordinate_plane(points_to_draw, lines_to_draw, max_coord=max_coord_val)

    # [數據與欄位] 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 該欄位用於多選題選項，此處留空。
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# --- 閱卷邏輯函式 (Check Function) ---
# [強韌閱卷邏輯 (Robust Check Logic)] check 函式必須具備輸入清洗能力。
# [V13.6 API Hardened Spec] 必須逐字複製 4-line check logic。

    """
    強韌的閱卷函式，用於數值答案，支援數值序列比對。
    """
    # 1. 輸入清洗 (Input Sanitization)
    # 使用 Regex 自動移除使用者輸入中的 LaTeX 符號、變數前綴和所有空白字元。
    cleaned_user_answer = re.sub(r'[\\$}{kxya=Ans:]', '', user_answer)
    cleaned_user_answer = re.sub(r'\s+', '', cleaned_user_answer) # 移除所有空白字元

    # 2. 強韌比對邏輯 (Robust Comparison Logic)
    try:
        # 將使用者答案和正確答案都拆分為浮點數列表，支援多個數值 (如座標 "x,y")
        user_parts = [float(p) for p in cleaned_user_answer.split(',') if p.strip()]
        correct_parts = [float(p) for p in correct_answer.split(',') if p.strip()]

        if len(user_parts) != len(correct_parts):
            return False

        # 比較每個部分，考慮浮點數的容忍度 (V13.5 禁絕複雜比對，統一使用數字序列比對)
        tolerance = 1e-2 # 允許小數點後兩位的誤差
        for u, c in zip(user_parts, correct_parts):
            if not math.isclose(u, c, rel_tol=tolerance, abs_tol=tolerance):
                return False
        return True
    except ValueError:
        # 如果使用者輸入無法轉換為浮點數，則判定為錯誤
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
