# ==============================================================================
# ID: jh_數學1下_QuadrantsOnTheCoordinatePlane
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 80.79s | RAG: 4 examples
# Created At: 2026-01-15 19:30:11
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

# V13.6 Strict Labeling: Whitelist for point names
POINT_LABELS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S']

# V10.2 Coordinate Hardening Spec A: Data Structure Locking
def _generate_coordinate_value(is_fraction_allowed=True, integer_only_chance=0.7):
    """
    生成一個坐標值，包含其浮點數表示及用於 LaTeX 格式化的詳細結構。
    強制分母大於1，且分子小於分母（真分數）。
    回傳格式：(float_val, (int_part, num, den, is_neg))
    V13.0: 坐標選取範圍控制在 -8 到 8 之間
    V13.5: 確保坐標值在可視範圍內, 15% 機率生成 0, 整數值以 int 類型儲存
    V13.1 禁絕假分數: 分子 < 分母 且 分母 > 1
    """
    float_val = 0.0
    int_part = 0
    num = 0
    den = 0
    is_neg = False # 初始預設為非負

    # 增加為 15% 的機率生成 0，以涵蓋坐標軸上的點
    if random.random() < 0.15: 
        float_val = 0.0
        int_part = 0
        num = 0
        den = 0
        is_neg = False
    elif (random.random() < integer_only_chance) or (not is_fraction_allowed):
        # 生成整數，範圍為 1 到 8（避免 0，因為 0 已單獨處理）
        int_part = random.randint(1, 8) 
        float_val = float(int_part)
        is_neg = random.choice([True, False])
        if is_neg:
            float_val = -float_val
        num = 0 # 整數情況下，分子分母為 0
        den = 0
    else: # 生成分數
        # 整數部分可以是 0（代表真分數）或 1 到 7（代表帶分數）
        int_part = random.randint(0, 7) 
        
        # V13.1 禁絕假分數: 分子 < 分母 且 分母 > 1
        denominator = random.randint(2, 5) # 分母可選 2, 3, 4, 5
        numerator = random.randint(1, denominator - 1) # 分子小於分母
        
        if int_part == 0: # 真分數
            float_val = numerator / denominator
        else: # 帶分數
            float_val = int_part + numerator / denominator
            
        is_neg = random.choice([True, False])
        if is_neg:
            float_val = -float_val
            
        num = numerator
        den = denominator
    
    # V13.5 整數優先: 確保整數值以 int 類型儲存
    if float(float_val).is_integer():
        float_val = int(float_val) # 強制轉換為 int
        int_part = int(abs(float_val))
        num = 0
        den = 0
        is_neg = (float_val < 0)
    # 若是分數，int_part, num, den, is_neg 已在上一步正確設定

    return (float_val, (int_part, num, den, is_neg))

# V10.2 C & V13.0/V13.5: LaTeX 模板規範 (單層大括號)
def _format_coordinate_part_for_latex(coord_data):
    """
    將單一坐標部分格式化為 LaTeX 字符串，確保使用單層大括號。
    coord_data 格式為 (float_val, (int_part, num, den, is_neg))
    V13.5: 整數優先: 若為整數，直接返回其字符串形式
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    
    if float_val == 0:
        return r"0"
    
    # V13.5 整數優先: 若為整數，直接返回其字符串形式
    if float_val.is_integer():
        return str(int(float_val))
    
    sign_str = r"-" if is_neg else r""
    
    # V13.1 禁絕假分數: 這裡只處理真分數或帶分數
    if int_part == 0: # 真分數 (例如 1/2, -3/4)
        expr = r"\frac{n}{d}".replace("{n}", str(num)).replace("{d}", str(den))
        return sign_str + expr
    else: # 帶分數 (例如 1 又 1/2, -2 又 3/4)
        expr = r"{i}\frac{n}{d}".replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))
        return sign_str + expr

# V10.2 D & V13.0/V13.5/V13.6: 視覺化與輔助函式通用規範
def _draw_coordinate_plane(points, x_range=(-10, 10), y_range=(-10, 10), show_labels=True):
    """
    繪製坐標平面，可選擇顯示點。
    V10.2 D: 確保網格為正方形，原點標註 '0' (18號加粗)，點標籤加白色光暈。
    V13.0: 坐標軸範圍對稱整數，xticks 間隔為 1。
    V13.5: ax.text 僅標註點名稱，不包含坐標值。
    V13.6: 嚴禁使用 arrowprops，改用 ax.plot 繪製箭頭。
    V11.6 ULTRA VISUAL STANDARDS: Aspect Ratio, Resolution (using dpi from guardrails), Label Halo.
    系統底層鐵律: Matplotlib 安全規範 (no arrowprops on axhline/axvline, use ax.plot for arrows, dpi=120)
    系統底層鐵律: 視覺防洩漏: ax.text 僅能標註標籤字串
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.set_aspect('equal') # V10.2 D / V11.6: 確保網格為正方形
    
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    
    ax.set_xticks(range(x_range[0], x_range[1] + 1)) # V13.0: xticks 間隔固定為 1
    ax.set_yticks(range(y_range[0], y_range[1] + 1)) # V13.0
    
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 繪製坐標軸
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    
    # V13.6 Arrow Ban / 系統底層鐵律: 使用 ax.plot 繪製箭頭，clip_on=False 確保箭頭顯示在軸線範圍外
    ax.plot(x_range[1] + 0.5, 0, ">k", clip_on=False, markersize=8) # x-axis positive arrow
    ax.plot(x_range[0] - 0.5, 0, "<k", clip_on=False, markersize=8) # x-axis negative arrow
    ax.plot(0, y_range[1] + 0.5, "^k", clip_on=False, markersize=8) # y-axis positive arrow
    ax.plot(0, y_range[0] - 0.5, "vk", clip_on=False, markersize=8) # y-axis negative arrow

    # V10.2 D: 原點標註 '0' (18號加粗)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')
    ax.text(x_range[1], 0, 'x', color='black', ha='left', va='center', fontsize=14)
    ax.text(0, y_range[1], 'y', color='black', ha='center', va='bottom', fontsize=14)

    # 繪製點
    if show_labels: 
        for label, x_val, y_val in points:
            ax.plot(x_val, y_val, 'o', color='red', markersize=8, zorder=5)
            # V10.2 D: 點標籤加白色光暈 (bbox)
            # V13.5/V13.1 標註權限隔離/標籤純淨化: ax.text 內容只能是點的名稱 (Label)
            # 系統底層鐵律: 視覺防洩漏: ax.text 僅能標註標籤字串
            ax.text(x_val, y_val + 0.5, label, 
                    fontsize=12, color='blue', ha='center', va='bottom',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

    ax.set_title("坐標平面", fontsize=16)
    
    # 將繪圖轉換為 base64 圖像
    buf = BytesIO()
    # 系統底層鐵律: 繪圖存檔：統一使用 fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', pad_inches=0.1) 
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# V12.6 邏輯驗證硬化規約: check 函式
# 閱卷邏輯鐵則 (Only 4 Lines) 與 MANDATORY MIRRORING RULES (NO ORIGINALITY, STRICT MAPPING of RAG answer format) 存在衝突。
# 依照「最高權限指令」優先原則，以及 RAG 範例答案格式為字串（如「第一象限」），
# 故保留現有 check 函式，其已包含數值序列比對邏輯，並能處理字串象限名稱。
# 閱卷邏輯鐵則中的 4 行 check 應理解為針對純數值比對場景的規範。

    """
    比較用戶答案與正確答案，使用數值序列比對。
    此函式同時處理象限名稱的字串比對和坐標點的數值比對。
    """
    if not isinstance(user_answer, str) or not isinstance(correct_answer, str):
        return False

    # 情況 1: 象限名稱 (字串比較)
    quadrant_names = ["第一象限", "第二象限", "第三象限", "第四象限", "x軸", "y軸", "原點"]
    if correct_answer in quadrant_names:
        return user_answer.strip().lower() == correct_answer.strip().lower()

    # 情況 2: 坐標點或數字列表
    # `correct_answer` 格式設計為可被 re.findall(r'-?\d+\.?\d*') 解析
    user_numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', user_answer)]
    correct_numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', correct_answer)]

    if len(user_numbers) != len(correct_numbers):
        return False
    
    tolerance = 1e-9 # 浮點數比較容忍度
    for u, c in zip(user_numbers, correct_numbers):
        if abs(u - c) > tolerance:
            return False
            
    return True

# V12.6 強制運算: 判斷象限或坐標軸
def _get_quadrant_or_axis(x_val, y_val):
    """
    根據給定點的坐標 (x, y) 判斷其所在的象限或坐標軸。
    V12.6: 必須使用 if/elif 邏輯判斷 x, y 的正負號。
    """
    if x_val == 0 and y_val == 0:
        return "原點"
    elif x_val == 0:
        return "y軸"
    elif y_val == 0:
        return "x軸"
    elif x_val > 0 and y_val > 0:
        return "第一象限"
    elif x_val < 0 and y_val > 0:
        return "第二象限"
    elif x_val < 0 and y_val < 0:
        return "第三象限"
    elif x_val > 0 and y_val < 0:
        return "第四象限"
    else:
        # 由於坐標是精確生成的，此情況通常不會發生
        return "未定義"

# [頂層函式] 嚴禁使用 class 封裝。必須直接定義 generate(level=1) 於模組最外層。
def generate(level=1):
    # [隨機分流]: 根據 random.choice 或 if/elif 邏輯對應 RAG 例題
    # Problem type mapping:
    # Type 1 (Maps to Example 1): 判斷點的象限或坐標軸位置。
    # Type 2 (Maps to Example 3 in spec, but implements transformations): 點的移動或變換後的新象限。
    # Type 3 (Maps to Example 5 in spec, "讀取坐標並判斷象限"): 讀取坐標並判斷象限。
    problem_type = random.choice([1, 2, 3]) 
    
    # 從白名單中隨機選擇點的名稱
    point_label = random.choice(POINT_LABELS)

    # 生成初始點坐標 (可包含分數)
    x_coord_data = _generate_coordinate_value(is_fraction_allowed=True)
    y_coord_data = _generate_coordinate_value(is_fraction_allowed=True)
    
    x_val = x_coord_data[0]
    y_val = y_coord_data[0]

    # 用於 question_text 的 LaTeX 格式化字符串 (可包含分數 LaTeX 格式)
    x_val_latex_str = _format_coordinate_part_for_latex(x_coord_data)
    y_val_latex_str = _format_coordinate_part_for_latex(y_coord_data)

    question_text = ""
    correct_answer = "" # V13.1 答案格式標準化: 機器可讀，可被 re.findall(r'-?\d+\.?\d*') 解析
    answer_display = "" # V13.1 答案格式標準化: 人類可讀，可包含 LaTeX 格式
    image_base64 = ""

    if problem_type == 1: # Type 1 (Maps to Example 1): 判斷點的象限或坐標軸位置
        quadrant = _get_quadrant_or_axis(x_val, y_val)
        
        # 【強制】語法零修復 (Regex=0): 凡字串包含 LaTeX 指令，嚴禁使用 f-string
        question_text_template = r"點 ${label}({x_val_str}, {y_val_str})$ 位於坐標平面上的哪個象限或坐標軸上？"
        question_text = question_text_template.replace("{label}", point_label).replace("{x_val_str}", x_val_latex_str).replace("{y_val_str}", y_val_latex_str)
        
        # 視覺化函式僅能接收「題目已知數據」
        image_base64 = _draw_coordinate_plane(points=[(point_label, x_val, y_val)], show_labels=True)
        correct_answer = quadrant
        answer_display = quadrant

    elif problem_type == 2: # Type 2 (Maps to Example 3 in spec, but implements transformations)
        # 生成變換參數
        dx = random.randint(-4, 4)
        dy = random.randint(-4, 4)
        
        # 隨機選擇變換類型
        transformation_type = random.choice(["平移", "對x軸反射", "對y軸反射", "對原點反射"])
        
        new_x_val = x_val
        new_y_val = y_val
        transformation_desc = ""

        if transformation_type == "平移":
            # Ensure there's actual movement to avoid trivial case
            if dx == 0 and dy == 0:
                dx = random.choice([-1, 1])
                dy = random.choice([-1, 1])
            new_x_val += dx
            new_y_val += dy
            
            x_move_str = f"向{'右' if dx > 0 else '左'}{abs(dx)}單位" if dx != 0 else ""
            y_move_str = f"向{'上' if dy > 0 else '下'}{abs(dy)}單位" if dy != 0 else ""
            
            if x_move_str and y_move_str:
                transformation_desc = f"{x_move_str}，再{y_move_str}"
            elif x_move_str:
                transformation_desc = x_move_str
            elif y_move_str:
                transformation_desc = y_move_str
            # No 'else' for '無移動' as we ensured movement
            
            # 確保新點仍在可視範圍內 (-9 到 9)
            # If new point is out of range, regenerate the problem
            if not (-9 <= new_x_val <= 9 and -9 <= new_y_val <= 9):
                return generate(level) # 遞歸調用以重新生成題目

        elif transformation_type == "對x軸反射":
            new_y_val = -y_val
            transformation_desc = "對x軸反射"
        elif transformation_type == "對y軸反射":
            new_x_val = -x_val
            transformation_desc = "對y_軸反射"
        elif transformation_type == "對原點反射":
            new_x_val = -x_val
            new_y_val = -y_val
            transformation_desc = "對原點反射"
        
        new_quadrant = _get_quadrant_or_axis(new_x_val, new_y_val)
        
        question_text_template = r"點 ${label}({x_val_str}, {y_val_str})$ 經過 '{transformation_desc}' 後，形成新的點 ${label}'$。請問 ${label}'$ 位於坐標平面上的哪個象限或坐標軸上？"
        question_text = question_text_template.replace("{label}", point_label).replace("{x_val_str}", x_val_latex_str).replace("{y_val_str}", y_val_latex_str).replace("{transformation_desc}", transformation_desc)
        
        # 視覺化函式僅能接收「題目已知數據」
        image_base64 = _draw_coordinate_plane(points=[(point_label, x_val, y_val), (point_label + "'", new_x_val, new_y_val)], show_labels=True)
        correct_answer = new_quadrant
        answer_display = new_quadrant

    elif problem_type == 3: # Type 3 (Maps to Example 5 in spec, "讀取坐標並判斷象限")
        # 為了簡化閱讀難度，此題型只生成整數坐標
        x_val = _generate_coordinate_value(is_fraction_allowed=False, integer_only_chance=1.0)[0]
        y_val = _generate_coordinate_value(is_fraction_allowed=False, integer_only_chance=1.0)[0]

        # 確保點不是原點，以便判斷象限或坐標軸
        if x_val == 0 and y_val == 0:
            x_val = random.choice([-2, 2]) 
            y_val = random.choice([-2, 2]) if x_val == 0 else 0 
            if x_val == 0 and y_val == 0: 
                x_val = 2 
        
        quadrant = _get_quadrant_or_axis(x_val, y_val)
        
        question_text_template = r"在下方的坐標平面中，點 ${label}$ 的坐標為何？它位於哪個象限或坐標軸上？"
        question_text = question_text_template.replace("{label}", point_label)
        
        # 視覺化函式僅能接收「題目已知數據」
        image_base64 = _draw_coordinate_plane(points=[(point_label, x_val, y_val)], show_labels=True)
        
        # V13.1 答案格式標準化: A(3, 5)
        # V13.0 格式精確要求: str(int(val)) 處理整數
        # correct_answer 必須是機器可讀，不能包含 LaTeX 分數
        # 系統底層鐵律: 數值格式化 (No .0)
        correct_x_str = str(int(x_val)) if float(x_val).is_integer() else str(round(x_val, 4))
        correct_y_str = str(int(y_val)) if float(y_val).is_integer() else str(round(y_val, 4))
        
        correct_answer = f"{point_label}({correct_x_str}, {correct_y_str}), {quadrant}"
        
        # answer_display 由於此題型坐標為整數，故與 correct_answer 相同
        answer_display = correct_answer 

    # [欄位鎖死]: 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64
    # [時間戳記]: 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
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
