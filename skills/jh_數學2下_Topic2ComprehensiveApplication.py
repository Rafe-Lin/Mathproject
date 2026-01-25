# ==============================================================================
# ID: jh_數學2下_Topic2ComprehensiveApplication
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 77.49s | RAG: 5 examples
# Created At: 2026-01-23 14:44:21
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



import io
import base64
import matplotlib.pyplot as plt
from datetime import datetime
import re

# Helper Functions adhering to Architect's Specification and System Guardrails

def _generate_coordinate_value(is_fraction=False, min_val=-8, max_val=8):
    """
    功能: 生成一個符合 V10.2 規範的座標值，並嚴格遵守「座標值僅限整數或 0.5」的守則。
    參數:
        is_fraction: 布林值，指示是否生成帶分數形式的座標值 (在此處特指 X.5)。
        min_val, max_val: 座標值的範圍。
    回傳: (float_val, (int_part, num, den, is_neg)) 統一格式。
          其中 int_part 是絕對值的整數部分，num/den 是分數部分 (例如 3.5 -> (3.5, (3, 1, 2, False)))。
    """
    if is_fraction:
        # 為了確保座標值僅限整數或 X.5，我們生成一個乘以2的整數，然後除以2。
        # 這樣可以保證結果是 N 或 N.5。
        val_float = random.randint(min_val * 2, max_val * 2) / 2.0
    else:
        val_float = float(random.randint(min_val, max_val))
    
    # 解析 val_float 以生成 (int_part, num, den, is_negative) 格式
    is_negative = val_float < 0
    abs_val = abs(val_float)
    
    int_part = int(abs_val)
    fractional_part = abs_val - int_part
    
    num = 0
    den = 0
    if fractional_part > 1e-9: # 使用小容忍度檢查是否存在分數部分
        # 根據生成邏輯，如果存在分數部分，它一定是 0.5
        num = 1
        den = 2
            
    return (val_float, (int_part, num, den, is_negative))

def _format_coordinate_display(coord_data):
    """
    功能: 將 _generate_coordinate_value 的回傳值格式化為 LaTeX 友善的字串。
    參數: coord_data (由 _generate_coordinate_value 回傳的 (float_val, (int_part, num, den, is_neg)) 元組)。
    回傳: str。
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    
    if num == 0: # 整數 (包含 0)
        return str(int(float_val))
    
    # 帶分數或純分數 (在此情境下一定是 X.5)
    sign = "-" if is_neg else ""
    
    if int_part == 0: # 純分數，例如 0.5 或 -0.5
        return r"{s}\frac{n}{d}".replace("{s}", sign).replace("{n}", str(num)).replace("{d}", str(den))
    else: # 帶分數，例如 3.5 或 -3.5
        return r"{s}{i}\frac{n}{d}".replace("{s}", sign).replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))

def _draw_coordinate_plane(points_with_labels, x_range, y_range):
    """
    功能: 繪製座標平面及點，遵循 ULTRA VISUAL STANDARDS (V11.6)。
    參數:
        points_with_labels: 列表，每個元素為 (x_coord_float, y_coord_float, label_str)。
        x_range, y_range: 座標軸範圍，例如 (-10, 10)。
    回傳: str (base64 編碼的圖片)。
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # V11.6 Resolution: dpi=300
    ax.set_aspect('equal', adjustable='box') # V10.2 D, V11.6 Aspect Ratio
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.grid(True, linestyle='--', alpha=0.6) # V13.0 Grid Lines
    
    # 繪製座標軸 (V13.6 Arrow Ban 已被 Architect's Spec 重新引入箭頭)
    ax.plot(x_range, [0, 0], 'k-', lw=1) # X-axis
    ax.plot([0, 0], y_range, 'k-', lw=1) # Y-axis
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8) # X軸箭頭
    ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8) # Y軸箭頭
    
    # 標註原點 (V10.2 D)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')
    
    # 強制標示 X 軸與 Y 軸主要整數刻度 (V17.1 Visual Solvability, V13.0 Mandatory Axis Ticks)
    ax.set_xticks(range(x_range[0], x_range[1] + 1))
    ax.set_yticks(range(y_range[0], y_range[1] + 1))
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # 遍歷 points_with_labels 繪製點並標註 (V10.2 D, V13.0, V13.1, V13.5 標籤隔離與光暈)
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='red', markersize=8, zorder=5)
        ax.text(x + 0.3, y + 0.3, label, fontsize=14, color='blue', ha='left', va='bottom', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)) # V11.6 Label Halo
                
    plt.xlabel('X', fontsize=14)
    plt.ylabel('Y', fontsize=14)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300) # V11.6 Resolution
    plt.close(fig)
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

# Main functions

def generate(level: int = 1) -> dict:
    """
    `generate()` 函式將根據 `level` 參數或隨機選擇不同的題型，以鏡射 RAG 資料庫中
    「綜合應用」的例題模式。本單元將隨機生成兩類問題：
    *   Type 1 (Maps to Example 1, 3 - Area Calculation): 給定多邊形的頂點座標，計算其面積。
    *   Type 2 (Maps to Example 2, 4 - Missing Vertex): 給定平行四邊形的三個頂點座標，找出第四個頂點座標。
    """
    problem_type = random.choice([1, 2])
    
    x_range = (-10, 10) # V13.0, V13.5 座標範圍
    y_range = (-10, 10)

    if problem_type == 1: # Type 1: 給定多邊形頂點，計算面積
        # jh_數學2下_Topic2ComprehensiveApplication 綜合應用 - 多邊形面積
        # RAG Example Mapping: 類似於計算不規則四邊形或三角形面積的題目
        
        while True:
            # 隨機生成四個點的座標，確保它們不重合且不共線。
            # 為了增加變化，座標值可以是整數或 X.5 的形式。
            x1_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y1_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            x2_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y2_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            x3_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y3_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            x4_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y4_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)

            A = (x1_data[0], y1_data[0])
            B = (x2_data[0], y2_data[0])
            C = (x3_data[0], y3_data[0])
            D = (x4_data[0], y4_data[0])

            points_list = [A, B, C, D]
            
            # 檢查點的唯一性
            if len(set(points_list)) < 4:
                continue # 重新生成，如果點不唯一

            # 檢查任意三點是否共線
            def is_collinear(p1, p2, p3):
                # 使用叉積法：(x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0
                return abs((p2[0]-p1[0])*(p3[1]-p1[1]) - (p2[1]-p1[1])*(p3[0]-p1[0])) < 1e-6 

            if is_collinear(A, B, C) or is_collinear(A, B, D) or \
               is_collinear(A, C, D) or is_collinear(B, C, D):
                continue # 重新生成，如果任意三點共線
            
            # 計算四邊形面積 (使用鞋帶公式)
            # Area = 0.5 * |(x1y2 + x2y3 + x3y4 + x4y1) - (y1x2 + y2x3 + y3x4 + y4x1)|
            area = 0.5 * abs(A[0]*B[1] + B[0]*C[1] + C[0]*D[1] + D[0]*A[1] - \
                             (A[1]*B[0] + B[1]*C[0] + C[1]*D[0] + D[1]*A[0]))
            
            # 確保面積不為零且足夠大 (避免因浮點數精度或近乎共線導致的問題)
            if area < 0.5: 
                continue # 重新生成，如果面積太小

            break # 找到有效點集

        # 格式化顯示座標
        A_display = f"({_format_coordinate_display(x1_data)}, {_format_coordinate_display(y1_data)})"
        B_display = f"({_format_coordinate_display(x2_data)}, {_format_coordinate_display(y2_data)})"
        C_display = f"({_format_coordinate_display(x3_data)}, {_format_coordinate_display(y3_data)})"
        D_display = f"({_format_coordinate_display(x4_data)}, {_format_coordinate_display(y4_data)})"

        question_text = r"已知平面上四個點的座標分別為 $A{A_disp}$, $B{B_disp}$, $C{C_disp}$ 和 $D{D_disp}$。試求四邊形 $ABCD$ 的面積。".replace("{A_disp}", A_display).replace("{B_disp}", B_display).replace("{C_disp}", C_display).replace("{D_disp}", D_display)
        
        # correct_answer 必須為純數據，且確保為整數或小數，不含單位或符號
        correct_answer = str(round(area, 2)) # 四捨五入到小數點後兩位
        
        points_for_drawing = [
            (A[0], A[1], 'A'),
            (B[0], B[1], 'B'),
            (C[0], C[1], 'C'),
            (D[0], D[1], 'D')
        ]
        image_base64 = _draw_coordinate_plane(points_for_drawing, x_range, y_range)

    else: # problem_type == 2: Type 2: 給定平行四邊形三頂點，求第四頂點
        # jh_數學2下_Topic2ComprehensiveApplication 綜合應用 - 平行四邊形性質與座標
        # RAG Example Mapping: 類似於利用中點公式或向量性質求解第四點的題目
        
        while True:
            x1_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y1_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            x2_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y2_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            x3_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)
            y3_data = _generate_coordinate_value(is_fraction=random.choice([True, False]), min_val=-6, max_val=6)

            A = (x1_data[0], y1_data[0])
            B = (x2_data[0], y2_data[0])
            C = (x3_data[0], y3_data[0])

            # 確保三點不共線
            # 使用向量 AB 和 AC 的叉積判斷
            if abs((B[0]-A[0])*(C[1]-A[1]) - (B[1]-A[1])*(C[0]-A[0])) < 1e-6:
                continue # 重新生成，如果點共線

            # 平行四邊形 ABCD 的第四點 D
            # 根據向量性質，AD = BC => D = A + C - B
            Dx_float = A[0] + C[0] - B[0]
            Dy_float = A[1] + C[1] - B[1]

            # 確保 D 點的座標在顯示範圍內，且 D 不與 A, B, C 重合
            if not (x_range[0] <= Dx_float <= x_range[1] and \
                    y_range[0] <= Dy_float <= y_range[1]):
                continue # 重新生成，如果 D 點超出範圍
            
            D_ans = (Dx_float, Dy_float)
            if D_ans in [A, B, C]:
                continue # 重新生成，如果 D 點與 A, B, C 重合

            break # 找到有效點集

        # 格式化顯示座標
        A_display = f"({_format_coordinate_display(x1_data)}, {_format_coordinate_display(y1_data)})"
        B_display = f"({_format_coordinate_display(x2_data)}, {_format_coordinate_display(y2_data)})"
        C_display = f"({_format_coordinate_display(x3_data)}, {_format_coordinate_display(y3_data)})"
        
        # V13.0, V13.5 整數優先：將浮點數格式化為整數或小數形式
        Dx_display = str(int(Dx_float)) if Dx_float.is_integer() else str(Dx_float)
        Dy_display = str(int(Dy_float)) if Dy_float.is_integer() else str(Dy_float)

        question_text = r"已知平面上三點 $A{A_disp}$, $B{B_disp}$, $C{C_disp}$ 為平行四邊形 $ABCD$ 的三個頂點。試求 $D$ 點的座標。".replace("{A_disp}", A_display).replace("{B_disp}", B_display).replace("{C_disp}", C_display)
        
        # correct_answer 必須為純數據列表，格式為 "x,y" (V13.1 答案格式標準化)
        correct_answer = f"{Dx_display},{Dy_display}"
        
        points_for_drawing = [
            (A[0], A[1], 'A'),
            (B[0], B[1], 'B'),
            (C[0], C[1], 'C')
            # D點不顯示在圖上，讓學生自己計算
        ]
        image_base64 = _draw_coordinate_plane(points_for_drawing, x_range, y_range)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 留空，待前端填充
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def check(user_answer: str, correct_answer: str) -> bool:
    """
    `check()` 函式必須具備強韌的閱卷邏輯，支援輸入清洗與多種數學格式的等價性判斷。
    針對座標格式 (x,y) 進行數值序列比對。
    """
    # CRITICAL RULE: Answer Data Purity - correct_answer is pure data.
    # CRITICAL RULE: Robust Check Logic - Input Sanitization using Regex.
    # V13.5 禁絕複雜比對 - 統一要求使用數字序列比對。

    # Regex to clean user input: remove non-numeric characters except for comma, dot, and minus sign.
    # This specifically targets coordinate formats like "x,y" or "(x,y)".
    cleaned_user_answer = re.sub(r'[^\d.,\-]', '', user_answer) 
    cleaned_correct_answer = re.sub(r'[^\d.,\-]', '', correct_answer)

    user_parts = []
    correct_parts = []
    
    try:
        # 將清洗後的字串按逗號分割，並嘗試轉換為浮點數
        user_parts = [float(p.strip()) for p in cleaned_user_answer.split(',') if p.strip()]
        correct_parts = [float(p.strip()) for p in cleaned_correct_answer.split(',') if p.strip()]
    except ValueError:
        # 如果任何部分無法轉換為浮點數，則視為格式錯誤，答案不正確
        return False

    # V12.6 結構鎖死 - 數值序列比對
    # 檢查答案部分的數量是否一致 (例如，座標應有 x 和 y 兩個部分)
    if len(user_parts) != len(correct_parts):
        return False

    # 使用容忍度比較每個數值部分，以處理浮點數精度問題
    tolerance = 1e-6
    for u, c in zip(user_parts, correct_parts):
        if abs(u - c) > tolerance:
            return False # 任何一個部分不匹配則答案錯誤
            
    return True # 所有部分都匹配則答案正確

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
