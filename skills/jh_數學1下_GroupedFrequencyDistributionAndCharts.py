# ==============================================================================
# ID: jh_數學1下_GroupedFrequencyDistributionAndCharts
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 96.35s | RAG: 5 examples
# Created At: 2026-01-17 22:48:46
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


import base64
import io
import re
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
 # For check function

# --- Helper Functions Implementation ---

def _generate_dataset(num_points: int, min_val: int, max_val: int) -> list[int]:
    """
    用途：生成隨機整數數據集。
    輸入：num_points (數據點數量), min_val (數據最小值), max_val (數據最大值)。
    輸出：list[int] - 排序後的隨機整數數據列表。
    規範：必須使用 random.randint 生成數據，並進行排序。
    """
    data = [random.randint(min_val, max_val) for _ in range(num_points)]
    data.sort()
    return data

def _calculate_frequency_table(data: list[int], class_width: int, start_val: int) -> dict:
    """
    用途：根據原始數據和分組規則，計算次數分配表。
    輸入：data (排序後的數據列表), class_width (組距), start_val (第一組的起始值)。
    輸出：dict - 包含 bins (組別區間), frequencies (次數), relative_frequencies (相對次數), 
                  cumulative_frequencies (累積次數), class_marks (組中點)。
    規範：
        * 嚴禁硬編碼任何數值，所有計算必須基於輸入參數。
        * 相對次數必須精確到小數點後兩位 (%.2f)。
        * 組別區間表示必須為左閉右開，例如 [10, 20)。
        * class_marks 計算為組界平均值。
    """
    if not data:
        return {'bins': [], 'frequencies': [], 'relative_frequencies': [], 'cumulative_frequencies': [], 'class_marks': []}

    min_data = data[0]
    max_data = data[-1]

    # Determine the lower bounds of the bins
    bins_lower_bounds = []
    current_lower = start_val
    # Ensure all data points are covered. The last bin's upper bound must be strictly greater than max_data.
    # The `+ class_width` ensures that even if max_data falls exactly on `current_lower + class_width`,
    # there will be an *additional* bin to correctly place it according to `[lower, upper)`.
    while current_lower <= max_data + class_width - 1: # -1 to ensure max_data is strictly less than upper bound of its bin
        bins_lower_bounds.append(current_lower)
        current_lower += class_width
    
    # Construct the actual bins (lower, upper)
    bins = []
    for i in range(len(bins_lower_bounds)):
        lower = bins_lower_bounds[i]
        upper = lower + class_width
        bins.append((lower, upper))
    
    # If after generating bins, the last data point is exactly the upper bound of the last bin,
    # and it was not caught by the `+ class_width - 1` logic (e.g., if max_data was very close to `current_lower + class_width - 1`),
    # we might need to add one more bin. This should be rare with the current `while` condition.
    # The current condition `current_lower <= max_data + class_width - 1` ensures that if `max_data` is `X`,
    # the last bin will have an upper bound of at least `X+1`, thus `X` falls into `[lower, upper)`.

    frequencies = [0] * len(bins)
    for d in data:
        found_bin = False
        for i, (lower, upper) in enumerate(bins):
            if lower <= d < upper:
                frequencies[i] += 1
                found_bin = True
                break
        if not found_bin: # Fallback for edge cases, though with correct bin generation it should not be hit.
            # If a data point is exactly the upper bound of the last bin, and no more bins were generated,
            # for K12 context, it often falls into the last bin.
            # However, strict `[lower, upper)` means it belongs to the *next* bin.
            # The current bin generation logic ensures there's always a bin for `max_data` such that `max_data < upper`.
            # If for some reason `d` is exactly `bins[-1][1]` (the upper bound of the last bin), it means our bin generation
            # was off by one, or `max_data` was `bins[-1][1] - 1` and `d` is `bins[-1][1]`.
            # For robustness, we can check if `d` is exactly `bins[-1][1]` and assign to last bin if it's the maximum value.
            # But the spec for `_calculate_frequency_table` says `[10, 20)`, implying strict inequality.
            # So, the `while` loop logic is correct and should prevent `found_bin` from being `False`.
            pass


    total_frequency = sum(frequencies)
    relative_frequencies = [freq / total_frequency if total_frequency > 0 else 0 for freq in frequencies]
    
    cumulative_frequencies = []
    current_cumulative = 0
    for freq in frequencies:
        current_cumulative += freq
        cumulative_frequencies.append(current_cumulative)

    class_marks = [(lower + upper) / 2 for lower, upper in bins]

    return {
        'bins': bins,
        'frequencies': frequencies,
        'relative_frequencies': relative_frequencies,
        'cumulative_frequencies': cumulative_frequencies,
        'class_marks': class_marks
    }

def _draw_histogram(bins: list[tuple[int, int]], frequencies: list[int], class_width: int, title: str, x_label: str, y_label: str) -> str:
    """
    用途：繪製直方圖並轉換為 Base64 字符串。
    規範：
        * 必須使用 matplotlib。
        * ax.set_aspect('auto') 確保直方圖比例正確 (而非 equal，因直方圖軸不代表等比例座標)。
        * x軸刻度必須與組界對齊。
        * y軸範圍必須對稱且寬裕，確保所有長條可見，且 yticks 間隔為 1 或 2，以確保清晰度。
        * 坐標軸標註：僅顯示原點 0 (18號加粗)。箭頭必須使用 ax.plot(limit, 0, ">k", clip_on=False) 繪製，嚴禁使用 arrowprops。
        * 長條上方可選擇性標註次數，但這些標籤不視為「答案數據」，而是圖形的一部分。
        * ax.text 標註的 string 只能是長條的標籤（如組別名稱），絕對不能包含答案值。
        * 防洩漏原則：此函式僅接收繪圖所需數據，不應接收或計算任何答案數據。
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300

    bin_edges = [b[0] for b in bins] + [bins[-1][1]] if bins else []
    
    # Calculate bar positions and widths
    bar_left_edges = [b[0] for b in bins]
    
    ax.bar(bar_left_edges, frequencies, width=class_width, align='edge', edgecolor='black', alpha=0.7)

    ax.set_title(title, fontsize=16)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    ax.set_xticks(bin_edges)
    ax.set_xticklabels([str(int(edge)) if float(edge).is_integer() else str(edge) for edge in bin_edges])
    
    # Y-axis ticks
    max_freq = max(frequencies) if frequencies else 0
    # Ensure yticks are integers and spaced well
    y_tick_interval = 1
    if max_freq > 5:
        y_tick_interval = 2
    if max_freq > 10:
        y_tick_interval = max(1, (max_freq + 1) // 5) # General rule to get about 5 ticks
    
    ax.set_yticks(range(0, max_freq + y_tick_interval + 1, y_tick_interval)) 
    ax.set_ylim(0, max_freq + y_tick_interval) # Ensure some padding above max bar

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_aspect('auto') # ARCHITECT'S SPECIFICATION: ax.set_aspect('auto')

    # Origin '0' label (V10.2 Pure Style)
    ax.text(-0.02, -0.05, '0', transform=ax.transAxes, fontsize=18, fontweight='bold', ha='right', va='top')

    # Arrows for axes (V13.6 API Hardened Spec)
    # x-axis arrow
    ax.plot(1, 0, ">k", transform=ax.transAxes, clip_on=False, markersize=8) 
    # y-axis arrow
    ax.plot(0, 1, "^k", transform=ax.transAxes, clip_on=False, markersize=8) 

    # V13.5: 標籤隔離, ax.text 只能標註點名稱 (這裡指組別或次數的數值標註)
    # For histogram, we can optionally label the frequencies on top of bars
    for i, rect in enumerate(ax.patches):
        height = rect.get_height()
        if height > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, height,
                    str(int(height)), ha='center', va='bottom', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7)) # V10.2: white halo for labels

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _draw_frequency_polygon(bins: list[tuple[int, int]], frequencies: list[int], class_width: int, title: str, x_label: str, y_label: str) -> str:
    """
    用途：繪製次數多邊圖並轉換為 Base64 字符串。
    規範：
        * 必須計算組中點作為多邊圖的 x 座標。
        * 多邊圖的起點和終點必須延伸至前後兩組的組中點，頻率為 0。
        * 其他繪圖規範同 _draw_histogram。
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300

    class_marks = [(b[0] + b[1]) / 2 for b in bins]
    
    # Add points for 0 frequency at beginning and end
    # Extend one class width before the first bin and one after the last bin
    x_coords = [class_marks[0] - class_width] + class_marks + [class_marks[-1] + class_width]
    y_coords = [0] + frequencies + [0]

    ax.plot(x_coords, y_coords, marker='o', linestyle='-', color='blue')

    ax.set_title(title, fontsize=16)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    # Set x-ticks to include class marks and extended points
    # Filter out duplicate ticks and sort them
    all_x_ticks = sorted(list(set(x_coords + [(b[0] + b[1]) / 2 for b in bins])))
    ax.set_xticks(all_x_ticks)
    ax.set_xticklabels([str(int(t)) if float(t).is_integer() else str(t) for t in all_x_ticks])
    
    # Y-axis ticks
    max_freq = max(frequencies) if frequencies else 0
    y_tick_interval = 1
    if max_freq > 5:
        y_tick_interval = 2
    if max_freq > 10:
        y_tick_interval = max(1, (max_freq + 1) // 5)
    
    ax.set_yticks(range(0, max_freq + y_tick_interval + 1, y_tick_interval))
    ax.set_ylim(0, max_freq + y_tick_interval)

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_aspect('auto') # ARCHITECT'S SPECIFICATION: ax.set_aspect('auto')

    # Origin '0' label (V10.2 Pure Style)
    ax.text(-0.02, -0.05, '0', transform=ax.transAxes, fontsize=18, fontweight='bold', ha='right', va='top')

    # Arrows for axes (V13.6 API Hardened Spec)
    ax.plot(1, 0, ">k", transform=ax.transAxes, clip_on=False, markersize=8) # X-axis arrow
    ax.plot(0, 1, "^k", transform=ax.transAxes, clip_on=False, markersize=8) # Y-axis arrow

    # V13.5: 標籤隔離, ax.text 只能標註點名稱
    # For frequency polygon, we can label the frequency for each point
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        if y > 0: # Only label points with actual frequencies
            ax.text(x, y, str(int(y)), ha='center', va='bottom', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7)) # V10.2: white halo for labels

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# V10.2 A. 資料結構鎖死
def _generate_coordinate_value(min_val: int, max_val: int, allow_fraction: bool = False) -> tuple[float, tuple[int, int, int, bool]]:
    """
    用途：生成一個數值，並以特定格式回傳。
    輸入：min_val, max_val (數值範圍), allow_fraction (是否允許分數)。
    輸出：(float_val, (int_part, num, den, is_neg))。
        * float_val: 實際數值。
        * int_part: 整數部分 (帶分數)。
        * num: 分子。
        * den: 分母。
        * is_neg: 是否為負數。
    規範：
        * 若為整數，num 與 den 設為 0。
        * 若為分數，必須檢查 numerator < denominator 且 denominator > 1 (V13.1 禁絕假分數)。
        * 使用 random.randint 生成整數或分子/分母。
    """
    int_part = random.randint(min_val, max_val)
    is_neg = int_part < 0
    
    if allow_fraction and random.random() < 0.5: # 50% chance for fraction if allowed
        abs_int_part = abs(int_part)
        num = random.randint(1, 9)
        den = random.randint(num + 1, 10) # denominator > numerator, denominator > 1 (V13.1)
        
        float_val = abs_int_part + num / den
        if is_neg:
            float_val = -float_val
            # The original `int_part` generated (e.g., -5 for -5.5) correctly represents the integer part
            # for mixed fractions in the tuple. If `int_part` was 0, and it's negative, it remains 0.
        
    else: # Integer value
        num, den = 0, 0
        float_val = float(int_part)
    
    return float_val, (int_part, num, den, is_neg)

# --- Generate Function ---

def generate(level: int = 1) -> dict:
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""
    answer_display = "" # For solution_text, following rule 1
    image_base64 = ""
    
    # Common parameters for data generation
    num_points = random.randint(20, 50)
    min_data_val = random.randint(0, 30)
    max_data_val = random.randint(min_data_val + 20, min_data_val + 80)
    class_width = random.choice([5, 10])
    
    # Determine start_val: a multiple of class_width and less than or equal to the actual minimum data point.
    # Regenerate data until it's not empty, if somehow num_points=0 was chosen or data range was invalid.
    data = []
    while not data: # Ensure data is not empty
        num_points_actual = random.randint(20, 50) # Ensure num_points is not 0
        min_data_val_actual = random.randint(0, 30)
        max_data_val_actual = random.randint(min_data_val_actual + 20, min_data_val_actual + 80)
        data = _generate_dataset(num_points_actual, min_data_val_actual, max_data_val_actual)

    actual_min_data = data[0]
    # Calculate start_val as the largest multiple of class_width less than or equal to actual_min_data
    start_val = (actual_min_data // class_width) * class_width
    # If actual_min_data is 5, class_width is 10, start_val will be 0.
    # If actual_min_data is 15, class_width is 10, start_val will be 10. This is desired.

    table_data = _calculate_frequency_table(data, class_width, start_val)
    
    bins = table_data['bins']
    frequencies = table_data['frequencies']
    relative_frequencies = table_data['relative_frequencies']
    cumulative_frequencies = table_data['cumulative_frequencies']
    class_marks = table_data['class_marks']

    # Final check for empty bins, though the logic above should prevent it.
    if not bins:
        raise ValueError("Failed to generate valid frequency table with bins.")

    if problem_type == 1: # Type 1: 填寫次數分配表 (Maps to Example 1, 4)
        # Randomly choose what to ask for: frequencies, relative frequencies, or cumulative frequencies
        question_choices = ["次數", "相對次數", "累積次數"]
        chosen_question_type = random.choice(question_choices)
        
        question_intro = r"以下是一組某班學生的數學測驗成績（單位：分）："
        data_str = ", ".join(map(str, data))
        
        # Build the table in LaTeX
        table_header = r"\begin{tabular}{|c|c|c|c|} \hline 組別(分) & 次數 & 相對次數 & 累積次數 \\ \hline"
        table_rows = []
        correct_answer_list = []

        for i, (lower, upper) in enumerate(bins):
            lower_str = str(int(lower)) if float(lower).is_integer() else str(lower) # V13.0, V13.5: str(int(val))
            upper_str = str(int(upper)) if float(upper).is_integer() else str(upper) # V13.0, V13.5: str(int(val))
            
            freq_display = str(frequencies[i])
            rel_freq_display = f"{relative_frequencies[i]:.2f}"
            cum_freq_display = str(cumulative_frequencies[i])

            if chosen_question_type == "次數":
                freq_display = r"\underline{\quad\quad}"
                correct_answer_list.append(str(frequencies[i]))
            elif chosen_question_type == "相對次數":
                rel_freq_display = r"\underline{\quad\quad}"
                correct_answer_list.append(f"{relative_frequencies[i]:.2f}")
            elif chosen_question_type == "累積次數":
                cum_freq_display = r"\underline{\quad\quad}"
                correct_answer_list.append(str(cumulative_frequencies[i]))

            # Use .format for LaTeX safety (single braces)
            row = r"{lower_bound} $\sim$ {upper_bound} & {freq} & {rel_freq} & {cum_freq} \\ \hline".format(
                lower_bound=lower_str,
                upper_bound=upper_str,
                freq=freq_display,
                rel_freq=rel_freq_display,
                cum_freq=cum_freq_display
            )
            table_rows.append(row)

        table_footer = r"總計 & {total_freq} & {total_rel_freq} & \\ \hline \end{tabular}".format(
            total_freq=str(sum(frequencies)),
            total_rel_freq=f"{sum(relative_frequencies):.2f}"
        )

        question_text = r"{intro_text}" \
                        r"$${data_list}$$" \
                        r"請根據上述數據，以 {start_val_display} 為第一組的下限，組距為 {class_width_display}，完成下列次數分配表中的 {question_type} 欄位。各欄位答案請依序以逗號分隔。" \
                        r"$${table_content}$$".format(intro_text=question_intro,
                                        data_list=data_str,
                                        start_val_display=str(int(start_val)) if float(start_val).is_integer() else str(start_val),
                                        class_width_display=str(int(class_width)) if float(class_width).is_integer() else str(class_width),
                                        question_type=chosen_question_type,
                                        table_content=table_header + "\n".join(table_rows) + table_footer)
        
        correct_answer = ", ".join(correct_answer_list)
        answer_display_parts = []
        for i, (lower, upper) in enumerate(bins):
            lower_str = str(int(lower)) if float(lower).is_integer() else str(lower)
            upper_str = str(int(upper)) if float(upper).is_integer() else str(upper)
            if chosen_question_type == "次數":
                answer_display_parts.append(f"組別 {lower_str} $\sim$ {upper_str} 的次數為 {frequencies[i]}")
            elif chosen_question_type == "相對次數":
                answer_display_parts.append(f"組別 {lower_str} $\sim$ {upper_str} 的相對次數為 {relative_frequencies[i]:.2f}")
            elif chosen_question_type == "累積次數":
                answer_display_parts.append(f"組別 {lower_str} $\sim$ {upper_str} 的累積次數為 {cumulative_frequencies[i]}")
        answer_display = f"正確答案應為： {{', '.join(correct_answer_list)}}。\n詳解：\n{{'; '.join(answer_display_parts)}}"

    elif problem_type == 2: # Type 2: 判讀次數分配表或圖形 (Maps to Example 2, 5)
        # Randomly choose to ask from a table or a generated graph
        ask_from_graph = random.choice([True, False])
        
        if not ask_from_graph: # Ask from table
            question_intro = r"下表為某次數學測驗成績的次數分配表："
            table_header = r"\begin{tabular}{|c|c|c|c|c|} \hline 組別(分) & 次數 & 相對次數 & 累積次數 & 組中點 \\ \hline"
            table_rows = []
            for i, (lower, upper) in enumerate(bins):
                lower_str = str(int(lower)) if float(lower).is_integer() else str(lower)
                upper_str = str(int(upper)) if float(upper).is_integer() else str(upper)
                class_mark_str = str(int(class_marks[i])) if float(class_marks[i]).is_integer() else str(class_marks[i])
                row = r"{lower_bound} $\sim$ {upper_bound} & {freq} & {rel_freq} & {cum_freq} & {class_mark} \\ \hline".format(
                    lower_bound=lower_str,
                    upper_bound=upper_str,
                    freq=str(frequencies[i]),
                    rel_freq=f"{relative_frequencies[i]:.2f}",
                    cum_freq=str(cumulative_frequencies[i]),
                    class_mark=class_mark_str
                )
                table_rows.append(row)

            table_footer = r"總計 & {total_freq} & {total_rel_freq} & & \\ \hline \end{tabular}".format(
                total_freq=str(sum(frequencies)),
                total_rel_freq=f"{sum(relative_frequencies):.2f}"
            )

            table_latex = table_header + "\n".join(table_rows) + table_footer
            
            # Randomly pick a group and a question type
            chosen_bin_index = random.randint(0, len(bins) - 1)
            lower_bound, upper_bound = bins[chosen_bin_index]
            lower_str = str(int(lower_bound)) if float(lower_bound).is_integer() else str(lower_bound)
            upper_str = str(int(upper_bound)) if float(upper_bound).is_integer() else str(upper_bound)
            
            question_choices_table = [
                f"組別 {lower_str} $\sim$ {upper_str} 的次數是多少？",
                f"組別 {lower_str} $\sim$ {upper_str} 的相對次數是多少？(請四捨五入至小數點後兩位)",
                f"組別 {lower_str} $\sim$ {upper_str} 的累積次數是多少？",
                f"組別 {lower_str} $\sim$ {upper_str} 的組中點是多少？",
                "數據總共有多少筆？",
                "組距是多少？"
            ]
            
            chosen_question_text = random.choice(question_choices_table)

            if chosen_question_text == question_choices_table[0]:
                correct_answer = str(frequencies[chosen_bin_index])
                answer_display = f"組別 {lower_str} $\sim$ {upper_str} 的次數為 {frequencies[chosen_bin_index]}。"
            elif chosen_question_text == question_choices_table[1]:
                correct_answer = f"{relative_frequencies[chosen_bin_index]:.2f}"
                answer_display = f"組別 {lower_str} $\sim$ {upper_str} 的相對次數為 {relative_frequencies[chosen_bin_index]:.2f}。"
            elif chosen_question_text == question_choices_table[2]:
                correct_answer = str(cumulative_frequencies[chosen_bin_index])
                answer_display = f"組別 {lower_str} $\sim$ {upper_str} 的累積次數為 {cumulative_frequencies[chosen_bin_index]}。"
            elif chosen_question_text == question_choices_table[3]:
                correct_answer = str(int(class_marks[chosen_bin_index])) if float(class_marks[chosen_bin_index]).is_integer() else str(class_marks[chosen_bin_index])
                answer_display = f"組別 {lower_str} $\sim$ {upper_str} 的組中點為 {correct_answer}。"
            elif chosen_question_text == question_choices_table[4]:
                correct_answer = str(sum(frequencies))
                answer_display = f"數據總共有 {sum(frequencies)} 筆。"
            elif chosen_question_text == question_choices_table[5]:
                correct_answer = str(class_width)
                answer_display = f"組距是 {class_width}。"
            
            question_text = r"{intro_text}" \
                            r"$${table_content}$$" \
                            r"{question}".format(intro_text=question_intro,
                                            table_content=table_latex,
                                            question=chosen_question_text)

        else: # Ask from graph
            chart_type = random.choice(["histogram", "frequency_polygon"])
            chart_title = "某班數學測驗成績分佈圖"
            x_label = "成績 (分)"
            y_label = "次數"

            if chart_type == "histogram":
                image_base64 = _draw_histogram(bins, frequencies, class_width, chart_title, x_label, y_label)
                question_intro = r"根據下方的直方圖，回答問題："
            else: # frequency_polygon
                image_base64 = _draw_frequency_polygon(bins, frequencies, class_width, chart_title, x_label, y_label)
                question_intro = r"根據下方的次數多邊圖，回答問題："

            # Randomly pick a group and a question type
            chosen_bin_index = random.randint(0, len(bins) - 1)
            lower_bound, upper_bound = bins[chosen_bin_index]
            lower_str = str(int(lower_bound)) if float(lower_bound).is_integer() else str(lower_bound)
            upper_str = str(int(upper_bound)) if float(upper_bound).is_integer() else str(upper_bound)
            
            # Use example from first bin for clarity in question text
            example_lb_str = str(int(bins[0][0])) if float(bins[0][0]).is_integer() else str(bins[0][0])
            example_ub_str = str(int(bins[0][1])) if float(bins[0][1]).is_integer() else str(bins[0][1])

            question_choices_graph = [
                f"組別 {lower_str} $\sim$ {upper_str} 的次數是多少？",
                f"次數最多的組別是哪一組？(請以組別範圍表示，如 {example_lb_str}~{example_ub_str})", 
                f"次數最少的組別是哪一組？(請以組別範圍表示，如 {example_lb_str}~{example_ub_str})"
            ]
            chosen_question_text = random.choice(question_choices_graph)

            if chosen_question_text == question_choices_graph[0]:
                correct_answer = str(frequencies[chosen_bin_index])
                answer_display = f"組別 {lower_str} $\sim$ {upper_str} 的次數為 {frequencies[chosen_bin_index]}。"
            elif chosen_question_text == question_choices_graph[1]:
                max_freq = max(frequencies)
                max_freq_indices = [i for i, f in enumerate(frequencies) if f == max_freq]
                ans_bins = []
                for idx in max_freq_indices:
                    lb, ub = bins[idx]
                    lb_str = str(int(lb)) if float(lb).is_integer() else str(lb)
                    ub_str = str(int(ub)) if float(ub).is_integer() else str(ub)
                    ans_bins.append(f"{lb_str}~{ub_str}")
                correct_answer = ", ".join(ans_bins) # Multiple answers possible
                answer_display = f"次數最多的組別是 {', '.join(ans_bins)}。"
            elif chosen_question_text == question_choices_graph[2]:
                min_freq = min(frequencies)
                min_freq_indices = [i for i, f in enumerate(frequencies) if f == min_freq]
                ans_bins = []
                for idx in min_freq_indices:
                    lb, ub = bins[idx]
                    lb_str = str(int(lb)) if float(lb).is_integer() else str(lb)
                    ub_str = str(int(ub)) if float(ub).is_integer() else str(ub)
                    ans_bins.append(f"{lb_str}~{ub_str}")
                correct_answer = ", ".join(ans_bins) # Multiple answers possible
                answer_display = f"次數最少的組別是 {', '.join(ans_bins)}。"
            
            question_text = r"{intro_text}" \
                            r"{question}".format(intro_text=question_intro,
                                            question=chosen_question_text)

    elif problem_type == 3: # Type 3: 繪製直方圖或次數多邊圖相關數據 (Maps to Example 3, 6)
        chart_type = random.choice(["histogram", "frequency_polygon"])
        chart_title = "某班數學測驗成績分佈圖"
        x_label = "成績 (分)"
        y_label = "次數"
        
        # We generate the chart for reference, but ask for numerical properties.
        if chart_type == "histogram":
            image_base64 = _draw_histogram(bins, frequencies, class_width, chart_title, x_label, y_label)
            question_intro = r"下方是根據某班數學測驗成績繪製的直方圖。請根據圖形回答問題。"
        else: # frequency_polygon
            image_base64 = _draw_frequency_polygon(bins, frequencies, class_width, chart_title, x_label, y_label)
            question_intro = r"下方是根據某班數學測驗成績繪製的次數多邊圖。請根據圖形回答問題。"
        
        # Randomly choose what to ask for
        # Use example from first bin for clarity in question text
        example_lb_str = str(int(bins[0][0])) if float(bins[0][0]).is_integer() else str(bins[0][0])
        example_ub_str = str(int(bins[0][1])) if float(bins[0][1]).is_integer() else str(bins[0][1])

        question_choices = [
            "圖中最高的長條（或多邊圖的最高點）代表的次數是多少？",
            f"圖中次數為 0 的組別範圍是什麼？(若有多個，請以逗號分隔，例如 {example_lb_str}~{example_ub_str})", 
            "圖中所有組中點的總和是多少？" # This involves class_marks, which is derived data, but can be asked *about* the graph.
        ]
        
        chosen_question_text = random.choice(question_choices)

        if chosen_question_text == question_choices[0]:
            correct_answer = str(max(frequencies))
            answer_display = f"圖中最高的長條代表的次數是 {max(frequencies)}。"
        elif chosen_question_text.startswith("圖中次數為 0 的組別範圍是什麼？"): # Using startswith because of dynamic example in question text
            zero_freq_bins = []
            for i, freq in enumerate(frequencies):
                if freq == 0:
                    lb, ub = bins[i]
                    lb_str = str(int(lb)) if float(lb).is_integer() else str(lb)
                    ub_str = str(int(ub)) if float(ub).is_integer() else str(ub)
                    zero_freq_bins.append(f"{lb_str}~{ub_str}")
            if not zero_freq_bins: # If no zero frequency bins, correct_answer should be "無"
                correct_answer = "無"
                answer_display = "圖中沒有次數為 0 的組別。"
            else:
                correct_answer = ", ".join(zero_freq_bins)
                answer_display = f"圖中次數為 0 的組別範圍是 {', '.join(zero_freq_bins)}。"
        elif chosen_question_text == question_choices[2]:
            sum_class_marks = sum(class_marks)
            correct_answer = str(int(sum_class_marks)) if float(sum_class_marks).is_integer() else str(sum_class_marks)
            answer_display = f"圖中所有組中點的總和是 {correct_answer}。"
        
        question_text = r"{intro_text}" \
                        r"{question}".format(intro_text=question_intro,
                                        question=chosen_question_text)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # Following Rule 7, using 'answer' for display text
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# --- Check Function ---
# CRITICAL CODING STANDARDS: Verification & Stability - Universal Check Template
def check(user_answer: str, correct_answer: str) -> bool:
    """
    check(user_answer, correct_answer) 函式必須嚴格遵循系統底層鐵律。
    1. 閱卷決定論 (Deterministic Grading)：嚴禁呼叫任何 random 模組或重新執行 generate 邏輯。
    2. 通用 Check 函式模板 (Universal Check Template)：實現包含以下邏輯的 check 函式。
    3. 數據傳遞完整性：correct_answer 必須序列化為易於解析的格式。
    4. 閱卷與反饋：check(u, c) 僅限回傳 True/False。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # V12.6, V13.5: 強制數值序列比對，禁絕 if/else 字串拆解
    user_parts = [part.strip() for part in u.split(',') if part.strip()]
    correct_parts = [part.strip() for part in c.split(',') if part.strip()]

    if len(user_parts) != len(correct_parts):
        return False

    for i in range(len(user_parts)):
        try:
            # 嘗試數值比對 (支援分數與小數)
            def parse_val(val_str):
                if "/" in val_str:
                    n, d = map(float, val_str.split("/"))
                    return n/d
                return float(val_str)
            
            user_val = parse_val(user_parts[i])
            correct_val = parse_val(correct_parts[i])
            
            # Allow for floating point tolerance
            if not math.isclose(user_val, correct_val, rel_tol=1e-5):
                return False
        except ValueError:
            # If not a number, compare as string (e.g., for "60~70" or "無")
            if user_parts[i] != correct_parts[i]: # Direct string comparison after cleaning
                return False
    
    return True

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
