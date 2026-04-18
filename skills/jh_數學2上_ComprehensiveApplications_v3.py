# ==============================================================================
# ID: jh_數學2上_ComprehensiveApplications_v3
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 35.66s | RAG: 5 examples
# Created At: 2026-01-19 11:11:22
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


import datetime
import base64
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re

import numpy as np # For potential use in check, though not strictly needed for current logic

# --- Auxiliary Function: Drawing L-shape Diagram (Type 1) ---
def _draw_l_shape_diagram(a_val, b_val):
    """
    Draws an L-shape diagram representing a large square with a smaller square removed.
    Labels are algebraic expressions, not numerical values.
    Returns a base64 encoded PNG image string.
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    
    # Use fixed proportional units for drawing, labels are algebraic expressions
    L_units = 10
    S_units = 4 # Ensure S_units < L_units

    # Draw large square (outer frame)
    large_square = patches.Rectangle((0, 0), L_units, L_units, linewidth=1, edgecolor='black', facecolor='lightgray')
    ax.add_patch(large_square)

    # Draw the removed small square (white)
    # Removed from the top-right corner
    small_square = patches.Rectangle((L_units - S_units, L_units - S_units), S_units, S_units, linewidth=1, edgecolor='black', facecolor='white')
    ax.add_patch(small_square)

    # Draw L-shape boundary lines to make it more explicit
    # Outer L-shape
    ax.plot([0, L_units - S_units, L_units - S_units, 0, 0], 
            [L_units, L_units, S_units, S_units, L_units], 
            color='black', linewidth=1)
    # Inner L-shape (part of the removed square's boundary that touches the L-shape)
    ax.plot([L_units - S_units, L_units - S_units], [0, L_units - S_units], color='black', linewidth=1)
    ax.plot([0, L_units - S_units], [L_units - S_units, L_units - S_units], color='black', linewidth=1)


    # Label side lengths (algebraic expressions)
    # Large square side length
    ax.text(L_units / 2, L_units + 0.5, r"$(x+{a})$".replace("{a}", str(a_val)), 
            ha='center', va='bottom', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)) # Label Halo
    ax.text(-0.5, L_units / 2, r"$(x+{a})$".replace("{a}", str(a_val)), 
            ha='right', va='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)) # Label Halo

    # Small square side length
    ax.text(L_units - S_units / 2, L_units - S_units - 0.5, r"$(x-{b})$".replace("{b}", str(b_val)), 
            ha='center', va='top', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)) # Label Halo
    ax.text(L_units - S_units - 0.5, L_units - S_units / 2, r"$(x-{b})$".replace("{b}", str(b_val)), 
            ha='right', va='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)) # Label Halo

    ax.set_aspect('equal', adjustable='box') # ULTRA VISUAL STANDARDS: Aspect Ratio
    ax.set_xlim(-2, L_units + 2)
    ax.set_ylim(-2, L_units + 2)
    ax.axis('off') # Hide axes as it's a diagram, not a coordinate plane

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- Main Generation Function ---
def generate(level=1):
    """
    Generates a K12 math problem for '綜合應用' skill.
    Focuses on applications of multiplication formulas and polynomial operations.
    """
    problem_type = random.choice([1, 2])
    question_text = ""
    correct_answer_val = None
    image_base64 = None

    if problem_type == 1:
        # Type 1: Geometric Area Application (L-shape area)
        # Maps to the concept of (A)^2 - (B)^2, which is an application of multiplication formulas.
        
        # Ensure a > b and a-b >= 1 for valid dimensions
        a = random.randint(3, 8)
        b = random.randint(1, a - 2) # Ensures a-b >= 2, so x-b is smaller than x+a
        x_val = random.randint(b + 1, 10) # Ensures (x-b) > 0

        # Calculate the area of the remaining part: (x+a)^2 - (x-b)^2
        # Using difference of squares formula: A^2 - B^2 = (A-B)(A+B)
        # A = (x+a), B = (x-b)
        # (A-B) = (x+a) - (x-b) = x+a-x+b = a+b
        # (A+B) = (x+a) + (x-b) = x+a+x-b = 2x + a-b
        # Area = (a+b) * (2x + a-b)
        correct_answer_val = (a + b) * (2 * x_val + a - b)

        # LaTeX safe formatting for question text
        q_text_template = r"有一個邊長為 $(x+{a})$ 的大正方形，從中挖去一個邊長為 $(x-{b})$ 的小正方形，如圖所示。請問剩下部分的面積為何？當 $x={x_val}$ 時，其面積為多少？"
        question_text = q_text_template.replace("{a}", str(a)).replace("{b}", str(b)).replace("{x_val}", str(x_val))
        
        # Generate the diagram (reference only, no answer data)
        image_base64 = _draw_l_shape_diagram(a, b)

    elif problem_type == 2:
        # Type 2: Polynomial Operations and Evaluation
        # Maps to general polynomial manipulation and substitution.
        sub_type = random.choice([1, 2, 3])

        a = random.randint(1, 8)
        b = random.randint(1, 8)
        c = random.randint(1, 8) # Used only in sub_type 1
        x_val = random.randint(-5, 5)

        if sub_type == 1:
            # Expression: (x+a)(x-b) - (x+c)^2
            # Expand: (x^2 + (a-b)x - ab) - (x^2 + 2cx + c^2)
            # Simplify: (x^2 - x^2) + ((a-b)x - 2cx) - (ab + c^2)
            # = (a-b-2c)x - (ab + c^2)
            correct_answer_val = (a - b - 2 * c) * x_val - (a * b + c * c)
            q_text_template = r"請化簡多項式 $(x+{a})(x-{b}) - (x+{c})^2$。當 $x={x_val}$ 時，此多項式的值為多少？"
            question_text = q_text_template.replace("{a}", str(a)).replace("{b}", str(b)).replace("{c}", str(c)).replace("{x_val}", str(x_val))
        elif sub_type == 2:
            # Expression: (x+a)^2 + (x-b)(x+b)
            # Expand: (x^2 + 2ax + a^2) + (x^2 - b^2)
            # Simplify: (x^2 + x^2) + 2ax + (a^2 - b^2)
            # = 2x^2 + 2ax + a^2 - b^2
            correct_answer_val = 2 * (x_val**2) + 2 * a * x_val + (a**2) - (b**2)
            q_text_template = r"請化簡多項式 $(x+{a})^2 + (x-{b})(x+{b})$。當 $x={x_val}$ 時，此多項式的值為多少？"
            question_text = q_text_template.replace("{a}", str(a)).replace("{b}", str(b)).replace("{x_val}", str(x_val))
        elif sub_type == 3:
            # Expression: (x+a)^2 - (x-b)^2
            # Expand: (x^2 + 2ax + a^2) - (x^2 - 2bx + b^2)
            # Simplify: (x^2 - x^2) + (2ax - (-2bx)) + (a^2 - b^2)
            # = (2a+2b)x + (a^2 - b^2)
            correct_answer_val = (2 * a + 2 * b) * x_val + (a**2 - b**2)
            q_text_template = r"請化簡多項式 $(x+{a})^2 - (x-{b})^2$。當 $x={x_val}$ 時，此多項式的值為多少？"
            question_text = q_text_template.replace("{a}", str(a)).replace("{b}", str(b)).replace("{x_val}", str(x_val))
        
        image_base64 = None # Polynomial simplification problems do not require images

    return {
        "question_text": question_text,
        "correct_answer": str(correct_answer_val), # Must be a pure data string
        "answer": str(correct_answer_val), # For frontend display, same as correct_answer
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0"
    }

# --- Check Function ---

    """
    Checks if the user's answer is correct against the generated correct answer.
    Implements robust input sanitization and numerical comparison.
    Returns True for correct, False for incorrect.
    """
    # CRITICAL RULE: Robust Check Logic - 輸入清洗 (Input Sanitization)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Remove common LaTeX symbols, variable prefixes (e.g., 'x=', 'ans:'), and parentheses
        s = re.sub(r'^[a-z]+(=|:)?', '', s) # Removes k=, x=, y=, Ans: at the beginning
        s = s.replace("$", "").replace("\\", "") # Remove LaTeX math delimiters and backslashes
        s = re.sub(r'[\(\)\{\}\[\]]', '', s) # Remove parentheses, braces, brackets
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # Attempt numerical comparison (supports fractions and decimals)
    try:
        def parse_val(val_str):
            if not val_str: # Handle empty string after cleaning
                raise ValueError("Empty string after cleaning, cannot parse as number.")
            if "/" in val_str:
                n_str, d_str = val_str.split("/")
                n = float(n_str)
                d = float(d_str)
                if d == 0: # Prevent division by zero
                    raise ValueError("Division by zero in fraction.")
                return n / d
            return float(val_str)
        
        # Only attempt parsing if both cleaned strings are not empty
        if u and c:
            if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
                return True
    except ValueError:
        # If parsing fails or division by zero, fall through to string comparison
        pass
        
    # Fallback to string comparison if numerical comparison failed or was not applicable
    return u == c


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
