# ==============================================================================
# ID: jh_數學1下_IntroductionToOneVariableLinearInequalities
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 80.76s | RAG: 3 examples
# Created At: 2026-01-16 23:41:50
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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plots

# V11.8 A. 資料結構鎖死: 統一回傳 (float_val, (int_part, num, den, is_neg))
# V13.0 座標選取控制: 使用 random.randint(-8, 8) 或 + 0.5
# V13.1 禁絕假分數: numerator < denominator 且 denominator > 1
def _generate_number_value(allow_fraction=True, allow_decimal_half=True):
    is_neg = random.choice([True, False])
    float_val = 0.0
    int_part = 0
    num = 0
    den = 0

    # 1-6 for integer, 7-8 for fraction, 9-10 for decimal .5
    choice = random.randint(1, 10) 
    
    if choice <= 6: # Integer
        int_part = random.randint(1, 8) # Magnitude within a reasonable range
        float_val = float(int_part)
        if is_neg:
            float_val *= -1
        
    elif choice <= 8 and allow_fraction: # Proper Fraction (can have integer part)
        int_part = random.randint(0, 3) # Integer part can be 0 for pure fraction
        den = random.randint(2, 5) # Denominator > 1
        num = random.randint(1, den - 1) # Proper fraction: numerator < denominator
        
        float_val = float(int_part) + float(num) / den
        if is_neg:
            float_val *= -1
            
    elif allow_decimal_half: # Decimal .5 (as per V13.0 spec)
        int_part = random.randint(1, 8)
        float_val = float(int_part) + 0.5
        if is_neg:
            float_val *= -1
        num = 1 # Represent .5 as 1/2 for LaTeX formatting
        den = 2

    # V13.5 整數優先: 確保輸出如 (5, 4) 而非 (5.0, 4.0)
    # 對於 float_val, 如果是整數，直接轉為 int
    if float_val.is_integer():
        float_val = int(float_val)

    return float_val, (int_part, num, den, is_neg)

# V11.8 C. LaTeX 模板規範: 使用單層大括號，搭配 .replace()
def _format_number_latex(data_tuple):
    float_val, (int_part, num, den, is_neg) = data_tuple
    sign = "-" if is_neg and float_val != 0 else "" # Only show sign if not zero

    if float_val == 0:
        return "0"
    
    if num == 0 and den == 0: # Integer (or was a decimal that became integer, e.g., 3.0)
        # Check if float_val is actually an integer
        if float_val.is_integer():
            return r"{s}{i}".replace("{s}", sign).replace("{i}", str(int(abs(float_val))))
        else: # This path should ideally not be hit with current _generate_number_value for non-integer floats
              # but as a fallback, format as float
            return str(float_val)
    elif num != 0 and den != 0: # Fraction or .5 decimal
        if int_part == 0: # Pure proper fraction
            return r"{s}\frac{{{n}}}{{{d}}}".replace("{s}", sign).replace("{n}", str(num)).replace("{d}", str(den))
        else: # Mixed fraction
            return r"{s}{i}\frac{{{n}}}{{{d}}}".replace("{s}", sign).replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))
    else: # Fallback (shouldn't happen with current logic if num/den are consistently set)
        return str(float_val)

# V6. 視覺化與輔助函式通用規範: 必須回傳, 類型一致, 防洩漏原則
# V11.8 D. 視覺一致性: 鎖定 ax.set_aspect('equal') (not strictly for number line, but for consistency), 0 粗體
# V13.0 格線對齊: 座標軸範圍對稱整數, xticks 間隔 1
# V13.6 API Hardened Spec: Arrow Ban - 使用 ax.plot 繪製箭頭
# V13.1 標籤純淨化: ax.text 只能是標籤文字
def draw_number_line(critical_value, inequality_type, x_range=(-10, 10), label_step=1):
    fig, ax = plt.subplots(figsize=(8, 2))

    ax.set_aspect('auto') 
    ax.set_ylim(-1, 1) 
    ax.set_xlim(x_range[0] - 1.5, x_range[1] + 1.5) # Add more padding for arrows

    ax.axhline(0, color='black', linewidth=1.5)

    # V13.6 Arrow Ban: 使用 ax.plot 繪製箭頭
    ax.plot(x_range[0] - 1.5, 0, "<k", clip_on=False, markersize=8) 
    ax.plot(x_range[1] + 1.5, 0, ">k", clip_on=False, markersize=8)

    ax.set_xticks(range(math.floor(x_range[0]), math.ceil(x_range[1]) + 1, label_step))
    ax.set_yticks([]) # No y-ticks

    # V11.8 D. 標註坐標軸: 僅顯示原點 0 (18號加粗), 點標籤須加白色光暈 (bbox)
    ax.text(0, -0.3, '0', fontsize=18, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))

    # Draw ticks for other integers (no labels as per V13.1/V13.5 strict labeling)
    for tick in range(math.floor(x_range[0]), math.ceil(x_range[1]) + 1):
        if tick != 0:
            ax.plot([tick, tick], [0.05, -0.05], color='black', linewidth=1)

    # Draw the solution set
    if inequality_type in ['>', '<', '>=', '<=']:
        # Point at critical_value
        if inequality_type in ['>', '<']:
            # Open circle
            ax.plot(critical_value, 0, 'o', markerfacecolor='white', markeredgecolor='blue', markersize=10, zorder=5)
        else: # '>=', '<='
            # Closed circle
            ax.plot(critical_value, 0, 'o', markerfacecolor='blue', markeredgecolor='blue', markersize=10, zorder=5)

        # Directional arrow/line
        if inequality_type in ['>', '>=']:
            ax.hlines(0, critical_value, x_range[1] + 1, color='blue', linewidth=3, zorder=4)
            ax.plot(x_range[1] + 1, 0, ">", color='blue', markersize=8, clip_on=False, zorder=5)
        elif inequality_type in ['<', '<=']:
            ax.hlines(0, x_range[0] - 1, critical_value, color='blue', linewidth=3, zorder=4)
            ax.plot(x_range[0] - 1, 0, "<", color='blue', markersize=8, clip_on=False, zorder=5)

    ax.axis('off') 

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# V3. 頂層函式: generate, check 於模組最外層
# V12.6, V15, V16. Exact Check Logic: 實作「數值序列比對」

    try:
        user_nums_str = user_answer.replace(" ", "").split(',')
        user_nums = [float(num) for num in user_nums_str if num]
        
        correct_nums_str = correct_answer.replace(" ", "").split(',')
        correct_nums = [float(num) for num in correct_nums_str if num]
        
        # V12.6 只要用戶輸入的數字順序與正確座標一致，即回傳 True
        # V15 禁絕複雜比對，統一要求使用數字序列比對
        return user_nums == correct_nums
    except ValueError:
        return False
    except Exception:
        return False

# V3. 頂層函式: generate 於模組最外層
# V4. 隨機分流: 使用 random.choice 或 if/elif 邏輯
# V10. 數據禁絕常數: random.randint 生成所有數據, 公式計算答案
def generate(level=1):
    # MANDATORY MIRRORING RULES: STRICT MAPPING -> Only 3 problem types matching RAG Ex 1, 2, 3
    problem_type_choice = random.randint(1, 3) 

    question_text = ""
    correct_answer = "" # Numerical list/single number as string for check() (V14.B)
    answer = "" # Full inequality string for display
    # [V16.6] Text-only mode: ensure empty string
    image_base64 = ""

    if problem_type_choice == 1:
        # Type 1: Maps to RAG Ex 1 - Translate verbal statement to inequality.
        # Model: Ax + B {verbal_op} C -> Ax + B {inequality_sign} C
        
        coeff_x = random.randint(1, 5)
        const_left = random.randint(-10, 10)
        const_right = random.randint(1, 20)

        inequality_type_map = {
            '不超過': r'\le',
            '超過': '>',
            '不低於': r'\ge',
            '未滿': '<',
            '不大於': r'\le', # additional common phrase
            '至少': r'\ge',   # additional common phrase
        }
        verbal_phrase_choice = random.choice(list(inequality_type_map.keys()))
        inequality_sign = inequality_type_map[verbal_phrase_choice]

        # Construct left side expression string carefully (Guardrail 1: avoid f-string for expressions)
        left_side_parts = []
        if coeff_x == 1:
            left_side_parts.append("x")
        else:
            left_side_parts.append(str(coeff_x) + "x")
        
        if const_left != 0:
            # [V16.6 Symbol Standardization] Use ASCII symbols + / -
            if const_left > 0:
                left_side_parts.append(" + " + str(const_left))
            else:
                left_side_parts.append(" - " + str(abs(const_left)))
        
        left_side_expr_str = "".join(left_side_parts)
        
        question_text = r"將下面的敘述改寫成不等式。⑴ ${left_expr} {verbal_op} {right_const}$".replace(
            "{left_expr}", left_side_expr_str).replace(
            "{verbal_op}", verbal_phrase_choice).replace(
            "{right_const}", str(const_right))

        # Calculate critical value for correct_answer (assuming system checks critical value numerically)
        # Solve coeff_x * x + const_left = const_right  => x = (const_right - const_left) / coeff_x
        critical_val_float = (const_right - const_left) / coeff_x
        if critical_val_float.is_integer():
            critical_val_float = int(critical_val_float)

        correct_answer = str(critical_val_float) # Numerical answer for check()
        # [V16.6] Fix spacing around operators
        answer = r"${left_expr} {sign} {right_const}$".replace( # Full inequality string for display
            "{left_expr}", left_side_expr_str).replace(
            "{sign}", inequality_sign).replace(
            "{right_const}", str(const_right))

    elif problem_type_choice == 2:
        # Type 2: Maps to RAG Ex 2 - Formulate an inequality from a word problem scenario.
        # Context Retention: Use names like '巴奈', 'ACEF', 'BDF'
        
        scenario_type = random.choice([1, 2])

        if scenario_type == 1: # Model: Ax {sign} C (e.g., mineral water cost)
            A = random.randint(2, 10) # Number of items
            C = random.randint(50, 200) # Total amount
            
            phrase_choice = random.choice(['不夠', '足夠']) # Match RAG Ex 2 phrases
            
            if phrase_choice == '不夠': # 錢不夠 -> total cost > money available
                inequality_sign = '>'
                scenario_desc = r"巴奈帶了 {C_val} 元到便利商店買果汁，若他拿了 {A_val} 瓶售價 x 元的果汁，付錢時卻發現錢不夠。".replace(
                    "{C_val}", str(C)).replace("{A_val}", str(A))
            else: # 錢足夠 -> total cost <= money available
                # [V16.6] Use standard LaTeX
                inequality_sign = r'\le'
                scenario_desc = r"巴奈帶了 {C_val} 元到便利商店買果汁，若他拿了 {A_val} 瓶售價 x 元的果汁，付錢時發現錢足夠。".replace(
                    "{C_val}", str(C)).replace("{A_val}", str(A))

            question_text = r"依下列情境列出 x 的不等式。（不需化簡）⑴ {scenario}".replace("{scenario}", scenario_desc)
            
            # For Ax {sign} C, critical value is C/A
            critical_val_float = C / A
            if critical_val_float.is_integer():
                critical_val_float = int(critical_val_float)
            
            correct_answer = str(critical_val_float)
            answer = r"${A_val}x {sign} {C_val}$".replace("{A_val}", str(A)).replace("{sign}", inequality_sign).replace("{C_val}", str(C))

        else: # Model: x + B {sign} C (e.g., money combined)
            B = random.randint(100, 500) # Amount from another person
            C = random.randint(500, 1000) # Total cost
            
            phrase_choice = random.choice(['足夠', '不夠']) # Match RAG Ex 2 phrases
            
            if phrase_choice == '足夠': # 足夠 -> x + B >= C
                # [V16.6] Use standard LaTeX
                inequality_sign = r'\ge'
                scenario_desc = r"ACEF 身上原有 x 元，如果再加上 BDF 的 {B_val} 元後，姐弟倆就有足夠的錢訂購定價 {C_val} 元的母親節蛋糕。".replace(
                    "{B_val}", str(B)).replace("{C_val}", str(C))
            else: # 不夠 -> x + B < C
                inequality_sign = '<'
                scenario_desc = r"ACEF 身上原有 x 元，如果再加上 BDF 的 {B_val} 元後，姐弟倆的錢仍不足以訂購定價 {C_val} 元的母親節蛋糕。".replace(
                    "{B_val}", str(B)).replace("{C_val}", str(C))

            question_text = r"依下列情境列出 x 的不等式。（不需化簡）⑵ {scenario}".replace("{scenario}", scenario_desc)
            
            # For x + B {sign} C, critical value is C - B
            critical_val_float = C - B
            if critical_val_float.is_integer():
                critical_val_float = int(critical_val_float)
            
            correct_answer = str(critical_val_float)
            # Guardrail 1: Construct expression carefully. Here it's simple "x + B" or "x - B"
            # [V16.6 Symbol Standardization] Use ASCII symbols + / - with padding spaces
            op_str = " + " if B >= 0 else " - "
            answer = r"$x {op} {B_val} {sign} {C_val}$".replace("{op}", op_str).replace("{B_val}", str(abs(B))).replace("{sign}", inequality_sign).replace("{C_val}", str(C))

    else: # problem_type_choice == 3
        # Type 3: Maps to RAG Ex 3 - Express a range using a compound inequality.
        # Model: lower <= x <= upper

        # Use predefined ranges as in RAG Ex 3 (AQI) and other contexts
        range_data = [
            {'lower': 101, 'upper': 150, 'description': '對敏感族群不健康', 'color': '橘色', 'variable': 'x', 'context': '空氣品質指標（AQI）'},
            {'lower': 151, 'upper': 200, 'description': '對所有族群不健康', 'color': '紅色', 'variable': 'y', 'context': '空氣品質指標（AQI）'},
            {'lower': 0, 'upper': 50, 'description': '良好', 'color': '綠色', 'variable': 'x', 'context': '空氣品質指標（AQI）'},
            {'lower': 51, 'upper': 100, 'description': '普通', 'color': '黃色', 'variable': 'y', 'context': '空氣品質指標（AQI）'},
            {'lower': 25, 'upper': 35, 'description': '炎熱', 'color': '紅色', 'variable': 'T', 'context': '溫度等級'},
            {'lower': 10, 'upper': 20, 'description': '涼爽', 'color': '藍色', 'variable': 'Temp', 'context': '溫度等級'},
            {'lower': 60, 'upper': 70, 'description': '及格', 'color': '黃色', 'variable': 'score', 'context': '考試分數'},
            {'lower': 80, 'upper': 95, 'description': '優異', 'color': '綠色', 'variable': 'grade', 'context': '考試分數'}
        ]
        chosen_range = random.choice(range_data)

        lower = chosen_range['lower']
        upper = chosen_range['upper']
        description = chosen_range['description']
        color = chosen_range['color']
        variable = chosen_range['variable']
        context = chosen_range['context']
        
        # Construct the table part (Guardrail 1: avoid f-string for expressions)
        table_entry_template = "{context_val}{lower_val}∼{upper_val}: {desc}（{color_val}）"
        table_entry = table_entry_template.replace("{context_val}", context).replace(
            "{lower_val}", str(lower)).replace("{upper_val}", str(upper)).replace(
            "{desc}", description).replace("{color_val}", color)

        question_text = r"下表為某指標等級對照表，試問：{table_entry}⑴ 若某日的情境為『{description}』，且當時的指標值為 ${variable}$，試以不等式表示 ${variable}$ 的範圍。".replace(
            "{table_entry}", table_entry).replace(
            "{description}", description).replace(
            "{variable}", variable)
        
        correct_answer = f"{lower},{upper}" # Numerical list for check()
        answer = r"${lower} \le {variable} \le {upper}$".replace( # Full inequality string for display (Guardrail 3: single braces)
            "{lower}", str(lower)).replace(
            "{variable}", variable).replace(
            "{upper}", str(upper))
    
    # V7. 數據與欄位: 返回字典必須且僅能包含指定欄位
    # V7. 時間戳記: 更新時必須將 created_at 設為 datetime.now() 並遞增 version
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64, # Always None for these 3 types
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
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
