# ==============================================================================
# ID: jh_數學2上_PolynomialDefinitionAndTerms
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 72.41s | RAG: 4 examples
# Created At: 2026-01-18 14:16:06
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


# --- Helper Functions ---

def _generate_polynomial_term(degree, allow_zero_coeff=False):
    """
    生成一個多項式項 (例如 3x^2)。
    返回 (coefficient, degree_val, term_str)
    """
    coefficient = random.randint(-9, 9)
    if not allow_zero_coeff:
        while coefficient == 0:
            coefficient = random.randint(-9, 9)

    term_str = ""
    if coefficient == 0:
        return (0, degree, "")

    if degree == 0:
        term_str = str(coefficient)
    elif degree == 1:
        if coefficient == 1:
            term_str = "x"
        elif coefficient == -1:
            term_str = "-x"
        else:
            term_str = r"{coeff}x".replace("{coeff}", str(coefficient))
    else: # degree > 1
        if coefficient == 1:
            term_str = r"x^{deg}".replace("{deg}", str(degree))
        elif coefficient == -1:
            term_str = r"-x^{deg}".replace("{deg}", str(degree))
        else:
            term_str = r"{coeff}x^{deg}".replace("{coeff}", str(coefficient)).replace("{deg}", str(degree))
    
    return (coefficient, degree, term_str)


def _generate_polynomial_expression(max_degree, num_terms_range=(2, 4)):
    """
    生成一個完整的多項式表達式。
    返回 (polynomial_dict, poly_str)
    """
    num_terms = random.randint(num_terms_range[0], num_terms_range[1])
    
    poly_dict = {}
    
    # Ensure the max_degree term exists and has a non-zero coefficient
    coeff_max_degree = 0
    while coeff_max_degree == 0:
        coeff_max_degree = random.randint(-9, 9)
    poly_dict[max_degree] = coeff_max_degree

    # Generate coefficients for other degrees (0 to max_degree-1)
    other_degrees = [d for d in range(max_degree) if d >= 0]
    random.shuffle(other_degrees)

    # Add other terms up to num_terms, ensuring unique degrees if possible
    # We already have one term (max_degree)
    terms_added_count = 1 
    
    for deg in other_degrees:
        if terms_added_count >= num_terms:
            break
        
        coeff = random.randint(-9, 9)
        if coeff != 0:
            # Add coefficient to existing if degree already present.
            # This handles cases where a degree might have been added implicitly.
            poly_dict[deg] = poly_dict.get(deg, 0) + coeff
            # Only count as a new term if it results in a non-zero coefficient for a new degree.
            # If the degree was already in poly_dict, it's not a 'new' term count-wise.
            # This logic is complex to precisely control `num_terms`.
            # A simpler approach: generate unique degrees first, then assign coefficients.
            terms_added_count += 1 # Increment for each attempt to add, then filter later
    
    # Filter out zero coefficients after combining
    final_poly_dict = {deg: coeff for deg, coeff in poly_dict.items() if coeff != 0}

    # Ensure max_degree is indeed the highest degree, and its coefficient is non-zero
    # If the max_degree term was cancelled out, or if fewer terms than requested, regenerate.
    actual_max_degree = max(final_poly_dict.keys()) if final_poly_dict else 0
    if actual_max_degree != max_degree or final_poly_dict.get(max_degree, 0) == 0 or len(final_poly_dict) < num_terms_range[0]:
        return _generate_polynomial_expression(max_degree, num_terms_range)

    # Sort terms by degree in descending order
    sorted_terms = sorted(final_poly_dict.items(), key=lambda item: item[0], reverse=True)
    
    poly_str_parts = []
    for i, (deg, coeff) in enumerate(sorted_terms):
        term_str = ""
        abs_coeff = abs(coeff)
        sign = "+" if coeff > 0 else "-"

        if deg == 0: # Constant term
            term_str = str(abs_coeff)
        elif deg == 1: # x term
            if abs_coeff == 1:
                term_str = "x"
            elif abs_coeff == 0: # Should not happen after filtering
                term_str = ""
            else:
                term_str = r"{abs_c}x".replace("{abs_c}", str(abs_coeff))
        else: # x^n term
            if abs_coeff == 1:
                term_str = r"x^{deg}".replace("{deg}", str(deg))
            elif abs_coeff == 0: # Should not happen after filtering
                term_str = ""
            else:
                term_str = r"{abs_c}x^{deg}".replace("{abs_c}", str(abs_coeff)).replace("{deg}", str(deg))
        
        if not term_str: # Skip if term is empty (coeff was 0)
            continue

        if i > 0: # Not the first term, prepend sign
            poly_str_parts.append(f" {sign} {term_str}")
        else: # First term
            if sign == "-":
                poly_str_parts.append(f"{sign}{term_str}")
            else:
                poly_str_parts.append(term_str) # Positive sign not shown for first term

    final_poly_str = "".join(poly_str_parts)
    
    # Remove leading '+' if any, after string assembly
    if final_poly_str.startswith('+'):
        final_poly_str = final_poly_str[1:].strip()
    
    # Ensure the string is not empty if poly_dict is not empty (shouldn't happen with current logic)
    if not final_poly_str and final_poly_dict:
        # Fallback for single constant term e.g., if only {0: 5} remains
        if 0 in final_poly_dict:
            final_poly_str = str(final_poly_dict[0])

    return (final_poly_dict, final_poly_str)

# --- Check Function (as provided in spec - CRITICAL CODING STANDARDS) ---

    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, a=, b=
        s = s.replace("$", "").replace("\\", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except:
        pass
        
    # 3. 降級為字串比對
    if u == c: return {"correct": True, "result": "正確！"}
    return {"correct": False, "result": f"答案錯誤。"}

# --- Generate Function ---
def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4]) # 隨機選擇題型

    # For Type 1, 3, 4, we need a base polynomial
    # For Type 2, we construct it differently.
    
    poly_data = {}
    poly_str_display = ""
    
    if problem_type != 2: # Only generate a standard polynomial if not Type 2
        max_degree = random.randint(2, 4) # 多項式最高次數，符合國二範疇
        poly_data, poly_str_display = _generate_polynomial_expression(max_degree)
        # Ensure poly_str_display is not empty, if for some reason generation failed.
        # _generate_polynomial_expression has regeneration logic to prevent this, but as a safeguard.
        while not poly_str_display:
            poly_data, poly_str_display = _generate_polynomial_expression(max_degree)

    question_text = ""
    correct_answer = ""

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1): Asking for degree or a specific coefficient
        # RAG Ex 1 asks for degree, x^3 coeff, x^2 coeff, x coeff, constant term.
        # To fit `check` function's single-value comparison, we ask for one specific item.
        
        question_choice = random.choice(['degree', 'coeff_x3', 'coeff_x2', 'coeff_x1', 'coeff_const'])
        
        if question_choice == 'degree':
            # Degree is the maximum key in poly_data with non-zero coefficient
            degree_val = 0
            for deg, coeff in poly_data.items():
                if coeff != 0 and deg > degree_val:
                    degree_val = deg
            question_text = r"多項式 ${poly_str}$ 的次數為何？".replace("{poly_str}", poly_str_display)
            correct_answer = str(degree_val)
        else:
            target_degree = 0
            if question_choice == 'coeff_x3': target_degree = 3
            elif question_choice == 'coeff_x2': target_degree = 2
            elif question_choice == 'coeff_x1': target_degree = 1
            elif question_choice == 'coeff_const': target_degree = 0

            coeff_val = poly_data.get(target_degree, 0) # Get coefficient, 0 if not present

            if target_degree == 0:
                question_text = r"在多項式 ${poly_str}$ 中，常數項為何？".replace("{poly_str}", poly_str_display)
            elif target_degree == 1:
                question_text = r"在多項式 ${poly_str}$ 中，$x$ 項的係數為何？".replace("{poly_str}", poly_str_display)
            else:
                question_text = r"在多項式 ${poly_str}$ 中，$x^{deg}$ 項的係數為何？".replace("{poly_str}", poly_str_display).replace("{deg}", str(target_degree))
            
            correct_answer = str(coeff_val)

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 2): Constant polynomial condition
        # RAG Ex 2: (a-2)x^2 + (b+3)x + 7 is a constant polynomial => a=2, b=-3
        # We generate a similar polynomial with variable coefficients and ask for 'a' or 'b'.
        
        # Generate constant term, ensure it's non-zero
        const_val = random.randint(-9, 9)
        while const_val == 0:
            const_val = random.randint(-9, 9)

        # Generate target values (the values 'a' and 'b' must take)
        target_a = random.randint(-5, 5) # If target_a is 2, term should be (a - 2)
        target_b = random.randint(-5, 5) # If target_b is -3, term should be (b + 3) -> b = -3

        # Build polynomial terms strings WITHOUT internal LaTeX delimiters ($)
        poly_parts = []
        
        # x^2 term: Coefficient should be 0, represented as (a - target_a)
        # Display logic: 
        # If target_a > 0: (a - 2)
        # If target_a < 0: (a + 2)  [Simplifying a - (-2)]
        # If target_a = 0: a
        if target_a == 0:
            poly_parts.append(r"ax^2")
        elif target_a > 0:
            poly_parts.append(r"(a - {val})x^2".replace("{val}", str(target_a)))
        else:
            poly_parts.append(r"(a + {val})x^2".replace("{val}", str(abs(target_a))))
        
        # x term: Coefficient should be 0, represented as (b - target_b)
        # Wait, previous logic was (b + K_b). Let's stick to the simplest form: (b - value).
        # We want coeff = 0 -> b = target_b.
        # So we display (b - target_b).
        # If target_b > 0: (b - 3)
        # If target_b < 0: (b + 3)
        # If target_b = 0: b
        
        # However, to vary it, we can sometimes display (b + k).
        # If we display (b + 3), then b = -3. So target_b = -3.
        # So the display logic is the same as 'a'.
        
        term_x_str = ""
        if target_b == 0:
            term_x_str = r"bx"
        elif target_b > 0:
            term_x_str = r"(b - {val})x".replace("{val}", str(target_b))
        else:
            term_x_str = r"(b + {val})x".replace("{val}", str(abs(target_b)))
            
        # Add sign for x term (always + because we are grouping coefficients)
        # e.g. (a-2)x^2 + (b+3)x ...
        poly_parts.append(f"+ {term_x_str}")
        
        # Constant term
        sign_const = "+" if const_val > 0 else "-"
        poly_parts.append(f"{sign_const} {abs(const_val)}")

        # Join parts
        # e.g., "(a - 2)x^2 + (b + 3)x - 7"
        poly_str_variable = " ".join(poly_parts)

        # Randomly ask for 'a' or 'b'
        ask_for_a = random.choice([True, False])
        if ask_for_a:
            # Wrap the FULL polynomial in $$ here
            question_text = r"若多項式 ${poly_var}$ 是一個常數多項式，則 $a$ 的條件為何？".replace("{poly_var}", poly_str_variable)
            correct_answer = str(target_a)
        else:
            question_text = r"若多項式 ${poly_var}$ 是一個常數多項式，則 $b$ 的條件為何？".replace("{poly_var}", poly_str_variable)
            correct_answer = str(target_b)

    elif problem_type == 3:
        # Type 3 (Maps to RAG Ex 3): Like terms
        # RAG Ex 3 asks to mark multiple options with '○' or '×'.
        # To fit `check` function's single-value comparison, we ask for one specific candidate.
        
        target_degree = random.randint(1, 4)
        target_term_str = r"x^{deg}".replace("{deg}", str(target_degree)) if target_degree > 1 else r"x"

        # Generate 4 candidate terms
        candidates = []
        for _ in range(4):
            coeff = random.randint(-9, 9)
            while coeff == 0: coeff = random.randint(-9, 9) # Ensure non-zero coeff for display
            
            # Randomly make it a like term or not
            is_like_term = random.choice([True, False])
            
            if is_like_term:
                cand_deg = target_degree
            else:
                # Make it a non-like term: different degree
                possible_other_degrees = [d for d in range(0, 5) if d != target_degree]
                if not possible_other_degrees: # Fallback if target_degree covers all (e.g., if range was 0-0)
                    possible_other_degrees = [random.choice([0,1,2,3,4])]
                cand_deg = random.choice(possible_other_degrees)

            _, _, term_str = _generate_polynomial_term(cand_deg, allow_zero_coeff=False)
            candidates.append((term_str, is_like_term))

        # Pick one candidate to ask about
        question_candidate_idx = random.randint(0, 3)
        question_candidate_term = candidates[question_candidate_idx][0]
        actual_is_like_term = candidates[question_candidate_idx][1]

        question_text = r"下列式子 ${cand_term}$ 是否是 ${target_term}$ 的同類項？是的打「○」，不是的打「×」。".replace("{cand_term}", question_candidate_term).replace("{target_term}", target_term_str)
        # The clean function in check converts '○' to 'o' and '×' to 'x'. So correct_answer should be 'o' or 'x'.
        correct_answer = "o" if actual_is_like_term else "x"


    elif problem_type == 4:
        # Type 4 (Maps to RAG Ex 4): Polynomial ordering and coefficient
        # RAG Ex 4 asks for full ascending/descending expressions.
        # To fit `check` function's single-value comparison, we ask for a specific coefficient after ordering.
        
        # _generate_polynomial_expression already returns poly_data (dict sorted by degree implicitly)
        # and poly_str_display (descending order).
        
        # To make it ascending, we need to reconstruct the string from poly_data
        sorted_terms_asc = sorted(poly_data.items(), key=lambda item: item[0])
        asc_poly_str_parts = []
        for i, (deg, coeff) in enumerate(sorted_terms_asc):
            term_str = ""
            abs_coeff = abs(coeff)
            sign = "+" if coeff > 0 else "-"

            if deg == 0:
                term_str = str(abs_coeff)
            elif deg == 1:
                if abs_coeff == 1: term_str = "x"
                else: term_str = r"{abs_c}x".replace("{abs_c}", str(abs_coeff))
            else:
                if abs_coeff == 1: term_str = r"x^{deg}".replace("{deg}", str(deg))
                else: term_str = r"{abs_c}x^{deg}".replace("{abs_c}", str(abs_coeff)).replace("{deg}", str(deg))
            
            if i > 0:
                asc_poly_str_parts.append(f" {sign} {term_str}")
            else:
                if sign == "-": asc_poly_str_parts.append(f"{sign}{term_str}")
                else: asc_poly_str_parts.append(term_str)
        
        asc_poly_str = "".join(asc_poly_str_parts)
        if asc_poly_str.startswith('+'):
            asc_poly_str = asc_poly_str[1:].strip()

        # Randomly choose to ask about descending or ascending order
        order_choice = random.choice(['descending', 'ascending'])
        
        # Randomly choose a degree to ask for its coefficient
        # Ensure the degree exists in the polynomial or is 0 (constant term)
        valid_degrees = list(poly_data.keys())
        if 0 not in valid_degrees: # Ensure constant term is a possible target
            valid_degrees.append(0)
        
        target_degree = random.choice(valid_degrees)
        coeff_val = poly_data.get(target_degree, 0)

        if order_choice == 'descending':
            if target_degree == 0:
                question_text = r"將多項式 ${poly_str}$ 依降冪排列後，常數項為何？".replace("{poly_str}", poly_str_display)
            elif target_degree == 1:
                question_text = r"將多項式 ${poly_str}$ 依降冪排列後，$x$ 項的係數為何？".replace("{poly_str}", poly_str_display)
            else:
                question_text = r"將多項式 ${poly_str}$ 依降冪排列後，$x^{deg}$ 項的係數為何？".replace("{poly_str}", poly_str_display).replace("{deg}", str(target_degree))
            correct_answer = str(coeff_val)
        else: # ascending
            if target_degree == 0:
                question_text = r"將多項式 ${poly_str}$ 依升冪排列後，常數項為何？".replace("{poly_str}", asc_poly_str)
            elif target_degree == 1:
                question_text = r"將多項式 ${poly_str}$ 依升冪排列後，$x$ 項的係數為何？".replace("{poly_str}", asc_poly_str)
            else:
                question_text = r"將多項式 ${poly_str}$ 依升冪排列後，$x^{deg}$ 項的係數為何？".replace("{poly_str}", asc_poly_str).replace("{deg}", str(target_degree))
            correct_answer = str(coeff_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 預留欄位
        "image_base64": None, # 無需圖片
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
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
