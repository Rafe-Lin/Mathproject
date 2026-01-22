# ==============================================================================
# ID: jh_數學2上_CumulativeFrequencyDistributionAndLineChart
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 31.22s | RAG: 5 examples
# Created At: 2026-01-19 13:48:48
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


import re
from datetime import datetime
import base64
import matplotlib.pyplot as plt
import io

# Helper to convert plot to base64 (if ever needed, but image_base64 will be None for this skill)
def _plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

# --- Helper functions for data generation and calculation ---

def _generate_distribution_data():
    total_score_range = 100 # Max score for example (0-100分)
    
    # Choose a suitable interval width that divides the range reasonably
    possible_widths = [5, 10, 20]
    interval_width = random.choice(possible_widths)
    
    # Ensure num_intervals is at least 4 for meaningful distribution
    # Calculate initial num_intervals
    num_intervals = total_score_range // interval_width
    
    # If width is too large resulting in too few intervals, adjust width
    if num_intervals < 4: 
        # Fallback to smaller widths, ensuring at least 4 intervals
        if interval_width == 20:
            interval_width = random.choice([5, 10])
        elif interval_width == 10:
            interval_width = 5
        num_intervals = total_score_range // interval_width
    
    intervals = []
    current_start = 0
    for _ in range(num_intervals):
        current_end = current_start + interval_width
        intervals.append((current_start, current_end))
        current_start = current_end
    
    # Ensure the last interval covers up to total_score_range
    # This handles cases where total_score_range is not perfectly divisible by interval_width
    if intervals and intervals[-1][1] < total_score_range:
        intervals[-1] = (intervals[-1][0], total_score_range)
    elif intervals and intervals[-1][1] > total_score_range:
        intervals[-1] = (intervals[-1][0], total_score_range)
    # Edge case: If 0-100 and width 20, intervals are (0,20), (20,40), (40,60), (60,80), (80,100). This logic is fine.
    # If total_score_range is 100 and width is 15, intervals would be (0,15)...(90,105). Last interval becomes (90,100).

    # Generate frequencies
    frequencies = []
    min_freq_per_interval = 3
    max_freq_per_interval = 15

    for _ in range(len(intervals)): # Use len(intervals) as the actual number of intervals might change
        freq = random.randint(min_freq_per_interval, max_freq_per_interval)
        frequencies.append(freq)
    
    total_frequency = sum(frequencies)

    # Ensure total frequency is at least 20 for meaningful statistics
    while total_frequency < 20:
        idx = random.randint(0, len(intervals) - 1)
        frequencies[idx] += random.randint(1, 5) # Increase by a small random amount
        total_frequency = sum(frequencies)

    return intervals, frequencies, total_frequency

def _calculate_cumulative_frequencies(frequencies, total_frequency):
    cumulative_abs = []
    cumulative_rel = [] # in percentage
    current_cumulative_abs = 0
    for freq in frequencies:
        current_cumulative_abs += freq
        cumulative_abs.append(current_cumulative_abs)
        # Round to 2 decimal places for internal calculation, then to 1 for display if needed
        cumulative_rel.append(round((current_cumulative_abs / total_frequency) * 100, 2)) 
    return cumulative_abs, cumulative_rel

# --- Main functions ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4]) # 4 distinct problem types as per spec
    
    intervals, frequencies, total_frequency = _generate_distribution_data()
    cumulative_abs, cumulative_rel = _calculate_cumulative_frequencies(frequencies, total_frequency)

    question_text = ""
    correct_answer = ""
    image_base64 = None # Default to None, as per anti-leak protocol and spec

    # Prepare table data for question_text (only class intervals and frequencies)
    # [V16.55 Table Format Migration] Using Markdown Table
    question_table_rows = []
    question_table_rows.append(r"| 分數 (分) | 頻率 (人) |")
    question_table_rows.append(r"| :---: | :---: |")
    for i in range(len(intervals)):
        question_table_rows.append(r"| {start} ~ {end} | {freq} |".replace("{start}", str(intervals[i][0]))
                                                                   .replace("{end}", str(intervals[i][1]))
                                                                   .replace("{freq}", str(frequencies[i])))
    question_table_str = "\n".join(question_table_rows)

    # Randomly select an interval index to query for types 1, 3, 4
    query_idx = random.randint(0, len(intervals) - 1)
    
    if problem_type == 1: # Type 1 (Maps to Example 1): Calculate Absolute Cumulative Frequency
        question_template = r"下表為某班級數學小考分數的頻率分布表。請問分數在 ${upper_bound}$ 分以下的累積頻率是多少人？" + "\n\n" + "{question_table_str}" + "\n"
        
        upper_bound_query = str(intervals[query_idx][1])
        question_text = question_template.replace("{upper_bound}", upper_bound_query).replace("{question_table_str}", question_table_str)
        correct_answer = str(cumulative_abs[query_idx])

    elif problem_type == 2: # Type 2 (Maps to Example 2): Interpret a Cumulative Frequency
        sub_type = random.choice([1, 2])
        if sub_type == 1: # Ask for total frequency
            question_template = r"根據下表所示的頻率分布，請問本次數學小考的總人數是多少？" + "\n\n" + "{question_table_str}" + "\n"
            question_text = question_template.replace("{question_table_str}", question_table_str)
            correct_answer = str(total_frequency)
        else: # Ask for cumulative count up to a certain point
            upper_bound_query = str(intervals[query_idx][1])
            question_template = r"下表為某班級數學小考分數的頻率分布表。請問分數低於 ${upper_bound}$ 分的學生有多少人？" + "\n\n" + "{question_table_str}" + "\n"
            question_text = question_template.replace("{upper_bound}", upper_bound_query).replace("{question_table_str}", question_table_str)
            correct_answer = str(cumulative_abs[query_idx])

    elif problem_type == 3: # Type 3 (Maps to Example 3): Calculate Relative Cumulative Frequency
        question_template = r"下表為某班級數學小考分數的頻率分布表。請問分數在 ${upper_bound}$ 分以下的相對累積頻率是多少 \%？(請填入數字，四捨五入至小數點後一位)" + "\n\n" + "{question_table_str}" + "\n"
        
        upper_bound_query = str(intervals[query_idx][1])
        question_text = question_template.replace("{upper_bound}", upper_bound_query).replace("{question_table_str}", question_table_str)
        correct_answer = str(round(cumulative_rel[query_idx], 1)) 

    elif problem_type == 4: # Type 4 (Maps to Example 4): Reconstruct Original Frequency
        
        cumulative_table_rows = []
        cumulative_table_rows.append(r"| 分數 (分) | 累積頻率 (人) |")
        cumulative_table_rows.append(r"| :---: | :---: |")
        
        # Ensure query_idx logic is sound
        if len(intervals) > 1:
            query_idx = random.randint(0, len(intervals) - 1)
            if query_idx == 0 and len(intervals) > 1:
                 query_idx = random.randint(1, len(intervals) - 1)
        
        query_interval_str_latex = r"{start} \sim {end}".replace("{start}", str(intervals[query_idx][0])).replace("{end}", str(intervals[query_idx][1]))

        for i in range(len(intervals)):
            interval_str = f"{intervals[i][0]} ~ {intervals[i][1]}"
            if i <= query_idx: 
                cumulative_table_rows.append(r"| {interval_str} | {cum_abs} |".replace("{interval_str}", interval_str).replace("{cum_abs}", str(cumulative_abs[i])))
            else: 
                cumulative_table_rows.append(r"| {interval_str} | - |".replace("{interval_str}", interval_str)) 
        
        cumulative_table_str = "\n".join(cumulative_table_rows)

        question_template = r"下表為某班級數學小考分數的累積頻率分布表。請問分數介於 ${query_interval_str}$ 的學生有多少人？" + "\n\n" + "{cumulative_table_str}" + "\n"
        
        question_text = question_template.replace("{query_interval_str}", query_interval_str_latex).replace("{cumulative_table_str}", cumulative_table_str)
        
        if query_idx == 0:
            original_freq_at_idx = cumulative_abs[0]
        else:
            original_freq_at_idx = cumulative_abs[query_idx] - cumulative_abs[query_idx - 1]
        
        correct_answer = str(original_freq_at_idx)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # For internal use/redundancy as per spec
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # CRITICAL RULE: Robust Check Logic (V13.6 API Hardened Spec)
    # Input Sanitization using Regex
    cleaned_user_answer = re.sub(r'[^\d\.\-]+', '', str(user_answer)).strip()
    cleaned_correct_answer = re.sub(r'[^\d\.\-]+', '', str(correct_answer)).strip()

    try:
        user_num = float(cleaned_user_answer)
        correct_num = float(cleaned_correct_answer)
        
        # Support for multiple mathematical formats (e.g., 1/2 = 0.5)
        # For this skill, answers are typically single numbers (integers or decimals),
        # so direct float comparison with a small epsilon is sufficient for equivalence.
        return abs(user_num - correct_num) < 1e-6
    except ValueError:
        # If conversion to float fails, it's not a valid numerical answer
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
