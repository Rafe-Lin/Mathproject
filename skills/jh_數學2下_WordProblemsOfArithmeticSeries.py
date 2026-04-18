# ==============================================================================
# ID: jh_數學2下_WordProblemsOfArithmeticSeries
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 108.07s | RAG: 5 examples
# Created At: 2026-01-19 15:43:47
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
import re

# --- Helper functions ---

def _generate_type_1():
    # Coder Instructions for _generate_type_1():
    # 1. 隨機生成參數:
    n = random.randint(8, 15)
    is_increasing = random.choice([True, False])

    if is_increasing:
        d = random.randint(2, 7)
        a1 = random.randint(5, 20)
    else:
        d_abs = random.randint(2, 5)
        d = -d_abs
        # CRITICAL LOGIC: 確保第 n 項 an 仍為正數。
        # a_n = a_1 + (n-1)d > 0 => a_1 > -(n-1)d = (n-1)d_abs
        min_a1 = (n - 1) * d_abs + random.randint(1, 5) # Ensure a_n >= 1
        a1 = random.randint(min_a1, min_a1 + 10)

    # 2. 計算答案: an = a1 + (n - 1) * d
    an = a1 + (n - 1) * d

    # 3. 建構 question_text:
    context_options = [
        ("禮堂", "排座位", "第一排有 {a1_val} 個座位，且每一排比前一排{d_desc}個座位", "第 {n_val} 排有多少個座位？", "個座位"),
        ("木材堆", "層", "最底層有 {a1_val} 根木材，往上每一層比下一層{d_desc}根", "第 {n_val} 層有多少根木材？", "根木材"),
        ("閱讀", "天", "第一天閱讀 {a1_val} 頁，之後每天比前一天{d_desc}頁", "第 {n_val} 天閱讀了多少頁？", "頁")
    ]
    context_type, unit, initial_desc, question_desc, unit_single_for_solution = random.choice(context_options)

    d_desc = f"多 {d}" if d > 0 else f"少 {abs(d)}"
    
    # The spec has `n_max_rows` in question_template, which is not `n`. I'll use a random value for it.
    n_max_rows = n + random.randint(2, 5) 
    
    question_template = r"某{context_type}共有 {n_max_rows} {unit}。若{initial_desc}，則{question_desc}"
    question_text = question_template.replace("{context_type}", context_type) \
                                 .replace("{n_max_rows}", str(n_max_rows)) \
                                 .replace("{unit}", unit) \
                                 .replace("{initial_desc}", initial_desc.replace("{a1_val}", str(a1)).replace("{d_desc}", d_desc)) \
                                 .replace("{n_val}", str(n)) \
                                 .replace("{question_desc}", question_desc.replace("{n_val}", str(n)))
    
    # 4. 定義 correct_answer: str(an)
    correct_answer = str(an)

    # 5. 建構 solution_text:
    solution_template = r"此為等差數列問題。已知首項 $a_1 = {a1_val}$，公差 $d = {d_val}$，欲求第 {n_val} 項 $a_{n}$。\\根據等差數列的第 $n$ 項公式 $a_n = a_1 + (n-1)d$：\\$a_{n} = {a1_val} + ({n_val}-1) \times ({d_val}) = {result_val}$。\\因此，{context_type}第 {n_val} {unit_single}有 {result_val} {unit_single}。"
    
    solution_text = solution_template.replace("{a1_val}", str(a1)) \
                                 .replace("{d_val}", str(d)) \
                                 .replace("{n_val}", str(n)) \
                                 .replace("{result_val}", str(an)) \
                                 .replace("{context_type}", context_type) \
                                 .replace("{unit_single}", unit_single_for_solution)
    
    # 6. 回傳字典:
    return {"question_text": question_text, "correct_answer": correct_answer, "solution_text": solution_text, "image_base64": None}


def _generate_type_2():
    # Coder Instructions for _generate_type_2():
    # 1. 隨機生成參數:
    a1 = random.randint(5, 20)
    d = random.randint(2, 5)
    n = random.randint(8, 20)

    # 2. 計算答案:
    an = a1 + (n - 1) * d
    Sn = n * (a1 + an) // 2

    # 3. 建構 question_text:
    context_options = [
        ("儲蓄計畫", "第一天儲蓄了 {a1_val} 元，之後每天比前一天多儲蓄 {d_val} 元", "{n_val} 天後，他總共儲蓄了多少元？"),
        ("金字塔", "最頂層有 {a1_val} 塊磚，往下每一層比上一層多 {d_val} 塊磚", "若金字塔共有 {n_val} 層，則總共有多少塊磚？"),
        ("跑步訓練", "第一天跑了 {a1_val} 公尺，之後每天比前一天多跑 {d_val} 公尺", "{n_val} 天內，他總共跑了多少公尺？")
    ]
    context_type, initial_desc, question_desc = random.choice(context_options)

    question_template = r"某{context_type}。{initial_desc}。請問{question_desc}"
    question_text = question_template.replace("{context_type}", context_type) \
                                 .replace("{initial_desc}", initial_desc.replace("{a1_val}", str(a1)).replace("{d_val}", str(d))) \
                                 .replace("{n_val}", str(n)) \
                                 .replace("{question_desc}", question_desc.replace("{n_val}", str(n)))
    
    # 4. 定義 correct_answer: str(Sn)
    correct_answer = str(Sn)

    # 5. 建構 solution_text:
    solution_template = r"此為等差級數問題。已知首項 $a_1 = {a1_val}$，公差 $d = {d_val}$，項數 $n = {n_val}$。\\首先計算第 $n$ 項 $a_n$：$a_n = {a1_val} + ({n_val}-1) \times {d_val} = {an_val}$。\\接著使用等差級數和公式 $S_n = \frac{n}{2}(a_1 + a_n)$：\\$S_n = \frac{{{n_val}}}{2}({a1_val} + {an_val}) = {Sn_val}$。\\因此，總共是 {Sn_val}。"
    solution_text = solution_template.replace("{a1_val}", str(a1)) \
                                 .replace("{d_val}", str(d)) \
                                 .replace("{n_val}", str(n)) \
                                 .replace("{an_val}", str(an)) \
                                 .replace("{Sn_val}", str(Sn))
    
    # 6. 回傳字典:
    return {"question_text": question_text, "correct_answer": correct_answer, "solution_text": solution_text, "image_base64": None}


def _generate_type_3():
    # Coder Instructions for _generate_type_3():
    # 1. 隨機生成參數:
    a1_gen = random.randint(5, 15) # Use gen suffix to avoid conflict with a1 for find_a1 sub-type
    d_gen = random.randint(2, 5)
    n_gen = random.randint(5, 12)

    # 2. 計算相關值:
    Sn_gen = n_gen * (2 * a1_gen + (n_gen - 1) * d_gen) // 2
    an_gen = a1_gen + (n_gen - 1) * d_gen

    # 3. 子類型選擇 (Find n or a1):
    sub_type = random.choice(["find_n", "find_a1"])

    question_text = ""
    correct_answer = ""
    solution_text = ""

    if sub_type == "find_n":
        # 子類型 3a: 尋找項數 (find_n)
        question_template = r"某儲蓄計畫中，第一天儲蓄 {a1_val} 元，之後每天比前一天多儲蓄 {d_val} 元。若總共儲蓄了 {Sn_val} 元，請問他儲蓄了多少天？"
        question_text = question_template.replace("{a1_val}", str(a1_gen)).replace("{d_val}", str(d_gen)).replace("{Sn_val}", str(Sn_gen))
        
        correct_answer = str(n_gen)

        two_a1 = 2 * a1_gen
        two_Sn = 2 * Sn_gen
        two_a1_minus_d = 2 * a1_gen - d_gen
        
        solution_template = r"已知首項 $a_1 = {a1_val}$，公差 $d = {d_val}$，總和 $S_n = {Sn_val}$。\\使用公式 $S_n = \frac{n}{2}(2a_1 + (n-1)d)$：\\${Sn_val} = \frac{n}{2}(2 \times {a1_val} + (n-1) \times {d_val})$\\${Sn_val} \times 2 = n({two_a1} + {d_val}n - {d_val})$\\${two_Sn} = n({d_val}n + {two_a1_minus_d}) = {d_val}n^2 + {two_a1_minus_d}n$\\整理成二次方程式：${d_val}n^2 + {two_a1_minus_d}n - {two_Sn} = 0$\\解此二次方程式可得 $n = {n_val}$ (另一解為負數，不合)。\\因此，他儲蓄了 {n_val} 天。"
        solution_text = solution_template.replace("{a1_val}", str(a1_gen)) \
                                     .replace("{d_val}", str(d_gen)) \
                                     .replace("{Sn_val}", str(Sn_gen)) \
                                     .replace("{two_a1}", str(two_a1)) \
                                     .replace("{two_Sn}", str(two_Sn)) \
                                     .replace("{two_a1_minus_d}", str(two_a1_minus_d)) \
                                     .replace("{n_val}", str(n_gen))
        
    elif sub_type == "find_a1":
        # 子類型 3b: 尋找首項 (find_a1) - Adjusted to mirror RAG Ex 3 more closely
        # RAG Ex 3: Sn, n, d -> find a1
        
        # We use a1_gen, d_gen, n_gen, Sn_gen as the hidden correct values.
        a1 = a1_gen # This is the target answer
        d = d_gen
        n = n_gen
        Sn = Sn_gen

        context_options_a1 = [
            ("學校禮堂", "排座位", "預計要排 {Sn_val} 個座位，一共 {n_val} 排，且每一排都比前一排多 {d_val} 個座位", "則第一排要放多少個座位？", "個座位", "第一排要放"),
            ("書架", "層", "總共有 {Sn_val} 本書，堆疊成 {n_val} 層，且每一層都比上一層多 {d_val} 本書", "則最頂層(第一層)要放多少本書？", "本書", "最頂層要放")
        ]
        context_type_a1, unit_a1, initial_desc_a1, question_desc_a1, final_unit_text, final_context_text = random.choice(context_options_a1)

        question_template_a1 = r"{context_type}。{initial_desc}，{question_desc}"
        question_text = question_template_a1.replace("{context_type}", context_type_a1) \
                                            .replace("{initial_desc}", initial_desc_a1.replace("{Sn_val}", str(Sn)).replace("{n_val}", str(n)).replace("{d_val}", str(d))) \
                                            .replace("{question_desc}", question_desc_a1)
            
        correct_answer = str(a1)

        two_Sn = 2 * Sn
        n_minus_1_d = (n - 1) * d
        
        solution_template_a1 = r"已知總和 $S_n = {Sn_val}$，項數 $n = {n_val}$，公差 $d = {d_val}$。\\使用公式 $S_n = \frac{n}{2}(2a_1 + (n-1)d)$：\\${Sn_val} = \frac{{{n_val}}}{2}(2a_1 + ({n_val}-1) \times {d_val})$\\${two_Sn} = {n_val}(2a_1 + {n_minus_1_d})$\\$\frac{{{two_Sn}}}{{{n_val_denom}}} = 2a_1 + {n_minus_1_d}$\\${two_Sn_div_n} = 2a_1 + {n_minus_1_d}$\\$2a_1 = {two_Sn_div_n} - {n_minus_1_d}$\\$a_1 = \frac{{{two_Sn_div_n} - {n_minus_1_d}}}{2} = {a1_val}$。\\因此，{final_context_text} {a1_val} {final_unit_text}。"
        
        solution_text = solution_template_a1.replace("{Sn_val}", str(Sn)) \
                                             .replace("{n_val}", str(n)) \
                                             .replace("{d_val}", str(d)) \
                                             .replace("{two_Sn}", str(two_Sn)) \
                                             .replace("{n_minus_1_d}", str(n_minus_1_d)) \
                                             .replace("{n_val_denom}", str(n)) \
                                             .replace("{two_Sn_div_n}", str(two_Sn // n)) \
                                             .replace("{a1_val}", str(a1)) \
                                             .replace("{final_context_text}", final_context_text) \
                                             .replace("{final_unit_text}", final_unit_text)
            
    # 4. 回傳字典:
    return {"question_text": question_text, "correct_answer": correct_answer, "solution_text": solution_text, "image_base64": None}


def _generate_type_4():
    # Coder Instructions for _generate_type_4():
    # 1. 隨機生成參數 (帶有驗證循環):
    while True:
        a1_A = random.randint(10, 30)
        d_A = random.randint(2, 4)
        a1_B = random.randint(5, 20)
        d_B = random.randint(d_A + 1, d_A + 3) # Ensure d_B > d_A

        # Ensure a1_A is initially greater than a1_B for a realistic "catch-up" scenario
        if a1_A <= a1_B:
            continue

        # Solve for n: a1_A + (n-1)*d_A = a1_B + (n-1)*d_B
        # (n-1)*(d_A - d_B) = a1_B - a1_A
        numerator = a1_B - a1_A
        denominator = d_A - d_B # This will be negative, e.g., (2-5) = -3

        if denominator == 0: # Should not happen with d_B > d_A
            continue

        if numerator % denominator == 0:
            n_minus_1 = numerator // denominator
            n = n_minus_1 + 1
            if n > 1 and n <= 20: # Ensure n is a positive integer and reasonable (e.g., within 20 days)
                break # Valid n found, exit loop
    
    # 2. 建構 question_text:
    question_template = r"小明第一天儲蓄 {a1_A_val} 元，之後每天多儲蓄 {d_A_val} 元。小華第一天儲蓄 {a1_B_val} 元，之後每天多儲蓄 {d_B_val} 元。請問從第幾天開始，小華當天的儲蓄金額會與小明當天的儲蓄金額相等？"
    question_text = question_template.replace("{a1_A_val}", str(a1_A)) \
                                 .replace("{d_A_val}", str(d_A)) \
                                 .replace("{a1_B_val}", str(a1_B)) \
                                 .replace("{d_B_val}", str(d_B))
    
    # 3. 定義 correct_answer: str(n)
    correct_answer = str(n)

    # 4. 建構 solution_text:
    diff_d = d_A - d_B
    diff_a1 = a1_B - a1_A
    n_minus_1_val_calc = int(diff_a1 / diff_d) # Use int() to avoid float representation in solution
    
    solution_template = r"設第 $n$ 天小明與小華的儲蓄金額相等。\\小明的每日儲蓄為等差數列，首項 $a_{1,A} = {a1_A_val}$，公差 $d_A = {d_A_val}$。\\第 $n$ 天的儲蓄金額 $a_{n,A} = {a1_A_val} + (n-1){d_A_val}$。\\小華的每日儲蓄為等差數列，首項 $a_{1,B} = {a1_B_val}$，公差 $d_B = {d_B_val}$。\\第 $n$ 天的儲蓄金額 $a_{n,B} = {a1_B_val} + (n-1){d_B_val}$。\\令 $a_{n,A} = a_{n,B}$：\\${a1_A_val} + (n-1){d_A_val} = {a1_B_val} + (n-1){d_B_val}$\\$(n-1)({d_A_val} - {d_B_val}) = {a1_B_val} - {a1_A_val}$\\$(n-1)({diff_d}) = {diff_a1}$\\$n-1 = \frac{{{diff_a1}}}{{{diff_d}}}$\\$n-1 = {n_minus_1_val}$\\$n = {n_val}$。\\因此，從第 {n_val} 天開始，小華當天的儲蓄金額會與小明當天的儲蓄金額相等。"
    solution_text = solution_template.replace("{a1_A_val}", str(a1_A)) \
                                 .replace("{d_A_val}", str(d_A)) \
                                 .replace("{a1_B_val}", str(a1_B)) \
                                 .replace("{d_B_val}", str(d_B)) \
                                 .replace("{diff_d}", str(diff_d)) \
                                 .replace("{diff_a1}", str(diff_a1)) \
                                 .replace("{n_minus_1_val}", str(n_minus_1_val_calc)) \
                                 .replace("{n_val}", str(n))
    
    # 5. 回傳字典:
    return {"question_text": question_text, "correct_answer": correct_answer, "solution_text": solution_text, "image_base64": None}

# --- End of Helper functions ---

def generate(level=1):
    problem_type = random.choice([
        "type_1_find_term_or_diff",
        "type_2_find_sum",
        "type_3_find_n_or_a1",
        "type_4_multi_step"
    ])

    if problem_type == "type_1_find_term_or_diff":
        problem_data = _generate_type_1()
    elif problem_type == "type_2_find_sum":
        problem_data = _generate_type_2()
    elif problem_type == "type_3_find_n_or_a1":
        problem_data = _generate_type_3()
    elif problem_type == "type_4_multi_step":
        problem_data = _generate_type_4()
    
    problem_data["created_at"] = datetime.now().isoformat()
    problem_data["version"] = "1.0.0" 
    return problem_data


# Check function as per CRITICAL CODING STANDARDS: Universal Check Template

    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        # Added explicit removal for common LaTeX/formatting characters as per spec and general robustness
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "").replace("ans:", "") 
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                if d == 0: raise ValueError("Denominator cannot be zero.") # Prevent division by zero
                return n/d
            return float(val_str)
        
        # Using math.isclose for float comparison robustness, though for arithmetic series answers are usually integers.
        # But the template supports floats, so keep it.
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch specific ValueError from parse_val for invalid numbers/division by zero
        pass
    except Exception as e: # Catch any other general exceptions during parsing/comparison
        # print(f"Error during numerical check: {e}") # For debugging, remove in production
        pass
        
    # 3. 降級為字串比對
    if u == c: return {"correct": True, "result": "正確！"}
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
