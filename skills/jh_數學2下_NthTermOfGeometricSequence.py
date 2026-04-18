# ==============================================================================
# ID: jh_數學2下_NthTermOfGeometricSequence
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 44.53s | RAG: 5 examples
# Created At: 2026-01-19 16:02:19
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
from fractions import Fraction

# --- Helper Functions ---

def _generate_fraction(max_val=10, allow_negative=True):
    """
    用途: 生成一個非整數的有理數（真分數）。
    邏輯:
        - 隨機生成 numerator (1 到 denominator - 1) 和 denominator (2 到 max_val)。
        - 確保 numerator < denominator (真分數)。
        - 簡化分數：使用 math.gcd 找到最大公約數並約分。
        - 隨機決定正負號（如果 allow_negative 為 True）。
    回傳值: (float_value, latex_string)，例如 (0.5, r"\frac{1}{2}") 或 (-0.25, r"-\frac{1}{4}")。
    """
    denominator = random.randint(2, max_val)
    numerator = random.randint(1, denominator - 1) # Guarantees proper fraction

    gcd_val = math.gcd(numerator, denominator)
    numerator //= gcd_val
    denominator //= gcd_val

    float_val = Fraction(numerator, denominator)
    latex_string = r"\frac{" + str(numerator) + r"}{" + str(denominator) + r"}"

    if allow_negative and random.choice([True, False]):
        float_val *= -1
        latex_string = r"-" + latex_string

    return (float(float_val), latex_string)

def _format_number_for_display(num):
    """
    用途: 將數字格式化為適合在 question_text 中顯示的字串（整數、真分數或帶分數）。
    邏輯:
        - 如果 num 是整數或可精確表示為整數的浮點數，回傳 str(int(num))。
        - 否則，使用 fractions.Fraction 轉換為分數。
        - 【禁絕假分數】: 如果是假分數，必須轉換為帶分數的 LaTeX 格式 (例如 1\frac{1}{2})。
        - 如果是真分數，則為 \frac{num}{den} 格式。
        - 若無法精確表示為分數，則保留浮點數格式，限制小數位數 (例如三位)。
    回傳值: str。
    """
    # Check if it's an integer
    if num == int(num):
        return str(int(num))
    
    # Try to convert to Fraction
    try:
        frac = Fraction(num).limit_denominator(1000) # Limit denominator to prevent very complex fractions
        if frac.denominator == 1:
            return str(frac.numerator)

        sign = "-" if num < 0 else ""
        abs_frac = Fraction(abs(num))
        
        whole_part = abs_frac.numerator // abs_frac.denominator
        remainder_numerator = abs_frac.numerator % abs_frac.denominator
        
        if remainder_numerator == 0: # Should be caught by frac.denominator == 1, but for safety
            return str(int(num))
        
        if whole_part == 0: # Proper fraction
            return sign + r"\frac{" + str(remainder_numerator) + r"}{" + str(abs_frac.denominator) + r"}"
        else: # Mixed fraction
            return sign + str(whole_part) + r"\frac{" + str(remainder_numerator) + r"}{" + str(abs_frac.denominator) + r"}"
    except (TypeError, ValueError):
        # Fallback for non-representable floats (should be rare with current generation logic)
        return f"{num:.3f}"

def _format_answer_value(val):
    """
    將數值格式化為純數據字串，以供 correct_answer 欄位使用。
    分數格式為 "num/den"，整數則為 "integer"。
    """
    try:
        frac = Fraction(val).limit_denominator(1000)
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"{frac.numerator}/{frac.denominator}"
    except (TypeError, ValueError):
        # Fallback for floats that can't be perfectly represented as fractions
        return str(val)

# --- Main Functions ---

def generate(level=1):
    """
    生成等比數列的第 n 項問題。
    根據 level 選擇不同類型的問題。
    [V17.4 Safety Update]: Enforce strict limits on r, n, and a1 to prevent data explosion.
    """
    problem_type = random.choice([1, 2, 3, 4]) # Maps to RAG Ex 1, 2, 3, 5

    question_text = ""
    correct_answer_val = None

    # [V17.4 Constraint: Allowed Common Ratios]
    # Lock allowed values for common ratio r.
    # Integers: +/- 2, 3, 4
    # Simple Fractions: +/- 1/2, 1/3, 1/4
    allowed_r_vals = [
        2, 3, 4, -2, -3,
        Fraction(1, 2), Fraction(1, 3), Fraction(1, 4),
        Fraction(-1, 2), Fraction(-1, 3)
    ]

    # Helper to get safe n limit based on r
    def get_max_n(r_val):
        if abs(r_val) >= 2:
            return 6 # Integer r >= 2, max n=6 (e.g., 4^5 = 1024)
        else:
            return 5 # Fraction r < 1, max n=5 (e.g., (1/4)^4 = 1/256)

    # Helper to get safe a1
    # [V17.4 Constraint]: a1 integer within [-10, 10] or simple fraction compatible with r
    def get_safe_a1(r_val):
        # 80% integer a1
        if random.random() < 0.8:
            val = random.randint(-10, 10)
            while val == 0: val = random.randint(-10, 10)
            return val
        else:
            # 20% fraction a1, related to r's denominator or numerator
            # e.g. if r=1/2, a1 could be k*2 or something to make term integer
            # But requirement says a1 is simple fraction.
            # Let's just pick small fraction.
            den = random.randint(2, 5)
            num = random.randint(1, den-1)
            val = Fraction(num, den) * random.choice([1, -1])
            return val

    if problem_type == 1:
        # Type 1 (Maps to Example 1): 已知首項與公比，求第 n 項。
        r_val = random.choice(allowed_r_vals)
        a1_val = get_safe_a1(r_val)
        
        max_n = get_max_n(r_val)
        n_val = random.randint(4, max_n)

        # Calculate a_n
        correct_answer_val = Fraction(a1_val) * (Fraction(r_val)**(n_val - 1))

        a1_str = _format_number_for_display(a1_val)
        r_str = _format_number_for_display(r_val)
        
        # [V17.3 LaTeX Wrapper Fix]: Ensure all variables are wrapped in $
        question_template = r"一個等比數列的首項為 $a_1 = {a1_str}$，公比為 $r = {r_str}$，試求此數列的第 ${n_val}$ 項。"
        question_text = question_template.replace("{a1_str}", a1_str).replace("{r_str}", r_str).replace("{n_val}", str(n_val))

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 已知兩項 (非首項)，求公比。 (r > 0)
        # Filter allowed_r_vals for positive only
        pos_r_vals = [r for r in allowed_r_vals if r > 0 and r != 1] # already allowed_r doesn't have 1
        r_val = random.choice(pos_r_vals)
        a1_val = get_safe_a1(r_val)

        max_n = get_max_n(r_val)
        # Ensure distinct indices within safe range
        # Pick start index m (small)
        m_val = random.randint(2, max_n - 1)
        # Pick end index n > m
        possible_n = [x for x in range(m_val + 1, max_n + 1)]
        if not possible_n: # adjust m if needed
             m_val = random.randint(2, 3) 
             possible_n = [x for x in range(m_val + 1, max_n + 1)]
        n_val = random.choice(possible_n)

        a_m_val = Fraction(a1_val) * (Fraction(r_val)**(m_val - 1))
        a_n_val = Fraction(a1_val) * (Fraction(r_val)**(n_val - 1))
        correct_answer_val = r_val # The question asks for r

        am_str = _format_number_for_display(a_m_val)
        an_str = _format_number_for_display(a_n_val)

        question_template = r"一個等比數列的第 ${m_val}$ 項為 ${am_str}$，第 ${n_val}$ 項為 ${an_str}$。已知公比 $r > 0$，試求此數列的公比 $r$。"
        question_text = question_template.replace("{m_val}", str(m_val)).replace("{am_str}", am_str).replace("{n_val}", str(n_val)).replace("{an_str}", an_str)

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): 已知某項與公比，求首項。
        r_val = random.choice(allowed_r_vals)
        a1_true_val = get_safe_a1(r_val) # asking for this
        
        max_n = get_max_n(r_val)
        n_val = random.randint(3, max_n)

        a_n_val = Fraction(a1_true_val) * (Fraction(r_val)**(n_val - 1))
        correct_answer_val = a1_true_val

        an_str = _format_number_for_display(a_n_val)
        r_str = _format_number_for_display(r_val)

        question_template = r"一個等比數列的第 ${n_val}$ 項為 ${an_str}$，公比為 $r = {r_str}$，試求此數列的首項 $a_1$。"
        question_text = question_template.replace("{n_val}", str(n_val)).replace("{an_str}", an_str).replace("{r_str}", r_str)

    elif problem_type == 4:
        # Type 4 (Maps to Example 5): 已知兩項 (非首項)，求指定項。 (r > 0)
        pos_r_vals = [r for r in allowed_r_vals if r > 0 and r != 1]
        r_val = random.choice(pos_r_vals)
        a1_true_val = get_safe_a1(r_val)

        max_n = get_max_n(r_val)
        # We need three distinct indices m < n, and k within range.
        # But max_n is small (5 or 6).
        # Let's retry sampling indices until valid.
        indices = sorted(random.sample(range(2, max_n + 1), 3)) # Get 3 distinct indices in range [2, max_n]
        # Assign them to m, n, k in some way. usually m < n known. k unknown.
        # Let's say we give m, n. Ask for k.
        # k can be smaller or larger than m, n. 
        # But indices gives 3 ordered values. Let's just pick any 3 from range.
        all_indices = list(range(2, max_n + 1))
        if len(all_indices) < 3: # Fallback if range too small (unlikely with min max_n=5, start=2 => 2,3,4,5 = 4 items)
             all_indices = list(range(1, max_n + 1))
        
        chosen_indices = random.sample(all_indices, 3)
        m_val, n_val, k_val = chosen_indices[0], chosen_indices[1], chosen_indices[2]
        
        # Ensure m < n for "knowns" typically, or just random is fine. 
        # Standard phrasing: 第 m 項 is X, 第 n 項 is Y.
        if m_val > n_val: m_val, n_val = n_val, m_val

        a_m_val = Fraction(a1_true_val) * (Fraction(r_val)**(m_val - 1))
        a_n_val = Fraction(a1_true_val) * (Fraction(r_val)**(n_val - 1))
        correct_answer_val = Fraction(a1_true_val) * (Fraction(r_val)**(k_val - 1))

        am_str = _format_number_for_display(a_m_val)
        an_str = _format_number_for_display(a_n_val)

        question_template = r"一個等比數列的第 ${m_val}$ 項為 ${am_str}$，第 ${n_val}$ 項為 ${an_str}$。若公比 $r > 0$，試求此數列的第 ${k_val}$ 項。"
        question_text = question_template.replace("{m_val}", str(m_val)).replace("{am_str}", am_str).replace("{n_val}", str(n_val)).replace("{an_str}", an_str).replace("{k_val}", str(k_val))
    
    # Format correct_answer for pure data string
    final_correct_answer = _format_answer_value(correct_answer_val)

    return {
        "question_text": question_text,
        "correct_answer": final_correct_answer,
        "answer": final_correct_answer, # 'answer' field is usually the same as 'correct_answer'
        "image_base64": "",
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    強韌閱卷邏輯 (Robust Check Logic):
    1. 輸入清洗 (Input Sanitization):
        - 使用 Regex 移除 user_answer 中的 LaTeX 符號 ($、\、{、})、變數前綴 (x=、y=、k=、Ans:)，以及所有空白字元。
    2. 數值轉換與比對:
        - 將清洗後的 user_answer 和 correct_answer 都嘗試轉換為 fractions.Fraction 進行精確比對。
        - 支援分數比對：例如 "1/2" 應等價於 "0.5"。
        - 如果 Fraction 轉換失敗（例如輸入非數字），則退而求其次嘗試浮點數比對，使用一個小的容許誤差 (epsilon) 進行浮點數比對。
    3. 答案格式標準化: correct_answer 格式為純數字字串 (例如 "54", "-1/8")。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().lower()
        # Remove LaTeX symbols, variable prefixes, and all whitespace
        s = re.sub(r'[\\$xkyAns=\s{}]', '', s)
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        # Prioritize fractions.Fraction for precise comparison
        u_frac = Fraction(u)
        c_frac = Fraction(c)
        if u_frac == c_frac:
            return {"correct": True, "result": "正確！"}
    except (ValueError, ZeroDivisionError):
        # If Fraction conversion fails, try float comparison as a fallback
        try:
            u_float = float(u)
            c_float = float(c)
            # Use high precision for float comparison
            if math.isclose(u_float, c_float, rel_tol=1e-9, abs_tol=1e-9):
                return {"correct": True, "result": "正確！"}
        except (ValueError, ZeroDivisionError):
            pass # Fall through to string comparison if float conversion also fails
            
    # 3. 降級為字串比對 (should be less likely with robust numerical check)
    if u == c: 
        return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": f"答案錯誤。"}


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
