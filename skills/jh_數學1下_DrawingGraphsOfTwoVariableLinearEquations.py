# ==============================================================================
# ID: jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 51.82s | RAG: 5 examples
# Created At: 2026-01-16 09:22:52
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
# --- 4. Answer Checker [V15.0 Geometric Verification] ---
def check(user_answer, correct_answer):
    """
    [V15.0 Geometric Verification] 
    驗證使用者輸入的兩個點是否位於正確的直線上，而不強制要求特定的座標點。
    Algorithm: Vector Cross Product & Collinearity Check
    """
    import math

    # 1. 解析用戶輸入與正確答案的座標點
    def parse_points(text):
        try:
            # 移除 LaTeX 可能產生的額外符號，保留數字、負號、小數點與分割符
            # 預期格式: (x1, y1), (x2, y2)
            # 使用 Regex 提取所有的數值可能是最穩健的方法
            import re
            nums = re.findall(r'-?\d+(?:\.\d+)?(?: ?/ ?\d+)?', text)
            
            vals = []
            for s in nums:
                if '/' in s: # Handle fraction input like 1/2
                     n, d = map(float, s.split('/'))
                     vals.append(n/d)
                else: 
                     vals.append(float(s))

            # 必須剛好解析出 4 個數值 (兩組座標)
            if len(vals) != 4: return None
            
            p1 = (vals[0], vals[1])
            p2 = (vals[2], vals[3])
            return p1, p2
        except:
            return None

    user_pts = parse_points(user_answer)
    correct_pts = parse_points(correct_answer)

    if not user_pts or not correct_pts:
        # 如果解析失敗，嘗試退回原本的字串比對 (for Categorical answers like "是"/"否")
        # 但此 Skill 主要為座標題，若解析失敗很大機率是格式錯誤
        return False

    u1, u2 = user_pts
    c1, c2 = correct_pts
    
    # 2. 防呆：檢查使用者輸入的兩點是否重合
    # 若重合，無法決定一條直線，視為錯誤
    if math.isclose(u1[0], u2[0], abs_tol=1e-6) and math.isclose(u1[1], u2[1], abs_tol=1e-6):
        return False

    # 3. 幾何驗證：檢查 u1 與 u2 是否都在由 c1, c2 定義的直線上
    # 直線方程式向量式: (P - c1) x (c2 - c1) = 0
    # 其中 x 代表 2D 向量外積 (ad - bc)
    
    # 向量 V_line = c2 - c1
    vx = c2[0] - c1[0]
    vy = c2[1] - c1[1]

    def is_on_line(p, start_p, vec_x, vec_y):
        # 向量 V_point = p - start_p
        px = p[0] - start_p[0]
        py = p[1] - start_p[1]
        
        # Cross Product: px * vy - py * vx
        # 考慮垂直線或水平線的特殊情況，直接用外積最準
        cross_prod = px * vec_y - py * vec_x
        return math.isclose(cross_prod, 0, abs_tol=1e-4) # 給予較寬鬆的容忍度

    # 對使用者輸入的兩個點分別進行共線檢查
    u1_ok = is_on_line(u1, c1, vx, vy)
    u2_ok = is_on_line(u2, c1, vx, vy)

    if u1_ok and u2_ok:
        return True

    return False



from datetime import datetime
import base64
import io
import matplotlib.pyplot as plt
import numpy as np

# --- V10.2.A: 資料結構鎖死 (Prevent Unpacking Error) ---
# 統一回傳固定格式：(float_val, (int_part, num, den, is_neg))
# 若為整數，num 與 den 設為 0；若為分數，則 int_part 為帶分數整數部。
def _generate_coordinate_value(is_fraction=False, integer_range=(-8, 8)):
    """
    生成一個座標值，可以是整數或分數。
    Args:
        is_fraction (bool): 是否允許生成分數。
        integer_range (tuple): 整數部分的生成範圍。
    Returns:
        tuple: (float_val, (int_part, num, den, is_neg))
    """
    # V13.5: 座標選取控制 - 使用 random.randint(-8, 8)
    # 系統底層鐵律 5: 座標精度: 座標值僅限整數或 0.5。
    if is_fraction and random.random() < 0.5: # 50% 機率生成分數
        int_part_val = random.randint(integer_range[0], integer_range[1])
        
        # V13.1: 禁絕假分數 - numerator < denominator 且 denominator > 1
        # [V16.0] 放寬座標精度: 允許 0.25, 0.5, 0.75。
        # 因此，分母可為 2 或 4。
        denominator = random.choice([2, 4])
        if denominator == 2:
            numerator = 1
        else:
            numerator = random.choice([1, 3])

        is_neg = False
        if int_part_val == 0:
            if random.random() < 0.5: # 對於整數部分為0的，有時生成負分數
                is_neg = True
        elif int_part_val < 0:
            is_neg = True
        
        float_val = abs(int_part_val) + (numerator / denominator)
        if is_neg:
            float_val = -float_val
        
        # 調整 int_part_val 以符合帶分數表示，例如 -1/2 的 int_part 應為 0
        if is_neg and int_part_val == 0:
            pass # int_part_val 已經是 0
        elif is_neg and int_part_val != 0:
            int_part_val = -abs(int_part_val)

        return float_val, (int_part_val, numerator, denominator, is_neg)
    else:
        val = random.randint(integer_range[0], integer_range[1])
        return float(val), (val, 0, 0, val < 0)

# --- V13.5: 整數優先 ---
def _format_coordinate_value(val):
    """
    將座標值格式化為字串，若為整數則去除小數點。
    Args:
        val (float or int): 座標數值。
    Returns:
        str: 格式化後的字串。
    """
    # V13.0: 格式精確要求 - 確保回饋給學生的答案是 "(5, 4)" 而非 "(5.0, 4.0)"。
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)

# --- V10.2.D, V13.0, V13.1, V13.5, V13.6: 視覺化與輔助函式通用規範 ---
def _draw_coordinate_plane_with_line():
    """
    繪製一個空的直角坐標平面。
    Returns:
        str: 坐標平面圖片的 base64 編碼字串。
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # V13.0: 座標軸範圍必須是對稱整數（如 -8 到 8），且 xticks 間隔必須固定為 1。
    # V13.5: 座標範圍必須對稱且寬裕（如 -8 到 8），確保點與標籤不會被邊框切掉。
    plot_range = 8
    ax.set_xlim([-plot_range, plot_range])
    ax.set_ylim([-plot_range, plot_range])
    ax.set_xticks(np.arange(-plot_range, plot_range + 1, 1))
    ax.set_yticks(np.arange(-plot_range, plot_range + 1, 1))

    # V10.2.D: ax.set_aspect('equal') 確保網格為正方形。
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)

    # V13.6: Arrow Ban - 嚴禁在 axhline/axvline 使用 arrowprops
    # 必須指示使用 ax.plot(limit, 0, ">k", clip_on=False) 繪製箭頭。
    # Draw x-axis
    ax.axhline(0, color='black', linewidth=1.5)
    ax.plot(plot_range, 0, ">k", clip_on=False, transform=ax.get_yaxis_transform())
    ax.text(plot_range + 0.5, 0, "x", color='black', ha='center', va='center', fontsize=14)
    # Draw y-axis
    ax.axvline(0, color='black', linewidth=1.5)
    ax.plot(0, plot_range, "^k", clip_on=False, transform=ax.get_xaxis_transform())
    ax.text(0, plot_range + 0.5, "y", color='black', ha='center', va='center', fontsize=14)

    # V10.2.D: 坐標軸標註：僅顯示原點 0 (18號加粗)
    ax.text(0.1, -0.6, "0", color='black', ha='left', va='center', fontsize=18, fontweight='bold')

    # V6: 防洩漏原則：視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式，確保學生無法從圖形中直接看到答案。
    # 針對「判斷點是否在直線上」題型，image_base64 嚴禁包含任何線段或點。僅提供 1x1 的淺灰色網格、座標軸與原點 '0'。
    
    buf = io.BytesIO()
    # V11.6: ULTRA VISUAL STANDARDS: Resolution: dpi=300
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# --- Helper for formatting equation strings with LaTeX safety (V5) ---
def _format_equation_string(a, b, c, eq_type, k_val=None):
    """
    將方程式的參數格式化為 LaTeX 字串。
    Args:
        a, b, c (int): 方程式 ax + by = c 的係數和常數。
        eq_type (str): 方程式類型 ("general", "x_equals_k", "y_equals_k")。
        k_val (int, optional): 對於 x=k 或 y=k 類型，k 的值。
    Returns:
        str: 格式化後的 LaTeX 方程式字串。
    """
    # V5: 【強制】語法零修復 (Regex=0)：凡字串包含 LaTeX 指令 (如 \frac, \sqrt, \pm)，嚴禁使用 f-string 或 % 格式化。
    # 必須嚴格執行以下模板：expr = r"x = {a}".replace("{a}", str(ans_val))
    # V5: 【嚴禁】不可使用 f"x = {ans_val}"
    # V5: 【排版】嚴禁使用 \par 或 \[...\]. 所有數學式一律使用 $...$。
    # 系統底層鐵律 1: 方程式生成鎖死 (Equation Robustness) - 嚴禁使用 f-string 組合 `ax + by = c`。
    # 【強制流程】：必須分別判定 a, b 的正負與是否為 1，手動組合字串片段後合併。

    if eq_type == "general":
        parts = []
        if a != 0:
            if a == 1:
                parts.append("x")
            elif a == -1:
                parts.append("-x")
            else:
                parts.append(r"{a_val}x".replace("{a_val}", str(a)))

        if b != 0:
            if b == 1:
                if parts: # If x term exists, add '+'
                    parts.append("+y")
                else:
                    parts.append("y")
            elif b == -1:
                parts.append("-y")
            else:
                if b > 0 and parts: # If x term exists and b is positive, add '+'
                    parts.append(r"+{b_val}y".replace("{b_val}", str(b)))
                else:
                    parts.append(r"{b_val}y".replace("{b_val}", str(b)))
        
        # 確保至少有 x 或 y 項，防止生成空字串
        if not parts:
            # 這種情況不應該在有效的二元一次方程式中發生，但作為防禦性編程
            return r"$0 = {c_val}$".replace("{c_val}", str(c))

        eq_text = r"${terms} = {c_val}$".replace("{terms}", "".join(parts)).replace("{c_val}", str(c))
        return eq_text
    elif eq_type == "x_equals_k":
        eq_text = r"$x = {k_val}$".replace("{k_val}", _format_coordinate_value(k_val))
        return eq_text
    elif eq_type == "y_equals_k":
        eq_text = r"$y = {k_val}$".replace("{k_val}", _format_coordinate_value(k_val))
        return eq_text
    return ""

def generate(level=1):
    """
    生成二元一次方程式圖形的畫法題目。
    Args:
        level (int): 題目難度等級，目前未使用。
    Returns:
        dict: 包含題目文本、正確答案、答案、圖片 base64 編碼等資訊的字典。
    """
    # MANDATORY MIRRORING RULES: STRICT MAPPING
    # Ex 1, 2 use ax + by = c. Ex 5 uses x=k or y=k.
    # This problem asks for *any two points*, which aligns with the implicit task of Ex 1, 2, 5.
    problem_type = random.choice(["general_equation", "special_equation"])
    
    a, b, c = 0, 0, 0
    k = 0
    equation_str = ""
    correct_points_formatted = [] # Store points as tuples of formatted strings

    if problem_type == "general_equation":
        # Maps to RAG Ex 1 and Ex 2: ax + by = c
        # V10: 數據禁絕常數 (Data Prohibition) [CRITICAL] - 隨機生成所有幾何長度、角度與面積。
        # V10: 公式計算 - 嚴禁硬編碼 (Hardcode) 答案或座標。所有目標答案與圖形座標必須根據隨機生成的數據，透過幾何公式反向計算得出。
        while a == 0 and b == 0: # 確保至少有一個係數不為零
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
        c = random.randint(-15, 15) # 常數項範圍

        equation_str = _format_equation_string(a, b, c, "general")

        found_points_raw = [] # Store points as (float_val, float_val)
        
        # 嘗試尋找 x-截距 (y=0) 和 y-截距 (x=0)
        # V13.5: 座標範圍必須對稱且寬裕（如 -8 到 8）
        if b != 0:
            y_val = c / b
            if abs(y_val) <= 8: # [V16.0] Relaxed Filter: Allow any valid coordinate within range
                found_points_raw.append((0.0, y_val))
        
        if a != 0:
            x_val = c / a
            if abs(x_val) <= 8: # [V16.0] Relaxed Filter: Allow any valid coordinate within range
                if (x_val, 0.0) not in found_points_raw: # 確保點不重複
                    found_points_raw.append((x_val, 0.0))

        # 如果不足兩點，或需要更多樣的點，則隨機生成
        attempts = 0
        max_attempts = 100
        while len(found_points_raw) < 2 and attempts < max_attempts:
            if random.random() < 0.5: # 隨機選取 x 值
                x_coord_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                if b != 0:
                    y_coord_float = (c - a * x_coord_float) / b
                    if abs(y_coord_float) <= 8:
                        new_point = (x_coord_float, y_coord_float)
                        # 檢查點是否已存在（考慮浮點數精度）
                        is_duplicate = False
                        for p in found_points_raw:
                            if math.isclose(p[0], new_point[0], rel_tol=1e-6) and math.isclose(p[1], new_point[1], rel_tol=1e-6):
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            found_points_raw.append(new_point)
                elif a != 0: # b == 0, 方程式為 ax = c, x 值固定
                    x_fixed_float = c / a
                    if abs(x_fixed_float) <= 8 and math.isclose(x_fixed_float, x_coord_float, rel_tol=1e-6):
                            # 如果隨機生成的 x 恰好是固定值，則 y 可以是任意值
                            y_coord_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                            if abs(y_coord_float) <= 8:
                                new_point = (x_fixed_float, y_coord_float)
                                is_duplicate = False
                                for p in found_points_raw:
                                    if math.isclose(p[0], new_point[0], rel_tol=1e-6) and math.isclose(p[1], new_point[1], rel_tol=1e-6):
                                        is_duplicate = True
                                        break
                                if not is_duplicate:
                                    found_points_raw.append(new_point)

            else: # 隨機選取 y 值
                y_coord_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                if a != 0:
                    x_coord_float = (c - b * y_coord_float) / a
                    if abs(x_coord_float) <= 8:
                        new_point = (x_coord_float, y_coord_float)
                        is_duplicate = False
                        for p in found_points_raw:
                            if math.isclose(p[0], new_point[0], rel_tol=1e-6) and math.isclose(p[1], new_point[1], rel_tol=1e-6):
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            found_points_raw.append(new_point)
                elif b != 0: # a == 0, 方程式為 by = c, y 值固定
                    y_fixed_float = c / b
                    if abs(y_fixed_float) <= 8 and math.isclose(y_fixed_float, y_coord_float, rel_tol=1e-6):
                            # 如果隨機生成的 y 恰好是固定值，則 x 可以是任意值
                            x_coord_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                            if abs(x_coord_float) <= 8:
                                new_point = (x_coord_float, y_fixed_float)
                                is_duplicate = False
                                for p in found_points_raw:
                                    if math.isclose(p[0], new_point[0], rel_tol=1e-6) and math.isclose(p[1], new_point[1], rel_tol=1e-6):
                                        is_duplicate = True
                                        break
                                if not is_duplicate:
                                    found_points_raw.append(new_point)
            attempts += 1
        
        # 若經過多次嘗試仍不足兩點，則退回簡單的整數點生成策略
        # 確保生成的點符合「整數或 0.5」的精度要求
        if len(found_points_raw) < 2:
            found_points_raw = []
            # 遍歷 x 範圍尋找整數或 0.5 解
            x_values_to_try = [float(i) for i in range(-8, 9)] + [i + 0.5 for i in range(-8, 8)]
            for x_try in x_values_to_try:
                if b != 0:
                    y_try_float = (c - a * x_try) / b
                    if abs(y_try_float) <= 8:
                        new_point = (float(x_try), y_try_float)
                        if new_point not in found_points_raw:
                            found_points_raw.append(new_point)
                elif a != 0: # b == 0, 方程式為 ax = c, x 值固定
                    x_fixed_float = c / a
                    if abs(x_fixed_float) <= 8:
                        # For vertical line, x is fixed, y can be any valid value (integer or X.5)
                        y_val_for_vertical, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                        if abs(y_val_for_vertical) <= 8:
                            new_point = (x_fixed_float, y_val_for_vertical)
                            if new_point not in found_points_raw:
                                found_points_raw.append(new_point)
                        # Also try another y to ensure two distinct points if needed
                        y_val_for_vertical_2, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                        while math.isclose(y_val_for_vertical, y_val_for_vertical_2, rel_tol=1e-6):
                            y_val_for_vertical_2, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-7, 7))
                        if abs(y_val_for_vertical_2) <= 8:
                            new_point_2 = (x_fixed_float, y_val_for_vertical_2)
                            if new_point_2 not in found_points_raw:
                                found_points_raw.append(new_point_2)

                if len(found_points_raw) >= 2:
                    break
        
        # 取前兩個點並格式化為字串
        # If still less than 2 points (highly unlikely with the robust logic), ensure at least two
        if len(found_points_raw) < 2:
            # Fallback to a very basic, guaranteed solution if previous complex logic fails
            # [V16.0] Corrected Fallback Logic for Vertical/Horizontal Lines
            if a != 0 and b == 0: # Vertical Line ax = c => x = c/a
                x1 = c / a
                x2 = x1
                # y can be anything
                y1 = 0.0
                y2 = 1.0 
                found_points_raw = [(x1, y1), (x2, y2)]
            elif b != 0 and a == 0: # Horizontal Line by = c => y = c/b
                y1 = c / b
                y2 = y1
                # x can be anything
                x1 = 0.0
                x2 = 1.0
                found_points_raw = [(x1, y1), (x2, y2)]
            elif b != 0 and a != 0: # General Line
                # Point 1: Let x = 0
                x1 = 0.0
                y1 = c / b
                
                # Point 2: Let x = 1
                x2 = 1.0
                y2 = (c - a) / b
                
                found_points_raw = [(x1, y1), (x2, y2)]
            else: 
                # Impossible case if init checks pass (a=0 and b=0)
                found_points_raw = [(0.0, 0.0), (1.0, 1.0)]

        # Format the first two points found
        correct_points_formatted = [(_format_coordinate_value(p[0]), _format_coordinate_value(p[1])) for p in found_points_raw[:2]]


    elif problem_type == "special_equation":
        # Maps to RAG Ex 5: x = k or y = k
        is_x_equals_k = random.choice([True, False])
        k_val_float, _ = _generate_coordinate_value(is_fraction=False, integer_range=(-7, 7)) # K 值在範圍內
        
        if is_x_equals_k:
            equation_str = _format_equation_string(0, 0, 0, "x_equals_k", k_val_float)
            y1_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            y2_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            while math.isclose(y1_float, y2_float, rel_tol=1e-6): # 確保 y 值不同
                y2_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            correct_points_formatted = [(_format_coordinate_value(k_val_float), _format_coordinate_value(y1_float)), 
                                        (_format_coordinate_value(k_val_float), _format_coordinate_value(y2_float))]
        else: # y = k
            equation_str = _format_equation_string(0, 0, 0, "y_equals_k", k_val_float)
            x1_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            x2_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            while math.isclose(x1_float, x2_float, rel_tol=1e-6): # 確保 x 值不同
                x2_float, _ = _generate_coordinate_value(is_fraction=True, integer_range=(-5, 5))
            correct_points_formatted = [(_format_coordinate_value(x1_float), _format_coordinate_value(k_val_float)), 
                                        (_format_coordinate_value(x2_float), _format_coordinate_value(k_val_float))]

    question_text = r"請找出滿足方程式 {equation_text} 的任意兩個點的座標。".replace("{equation_text}", equation_str)
    
    # V13.1: 答案格式標準化：座標題：正確答案格式為 A(3, 5)。
    # 對於兩個點，格式為 "(x1, y1), (x2, y2)"
    correct_answer_str = r"({x1_val}, {y1_val}), ({x2_val}, {y2_val})".replace("{x1_val}", correct_points_formatted[0][0]).replace("{y1_val}", correct_points_formatted[0][1]).replace("{x2_val}", correct_points_formatted[1][0]).replace("{y2_val}", correct_points_formatted[1][1])
    
    # V6: 防洩漏原則 - 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
    image_base64 = _draw_coordinate_plane_with_line()

    # V7: 數據與欄位 (Standard Fields)
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str, # For display purposes, same as correct_answer
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1"
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
