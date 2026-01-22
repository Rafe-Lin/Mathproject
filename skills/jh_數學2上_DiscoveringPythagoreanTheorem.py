# ==============================================================================
# ID: jh_數學2上_DiscoveringPythagoreanTheorem
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 50.77s | RAG: 4 examples
# Created At: 2026-01-18 21:17:40
# Fix Status: [Repaired]
# Fixes: Regex=3, Logic=0
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
    # 隱藏刻度,僅保留 0
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
        # 雙向清理:剝除 LaTeX 符號與空格
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

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import base64
from io import BytesIO
import datetime

import re

# --- check function (from template, refined for LaTeX sqrt and multiple answers) ---

import re, math
    
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
def clean(s):
    s = str(s).strip().lower()
    s = s.replace(" ", "") # Remove spaces
    s = s.replace("$", "") # Remove LaTeX math delimiters

    # Convert \sqrt{X} to sqrt(X) for easier parsing
    s = re.sub(r'\\sqrt{([^}]+)}', r'sqrt(\1)', s)
    # Convert \frac{N}{D} to (N)/(D) for easier parsing
    s = re.sub(r'\\frac{([^}]+)}{([^}]+)}', r'((\1)/(\2))', s)
    
    s = s.replace("\\", "") # Remove any remaining backslashes

    # Remove variable names like 'a=' or 'x=' if they are at the beginning of a part
    # This is handled per part, not for the whole string initially
    return s
    
    u_cleaned = clean(user_answer)
    c_cleaned = clean(correct_answer)
    
    # Handle multiple answers like "a=3, b=sqrt(65)"
    # Split by comma and process each part
    u_parts_raw = [part.strip() for part in u_cleaned.split(',')]
    c_parts_raw = [part.strip() for part in c_cleaned.split(',')]

    # Sort parts for robust comparison regardless of order
    # Extract variable name and value for sorting
    def get_var_val_tuple(part_str):
        match = re.match(r'([a-z]+)=(.+)', part_str)
        if match:
            return (match.group(1), match.group(2))
        return (None, part_str) # No variable name, just value

    u_processed_parts = sorted([get_var_val_tuple(p) for p in u_parts_raw])
    c_processed_parts = sorted([get_var_val_tuple(p) for p in c_parts_raw])

    if len(u_processed_parts) != len(c_processed_parts):
        return {"correct": False, "result": f"答案格式錯誤或數量不符。預期 {len(c_processed_parts)} 個值，但收到 {len(u_processed_parts)} 個。"}

    all_correct = True
    feedback = []

    for i in range(len(u_processed_parts)):
        u_var, u_val_str = u_processed_parts[i]
        c_var, c_val_str = c_processed_parts[i]
        
        # Ensure variable names match if present
        if u_var and c_var and u_var != c_var:
            all_correct = False
            feedback.append(f"變數名稱不匹配：預期 '{c_var}' 但收到 '{u_var}'。")
            continue
        elif (u_var and not c_var) or (not u_var and c_var):
            all_correct = False
            feedback.append(f"變數名稱存在性不匹配。")
            continue

        # Try numerical comparison (supports fractions, square roots, and simple expressions)
        try:
            def parse_val(val_str_input):
                # Handle square roots: sqrt(X)
                sqrt_match = re.match(r'sqrt\((.+)\)', val_str_input)
                if sqrt_match:
                    # Use eval to handle potential fractions or simple arithmetic inside sqrt, e.g., sqrt(1/2) or sqrt(2*3)
                    return math.sqrt(float(eval(sqrt_match.group(1))))
                
                # Handle general expressions (fractions, decimals, integers, simple arithmetic)
                # eval is powerful but needs careful input control.
                # Here, inputs are cleaned and expected to be mathematical expressions.
                return float(eval(val_str_input))
            
            u_val = parse_val(u_val_str)
            c_val = parse_val(c_val_str)

            if math.isclose(u_val, c_val, rel_tol=1e-5):
                feedback.append(f"值 '{c_var if c_var else c_val_str}' 正確。")
            else:
                all_correct = False
                feedback.append(f"值 '{c_var if c_var else c_val_str}' 錯誤。預期 {c_val} 但收到 {u_val}。")
        except Exception as e:
            # Fallback to exact string comparison if numerical parsing fails or is not applicable
            if u_val_str == c_val_str:
                feedback.append(f"值 '{c_var if c_var else c_val_str}' 正確 (字串比對)。")
            else:
                all_correct = False
                feedback.append(f"值 '{c_var if c_var else c_val_str}' 錯誤 (字串比對)。")
    
    if all_correct:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": f"答案錯誤。 {' '.join(feedback)}"}

# --- generate function ---
# --- Helper: Simplify Square Root ---
def simplify_sqrt(n):
    if n == 0: return "0"
    if n == 1: return "1"
    i = 2
    res_coeff = 1
    res_radicand = n
    while i * i <= res_radicand:
        if res_radicand % (i * i) == 0:
            res_coeff *= i
            res_radicand //= (i * i)
        else:
            i += 1
    if res_radicand == 1:
        return str(res_coeff)
    elif res_coeff == 1:
        return f"\\sqrt{{{res_radicand}}}"
    else:
        return f"{res_coeff}\\sqrt{{{res_radicand}}}"

# --- Drawing Functions ---
def draw_right_triangle(leg_a, leg_b, hyp_c_label, label_a, label_b):
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    
    # Coordinates: C=(0,0), A=(0, leg_b), B=(leg_a, 0)
    C = np.array([0, 0])
    A = np.array([0, leg_b])
    B = np.array([leg_a, 0])
    
    # Draw Triangle
    ax.plot([C[0], B[0]], [C[1], B[1]], 'k-', lw=2) # Base a
    ax.plot([C[0], A[0]], [C[1], A[1]], 'k-', lw=2) # Height b
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k-', lw=2) # Hypotenuse c
    
    # Right Angle Mark
    size = min(leg_a, leg_b) * 0.15
    ax.plot([0, size, size], [size, size, 0], 'k-', lw=1.5)
    
    # Labels with Halo
    def add_text_with_halo(x, y, text, color='black', fontsize=16):
        ax.text(x, y, text, color=color, fontsize=fontsize, ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=0.9))

    # Side labels
    add_text_with_halo(leg_a/2, -size*0.6, label_a) # Base
    add_text_with_halo(-size*0.6, leg_b/2, label_b) # Height
    add_text_with_halo(leg_a/2 + size*0.5, leg_b/2 + size*0.5, hyp_c_label) # Hypotenuse
    
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Expand limits slightly
    margin = max(leg_a, leg_b) * 0.1
    ax.set_xlim(-margin - size, leg_a + margin)
    ax.set_ylim(-margin - size, leg_b + margin)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def draw_split_triangle(AD_val, AB_val, CD_val, BD_val):
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)

    # Let D be origin (0,0)
    D = np.array([0, 0])
    A = np.array([0, AD_val])
    B = np.array([-BD_val, 0])
    C = np.array([CD_val, 0])

    # Draw lines
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=2) # BC
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k-', lw=2) # AB
    ax.plot([A[0], C[0]], [A[1], C[1]], 'k-', lw=2) # AC
    ax.plot([A[0], D[0]], [A[1], D[1]], 'k--', lw=1.5) # AD

    # Right angle at D
    size = min(AD_val, BD_val, CD_val) * 0.15
    ax.plot([0, -size, -size], [size, size, 0], 'k-', lw=1) # Left side
    # ax.plot([0, size, size], [size, size, 0], 'k-', lw=1) # Right side (optional, usually one is enough)

    # Labels helper
    def add_text(x, y, txt, fs=14):
        ax.text(x, y, txt, fontsize=fs, ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.2))

    # Points
    add_text(A[0], A[1] + 0.5, 'A')
    add_text(B[0] - 0.5, B[1], 'B')
    add_text(C[0] + 0.5, C[1], 'C')
    add_text(D[0], D[1] - 0.5, 'D')

    # Given Values
    add_text(0.3, AD_val/2, str(AD_val)) # AD
    add_text((A[0]+B[0])/2 - 0.5, (A[1]+B[1])/2, str(AB_val)) # AB
    add_text(CD_val/2 + 0.2, -0.4, str(CD_val)) # CD

    # Unknown
    add_text(-BD_val/2, -0.4, 'a') # BD
    add_text((A[0]+C[0])/2 + 0.5, (A[1]+C[1])/2, 'b') # AC

    ax.set_aspect('equal')
    ax.axis('off')
    
    # Limits
    width = BD_val + CD_val
    height = AD_val
    margin = max(width, height) * 0.1
    ax.set_xlim(-BD_val - margin, CD_val + margin)
    ax.set_ylim(-margin, AD_val + margin)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# --- generate function ---
def generate(level=1, **kwargs):
    # Randomly select problem type
    # 1: Basic Pyth (Find c)
    # 2: Leg Calculation (Find b)
    # 3: Split Triangle (Find parts)
    p_type = random.choice([1, 2, 3])
    
    question_text = ""
    correct_answer = ""
    image_base64 = ""

    if p_type == 1: # Basic: Find hypotenuse
        # Triples: (3,4,5), (5,12,13), (8,15,17), (7,24,25)
        triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25)]
        a, b, c = random.choice(triples)
        
        # Randomize 'a' and 'b' labels visually
        if random.random() > 0.5:
            leg1, leg2 = a, b
        else:
            leg1, leg2 = b, a
            
        question_text = f"直角三角形兩股長分別為 ${leg1}$ 與 ${leg2}$，求斜邊長 $c$。"
        correct_answer = str(c)
        image_base64 = draw_right_triangle(leg1, leg2, "c", str(leg1), str(leg2))

    elif p_type == 2: # Root: Find leg
        # c must be hypotenuse. a is one leg.
        # Find b such that b = sqrt(c^2 - a^2)
        # Generate c, a such that result is not perfect square but simplifiable
        # Or just controllable randoms.
        # Example: a=2, c=4 -> b=sqrt(12)=2sqrt(3)
        # Strategy: Pick a random integer b_root, multiply by some factor?
        # Actually simplest: Pick 'a' and 'b_sq' such that c_sq is reasonable? 
        # No, better: Pick 'a' and 'c' integers.
        # Ensure c > a.
        
        # Let's generate pairs (a, c)
        pairs = []
        for _a in range(2, 10):
            for _c in range(_a + 1, 15):
                b2 = _c*_c - _a*_a
                # We want b2 not to be a perfect square ideally, for "Root" practice, 
                # but mixed is fine. User example: a=2, c=4 -> b=sqrt(12)=2rt3
                # Let's filter for cases that are NOT perfect squares to force radical practice?
                # User says "Type 2 (根號運算)... 需化簡根號".
                if int(math.isqrt(b2))**2 != b2: 
                    pairs.append((_a, _c, b2))
        
        if not pairs: # Fallback
             a, c, b2 = 2, 4, 12
        else:
            a, c, b2 = random.choice(pairs)
            
        question_text = f"直角三角形一股長為 ${a}$，斜邊長為 ${c}$，求另一股長 $b$。"
        b_simp = simplify_sqrt(b2)
        correct_answer = b_simp
        image_base64 = draw_right_triangle(a, math.sqrt(b2), str(c), str(a), "b")

    else: # Type 3: Split Triangle
        # Existing logic
        # △ABD (left): AD, BD, AB (hyp)
        # Use (6,8,10) or similar
        triples = [(3,4,5), (6,8,10), (5,12,13), (9,12,15)] # simple ones
        
        # Pick triple for Left Triangle (ABD) -> yields AD, BD
        # AD is common leg.
        # Let's pick AD first maybe?
        # Actually easier to pick a triple, assign one leg as AD.
        tr1 = random.choice(triples)
        # tr1 = (3,4,5) -> AD could be 3 or 4.
        if random.random() > 0.5:
            AD_val, BD_val, AB_val = tr1[0], tr1[1], tr1[2]
        else:
            BD_val, AD_val, AB_val = tr1[0], tr1[1], tr1[2]
            
        # Right Triangle (ADC) -> needs AD, CD, AC(hyp).
        # We have AD. We need another triple scaled to match AD? 
        # Or just pick random CD such that AC is "nice"?
        # User said: "ensure calculation numbers are pretty (e.g. use two Pythagorean triples)"
        # So we need another triple (leg, leg, hyp) where one leg is AD_val.
        
        # Find triples containing AD_val as a leg
        candidates = []
        for t in [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (6,8,10), (10,24,26), (9,12,15), (12,16,20), (15,20,25), (12,5,13)]:
            # standard triples (a,b,c)
            # check if AD_val in (a,b)
            if t[0] == AD_val: candidates.append(t[1]) # the other leg is CD
            if t[1] == AD_val: candidates.append(t[0]) # the other leg is CD
            
        if candidates:
            CD_val = random.choice(candidates)
        else:
            # Fallback if AD not found in common triples (unlikely for 3,4,6,8,12 etc)
            # Just pick CD=AD -> Isosceles Right Triangle -> AC = AD*sqrt(2)
            CD_val = AD_val
            
        # Recalculate AC
        AC_sq = AD_val**2 + CD_val**2
        AC_val_simp = simplify_sqrt(AC_sq)
        
        question_text = f"如圖，在 $\\triangle ABC$ 中，$AD \\perp BC$。已知 $AD={AD_val}, AB={AB_val}, CD={CD_val}$，求 $a$ (線段 $BD$) 與 $b$ (線段 $AC$) 的值。"
        correct_answer = f"a={BD_val}, b={AC_val_simp}"
        
        image_base64 = draw_split_triangle(AD_val, AB_val, CD_val, BD_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # Provide for reference/logging
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "2.0" # Bump version
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
                # 僅針對「文字反斜線+n」進行物理換行替換,不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則:若答案包含複雜運算符號,強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入,避免重複堆疊
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
