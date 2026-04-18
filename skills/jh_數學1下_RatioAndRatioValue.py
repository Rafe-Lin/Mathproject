# ==============================================================================
# ID: jh_數學1下_RatioAndRatioValue
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 82.07s | RAG: 5 examples
# Created At: 2026-01-16 11:58:11
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
import json
import re

# Auxiliary functions as specified
def _get_gcd(a, b):
    """Calculates the Greatest Common Divisor of two integers."""
    # math.gcd handles non-negative integers. For 0,0 it returns 0.
    # For our simplification context, if both are 0, we can treat gcd as 1 to avoid division by zero later,
    # or handle it as a special case in simplification functions.
    if a == 0 and b == 0:
        return 1 # Conventionally, gcd(0,0) is undefined or 0. For simplification, 1 is safer.
    return math.gcd(abs(a), abs(b))

def _simplify_ratio_to_list(n1, n2):
    """
    Simplifies a ratio n1:n2 to its simplest integer form [sn1, sn2].
    Handles cases where n1 or n2 might be zero, or negative.
    Ensures consistent sign representation (second term positive if possible).
    """
    if n1 == 0 and n2 == 0:
        return [0, 0] # Represents an indeterminate ratio
    if n1 == 0:
        return [0, 1] # 0:N simplifies to 0:1
    if n2 == 0:
        return [n1, 0] # N:0 is often considered undefined, but for representation, keep as is.

    g = _get_gcd(n1, n2)
    
    simplified_n1 = n1 // g
    simplified_n2 = n2 // g

    # Ensure the second term (denominator-like) is positive if possible.
    # If both negative, make both positive. If only second negative, move sign to first.
    if simplified_n2 < 0:
        simplified_n1 = -simplified_n1
        simplified_n2 = -simplified_n2
        
    return [simplified_n1, simplified_n2]

def _simplify_fraction_to_list(numerator, denominator):
    """
    Simplifies a fraction numerator/denominator to its simplest form [snumerator, sdenominator].
    Handles negative numbers and ensures denominator is positive.
    """
    if denominator == 0:
        # Division by zero. In K12, this usually means an invalid problem.
        # Returning [numerator, 0] to indicate the form.
        return [numerator, 0] 
    if numerator == 0:
        return [0, 1] # 0/N simplifies to 0/1

    g = _get_gcd(numerator, denominator)
    
    simplified_num = numerator // g
    simplified_den = denominator // g

    # Ensure the denominator is positive
    if simplified_den < 0:
        simplified_num = -simplified_num
        simplified_den = -simplified_den
        
    return [simplified_num, simplified_den]


def generate(level=1):
    problem_type = random.choice(range(1, 6)) # Choose a type from 1 to 5
    question_text = ""
    correct_answer = ""
    answer = ""
    image_base64 = None

    if problem_type == 1:
        # Type 1 (Maps to Example 1): 從已知數量表示比 (Expressing Ratio from Given Quantities)
        # RAG Ex 1 asks for ratio (A:B), ratio value (A/B), and "how many times".
        # Spec for Type 1 focuses on "寫出它們的比 a:b", so output [a,b].
        contexts = [("男生", "女生"), ("鉛筆", "橡皮擦"), ("蘋果", "橘子"), ("巴奈的錢", "ACEF的錢"), ("BDF的球", "ACEF的球")]
        item_pair = random.choice(contexts)
        label1, label2 = item_pair

        num1 = random.randint(10, 50)
        num2 = random.randint(10, 50)
        while num1 == num2: # Ensure distinct values for a non-trivial ratio
            num2 = random.randint(10, 50)

        # Randomly choose the order of comparison (A:B or B:A)
        ask_order_is_1_to_2 = random.choice([True, False])

        if ask_order_is_1_to_2:
            ask_l1, ask_l2 = label1, label2
            target_n1, target_n2 = num1, num2
        else:
            ask_l1, ask_l2 = label2, label1
            target_n1, target_n2 = num2, num1
        
        question_text_template = r"某班級有 {n1} 位{l1}，{n2} 位{l2}。請問{ask_l1}與{ask_l2}的人數比是多少？"
        
        # Using .replace() for all dynamic parts, as specified
        question_text = question_text_template.replace("{n1}", str(num1))
        question_text = question_text.replace("{l1}", label1)
        question_text = question_text.replace("{n2}", str(num2))
        question_text = question_text.replace("{l2}", label2)
        question_text = question_text.replace("{ask_l1}", ask_l1)
        question_text = question_text.replace("{ask_l2}", ask_l2)
        
        correct_ratio_list = _simplify_ratio_to_list(target_n1, target_n2)
        # [V16.2] Correct Format: Return "a:b" string
        correct_answer = f"{correct_ratio_list[0]}:{correct_ratio_list[1]}"
        answer = correct_answer

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 「A是B的幾倍？」 (Ratio Value - "A is how many times B?")
        # RAG Ex 2: "精製酒精"是"純水"的幾倍？ -> 15/4 倍. Output format [numerator, denominator]
        # Adhering to "STRICT MAPPING" rule over Spec's description of "化簡比".
        
        # Contexts for items and units
        contexts = [
            ("精製酒精", "純水", "c.c."),
            ("巴奈的體重", "ACEF的體重", "公斤"),
            ("甲班人數", "乙班人數", "人"),
            ("鉛筆長度", "橡皮擦長度", "公分")
        ]
        item_unit_tuple = random.choice(contexts)
        item_a_label, item_b_label, unit_label = item_unit_tuple

        val_a = random.randint(100, 500)
        val_b = random.randint(50, 200)
        while val_b == 0: # Ensure denominator is not zero
            val_b = random.randint(50, 200)
        
        question_text_template = r"在某情境中，有 {val_a} {unit} 的{item_a} 和 {val_b} {unit} 的{item_b}。請問{item_a}的量是{item_b}的幾倍？"
        
        question_text = question_text_template.replace("{val_a}", str(val_a))
        question_text = question_text.replace("{unit}", unit_label)
        question_text = question_text.replace("{item_a}", item_a_label)
        question_text = question_text.replace("{val_b}", str(val_b))
        question_text = question_text.replace("{item_b}", item_b_label)
        
        correct_fraction_list = _simplify_fraction_to_list(val_a, val_b)
        # [V16.2] Correct Format: Return "a/b" or "a" string
        if correct_fraction_list[1] == 1:
            correct_answer = str(correct_fraction_list[0])
        else:
            correct_answer = f"{correct_fraction_list[0]}/{correct_fraction_list[1]}"
        answer = correct_answer

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): 比值 (Ratio Value - Batting Average as Decimal)
        # RAG Ex 3: 打擊率=安打數/打數 (0.25). Adhering to "STRICT MAPPING" rule.
        
        player_name = random.choice(["大魁", "小明", "巴奈", "ACEF"])
        
        # Generate numbers that yield a clean decimal for level 1
        possible_ratios = [(1, 4), (1, 5), (1, 2), (3, 4), (2, 5), (3, 5)] # For simple decimals/fractions
        chosen_ratio = random.choice(possible_ratios)
        base_hit, base_at_bat = chosen_ratio
        
        multiplier = random.randint(5, 15) # To scale up numbers
        
        hit_num = base_hit * multiplier
        at_bats = base_at_bat * multiplier
        
        # Ensure at_bats are within reasonable range for K12 and larger than hit_num
        while at_bats > 150 or at_bats < hit_num + 5: # At least 5 more at-bats than hits
            multiplier = random.randint(5, 15)
            hit_num = base_hit * multiplier
            at_bats = base_at_bat * multiplier

        batting_avg_float = hit_num / at_bats
        
        question_text_template = r"某職棒選手 {player_name} 在最近 {at_bats} 次打數中，共擊出 {hit_num} 支安打。請問該選手這段期間的打擊率為多少？ (註：打擊率=「安打數」與「打數」的比值，通常以小數表示)"
        
        question_text = question_text_template.replace("{player_name}", player_name)
        question_text = question_text.replace("{at_bats}", str(at_bats))
        question_text = question_text.replace("{hit_num}", str(hit_num))
        
        # [V16.2] Correct Format: Return plain value string
        correct_answer = str(round(batting_avg_float, 3)) 
        answer = correct_answer


    elif problem_type == 4:
        # Type 4 (Maps to Example 4): 比例求解未知數 (Solving for Unknown in a Rate Problem)
        # RAG Ex 4: `made_shots / total_shots = hit_rate_percentage`, solve for `total_shots`.
        # Adhering to "STRICT MAPPING" rule.
        
        player_name = random.choice(["大魁", "小花", "巴奈", "BDF"])
        
        # Generate a hit rate that results in integer total shots
        possible_rates = [60, 70, 75, 80, 50, 40, 25] # Common percentages
        hit_rate_percent = random.choice(possible_rates)
        
        # Generate total_shots first, then calculate made_shots
        total_shots = random.randint(20, 60)
        
        # Ensure made_shots is an integer
        made_shots_float = total_shots * hit_rate_percent / 100
        while not made_shots_float.is_integer() or made_shots_float == 0:
            total_shots = random.randint(20, 60)
            made_shots_float = total_shots * hit_rate_percent / 100
        
        made_shots = int(made_shots_float)
        
        question_text_template = r"在某次投籃比賽中，{player_name} 共投了 x 球，且投進 {made_shots} 球。已知此次比賽中，{player_name} 投籃的命中率為 {hit_rate}%，則他的總投球數為多少球？ (註：命中率=「投進球數」與「總投球數」的比值，通常以百分率表示)"
        
        question_text = question_text_template.replace("{player_name}", player_name)
        question_text = question_text.replace("{made_shots}", str(made_shots))
        question_text = question_text.replace("{hit_rate}", str(hit_rate_percent))
        
        # [V16.2] Correct Format: Return plain value string
        correct_answer = str(total_shots)
        answer = correct_answer


    elif problem_type == 5:
        # Type 5 (Maps to Example 5): 尋找等比中的未知數 (Finding Unknown in an Equivalent Ratio)
        # Model: a:b = c:x, solve for x.
        
        val_a = random.randint(2, 10)
        val_b = random.randint(2, 10)
        while val_a == val_b: # Ensure distinct values for a non-trivial ratio
            val_b = random.randint(2, 10)
        
        multiplier = random.randint(2, 5) # Multiplier to create the equivalent ratio
        
        val_c = val_a * multiplier
        x_value = val_b * multiplier
        
        question_text_template = r"若 $ {a_val}:{b_val} = {c_val}:x $，請求出 $ x $ 的值。"
        
        question_text = question_text_template.replace("{a_val}", str(val_a))
        question_text = question_text.replace("{b_val}", str(val_b))
        question_text = question_text.replace("{c_val}", str(val_c))
        
        # [V16.2] Correct Format: Return plain value string
        correct_answer = str(x_value)
        answer = correct_answer

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64,
    }


# Coder must verbatim copy the check function and its helper
def _parse_and_normalize_ratio_or_fraction(input_str):
    """
    Parses a string like 'a:b' or 'a/b' and returns a simplified list [n1, n2].
    If parsing fails or it's not a ratio/fraction, returns None.
    Handles integer simplification for K12 context.
    """
    parts = re.split(r'[:/]', input_str)
    if len(parts) == 2:
        try:
            n1_float = float(parts[0])
            n2_float = float(parts[1])

            # V13.5 整數優先: 如果可以轉換為整數，則使用整數進行處理
            if n1_float.is_integer() and n2_float.is_integer():
                n1_int, n2_int = int(n1_float), int(n2_float)
                if n2_int == 0:
                    # 分母為零的特殊情況，直接返回，讓後續比較判斷
                    return [n1_int, n2_int]
                g = math.gcd(n1_int, n2_int)
                return [n1_int // g, n2_int // g]
            else:
                # 如果包含浮點數，則直接返回浮點數列表
                return [n1_float, n2_float]
        except ValueError:
            pass # Not valid numbers in ratio/fraction format
    return None


# --- 4. Answer Checker [V16.2 Ratio Fix] ---
def check(user_answer, correct_answer):
    """
    [V16.2 Ratio Fix]
    支援「比 (a:b)」、「分數 (a/b)」、「小數/整數」的寬容比對。
    自動根據 correct_answer 的格式決定比對模式：
    - 若 correct_answer 包含 ':'，則視為「比」，檢查交叉相乘是否相等 (a:b == c:d => ad == bc)。
    - 否則視為「數值」，檢查數值是否相等 (容許誤差)。
    """
    if user_answer is None: return False
    
    # Pre-processing: Clean strings
    def clean_str(s):
        return str(s).strip().replace(" ", "")

    u_str = clean_str(user_answer)
    c_str = clean_str(correct_answer)

    # Helper to parse "a:b" or "a/b" into (n1, n2) or float
    # Returns (val, is_ratio_pair)
    # is_ratio_pair is True if it parsed as a tuple (n1, n2)
    # is_ratio_pair is False if it parsed as a single float value
    def parse_val(s):
        # Remove non-numeric chars except : / . -
        # simplified cleanup
        s = re.sub(r'[^\d\.\:\/\-]', '', s)
        
        # Try splitting by ':'
        if ':' in s:
            parts = s.split(':')
            if len(parts) == 2:
                try:
                    return (float(parts[0]), float(parts[1])), True
                except: pass
        
        # Try splitting by '/'
        # Note: "a/b" can be a fraction (value) or ratio.
        # We will parse it as a pair (n, d) but treat it flexibly.
        if '/' in s:
             parts = s.split('/')
             if len(parts) == 2:
                 try:
                     return (float(parts[0]), float(parts[1])), True
                 except: pass
        
        # Try as single float
        try:
            return float(s), False
        except:
            return None, False

    c_val, c_is_pair = parse_val(c_str)
    if c_val is None:
        # Fallback for some edge cases or string matches if not numeric
        return u_str == c_str

    u_val, u_is_pair = parse_val(u_str)
    if u_val is None:
        return False

    # Comparison Logic
    
    # Case 1: Correct answer is a Ratio/Pair (e.g., "3:4" or "3/4" represented as simple fraction)
    # Note: Check explicitly for ':' in original correct string to enforce ratio logic if needed.
    # But usually, 3:4 and 3/4 are comparable in value, but context matters.
    # The requirement says: "a:b" vs "a/b" vs "decimal".
    # Let's use Cross Product for any Pair vs Pair comparison.
    
    if c_is_pair and u_is_pair:
        # (c1, c2) vs (u1, u2) => c1*u2 == c2*u1
        return math.isclose(c_val[0] * u_val[1], c_val[1] * u_val[0], rel_tol=1e-7)
    
    elif not c_is_pair and not u_is_pair:
        # Scalar vs Scalar
        return math.isclose(c_val, u_val, rel_tol=1e-7)
        
    elif c_is_pair and not u_is_pair:
        # Correct is Pair (3:4), User is Scalar (0.75)
        # Ratio Value check: c1/c2 == u
        if c_val[1] == 0: return False # Defined ratio shouldn't have 0 den
        return math.isclose(c_val[0] / c_val[1], u_val, rel_tol=1e-7)
        
    elif not c_is_pair and u_is_pair:
        # Correct is Scalar (0.75), User is Pair (3:4 or 3/4)
        if u_val[1] == 0: return False
        return math.isclose(c_val, u_val[0] / u_val[1], rel_tol=1e-7)

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
