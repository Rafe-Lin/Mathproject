# ==============================================================================
# ID: jh_數學1下_DirectProportion
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 47.04s | RAG: 3 examples
# Created At: 2026-01-16 15:07:41
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



from datetime import datetime
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

# --- Helper Functions (遵循 V6 視覺化與輔助函式通用規範) ---

def _gcd(a, b):
    """計算最大公因數的輔助函式。"""
    while b:
        a, b = b, a % b
    return a

def _generate_number_data(min_val, max_val, allow_fraction=False, den_limit=5, allow_zero=True):
    """
    生成一個數字（整數或分數）及其結構化數據，用於 LaTeX 格式化。
    遵循 V10.2 A 資料結構鎖死, V13.1 禁絕假分數。
    回傳格式：(float_val, (int_part, num, den, is_neg))。
    若為整數，num=0, den=0。
    若為分數，int_part 為帶分數的整數部，且 num < den, den > 1。
    """
    is_neg = random.choice([True, False]) # 隨機決定正負

    if not allow_fraction or random.random() < 0.7: # 大部分情況下生成整數
        float_val = random.randint(min_val, max_val)
        if not allow_zero:
            while float_val == 0: # 若不允許為零，則重新生成
                float_val = random.randint(min_val, max_val)
        
        # 確保 0 不帶負號
        if float_val == 0:
            is_neg = False
        
        # V13.5 整數優先：確保回傳的整數部分是 int 類型
        return float(float_val), (int(float_val), 0, 0, is_neg)
    else:
        # 生成一個真分數部分 (遵循 V13.1 禁絕假分數)
        abs_int_part = random.randint(0, max_val // 2) # 整數部分，避免過大
        
        numerator = random.randint(1, den_limit - 1) # 分子 < 分母
        denominator = random.randint(2, den_limit)   # 分母 > 1
        
        # 簡化分數
        common = _gcd(numerator, denominator)
        numerator //= common
        denominator //= common

        # 確保分子小於分母（真分數）
        while numerator >= denominator: # 再次檢查以防萬一
            numerator = random.randint(1, den_limit - 1)
            denominator = random.randint(2, den_limit)
            common = _gcd(numerator, denominator)
            numerator //= common
            denominator //= common

        float_val_abs = abs_int_part + (numerator / denominator)
        
        if not allow_zero and float_val_abs == 0:
            # 極端情況下如果生成為0且不允許為0，則重新生成
            return _generate_number_data(min_val, max_val, allow_fraction, den_limit, allow_zero)

        float_val = float_val_abs
        if is_neg:
            float_val = -float_val

        # 根據 V10.2 A，int_part 應為帶分數的整數部，其符號由 is_neg 決定或直接包含
        int_part_for_tuple = abs_int_part
        if is_neg and abs_int_part > 0:
            int_part_for_tuple = -abs_int_part
        
        return float_val, (int_part_for_tuple, numerator, denominator, is_neg)

def _format_number_for_latex(number_data):
    """
    將數字（整數或分數）格式化為 LaTeX 字串。
    遵循 V5 排版與 LaTeX 安全, V10.2 C LaTeX 模板規範。
    輸入: (float_val, (int_part, num, den, is_neg))
    輸出: LaTeX 字串
    """
    float_val, (int_part, num, den, is_neg) = number_data

    if num == 0 and den == 0: # 是一個整數
        return str(int(float_val))
    else: # 是一個分數或帶分數
        if int_part == 0: # 純分數
            sign_str = "-" if is_neg else ""
            expr = r"\frac{{n}}{{d}}".replace("{{n}}", str(num)).replace("{{d}}", str(den))
            return sign_str + expr
            expr = r"{i}\frac{{n}}{{d}}".replace("{i}", str(int_part)).replace("{{n}}", str(num)).replace("{{d}}", str(den))
            return expr

def _format_number_for_python(number_data):
    """
    將數字數據轉換為 Python 純值字串 (例如 "3", "1/2", "-5/3")。
    用於 correct_answer。
    """
    float_val, (int_part, num, den, is_neg) = number_data
    
    if num == 0 and den == 0:
        return str(int(float_val))
    
    # 轉換為假分數
    # int_part is the integer part (abs value usually in this tuple structure? check generate_number_data)
    # _generate_number_data: int_part_for_tuple = abs_int_part OR -abs_int_part
    
    total_num = abs(int_part) * den + num
    if is_neg:
        return f"-{total_num}/{den}"
    else:
        return f"{total_num}/{den}"

def _draw_coordinate_plane(points_to_plot, labels, x_range=(-8, 8), y_range=(-8, 8), title=""):
    """
    繪製坐標平面，可選點和標籤。
    遵循 V6, V10.2 B, D, V13.0, V13.1, V13.5, V13.6 規範。
    points_to_plot: 點的列表，格式為 (x, y)
    labels: 每個點的標籤字串
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # V11.6: Resolution: dpi=300

    # 設定長寬比相等以確保網格為正方形 (V10.2 D, V11.6 Aspect Ratio)
    ax.set_aspect('equal')

    # 設定坐標軸範圍和刻度 (V13.0, V13.5)
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))

    # 繪製網格
    ax.grid(True, linestyle='--', alpha=0.6)

    # 繪製坐標軸 (V13.6 Arrow Ban: 嚴禁使用 arrowprops)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # 繪製坐標軸箭頭 (V13.6)
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8)
    ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8)
    ax.plot(x_range[0], 0, "<k", clip_on=False, markersize=8)
    ax.plot(0, y_range[0], "vk", clip_on=False, markersize=8)

    # 標註坐標軸
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12, rotation=0)

    # 標註原點 '0' (V10.2 D)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))

    # 繪製點 (V10.2 B, V13.5)
    for i, (x, y) in enumerate(points_to_plot):
        ax.plot(x, y, 'ro', markersize=8) # 紅色圓點
        # 標註點 (V10.2 D, V13.0, V13.1, V13.5: ax.text 只能是點的名稱，不能包含座標值)
        if i < len(labels):
            ax.text(x + 0.2, y + 0.2, labels[i], fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7)) # V11.6 Label Halo

    ax.set_title(title)

    # 將圖形儲存為 base64 字串
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300) # V11.6: Resolution: dpi=300
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# --- Main Problem Generation and Check Functions ---

def generate(level=1):
    """
    生成一個正比問題。
    遵循 V3 頂層函式, V4 題型鏡射, V10 數據禁絕常數, V13.5 整數優先。
    """
    problem_type = random.choice([1, 2, 3]) # 隨機分流 (V4)
    
    question_text = ""
    correct_answer_val = None
    image_base64 = ""
    answer_latex = "" # 這是提供給前端顯示解答用的 LaTeX 字串

    # 1. 生成比例常數 k (遵循 V10 數據禁絕常數, V13.1 禁絕假分數)
    # k 可以是整數或真分數，範圍在 -3 到 3 之間 (不包含 0)
    k_data = _generate_number_data(1, 3, allow_fraction=True, den_limit=4, allow_zero=False)
    k_float = k_data[0]
    
    # 從 k_data 中提取分母，以確保 x1 和 y1 都是整數
    # (int_part, num, den, is_neg)
    _, _, k_den_part, _ = k_data[1]
    actual_k_den = k_den_part if k_den_part != 0 else 1 # 若 k 為整數，分母視為 1

    # 2. 生成 x1 (遵循 V10 數據禁絕常數, V13.0 座標選取控制)
    # x1 應為 actual_k_den 的倍數，確保 y1 為整數
    x1_val_raw = random.randint(-5, 5) # 基礎整數值
    while x1_val_raw == 0: # x 不能為零
        x1_val_raw = random.randint(-5, 5)
    
    x1 = x1_val_raw * actual_k_den # 確保 x1 是整數
    
    # 3. 計算 y1 = k * x1。這將是一個整數。
    y1 = round(k_float * x1) # round 處理浮點數精度問題，此處應為精確整數

    # 4. 創建 x1 和 y1 的數據結構 (它們是整數)
    x1_data = (float(x1), (x1, 0, 0, x1 < 0))
    y1_data = (float(y1), (y1, 0, 0, y1 < 0))
    
    # 將數據格式化為 LaTeX 字串
    k_latex = _format_number_for_latex(k_data)
    x1_latex = _format_number_for_latex(x1_data)
    y1_latex = _format_number_for_latex(y1_data)

    if problem_type == 1:
        # Type 1 MUST use the EXACT mathematical model of RAG Ex 1.
        # RAG Ex 1 is about determining if y and x are proportional.
        # The mathematical model is y = kx.
        # This problem type assumes y and x are proportional and asks for k.
        # This aligns with finding the constant k in y=kx.
        question_text_template = r"已知 $y$ 與 $x$ 成正比，且當 $x = {x1_val}$ 時，$y = {y1_val}$。" \
                                 r"試求比例常數 $k$。"
        
        question_text = question_text_template.replace("{x1_val}", x1_latex).replace("{y1_val}", y1_latex)
        
        # [V16.3] Pure Answer Fix: Return "3" or "1/3" (clean string)
        correct_answer_str = _format_number_for_python(k_data)
        answer_latex = r"$k = {k_val}$".replace("{k_val}", k_latex) # 解答顯示為 LaTeX格式

        # [V16.4 Text-Only Mode] 移除繪圖，減輕負擔
        image_base64 = ""

    elif problem_type == 2:
        # Type 2 MUST use the EXACT mathematical model of RAG Ex 2.
        # RAG Ex 2: Given y與x成正比, x=3, y=5. (a) relationship, (b) y when x=10.
        # This problem type maps to part (b) of Ex 2.
        
        x2_val_raw = random.randint(-5, 5)
        while x2_val_raw == 0 or x2_val_raw == x1_val_raw: # x2 不能為零或與 x1 相同
            x2_val_raw = random.randint(-5, 5)
        
        x2 = x2_val_raw * actual_k_den # 確保 x2 是整數
        y2 = round(k_float * x2) # y2 也是整數
        
        x2_data = (float(x2), (x2, 0, 0, x2 < 0))
        y2_data = (float(y2), (y2, 0, 0, y2 < 0)) # y2 是本題答案

        x2_latex = _format_number_for_latex(x2_data)
        
        question_text_template = r"已知 $y$ 與 $x$ 成正比。當 $x = {x1_val}$ 時，$y = {y1_val}$。" \
                                 r"試求當 $x = {x2_val}$ 時，$y$ 的值為何？"
        
        question_text = question_text_template.replace("{x1_val}", x1_latex) \
                                             .replace("{y1_val}", y1_latex) \
                                             .replace("{x2_val}", x2_latex)
        
        # [V16.3] Pure Answer Fix
        correct_answer_str = str(int(y2)) # y2 is integer
        answer_latex = r"$y = {y2_val}$".replace("{y2_val}", _format_number_for_latex(y2_data))

        # [V16.4 Text-Only Mode] 移除繪圖，減輕負擔
        image_base64 = ""

    else: # problem_type == 3
        # Type 3 MUST use the EXACT mathematical model of RAG Ex 3.
        # RAG Ex 3: Word problem (阿賢 work hours & salary).
        # This problem type mirrors the structure of a direct proportion word problem.
        
        # 設距離 (D) 與時間 (H) 成正比。D = kH。
        h1 = random.randint(2, 6) # 小時
        k_speed = random.randint(30, 80) # 公里/小時 (比例常數)
        
        d1 = k_speed * h1 # 行駛距離
        
        h2 = random.randint(1, 7)
        while h2 == h1: # 確保 H2 不等於 H1
            h2 = random.randint(1, 7)
        
        d2 = k_speed * h2 # 答案 (公里)
        
        question_text_template = r"某汽車以等速行駛，在 ${h1}$ 小時內行駛了 ${d1}$ 公里。" \
                                 r"若汽車繼續以相同速度行駛，則在 ${h2}$ 小時內可望行駛多少公里？"
        
        question_text = question_text_template.replace("{h1}", str(h1)) \
                                             .replace("{d1}", str(d1)) \
                                             .replace("{h2}", str(h2))
        
        # [V16.3] Pure Answer Fix
        correct_answer_str = str(int(d2) if d2.is_integer() else d2)
        answer_latex = r"${d2_val}$ 公里".replace("{d2_val}", str(d2))
        
        image_base64 = "" # 文字題通常不需複雜圖形

    # 遵循 V7 數據與欄位, V13.1 答案格式標準化
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str, # [V16.3] Pure string
        "answer": answer_latex, # answer 欄位用於顯示解答
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


# --- 5. Answer Checker [V16.3 Pure Answer Fix] ---
# --- 5. Answer Checker [V16.5 Clean & Robust Check] ---
def check(user_answer, correct_answer):
    """
    [V16.5 Clean & Robust Check]
    強力比對函式，支援：
    1. 自動移除變數前綴 (k=3, y=-2, x=...)
    2. 自動移除 LaTeX 符號 ($) 與空格
    3. 支援分數與小數比對 (1/3 == 0.333)
    4. 支援方程式字串比對 (正則化)
    """
    if user_answer is None: return False

    # 1. 前處理: 雙向清洗
    def clean_input(s):
        s = str(s).strip().lower()
        # Remove LaTeX delimiters: $ and \( \)
        s = re.sub(r'[\$\\]', '', s)
        # Remove spaces
        s = s.replace(' ', '')
        
        # Remove variable prefixes like "k=", "y=", "x="
        # Support "k=...", "y=...", "Ans=..."
        # Regex: Start of string, one or more chars followed by =, remove it.
        # But be careful not to remove equation parts if it's an equation?
        # Requirement: "y=-2" -> "-2". "k=3" -> "3". "y=3x" -> "3x" (system asks for relation? no, usually asks for k or y value type 2)
        # If the answer is an equation (Type 2 part a, but here we only have Type 2 part b seeking value), 
        # Type 1 asks for k (value).
        # Type 2 asks for y value.
        # Type 3 asks for value.
        # So in all cases we are looking for a value.
        # CAUTION: If the answer is "y=3x", and user types "y=3x", we want "3x"=="3x".
        # If correct is "3" and user "k=3", we want "3"=="3".
        
        if '=' in s:
            # Check if it looks like a prefix assignment ex: "k=3"
            parts = s.split('=')
            if len(parts) == 2:
                # heuristic: if part 0 is short (variable name), take part 1
                if len(parts[0]) < 5: 
                    return parts[1]
        
        return s

    u_str = clean_input(user_answer)
    c_str = clean_input(correct_answer)

    # 2. 數值解析器 (支援分數與小數)
    def parse_val(val_str):
        try:
            # Remove any residual non-numeric chars for pure value check?
            # No, equation logic might need x.
            # Only try float conversion if it looks like a number.
            if re.match(r'^-?\d+(\.\d+)?$|^-?\d+/\d+$', val_str):
                if '/' in val_str:
                    n, d = val_str.split('/')
                    return float(n) / float(d)
                return float(val_str)
            return None # Not a simple number
        except:
            return None

    u_val = parse_val(u_str)
    c_val = parse_val(c_str)

    # 3. 比對邏輯
    # (A) 數值比對
    if u_val is not None and c_val is not None:
        return math.isclose(u_val, c_val, rel_tol=1e-7, abs_tol=1e-7)

    # (B) 字串直接比對 (Fallback for non-numeric or equations)
    return u_str == c_str

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
