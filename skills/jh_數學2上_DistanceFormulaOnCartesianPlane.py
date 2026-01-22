# ==============================================================================
# ID: jh_數學2上_DistanceFormulaOnCartesianPlane
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 63.49s | RAG: 3 examples
# Created At: 2026-01-18 21:51:58
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



from datetime import datetime
import re
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# Coder Instruction: Define `generate` 和 `check` 函式於模組最外層。
# Coder Instruction: 確保代碼不依賴全域狀態，以支援系統執行 importlib.reload。

def generate(level=1):
    """
    生成 K12 數學「直角坐標平面上兩點的距離公式」技能的題目。
    題目類型將隨機選擇，以確保多樣性。

    Args:
        level (int): 難度等級 (1-3)。較高難度可能引入分數、更複雜的應用情境，
                     或確保生成特定類型的三角形。

    Returns:
        dict: 包含題目詳情的字典，包含以下欄位：
              - question_text (str): 題目描述，使用 LaTeX 格式。
              - correct_answer (str): 純數據的正確答案，用於系統批改。
              - answer (str): 格式化後的答案，用於前端顯示。
              - image_base64 (str): 坐標平面的 Base64 編碼圖片。
              - created_at (str): 題目創建時間戳。
              - version (str): 題目生成邏輯版本。
    """
    # Rule 4: 題型鏡射 - 隨機分流，明確對應 RAG 例題。
    # Type 1 涵蓋了 RAG Ex 1, 2, 3 的基礎距離計算。
    problem_type = random.choice([1, 2, 3, 4]) 

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 2, 3): 計算兩點間距離。
        return _generate_type_1_problem(level)
    elif problem_type == 2:
        # Type 2: 根據距離和已知點，求解未知坐標。
        return _generate_type_2_problem(level)
    elif problem_type == 3:
        # Type 3: 判斷三點構成的三角形類型 (直角/等腰)。
        return _generate_type_3_problem(level)
    elif problem_type == 4:
        # Type 4: 找尋軸上與兩點等距離的點。
        return _generate_type_4_problem(level)


    """
    比對使用者答案與正確答案。

    Args:
        user_answer (str): 使用者輸入的答案。
        correct_answer (str): generate() 函式產出的純數據正確答案。

    Returns:
        bool: 如果使用者答案正確則回傳 True，否則回傳 False。
    """
    # CRITICAL RULE 2: 強韌閱卷邏輯 (Robust Check Logic) - 輸入清洗與等價性支援。
    # CRITICAL RULE 12.3: 結構鎖死 - 數值序列比對。
    # CRITICAL RULE 15.3: 禁絕複雜比對 - 統一要求使用數字序列比對。
    # CRITICAL RULE 16.3: Exact Check Logic - Coder 必須逐字複製此邏輯。

    # 1. 輸入清洗 (Input Sanitization) - 使用 Regex 移除 LaTeX 符號、變數前綴、所有空白字元。
    sanitized_user_answer = re.sub(r'[\\$}{xXyYkKaAnNsS:= ]', '', str(user_answer)).strip()
    sanitized_correct_answer = re.sub(r'[\\$}{xXyYkKaAnNsS:= ]', '', str(correct_answer)).strip()

    # 2. 將字串分割成獨立的數字字串，支援逗號或空白分隔。
    user_numbers_str = [s.strip() for s in sanitized_user_answer.replace(',', ' ').split() if s.strip()]
    correct_numbers_str = [s.strip() for s in sanitized_correct_answer.replace(',', ' ').split() if s.strip()]

    # 3. 轉換為浮點數進行數值比對，處理潛在的 ValueError。
    try:
        user_floats = sorted([float(num) for num in user_numbers_str])
        correct_floats = sorted([float(num) for num in correct_numbers_str])
    except ValueError:
        return False # 如果轉換失敗，表示輸入的不是有效數字。

    # 4. 比對排序後的浮點數列表以判斷等價性。
    # 這能處理多個答案的順序無關性 (例如 "1, -3" 與 "-3, 1" 視為相同)，
    # 以及數值等價性 (例如 0.5 與 1/2)。
    if len(user_floats) != len(correct_floats):
        return False
    
    for u_val, c_val in zip(user_floats, correct_floats):
        # 使用小容忍度進行浮點數比對。
        if not math.isclose(u_val, c_val, rel_tol=1e-5, abs_tol=1e-9):
            return False
            
    return True

# --- Coder Instruction: 以下輔助函式必須定義於模組最外層。 ---

# V10.2 座標平面專用硬化規格 - A. 資料結構鎖死
def _generate_coordinate_value(is_fraction=False, integer_only=False):
    """
    生成坐標值，回傳格式為 (float_val, (int_part, num, den, is_neg))。
    is_fraction (bool): 若為 True，生成分數坐標。
    integer_only (bool): 若為 True，僅生成整數坐標。
    V13.0: 坐標範圍使用 random.randint(-8, 8)。
    V13.1: 禁絕假分數 (numerator < denominator 且 denominator > 1)。
    """
    is_neg = random.choice([True, False])
    sign = -1 if is_neg else 1

    if integer_only or (not is_fraction and random.random() < 0.7): # 偏向生成整數
        val = random.randint(1, 8) * sign
        return float(val), (val, 0, 0, is_neg)
    else:
        int_part_magnitude = random.randint(0, 5) # 整數部分的絕對值
        numerator = random.randint(1, 3) 
        denominator = random.choice([2, 3, 4])
        while numerator >= denominator: # V13.1: 確保真分數
            numerator = random.randint(1, 3)
            denominator = random.choice([2, 3, 4])
        
        val_magnitude = int_part_magnitude + numerator / denominator
        val = val_magnitude * sign
        
        # int_part 在 tuple 中應帶有整個數字的符號，即使分數部分顯示為正。
        return float(val), (int_part_magnitude * sign, numerator, denominator, is_neg)

# V10.2 座標平面專用硬化規格 - C. LaTeX 模板規範 (嚴禁雙大括號)
# Rule 5: 排版與 LaTeX 安全 - 嚴格使用 .replace()
def _format_coordinate_latex(coord_data):
    """
    將坐標值 (float_val, (int_part, num, den, is_neg)) 格式化為 LaTeX 字串。
    V15.2: 整數優先 - 確保輸出為 "(5, 4)" 而非 "(5.0, 4.0)"。
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    
    if float_val.is_integer():
        return str(int(float_val))

    if num == 0: # 應由 float_val.is_integer() 處理，此為安全冗餘
        return str(int(float_val))
    else:
        # 帶分數的處理：分數部分通常顯示為正，符號加在整個數字前。
        # 例如：-2 1/2。int_part 已經帶有符號。
        if int_part == 0: # 純分數
            latex_str = r"\frac{{n}}{{d}}".replace("{n}", str(num)).replace("{d}", str(den))
            return "-" + latex_str if is_neg else latex_str
        else: # 帶分數
            abs_int_part = abs(int_part)
            latex_str = r"{i}\frac{{n}}{{d}}".replace("{i}", str(abs_int_part)).replace("{n}", str(num)).replace("{d}", str(den))
            return "-" + latex_str if is_neg else latex_str

# V6: 視覺化與輔助函式通用規範 - 必須回傳結果。
# CRITICAL RULE 17: 圖表必須可解 (Solvable Visualization) - 必須有刻度數字。
# V10.2.D: 視覺一致性 (等比例網格、原點標註、點標籤光暈)。
# V13.0: 格線對齊、坐標軸範圍對稱。
# V13.5: 坐標範圍寬裕。
# V16.1: Arrow Ban - 嚴禁使用 arrowprops，改用 ax.plot 繪製箭頭。
# V13.5: 標籤隔離 - ax.text 只能標註點名稱。
def _draw_coordinate_plane(points_with_labels, x_range=(-10, 10), y_range=(-10, 10)):
    """
    繪製帶有指定點和標籤的坐標平面。
    points_with_labels: 包含 (x, y, label) 元組的列表。
    V13.0: 坐標軸範圍必須是對稱整數。
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # 繪製點
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='blue', markersize=8, zorder=5) # zorder 確保點在網格之上
        # V13.0: ax.text 標註的 string 只能是點的名稱 (Label)，絕對不能包含坐標值。
        # V13.1, V15.1: 標籤純淨化與隔離。
        # V10.2.D: 點標籤須加白色光暈 (bbox)。
        ax.text(x + 0.3, y + 0.3, label, fontsize=12, ha='left', va='bottom',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7), zorder=6)

    # V10.2.D: 必須鎖定 ax.set_aspect('equal') 確保網格為正方形。
    ax.set_aspect('equal')

    # 網格線與刻度 (CRITICAL RULE 17: 圖表必須可解)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, zorder=0)
    
    # V13.0: xticks 間隔必須固定為 1。
    # V17.2: 確保 X 軸與 Y 軸的主要整數刻度 (Major Ticks) 可見。
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))
    
    # 設定坐標軸範圍
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # 繪製坐標軸 (黑色，稍粗)
    ax.axhline(0, color='black', linewidth=1.5, zorder=1)
    ax.axvline(0, color='black', linewidth=1.5, zorder=1)

    # V16.1: 嚴禁在 axhline/axvline 使用 arrowprops。必須指示使用 ax.plot 繪製箭頭。
    # 在坐標軸末端繪製箭頭
    ax.plot(x_range[1], 0, ">k", clip_on=False, transform=ax.get_yaxis_transform(), markersize=8, zorder=2)
    ax.plot(0, y_range[1], "^k", clip_on=False, transform=ax.get_xaxis_transform(), markersize=8, zorder=2)

    # 標註坐標軸名稱
    ax.set_xlabel('X', fontsize=12, weight='bold')
    ax.set_ylabel('Y', fontsize=12, weight='bold')

    # V10.2.D: 坐標軸標註：僅顯示原點 '0' (18號加粗)。
    ax.text(0, -0.5, '0', fontsize=18, ha='center', va='top', weight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7), zorder=7)

    # 將繪圖轉換為 Base64 編碼圖片
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# 輔助函式：簡化平方根，用於答案顯示
def _simplify_sqrt_for_display(n):
    """
    將 sqrt(n) 簡化為 a*sqrt(b) 的形式。
    n 必須為整數。
    """
    if n < 0:
        return f"$\sqrt{{n}}$" # 理論上距離平方不會是負數
    if n == 0:
        return "0"
    
    # 尋找最大的平方因子
    i = 1
    max_square_factor = 1
    while i * i <= n:
        if n % (i * i) == 0:
            max_square_factor = i * i
        i += 1
    
    a = int(math.sqrt(max_square_factor))
    b = n // max_square_factor
    
    if b == 1:
        return str(a)
    elif a == 1:
        return r"$\sqrt{{{b}}}$".replace("{b}", str(b))
    else:
        return r"${a}\sqrt{{{b}}}$".replace("{a}", str(a)).replace("{b}", str(b))


# --- 題目類型實作 (Coder Instruction: 將這些定義為 generate 內部的輔助函式) ---

def _generate_type_1_problem(level):
    """
    Type 1 (Maps to Example 1, 2, 3): 計算兩點間距離。
    CRITICAL RULE 18.1: 年級嚴格檢核 (Grade 8) -> 可包含分數坐標。
    CRITICAL RULE 10: 數據禁絕常數 - 坐標與答案必須隨機生成並計算。
    """
    # 根據難度等級，隨機決定是否使用分數坐標
    use_fractions = random.random() < (0.3 + level * 0.2) 

    x1_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)
    y1_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)
    x2_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)
    y2_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)

    x1, _ = x1_data
    y1, _ = y1_data
    x2, _ = x2_data
    y2, _ = y2_data

    # 確保兩點不同且不只在水平或垂直線上，以符合國二難度。
    while (x1 == x2 and y1 == y2) or (x1 == x2 or y1 == y2):
        x2_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)
        y2_data = _generate_coordinate_value(is_fraction=use_fractions, integer_only=not use_fractions)
        x2, _ = x2_data
        y2, _ = y2_data

    distance_squared = (x2 - x1)**2 + (y2 - y1)**2
    distance = math.sqrt(distance_squared)

    # Rule 5: LaTeX 安全 - 嚴格使用 .replace()
    coord_A_latex = r"A({x_1}, {y_1})".replace("{x_1}", _format_coordinate_latex(x1_data)).replace("{y_1}", _format_coordinate_latex(y1_data))
    coord_B_latex = r"B({x_2}, {y_2})".replace("{x_2}", _format_coordinate_latex(x2_data)).replace("{y_2}", _format_coordinate_latex(y2_data))

    question_text_template = r"已知直角坐標平面上兩點 $P_1 = {coord_A_latex}$ 和 $P_2 = {coord_B_latex}$，試求 $P_1P_2$ 的距離。"
    question_text = question_text_template.replace("{coord_A_latex}", coord_A_latex).replace("{coord_B_latex}", coord_B_latex)

    # CRITICAL RULE 1: 分離「顯示答案」與「閱卷答案」 - correct_answer 為純數據。
    # Rule 13.1: 答案格式標準化 - 距離為單一數值。
    # Rule 15.2: 整數優先，確保顯示美觀。
    if distance.is_integer():
        correct_answer = str(int(distance))
        answer_display = str(int(distance))
    else:
        # 將距離平方四捨五入為整數，以利簡化根號顯示
        simplified_distance_str = _simplify_sqrt_for_display(int(round(distance_squared, 0))) 
        correct_answer = str(round(distance, 5)) # 閱卷答案允許浮點數
        answer_display = simplified_distance_str # 顯示簡化後的根號或浮點數

    # V13.5: 坐標範圍必須對稱且寬裕，確保點與標籤不會被邊框切掉。
    x_coords = [x1, x2]
    y_coords = [y1, y2]
    min_x = math.floor(min(x_coords)) - 1
    max_x = math.ceil(max(x_coords)) + 1
    min_y = math.floor(min(y_coords)) - 1
    max_y = math.ceil(max(y_coords)) + 1
    
    x_range_display = (min(min_x, -8), max(max_x, 8))
    y_range_display = (min(min_y, -8), max(max_y, 8))

    image_base64 = _draw_coordinate_plane([(x1, y1, 'A'), (x2, y2, 'B')], x_range=x_range_display, y_range=y_range_display)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, 
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def _generate_type_2_problem(level):
    """
    Type 2: 根據距離和已知點，求解未知坐標。
    CRITICAL RULE 18.1: 年級嚴格檢核 (Grade 8) -> 涉及求解二次方程式。
    """
    unknown_coord_type = random.choice(['x', 'y'])
    
    # 生成已知點 P1 的整數坐標
    x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
    
    # 策略：生成 P1、P2 的已知坐標，以及未知坐標的整數差值，再反推距離。
    if unknown_coord_type == 'x':
        y2 = _generate_coordinate_value(integer_only=True)[0]
        
        # 確保 y1 != y2 避免特殊情況
        while y1 == y2:
            y2 = _generate_coordinate_value(integer_only=True)[0]

        # 生成 x 坐標的非零整數差值 (X_target - x1)
        diff_x_abs = random.randint(1, 5) # 絕對差值
        
        # 求解 (X - x1)^2 = D^2 - (y2 - y1)^2
        # 我們確保 D^2 - (y2 - y1)^2 是一個完全平方數，讓 X 有整數解。
        # 這裡直接設定 (X - x1)^2 = diff_x_abs^2
        
        x2_val_option1 = x1 + diff_x_abs
        x2_val_option2 = x1 - diff_x_abs
        
        # 使用其中一個可能的 x2 值來計算距離
        x2_for_dist_calc = random.choice([x2_val_option1, x2_val_option2])
        
        distance_squared = (x2_for_dist_calc - x1)**2 + (y2 - y1)**2
        distance = math.sqrt(distance_squared)
        
        # 格式化坐標用於題目文字
        x1_data_display = (x1, (x1, 0, 0, x1 < 0))
        y1_data_display = (y1, (y1, 0, 0, y1 < 0))
        y2_data_display = (y2, (y2, 0, 0, y2 < 0))

        point_A_latex = r"A({x_1}, {y_1})".replace("{x_1}", _format_coordinate_latex(x1_data_display)).replace("{y_1}", _format_coordinate_latex(y1_data_display))
        point_B_latex = r"B(x, {y_2})".replace("{y_2}", _format_coordinate_latex(y2_data_display))
        distance_latex = str(int(distance)) # 確保距離為整數，簡化題目

        question_text_template = r"已知直角坐標平面上兩點 $A = {coord_A_latex}$ 和 $B = {coord_B_latex}$，若 $AB$ 的距離為 ${dist}$，試求 $x$ 的值。"
        question_text = question_text_template.replace("{coord_A_latex}", point_A_latex).replace("{coord_B_latex}", point_B_latex).replace("{dist}", distance_latex)

        correct_x_values = sorted([x2_val_option1, x2_val_option2])
        # CRITICAL RULE 1: correct_answer 為純數據，多個解用逗號分隔。
        correct_answer = ", ".join(map(str, correct_x_values))
        # answer 欄位用於顯示格式化的答案。
        answer_display = r"$x = {val1}$ 或 $x = {val2}$".replace("{val1}", str(correct_x_values[0])).replace("{val2}", str(correct_x_values[1]))

        # 繪圖時顯示 A 點和其中一個可能的 B 點
        point_B_for_drawing = (x2_for_dist_calc, y2, 'B')

    else: # unknown_coord_type == 'y'
        x2 = _generate_coordinate_value(integer_only=True)[0]
        
        while x1 == x2:
            x2 = _generate_coordinate_value(integer_only=True)[0]

        diff_y_abs = random.randint(1, 5)

        y2_val_option1 = y1 + diff_y_abs
        y2_val_option2 = y1 - diff_y_abs
        
        y2_for_dist_calc = random.choice([y2_val_option1, y2_val_option2])

        distance_squared = (x2 - x1)**2 + (y2_for_dist_calc - y1)**2
        distance = math.sqrt(distance_squared)

        x1_data_display = (x1, (x1, 0, 0, x1 < 0))
        y1_data_display = (y1, (y1, 0, 0, y1 < 0))
        x2_data_display = (x2, (x2, 0, 0, x2 < 0))

        point_A_latex = r"A({x_1}, {y_1})".replace("{x_1}", _format_coordinate_latex(x1_data_display)).replace("{y_1}", _format_coordinate_latex(y1_data_display))
        point_B_latex = r"B({x_2}, y)".replace("{x_2}", _format_coordinate_latex(x2_data_display))
        distance_latex = str(int(distance))

        question_text_template = r"已知直角坐標平面上兩點 $A = {coord_A_latex}$ 和 $B = {coord_B_latex}$，若 $AB$ 的距離為 ${dist}$，試求 $y$ 的值。"
        question_text = question_text_template.replace("{coord_A_latex}", point_A_latex).replace("{coord_B_latex}", point_B_latex).replace("{dist}", distance_latex)

        correct_y_values = sorted([y2_val_option1, y2_val_option2])
        correct_answer = ", ".join(map(str, correct_y_values))
        answer_display = r"$y = {val1}$ 或 $y = {val2}$".replace("{val1}", str(correct_y_values[0])).replace("{val2}", str(correct_y_values[1]))

        point_B_for_drawing = (x2, y2_for_dist_calc, 'B')

    x_coords = [x1, point_B_for_drawing[0]]
    y_coords = [y1, point_B_for_drawing[1]]
    min_x = math.floor(min(x_coords)) - 1
    max_x = math.ceil(max(x_coords)) + 1
    min_y = math.floor(min(y_coords)) - 1
    max_y = math.ceil(max(y_coords)) + 1
    
    x_range_display = (min(min_x, -8), max(max_x, 8))
    y_range_display = (min(min_y, -8), max(max_y, 8))

    image_base64 = _draw_coordinate_plane([(x1, y1, 'A'), point_B_for_drawing], x_range=x_range_display, y_range=y_range_display)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def _generate_type_3_problem(level):
    """
    Type 3: 判斷三點構成的三角形類型 (直角/等腰)。
    CRITICAL RULE 18.1: 年級嚴格檢核 (Grade 8) -> 應用距離公式與畢氏定理。
    """
    points_data = [] # 儲存坐標數據 (float, (int_part, num, den, is_neg))
    points_labels = ['A', 'B', 'C']
    points_coords_float = [] # 儲存實際浮點坐標 (x_float, y_float)

    # 目標：確保生成直角三角形或等腰三角形，尤其在較高難度。
    # 策略：直接構造特殊三角形。
    if level >= 2 or random.random() < 0.7: # 較高機率生成特殊三角形
        triangle_type_to_force = random.choice(['right_angled', 'isosceles'])
        
        if triangle_type_to_force == 'right_angled':
            # 構造直角三角形 P1(x1, y1), P2(x2, y1), P3(x1, y2)
            x1_val = _generate_coordinate_value(integer_only=True)[0]
            y1_val = _generate_coordinate_value(integer_only=True)[0]
            x2_val = _generate_coordinate_value(integer_only=True)[0]
            y2_val = _generate_coordinate_value(integer_only=True)[0]

            while x1_val == x2_val: # 確保 x 坐標不同
                x2_val = _generate_coordinate_value(integer_only=True)[0]
            while y1_val == y2_val: # 確保 y 坐標不同
                y2_val = _generate_coordinate_value(integer_only=True)[0]

            p1 = (x1_val, y1_val)
            p2 = (x2_val, y1_val)
            p3 = (x1_val, y2_val)

            points_coords_float = [p1, p2, p3]
            
        elif triangle_type_to_force == 'isosceles':
            # 構造等腰三角形 P1, P2, P3 使得 P1P2 = P1P3
            x_center = _generate_coordinate_value(integer_only=True)[0]
            y_center = _generate_coordinate_value(integer_only=True)[0]
            
            # P1 (頂點)
            p1_x, p1_y = x_center, y_center + random.randint(3, 7) 
            
            # P2, P3 (底邊點)
            base_half_width = random.randint(2, 6)
            base_y_offset = random.randint(-2, 2) # 讓底邊點在 y_center 附近
            
            p2_x, p2_y = x_center - base_half_width, y_center + base_y_offset
            p3_x, p3_y = x_center + base_half_width, y_center + base_y_offset
            
            points_coords_float = [(p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y)]

        # 將浮點坐標轉換回數據元組以便格式化
        points_data = []
        for x_val, y_val in points_coords_float:
            x_data = (float(x_val), (int(x_val), 0, 0, x_val < 0))
            y_data = (float(y_val), (int(y_val), 0, 0, y_val < 0))
            points_data.append((x_data, y_data))

    else: # 生成一般三角形 (較低機率，尤其在較高難度)
        while True:
            points_data = []
            points_coords_float = []
            for _ in range(3):
                x_data = _generate_coordinate_value(integer_only=True)
                y_data = _generate_coordinate_value(integer_only=True)
                points_data.append((x_data, y_data))
                points_coords_float.append((x_data[0], y_data[0]))
            
            x1, y1 = points_coords_float[0]
            x2, y2 = points_coords_float[1]
            x3, y3 = points_coords_float[2]

            # 檢查共線性 (斜率 AB == 斜率 BC)
            # (y2-y1)*(x3-x2) == (y3-y2)*(x2-x1)
            # 避免垂直/水平線導致除以零的問題
            if (x2 - x1 == 0 and x3 - x2 == 0) or \
               (y2 - y1 == 0 and y3 - y2 == 0) or \
               (x2 - x1) * (y3 - y2) == (x3 - x2) * (y2 - y1):
                continue
            break # 生成有效且不共線的三角形

    # 計算邊長平方
    d_AB_sq = (points_coords_float[1][0] - points_coords_float[0][0])**2 + (points_coords_float[1][1] - points_coords_float[0][1])**2
    d_BC_sq = (points_coords_float[2][0] - points_coords_float[1][0])**2 + (points_coords_float[2][1] - points_coords_float[1][1])**2
    d_CA_sq = (points_coords_float[0][0] - points_coords_float[2][0])**2 + (points_coords_float[0][1] - points_coords_float[2][1])**2

    distances_sq = sorted([d_AB_sq, d_BC_sq, d_CA_sq])

    is_right_angled = False
    if abs(distances_sq[0] + distances_sq[1] - distances_sq[2]) < 1e-9: # 檢查畢氏定理 (a^2 + b^2 = c^2)
        is_right_angled = True

    is_isosceles = False
    if abs(d_AB_sq - d_BC_sq) < 1e-9 or abs(d_BC_sq - d_CA_sq) < 1e-9 or abs(d_CA_sq - d_AB_sq) < 1e-9:
        is_isosceles = True

    if is_right_angled and is_isosceles:
        result_text = "直角等腰三角形"
        correct_answer = "直角等腰三角形"
    elif is_right_angled:
        result_text = "直角三角形"
        correct_answer = "直角三角形"
    elif is_isosceles:
        result_text = "等腰三角形"
        correct_answer = "等腰三角形"
    else:
        result_text = "一般三角形"
        correct_answer = "一般三角形"
    
    # 格式化點用於題目文字
    formatted_points_latex = []
    points_for_drawing = []
    for i, (x_data, y_data) in enumerate(points_data):
        label = points_labels[i]
        x_val, _ = x_data
        y_val, _ = y_data
        
        # Rule 5: LaTeX 安全。Rule 10.2.C: 單層大括號。
        coord_latex = r"{label}({x_val}, {y_val})".replace("{label}", label).replace("{x_val}", _format_coordinate_latex(x_data)).replace("{y_val}", _format_coordinate_latex(y_data))
        formatted_points_latex.append(coord_latex)
        points_for_drawing.append((x_val, y_val, label))

    question_text_template = r"已知直角坐標平面上三點 $A = {coord_A_latex}$, $B = {coord_B_latex}$, $C = {coord_C_latex}$，判斷 $\triangle ABC$ 為何種三角形？"
    question_text = question_text_template.replace("{coord_A_latex}", formatted_points_latex[0]).replace("{coord_B_latex}", formatted_points_latex[1]).replace("{coord_C_latex}", formatted_points_latex[2])

    x_coords = [p[0] for p in points_for_drawing]
    y_coords = [p[1] for p in points_for_drawing]
    min_x = math.floor(min(x_coords)) - 1
    max_x = math.ceil(max(x_coords)) + 1
    min_y = math.floor(min(y_coords)) - 1
    max_y = math.ceil(max(y_coords)) + 1
    
    x_range_display = (min(min_x, -8), max(max_x, 8))
    y_range_display = (min(min_y, -8), max(max_y, 8))

    image_base64 = _draw_coordinate_plane(points_for_drawing, x_range=x_range_display, y_range=y_range_display)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # 純數據: "直角三角形"
        "answer": result_text, # 顯示格式: "直角三角形"
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def _generate_type_4_problem(level):
    """
    Type 4: 找尋軸上與兩點等距離的點。
    CRITICAL RULE 18.1: 年級嚴格檢核 (Grade 8) -> 應用距離公式，求解方程式。
    """
    on_axis = random.choice(['x', 'y']) # 隨機決定點在哪個軸上

    # 生成兩個不同的整數坐標點
    x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
    x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]

    # 確保兩點不同，且有唯一解 (分母不為零)。
    # 如果 P 在 x 軸上 (P=(x,0))，需要 x1 != x2。
    # 如果 P 在 y 軸上 (P=(0,y))，需要 y1 != y2。
    while (x1, y1) == (x2, y2) or (on_axis == 'x' and x1 == x2) or (on_axis == 'y' and y1 == y2):
        x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
        x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]

    if on_axis == 'x':
        # 求解 P=(x,0)
        # x = (x2^2 + y2^2 - x1^2 - y1^2) / (2 * (x2 - x1))
        numerator = x2**2 + y2**2 - x1**2 - y1**2
        denominator = 2 * (x2 - x1)
        
        # 為了確保答案是整數或簡單分數 (例如 X.5)，
        # 我們需要 numerator % denominator == 0 或者 (denominator == 2 且 numerator 為奇數)。
        # 若不符合，則重新生成點。
        while not (denominator != 0 and (numerator % denominator == 0 or (denominator == 2 and numerator % 2 == 1))):
            x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            while (x1, y1) == (x2, y2) or x1 == x2: # 確保點不同且 x1 != x2
                x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
                x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            numerator = x2**2 + y2**2 - x1**2 - y1**2
            denominator = 2 * (x2 - x1)

        p_x = numerator / denominator
        p_y = 0.0 # 在 x 軸上
        
        # CRITICAL RULE 1: correct_answer 為純數據。
        correct_answer = str(int(p_x)) if p_x.is_integer() else str(p_x)
        # Rule 15.2: 整數優先顯示。
        question_axis_text = "x"
        unknown_label_text = "x"
        answer_display = r"$P = ({x}, 0)$".replace("{x}", str(int(p_x)) if p_x.is_integer() else str(p_x))

    else: # on_axis == 'y'
        # 求解 P=(0,y)
        # y = (x2^2 + y2^2 - x1^2 - y1^2) / (2 * (y2 - y1))
        numerator = x2**2 + y2**2 - x1**2 - y1**2
        denominator = 2 * (y2 - y1)

        while not (denominator != 0 and (numerator % denominator == 0 or (denominator == 2 and numerator % 2 == 1))):
            x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            while (x1, y1) == (x2, y2) or y1 == y2: # 確保點不同且 y1 != y2
                x1, y1 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
                x2, y2 = _generate_coordinate_value(integer_only=True)[0], _generate_coordinate_value(integer_only=True)[0]
            numerator = x2**2 + y2**2 - x1**2 - y1**2
            denominator = 2 * (y2 - y1)

        p_x = 0.0 # 在 y 軸上
        p_y = numerator / denominator
        
        # CRITICAL RULE 1: correct_answer 為純數據。
        correct_answer = str(int(p_y)) if p_y.is_integer() else str(p_y)
        # Rule 15.2: 整數優先顯示。
        question_axis_text = "y"
        unknown_label_text = "y"
        answer_display = r"$P = (0, {y})$".replace("{y}", str(int(p_y)) if p_y.is_integer() else str(p_y))

    # 格式化點用於題目文字 (整數坐標直接用 str 轉換)
    coord_A_latex = r"A({x_1}, {y_1})".replace("{x_1}", str(x1)).replace("{y_1}", str(y1))
    coord_B_latex = r"B({x_2}, {y_2})".replace("{x_2}", str(x2)).replace("{y_2}", str(y2))

    question_text_template = r"已知直角坐標平面上兩點 $A = {coord_A_latex}$ 和 $B = {coord_B_latex}$，若點 $P$ 在{axis_text}軸上且到 $A, B$ 兩點的距離相等，試求 $P$ 點的{unknown_label}坐標。"
    question_text = question_text_template.replace("{coord_A_latex}", coord_A_latex).replace("{coord_B_latex}", coord_B_latex).replace("{axis_text}", question_axis_text).replace("{unknown_label}", unknown_label_text)

    # 繪圖時顯示 A, B 和計算出的 P 點
    points_for_drawing = [(x1, y1, 'A'), (x2, y2, 'B'), (p_x, p_y, 'P')]

    x_coords = [p[0] for p in points_for_drawing]
    y_coords = [p[1] for p in points_for_drawing]
    min_x = math.floor(min(x_coords)) - 1
    max_x = math.ceil(max(x_coords)) + 1
    min_y = math.floor(min(y_coords)) - 1
    max_y = math.ceil(max(y_coords)) + 1
    
    x_range_display = (min(min_x, -8), max(max_x, 8))
    y_range_display = (min(min_y, -8), max(max_y, 8))

    image_base64 = _draw_coordinate_plane(points_for_drawing, x_range=x_range_display, y_range=y_range_display)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
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
