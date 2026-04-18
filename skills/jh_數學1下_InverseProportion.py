# ==============================================================================
# ID: jh_數學1下_InverseProportion
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 112.32s | RAG: 3 examples
# Created At: 2026-01-16 23:34:49
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
from datetime import datetime

# 假設 Coder 已準備好 Matplotlib 相關設定
# 例如：
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plots

# --- 輔助函式：V10.2 座標平面專用硬化規格: A. 資料結構鎖死 ---
def _generate_coordinate_value(min_val=-8, max_val=8):
    """
    生成一個座標值（整數或 X.5），並回傳其浮點值及分解後的部件。
    返回值: (float_val, (int_part, num, den, is_neg))
    - float_val: 實際浮點值。
    - int_part: 帶分數的整數部分 (絕對值)。
    - num: 分數的分子 (絕對值)。
    - den: 分數的分母 (絕對值)。
    - is_neg: 是否為負數 (布林值)。
    
    V13.0: 座標選取控制 - 使用 random.randint(-8, 8) 或 +0.5。
    V10.2: 確保反比關係中 x 值不為 0。
    V14.0: 座標精度 - 僅限整數或 0.5。
    """
    is_neg = random.choice([True, False])
    
    # 30% 機率生成 X.5，否則生成整數
    if random.random() < 0.3:
        # 生成整數部分
        int_val = random.randint(min_val, max_val)
        # 反比關係中，避免 x 座標為 0
        while int_val == 0:
            int_val = random.randint(min_val, max_val)
        
        float_val = abs(int_val) + 0.5
        if is_neg:
            float_val = -float_val
            
        return (float_val, (abs(int_val), 1, 2, is_neg)) # num=1, den=2 for 0.5
    else: # 生成整數
        val = random.randint(min_val, max_val)
        # 反比關係中，避免 x 座標為 0
        while val == 0:
            val = random.randint(min_val, max_val)
        
        float_val = float(val)
        return (float_val, (abs(val), 0, 0, val < 0))

def _is_int_or_half(val, tolerance=1e-9):
    """V14.0: 輔助函式，檢查浮點數是否為整數或 X.5。"""
    return abs(val - round(val)) < tolerance or abs(val - (round(val - 0.5) + 0.5)) < tolerance

def _format_coordinate(val_data):
    """
    將座標值數據格式化為 LaTeX 字串。
    val_data: (float_val, (int_part, num, den, is_neg))
    V10.2 C: LaTeX 模板規範 - 使用單層大括號。
    V13.5: 整數優先 - 確保整數格式為 "5" 而非 "5.0"。
    V14.0: 座標精度 - 僅限整數或 0.5。
    """
    float_val, (int_part, num, den, is_neg) = val_data
    
    # V13.5: 整數優先
    if abs(float_val - round(float_val)) < 1e-9: # 檢查是否為整數 (考慮浮點數精度)
        return str(int(round(float_val)))
    
    sign = "-" if is_neg else ""
    
    # V14.0: 僅限 0.5 的情況
    if abs(float_val - (round(float_val - 0.5) + 0.5)) < 1e-9: # 檢查是否為 X.5 (考慮浮點數精度)
        actual_int_part = int(abs(float_val) - 0.5)
        if actual_int_part == 0: # 純分數 0.5 或 -0.5
            return sign + r"\frac{1}{2}"
        else: # 帶分數 X 又 0.5
            return sign + r"{i}\frac{1}{2}".replace("{i}", str(actual_int_part))
    else:
        # 此處應不會被觸及，因為數據生成已確保為整數或 X.5
        return str(float_val)

# --- 輔助函式：視覺化與輔助函式通用規範 ---
def _draw_coordinate_plane(points_to_plot=None, func_to_plot=None, x_range=(-10, 10), y_range=(-10, 10), label_x="x", label_y="y"):
    """
    繪製座標平面，可選點和函數曲線。
    遵循 V10.2, V13.0, V13.1, V13.5, V13.6, V11.6, V14.0 規範。
    points_to_plot: 包含 (x, y, label) 元組的列表。label 是點的名稱 (e.g., "A")。
                    V10.2 B: 若為「標點」題型，此參數必須傳入空列表 `[]`。
    func_to_plot: 要繪製的函數，例如 lambda x: k/x。
    
    防洩漏原則: 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
    """
    # 【Coder 實作細節，此處僅為規範描述】
    # Coder 應使用 matplotlib 進行繪圖。
    # import matplotlib.pyplot as plt
    # import matplotlib
    # matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plots
    # fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # V11.6: Resolution: dpi=300
    #
    # # V10.2 D, V11.6: 視覺一致性 - 鎖定 ax.set_aspect('equal') 確保網格為正方形。
    # ax.set_aspect('equal')
    #
    # # V13.0: 格線對齊 - 座標軸範圍必須是對稱整數，且 xticks 間隔必須固定為 1。
    # ax.set_xlim(x_range[0], x_range[1])
    # ax.set_ylim(y_range[0], y_range[1])
    # ax.set_xticks(range(int(x_range[0]), int(x_range[1]) + 1))
    # ax.set_yticks(range(int(y_range[0]), int(y_range[1]) + 1))
    # ax.grid(True, linestyle='--', alpha=0.6)
    #
    # # 繪製座標軸
    # ax.axhline(0, color='black', linewidth=1.5)
    # ax.axvline(0, color='black', linewidth=1.5)
    #
    # # V13.6: Arrow Ban - 嚴禁在 axhline/axvline 使用 arrowprops。必須使用 ax.plot 繪製箭頭。
    # ax.plot(x_range[1], 0, ">k", clip_on=False, transform=ax.get_yaxis_transform()) # X 軸箭頭
    # ax.plot(0, y_range[1], "^k", clip_on=False, transform=ax.get_xaxis_transform()) # Y 軸箭頭
    #
    # # V10.2 D: 坐標軸標註：僅顯示原點 '0' (18號加粗)。
    # ax.text(-0.5, -0.8, '0', fontsize=18, fontweight='bold', ha='center', va='center')
    #
    # # 座標軸標籤
    # ax.text(x_range[1] + 0.5, -0.5, label_x, fontsize=12, ha='left', va='center')
    # ax.text(-0.5, y_range[1] + 0.5, label_y, fontsize=12, ha='center', va='bottom')
    #
    # # 繪製函數曲線 (例如反比函數的雙曲線)
    # if func_to_plot:
    #     # 生成正負兩部分的 x 值，以繪製雙曲線的兩個分支
    #     # V14.0: 繪製時的步長可以小於 0.5，以確保曲線平滑
    #     xs_pos = [i/100 for i in range(1, x_range[1]*100) if i/100 != 0]
    #     xs_neg = [i/100 for i in range(x_range[0]*100, -1) if i/100 != 0]
    #
    #     def plot_segment(xs_segment):
    #         ys_segment = []
    #         valid_xs = []
    #         for x_val in xs_segment:
    #             if x_val != 0: # 確保 x 不為 0
    #                 y_val = func_to_plot(x_val)
    #                 # 僅繪製在可視範圍內的點
    #                 if y_range[0] <= y_val <= y_range[1]:
    #                     valid_xs.append(x_val)
    #                     ys_segment.append(y_val)
    #         if valid_xs:
    #             ax.plot(valid_xs, ys_segment, color='blue', linewidth=2)
    #
    #     plot_segment(xs_pos)
    #     plot_segment(xs_neg)
    #
    # # 繪製點
    # if points_to_plot:
    #     for x, y, label in points_to_plot:
    #         ax.plot(x, y, 'ro', markersize=8) # 紅色圓點
    #         # V13.0, V13.1, V13.5: 標籤權限隔離 - ax.text 只能標註點的名稱 (Label)，絕對不能包含座標值。
    #         # V10.2 D, V11.6: 點標籤須加白色光暈 (bbox)。
    #         ax.text(x + 0.3, y + 0.3, label, fontsize=12, ha='left', va='bottom',
    #                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
    #
    # # 將圖形保存為 base64 編碼的 PNG 圖片
    # buf = BytesIO()
    # plt.savefig(buf, format='png', bbox_inches='tight')
    # plt.close(fig)
    # image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # return image_base64
    return "image_base64_placeholder" # Spec 僅回傳佔位符字串

# --- 輔助函式：V13.6 API Hardened Spec: Exact Check Logic ---
def _check_numeric_sequence(user_answer, correct_answer_list):
    """
    V12.6: 結構鎖死 - 實作「數值序列比對」。
    V13.5: 禁絕複雜比對 - 統一要求使用數字序列比對。
    V13.6: Coder 必須逐字複製此 4-line check logic，不得自行發揮。
    
    將用戶輸入字串解析為數字序列，並與正確答案的數字序列進行比對。
    用戶輸入可以是逗號分隔，或括號包圍。
    """
    try:
        # 移除括號，按逗號分割，過濾空字串，轉換為浮點數
        user_numbers = [float(s.strip()) for s in user_answer.replace('(', '').replace(')', '').split(',') if s.strip()]
        correct_numbers = [float(s) for s in correct_answer_list]

        if len(user_numbers) != len(correct_numbers):
            return False

        # 浮點數比較使用容忍度
        tolerance = 1e-6
        for u, c in zip(user_numbers, correct_numbers):
            if abs(u - c) > tolerance:
                return False
        return True
    except ValueError: # 用戶輸入無法解析為數字
        return False

# V13.6 Strict Labeling: 點名稱白名單
POINT_LABELS = ["A", "B", "C", "D", "P", "Q", "R", "S"]

# --- 頂層函式：嚴禁使用 class 封裝 ---
def generate(level=1):
    """
    生成反比關係相關的數學題目。
    V4: 題型鏡射 - 使用 random.choice 或 if/elif 邏輯對應 RAG 例題。
    V10: 數據禁絕常數 - 所有數據隨機生成，答案透過公式計算。
    V14.0: 座標精度 - 所有生成的 x, y 座標值必須是整數或 X.5。
    """
    problem_type = random.choice([1, 2, 3, 4, 5]) # 隨機選擇問題類型

    question_text = ""
    correct_answer = "" # V7: 欄位鎖死
    answer = ""         # V7: 欄位鎖死 (此欄位用於內部答案數值，而非顯示給學生)
    image_base64 = ""   # V7: 欄位鎖死
    
    # V14.0: 為確保所有生成的 x, y 值為整數或 X.5，且 k = xy，
    # 需確保 x 和 y 不能同時為 X.5 (否則 k 會是 X.25 或 X.75)。
    # 且後續由 k/x 得到的 y 也必須是整數或 X.5。
    
    # 策略：生成一個有效的 (x_base, y_base) 對，其中 x_base, y_base 均為整數或 X.5，
    # 且兩者中至多一個為 X.5。然後計算 k = x_base * y_base。
    # 這樣 k_val 就會是整數或 X.5。
    x_base_data = _generate_coordinate_value()
    y_base_data = _generate_coordinate_value()
    x_base_val = x_base_data[0]
    y_base_val = y_base_data[0]

    # 確保 x_base_val 和 y_base_val 中至多一個為 X.5 (即避免同時為浮點數)
    while (not x_base_val.is_integer() and not y_base_val.is_integer()):
        if random.choice([True, False]): # 隨機讓其中一個強制變為整數
            x_base_data = _generate_coordinate_value()
            while not x_base_data[0].is_integer():
                x_base_data = _generate_coordinate_value()
            x_base_val = x_base_data[0]
        else:
            y_base_data = _generate_coordinate_value()
            while not y_base_data[0].is_integer():
                y_base_data = _generate_coordinate_value()
            y_base_val = y_base_data[0]

    k_val = x_base_val * y_base_val
    while k_val == 0: # 反比關係的比例常數 k 不能為 0
        x_base_data = _generate_coordinate_value()
        y_base_data = _generate_coordinate_value()
        x_base_val = x_base_data[0]
        y_base_val = y_base_data[0]
        while (not x_base_val.is_integer() and not y_base_val.is_integer()):
            if random.choice([True, False]):
                x_base_data = _generate_coordinate_value()
                while not x_base_data[0].is_integer():
                    x_base_data = _generate_coordinate_value()
                x_base_val = x_base_data[0]
            else:
                y_base_data = _generate_coordinate_value()
                while not y_base_data[0].is_integer():
                    y_base_data = _generate_coordinate_value()
                y_base_val = y_base_data[0]
        k_val = x_base_val * y_base_val
    
    # V13.0: 座標範圍必須對稱且寬裕 (e.g., -10 到 10)
    coord_range = (-10, 10)

    if problem_type == 1:
        # Type 1 (Maps to Example 1): 基本判斷 (表格)
        # RAG Ex1.1 和 Ex1.2 顯示表格中的值可以是整數或非整數。
        # 對於成反比的情況，我們確保 x 和 y 都是整數。
        # 對於不成反比的情況，我們讓 y 值可以是整數或帶小數。
        
        is_inverse = random.choice([True, False])
        x_values = []
        y_values = []
        
        if is_inverse:
            # 為了確保 x 和 y 都是整數，我們選擇一個簡單的 k_val，並從其整數因子中選擇 x。
            k_val_for_table = random.choice([24, 36, 48, 60, 72, 80, 96, 100, 120, -24, -36, -48, -60, -72, -80, -96, -100, -120])
            
            possible_x = [i for i in range(1, 13) if k_val_for_table % i == 0 and k_val_for_table // i != 0]
            random.shuffle(possible_x)
            
            num_pairs = random.randint(3, min(4, len(possible_x)))
            # 確保至少有 3 對數據
            if num_pairs < 3: 
                # Fallback to simpler k if not enough divisors
                k_val_for_table = random.choice([12, 18, 20, 24, 30, 36, -12, -18, -20, -24, -30, -36])
                possible_x = [i for i in range(1, 13) if k_val_for_table % i == 0 and k_val_for_table // i != 0]
                random.shuffle(possible_x)
                num_pairs = random.randint(3, min(4, len(possible_x)))

            x_values = possible_x[:num_pairs]
            y_values = [k_val_for_table // x for x in x_values] # 使用整數除法
            
        else:
            # 不成反比 (例如成正比或線性關係)
            # 為了符合 RAG Ex1.2，y 值可以不是整數。
            temp_x_candidates = list(range(1, 11))
            random.shuffle(temp_x_candidates)
            num_pairs = random.randint(3, 4)
            x_values = temp_x_candidates[:num_pairs] # x 值為整數
            
            if random.random() < 0.5: # 成正比 (y = mx)
                m_val = random.randint(1, 5) * random.choice([-1, 1])
                while m_val == 0:
                    m_val = random.randint(1, 5) * random.choice([-1, 1])
                y_values = [m_val * x for x in x_values]
            else: # 線性關係 (y = mx + b)
                m_val = random.randint(1, 3) * random.choice([-1, 1])
                while m_val == 0:
                    m_val = random.randint(1, 3) * random.choice([-1, 1])
                b_val = random.randint(1, 5) * random.choice([-1, 1])
                y_values = [m_val * x + b_val for x in x_values]

        # 將數據構建為 LaTeX 表格
        table_rows_x = r"$x$"
        table_rows_y = r"$y$"
        for i in range(len(x_values)):
            x_val_str = str(x_values[i])
            # V13.5: 整數優先，否則保留兩位小數 (符合 RAG Ex1.2 的非整數情況)
            y_val_str = str(int(y_values[i])) if y_values[i].is_integer() else str(round(y_values[i], 2))
            table_rows_x = table_rows_x + r" & " + x_val_str
            table_rows_y = table_rows_y + r" & " + y_val_str
        
        table_latex = r"""
        $\begin{array}{|c|c|c|c|}
        \hline
        {x_row} \\
        \hline
        {y_row} \\
        \hline
        \end{array}$
        """.replace("{x_row}", table_rows_x).replace("{y_row}", table_rows_y)

        question_text = r"觀察下列表格，判斷 $x$ 和 $y$ 是否成反比關係？" + table_latex
        correct_answer = "是" if is_inverse else "否"
        answer = correct_answer

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 尋找比例常數
        
        x1_data = _generate_coordinate_value()
        x1_val = x1_data[0]
        y1_val = k_val / x1_val
        # V14.0: 確保 y1_val 也是整數或 X.5
        while not _is_int_or_half(y1_val):
            x1_data = _generate_coordinate_value()
            x1_val = x1_data[0]
            y1_val = k_val / x1_val
        
        # 格式化 x1, y1 以供顯示
        x1_str = _format_coordinate(x1_data)
        # 需要為 y1_val 重新構建 val_data 結構，以便 _format_coordinate 正確處理
        y1_is_neg = y1_val < 0
        y1_int_part = int(abs(y1_val)) if abs(y1_val - round(y1_val)) < 1e-9 else int(abs(y1_val) - 0.5)
        y1_num = 0
        y1_den = 0
        if not (abs(y1_val - round(y1_val)) < 1e-9): # 如果不是整數，則一定是 X.5
            y1_num = 1
            y1_den = 2
        y1_data = (y1_val, (y1_int_part, y1_num, y1_den, y1_is_neg))
        y1_str = _format_coordinate(y1_data)

        question_text = r"已知 $y$ 與 $x$ 成反比，當 $x = {x1_s}$ 時，$y = {y1_s}$。求其反比關係的比例常數。".replace("{x1_s}", x1_str).replace("{y1_s}", y1_str)
        
        # V13.5: 確保 k_val 格式化為整數或 X.5
        k_is_neg = k_val < 0
        k_int_part = int(abs(k_val)) if abs(k_val - round(k_val)) < 1e-9 else int(abs(k_val) - 0.5)
        k_num = 0
        k_den = 0
        if not (abs(k_val - round(k_val)) < 1e-9):
            k_num = 1
            k_den = 2
        k_data = (k_val, (k_int_part, k_num, k_den, k_is_neg))
        
        correct_answer = _format_coordinate(k_data)
        answer = correct_answer

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): 計算缺失值
        
        x1_data = _generate_coordinate_value()
        x1_val = x1_data[0]
        y1_val = k_val / x1_val
        while not _is_int_or_half(y1_val): # V14.0: 確保 y1_val 也是整數或 X.5
            x1_data = _generate_coordinate_value()
            x1_val = x1_data[0]
            y1_val = k_val / x1_val
        
        x2_data = _generate_coordinate_value()
        x2_val = x2_data[0]
        while x2_val == x1_val: # 確保 x2 與 x1 不同
            x2_data = _generate_coordinate_value()
            x2_val = x2_data[0]
        y2_val = k_val / x2_val
        while not _is_int_or_half(y2_val): # V14.0: 確保 y2_val 也是整數或 X.5
            x2_data = _generate_coordinate_value()
            x2_val = x2_data[0]
            while x2_val == x1_val:
                x2_data = _generate_coordinate_value()
                x2_val = x2_data[0]
            y2_val = k_val / x2_val
        
        # 隨機選擇隱藏哪個值 (x2 或 y2)
        hidden_var = random.choice(['x2', 'y2'])
        
        x1_str = _format_coordinate(x1_data)
        y1_is_neg = y1_val < 0
        y1_int_part = int(abs(y1_val)) if abs(y1_val - round(y1_val)) < 1e-9 else int(abs(y1_val) - 0.5)
        y1_num = 0
        y1_den = 0
        if not (abs(y1_val - round(y1_val)) < 1e-9):
            y1_num = 1
            y1_den = 2
        y1_data = (y1_val, (y1_int_part, y1_num, y1_den, y1_is_neg))
        y1_str = _format_coordinate(y1_data)

        x2_str_display = ""
        y2_str_display = ""
        
        if hidden_var == 'x2':
            x2_str_display = r"?"
            y2_is_neg = y2_val < 0
            y2_int_part = int(abs(y2_val)) if abs(y2_val - round(y2_val)) < 1e-9 else int(abs(y2_val) - 0.5)
            y2_num = 0
            y2_den = 0
            if not (abs(y2_val - round(y2_val)) < 1e-9):
                y2_num = 1
                y2_den = 2
            y2_data = (y2_val, (y2_int_part, y2_num, y2_den, y2_is_neg))
            y2_str_display = _format_coordinate(y2_data)
            
            x2_val_for_check = int(x2_val) if x2_val.is_integer() else x2_val
            correct_answer = str(x2_val_for_check)
        else: # hidden_var == 'y2'
            x2_str_display = _format_coordinate(x2_data)
            y2_str_display = r"?"
            
            y2_val_for_check = int(y2_val) if y2_val.is_integer() else y2_val
            correct_answer = str(y2_val_for_check)

        question_text = (
            r"已知 $y$ 與 $x$ 成反比。當 $x = {x1_s}$ 時，$y = {y1_s}$。"
            r"若 $x = {x2_s}$ 時，$y = {y2_s}$，求未知數的值。"
        ).replace("{x1_s}", x1_str).replace("{y1_s}", y1_str).replace("{x2_s}", x2_str_display).replace("{y2_s}", y2_str_display)
        
        answer = correct_answer

    elif problem_type == 4:
        # Type 4 (Maps to Example 3): 應用題 - 計算缺失值
        # RAG Ex3 應用題只使用整數，我們也遵循此規則。
        
        # 範例情境：工作人數與完成時間成反比 (總工作量 = 人數 * 時間)
        
        # 生成總工作量 K (必須是整數)
        k_word_val = random.randint(50, 200) 
        
        # 初始情境 (確保人數和時間都是整數)
        workers1 = random.randint(2, 10)
        time1 = k_word_val / workers1
        while not time1.is_integer():
            k_word_val = random.randint(50, 200)
            workers1 = random.randint(2, 10)
            time1 = k_word_val / workers1
            
        # 新情境 (確保人數和時間都是整數)
        workers2 = random.randint(2, 10)
        while workers2 == workers1: # 確保工人數量不同
            workers2 = random.randint(2, 10)
        
        time2 = k_word_val / workers2
        while not time2.is_integer():
            k_word_val = random.randint(50, 200)
            workers1 = random.randint(2, 10)
            time1 = k_word_val / workers1
            while not time1.is_integer(): # 重新生成直到 time1 為整數
                k_word_val = random.randint(50, 200)
                workers1 = random.randint(2, 10)
                time1 = k_word_val / workers1
            workers2 = random.randint(2, 10)
            while workers2 == workers1: # 重新生成直到 workers2 與 workers1 不同
                workers2 = random.randint(2, 10)
            time2 = k_word_val / workers2
        
        question_text = (
            r"一項工程，所需時間與工人數量成反比。若 {w1_s} 名工人需要 {t1_s} 天完成，"
            r"則 {w2_s} 名工人需要多少天完成？"
        ).replace("{w1_s}", str(int(workers1))).replace("{t1_s}", str(int(time1))).replace("{w2_s}", str(int(workers2)))
        
        correct_answer = str(int(time2))
        answer = correct_answer

    elif problem_type == 5:
        # Type 5 (Maps to Example 5): 圖像與點識別 (座標平面)
        
        # 生成一個點的 x 座標 (V13.0 座標選取控制)
        px_data = _generate_coordinate_value(min_val=-8, max_val=8)
        px_val = px_data[0]
        
        py_val = k_val / px_val
        # V14.0: 確保 py_val 也是整數或 X.5
        while not _is_int_or_half(py_val):
            px_data = _generate_coordinate_value(min_val=-8, max_val=8)
            px_val = px_data[0]
            py_val = k_val / px_val
        
        # 為 py_val 重新構建 val_data 結構，以便 _format_coordinate 正確處理
        py_is_neg = py_val < 0
        py_int_part = int(abs(py_val)) if abs(py_val - round(py_val)) < 1e-9 else int(abs(py_val) - 0.5)
        py_num = 0
        py_den = 0
        if not (abs(py_val - round(py_val)) < 1e-9): # 如果不是整數，則一定是 X.5
            py_num = 1
            py_den = 2
        py_data = (py_val, (py_int_part, py_num, py_den, py_is_neg))

        # 選擇一個點的標籤 (V13.6 Strict Labeling)
        point_label = random.choice(POINT_LABELS)

        # V14.0: LaTeX 單層大括號 - 嚴禁 `{{ }}` 結構
        # 替換 `r"y = \frac{{{k_s}}}{{x}}"`
        question_text = (
            r"已知 $y$ 與 $x$ 成反比，其關係式為 $y = \frac{K_VAL}{x}$。"
            r"圖中標示的 {label_s} 點在曲線上，其 $x$ 座標為 ${px_s}$，求其 $y$ 座標。"
        ).replace("K_VAL", str(int(k_val) if k_val.is_integer() else k_val)).replace("{label_s}", point_label).replace("{px_s}", _format_coordinate(px_data))
        
        # 準備繪圖的點 (防洩漏原則：只傳入已知數據，但這裡已知 x 和 k，可以計算 y)
        points_to_draw = [(px_val, py_val, point_label)]
        
        # 要繪製的函數
        func = lambda x: k_val / x
        image_base64 = _draw_coordinate_plane(points_to_plot=points_to_draw, func_to_plot=func, x_range=coord_range, y_range=coord_range)
        
        # V13.5: 禁絕複雜比對 - check() 統一使用數字序列比對。
        # V13.1: 答案格式標準化 - 座標題：正確答案格式為 A(3, 5)。
        # 將 `correct_answer` 設為數值列表供 `check` 函式使用，
        # 而 `answer` 欄位則用於儲存格式化後的顯示答案字串。
        correct_answer = [px_val, py_val] # 數值列表，用於 _check_numeric_sequence
        answer = f"{point_label}({_format_coordinate(px_data)}, {_format_coordinate(py_data)})" # 格式化為 A(x, y) 顯示

    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # V7: 欄位鎖死
        "answer": answer,                 # V7: 欄位鎖死 (此處儲存顯示答案)
        "image_base64": image_base64,     # V7: 欄位鎖死
        "created_at": datetime.now().isoformat(), # V7: 時間戳記
        "version": "1.0"                  # V7: 版本
    }

# --- 頂層函式：嚴禁使用 class 封裝 ---

    """
    檢查用戶答案是否正確。
    V12.6: 結構鎖死 - check() 必須實作「數值序列比對」。
    V13.5: 禁絕複雜比對 - 嚴禁在 check() 內寫 if/else 字串拆解，統一要求使用數字序列比對。
    """
    # 根據 correct_answer 的類型判斷是數值序列比對還是簡單字串比對
    if isinstance(correct_answer, list):
        # V12.6: 強制運算 - 透過 if/elif 判斷。
        # V13.6: Exact Check Logic - 逐字複製 4-line check logic。
        return _check_numeric_sequence(user_answer, correct_answer)
    elif isinstance(correct_answer, str):
        # 對於非座標題，進行字串比對 (不區分大小寫，去除前後空格)
        return user_answer.strip().lower() == correct_answer.strip().lower()
    else:
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
