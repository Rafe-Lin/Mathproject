# ==============================================================================
# ID: jh_數學2上_RelativeAndCumulativeRelativeFrequencyDistributionAndLineChart
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 46.63s | RAG: 5 examples
# Created At: 2026-01-19 13:49:35
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


import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# V13.6 API Hardened Spec: Arrow Ban - using ax.plot for arrows
# V10.2 Pure Style: Coordinate axis labeling, grid, and aspect ratio
# V13.5 Final Hardening: Labels isolated, integers handled, no complex check logic
# V13.0 Coordinate Teaching Logic: Labeling permissions isolated, format precision
# V13.1 Teaching Correctness: Labels pure
# V17 Critical Rule: Visual Solvability - ensure ticks and labels are visible

def _draw_line_chart(class_midpoints, data_values, chart_title, x_label, y_label, total_students=None, is_cumulative=False):
    """
    Helper function to draw a line chart for frequency or relative frequency distribution.
    [防洩漏原則]: 僅接收題目已知數據，嚴禁傳入答案數據。
    [視覺一致性]: 確保網格顯示，坐標軸標註清晰。
    [視覺可解性]: 必須有明確的刻度數字標示。
    [V13.6 Arrow Ban]: 使用 ax.plot 繪製箭頭。
    [V11.6 ULTRA VISUAL STANDARDS]: Resolution dpi=300.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(class_midpoints, data_values, marker='o', linestyle='-', color='blue')

    ax.set_title(chart_title, fontsize=16)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    # V17 Critical Rule: Visual Solvability - Ensure x-axis and y-axis have integer labels visible
    # V13.0 Grid Alignment: Coordinate axis range must be symmetric and wide
    min_x, max_x = min(class_midpoints), max(class_midpoints)
    x_range_buffer = (max_x - min_x) * 0.1
    ax.set_xlim(min_x - x_range_buffer, max_x + x_range_buffer)
    ax.set_xticks(class_midpoints) # Ensure midpoints are ticks

    min_y, max_y = 0, max(data_values) * 1.2
    if is_cumulative: # Cumulative relative frequency goes up to 100%
        max_y = 105
    elif total_students: # Max frequency can be total_students (though data_values here are percentages)
        # If data_values are frequencies, max_y would be total_students * 1.2
        # But here data_values are already percentages, so use percentage scaling.
        max_y = max(data_values) * 1.2 if max(data_values) * 1.2 > 1 else 10 # Ensure a minimum y_range if all are 0
        if max_y < 20: max_y = 20 # Ensure enough room for small percentages

    ax.set_ylim(0, max_y)

    # Dynamically set y-ticks based on max_y
    if is_cumulative:
        ax.set_yticks(np.arange(0, 101, 10)) # 0% to 100% in 10% increments
    elif max_y <= 20:
        ax.set_yticks(np.arange(0, int(max_y) + 1, 2))
    elif max_y <= 100:
        ax.set_yticks(np.arange(0, int(max_y) + 1, 10))
    else:
        ax.set_yticks(np.arange(0, int(max_y) + 1, int(max_y / 10) if max_y / 10 > 1 else 10))

    ax.grid(True, linestyle='--', alpha=0.6)
    # V10.2 Pure Style: No specific "0" label for line charts, but general tick labels are crucial.
    # V10.2 Pure Style: ax.set_aspect('auto') for line charts as x and y axes represent different scales.
    ax.set_aspect('auto') # As per previous internal decision for line charts

    # V13.6 API Hardened Spec: Arrow Ban - use ax.plot for arrows
    # Draw arrows on axes
    # The transform makes it relative to the axis limits, clip_on=False allows drawing outside the plot area
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False) # X-axis arrow
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False) # Y-axis arrow

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # Added dpi=300 as per V11.6
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _generate_frequency_data(num_classes, total_students, start_value, class_width):
    """
    Helper function to generate frequency distribution data.
    [數據禁絕常數]: 所有數據隨機生成。
    """
    class_intervals = []
    class_midpoints = []
    for i in range(num_classes):
        lower = start_value + i * class_width
        upper = lower + class_width
        class_intervals.append(f"{lower}~{upper-1}") # Assuming integer scores
        class_midpoints.append((lower + upper -1) / 2) # Midpoint for line chart

    frequencies = [0] * num_classes
    
    # Distribute total_students into frequencies ensuring each class has at least 1 if possible
    if total_students >= num_classes:
        remaining_students = total_students
        for i in range(num_classes):
            if i < num_classes - 1:
                min_freq = 1 # Each class must have at least 1 student
                max_freq = remaining_students - (num_classes - 1 - i) # Leave at least 1 for remaining classes
                if max_freq < min_freq: max_freq = min_freq
                
                freq = random.randint(min_freq, max_freq)
                frequencies[i] = freq
                remaining_students -= freq
            else:
                frequencies[i] = remaining_students # Last class gets remaining
        
        # Shuffle to avoid a pattern if all are >= 1
        random.shuffle(frequencies)
        
        # Re-verify sum after shuffle, and adjust if necessary (unlikely if initial distribution was good)
        current_sum = sum(frequencies)
        if current_sum != total_students:
            diff = total_students - current_sum
            # Simple adjustment: add/subtract from a random class
            if diff > 0:
                for _ in range(diff):
                    frequencies[random.randint(0, num_classes - 1)] += 1
            elif diff < 0:
                for _ in range(abs(diff)):
                    idx = random.randint(0, num_classes - 1)
                    while frequencies[idx] <= 1: # Ensure frequency doesn't drop below 1
                        idx = random.randint(0, num_classes - 1)
                    frequencies[idx] -= 1
    else: # total_students < num_classes, some frequencies must be 0
        frequencies = [0] * num_classes
        for _ in range(total_students):
            frequencies[random.randint(0, num_classes - 1)] += 1

    return class_intervals, class_midpoints, frequencies

def _calculate_relative_and_cumulative(frequencies, total_students):
    """
    Helper function to calculate relative and cumulative relative frequencies.
    """
    relative_frequencies_percent = [(f / total_students) * 100 for f in frequencies]
    cumulative_relative_frequencies_percent = []
    cumulative_sum = 0
    for rf in relative_frequencies_percent:
        cumulative_sum += rf
        cumulative_relative_frequencies_percent.append(cumulative_sum)
    return relative_frequencies_percent, cumulative_relative_frequencies_percent

def generate(level=1):
    # MANDATORY MIRRORING RULES: STRICT MAPPING to RAG Ex 1, 2, 3 (and 4, 5 for Type 3 chart interpretation)
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""
    image_base64 = None
    created_at = datetime.now().isoformat()
    version = "1.0"

    num_classes = random.randint(4, 6) # V14. Data Prohibition: Random classes
    total_students = random.choice([i * 10 for i in range(5, 12)]) # V14. Data Prohibition: Random total students, multiples of 10 (e.g., 50, 60, ..., 110)
    class_width = random.choice([5, 10, 15]) # V14. Data Prohibition: Random class width
    start_value = random.choice([i * 10 for i in range(5, 8)]) # V14. Data Prohibition: Random start value (e.g., 50, 60, 70)

    class_intervals, class_midpoints, frequencies = _generate_frequency_data(num_classes, total_students, start_value, class_width)
    relative_frequencies_percent, cumulative_relative_frequencies_percent = _calculate_relative_and_cumulative(frequencies, total_students)

    # Build the frequency table string
    table_header = r"| 級距 (分) | 次數 (人) | 相對次數 (%) | 累積相對次數 (%) |"
    table_separator = r"|:---------:|:---------:|:------------:|:-----------------:|"
    table_rows = []
    for i in range(num_classes):
        # V13.5 Final Hardening: Ensure integers are formatted as such
        interval_str = class_intervals[i]
        freq_str = str(int(frequencies[i]))
        rf_str = f"{relative_frequencies_percent[i]:.1f}" if relative_frequencies_percent[i] % 1 != 0 else str(int(relative_frequencies_percent[i]))
        crf_str = f"{cumulative_relative_frequencies_percent[i]:.1f}" if cumulative_relative_frequencies_percent[i] % 1 != 0 else str(int(cumulative_relative_frequencies_percent[i]))
        table_rows.append(f"| {interval_str} | {freq_str} | {rf_str} | {crf_str} |")
    full_table_md = "\n".join([table_header, table_separator] + table_rows)


    if problem_type == 1: # Type 1: Maps to RAG Ex 1 (Calculate Relative/Cumulative Frequency from Table)
        # Ask for a specific relative frequency or cumulative relative frequency
        target_index = random.randint(0, num_classes - 1)
        target_interval = class_intervals[target_index]

        if random.choice([True, False]): # Ask for relative frequency
            question_text = f"以下是某班學生數學成績的次數分配表。\n{full_table_md}\n\n試問，成績在 ${target_interval}$ 分這一級距的**相對次數**是多少？(請以百分比表示，取到小數點後一位)"
            correct_answer_val = relative_frequencies_percent[target_index]
            correct_answer = f"{correct_answer_val:.1f}" if correct_answer_val % 1 != 0 else str(int(correct_answer_val))
        else: # Ask for cumulative relative frequency

            # For "未滿 X 分", it's the cumulative relative frequency up to the *previous* interval's upper bound, or current interval if it implies "up to and including"
            # To be precise with "未滿 X 分", we should pick an interval and ask for students *below its upper bound*.
            # The cumulative_relative_frequencies_percent[target_index] is "up to and including" the target_interval.
            # Let's adjust for "未滿":
            if target_index == 0:
                # If asking for "未滿" the upper bound of the first class, it's 0%
                correct_answer_val = 0.0
                cutoff_score = class_intervals[0].split('~')[0]
                question_text = f"以下是某班學生數學成績的次數分配表。\n{full_table_md}\n\n試問，成績未滿 {cutoff_score} 分的學生，占全班人數的百分比 ( % ) 為多少？(請取到小數點後一位)"
            else:
                # Ask for "未滿" the upper bound of the *current* interval, which is the cumulative up to the *previous* interval's upper bound.
                correct_answer_val = cumulative_relative_frequencies_percent[target_index-1]
                cutoff_score = target_interval.split('~')[0]
                question_text = f"以下是某班學生數學成績的次數分配表。\n{full_table_md}\n\n試問，成績未滿 {cutoff_score} 分的學生，占全班人數的百分比 ( % ) 為多少？(請取到小數點後一位)"
            correct_answer = f"{correct_answer_val:.1f}" if correct_answer_val % 1 != 0 else str(int(correct_answer_val))


    elif problem_type == 2: # Type 2: Maps to RAG Ex 2 (Find Missing Value from Partial Table) - simplified to single table missing value
        # Hide one frequency value (X) and ask for it.
        hidden_index = random.randint(0, num_classes - 1)
        
        # Create a modified table with X
        modified_table_rows = []
        for i in range(num_classes):
            interval_str = class_intervals[i]
            freq_str = "X" if i == hidden_index else str(int(frequencies[i]))
            rf_str = f"{relative_frequencies_percent[i]:.1f}" if relative_frequencies_percent[i] % 1 != 0 else str(int(relative_frequencies_percent[i]))
            crf_str = f"{cumulative_relative_frequencies_percent[i]:.1f}" if cumulative_relative_frequencies_percent[i] % 1 != 0 else str(int(cumulative_relative_frequencies_percent[i]))
            modified_table_rows.append(f"| {interval_str} | {freq_str} | {rf_str} | {crf_str} |")
        modified_table_md = "\n".join([table_header, table_separator] + modified_table_rows)

        question_text = f"以下是某班學生數學成績的次數分配表，已知全班共有 {total_students} 人。\n{modified_table_md}\n\n試求出 $X$ 的值。"
        correct_answer = str(int(frequencies[hidden_index]))

    elif problem_type == 3: # Type 3: Maps to RAG Ex 3, 4, 5 (Interpret a Line Chart)
        # Generate a line chart and ask an interpretation question.
        chart_type = random.choice(["relative", "cumulative_relative"])
        
        if chart_type == "relative":
            chart_title = "某班學生數學成績相對次數折線圖"
            y_label = "相對次數 (%)"
            data_to_plot = relative_frequencies_percent
            question_type = random.choice(["range_percentage", "count_in_range"])
            
            if question_type == "range_percentage":
                # Ask percentage in a range
                idx1 = random.randint(0, num_classes - 2)
                idx2 = random.randint(idx1 + 1, num_classes - 1)
                lower_bound = class_intervals[idx1].split('~')[0]
                upper_bound = class_intervals[idx2].split('~')[1]
                
                # Sum relative frequencies for the range (inclusive of idx1 to idx2)
                # Sum relative frequencies for the range (inclusive of idx1 to idx2)
                sum_rf = sum(relative_frequencies_percent[idx1 : idx2 + 1])
                
                # [V16.56 Pre-calculation Fix]
                upper_bound_val = int(upper_bound) + 1
                question_text = f"以下是某班學生數學成績的相對次數折線圖。\n\n試問，成績在 ${lower_bound}$ 分以上 (含)，未滿 ${upper_bound_val}$ 分的學生，佔全班的百分比是多少？(請取到小數點後一位)"
                correct_answer_val = sum_rf
                correct_answer = f"{correct_answer_val:.1f}" if correct_answer_val % 1 != 0 else str(int(correct_answer_val))

            else: # count_in_range
                # Ask count in a specific interval
                idx = random.randint(0, num_classes - 1)
                target_interval = class_intervals[idx]
                
                question_text = f"以下是某班學生數學成績的相對次數折線圖，已知全班共有 {total_students} 人。\n\n試問，成績在 ${target_interval}$ 分這一級距的學生有多少人？(請取整數)"
                correct_answer_val = (relative_frequencies_percent[idx] / 100) * total_students
                correct_answer = str(int(round(correct_answer_val))) # V13.5 Final Hardening: Ensure integer output

            image_base64 = _draw_line_chart(class_midpoints, data_to_plot, chart_title, "成績 (分)", y_label, total_students=total_students)

        else: # cumulative_relative
            chart_title = "某班學生數學成績累積相對次數折線圖"
            y_label = "累積相對次數 (%)"
            data_to_plot = cumulative_relative_frequencies_percent
            
            target_index = random.randint(0, num_classes - 1)
            target_upper_bound_str = class_intervals[target_index].split('~')[1]
            
            # [V16.56 Pre-calculation Fix]
            target_upper_val = int(target_upper_bound_str) + 1
            question_text = f"以下是某班學生數學成績的累積相對次數折線圖。\n\n試問，成績未滿 ${target_upper_val}$ 分的學生，佔全班的百分比是多少？(請取到小數點後一位)"
            correct_answer_val = cumulative_relative_frequencies_percent[target_index]
            correct_answer = f"{correct_answer_val:.1f}" if correct_answer_val % 1 != 0 else str(int(correct_answer_val))
            
            image_base64 = _draw_line_chart(class_midpoints, data_to_plot, chart_title, "成績 (分)", y_label, is_cumulative=True)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # This field is typically for student's answer in a full system
        "image_base64": image_base64,
        "created_at": created_at,
        "version": version
    }

def check(user_answer_raw, correct_answer_raw):
    """
    [強韌閱卷邏輯]: 具備輸入清洗與等價性判斷能力。
    [V13.5 禁絕複雜比對]: 統一使用數字序列比對。
    [V13.6 Exact Check Logic]: 逐字複製 4-line check logic。
    [閱卷與反饋]: check(u, c) 僅限回傳 True/False。
    """
    # 1. Input Sanitization (Regex to remove LaTeX, variables, spaces)
    user_answer = re.sub(r'[$\\\{\}x=y=k=Ans:\s]', '', str(user_answer_raw)).strip()
    correct_answer = re.sub(r'[$\\\{\}x=y=k=Ans:\s]', '', str(correct_answer_raw)).strip()

    # 2. Robust Check Logic - Numerical Sequence Comparison
    # Split by common delimiters for multiple answers (e.g., "3,4" or "3 4")
    user_parts = re.split(r'[,;\s]+', user_answer)
    correct_parts = re.split(r'[,;\s]+', correct_answer)

    if len(user_parts) != len(correct_parts):
        return False

    for u_part, c_part in zip(user_parts, correct_parts):
        try:
            # V12.6 Forced Operation: Convert to float for numerical equivalence
            # Allow for minor floating point differences (e.g., due to rounding)
            if abs(float(u_part) - float(c_part)) > 1e-5: # Increased tolerance slightly for .1f questions
                return False
        except ValueError:
            # If conversion to float fails for any part, it's not a match
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
