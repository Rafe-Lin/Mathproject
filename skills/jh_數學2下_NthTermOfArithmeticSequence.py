# ==============================================================================
# ID: jh_數學2下_NthTermOfArithmeticSequence
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 52.13s | RAG: 5 examples
# Created At: 2026-01-19 15:15:02
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

# [CRITICAL] 輔助函式定義於模組頂層 (Helper functions defined at the top level)

def _generate_arithmetic_sequence_params_for_type1():
    """
    用途: 生成用於「已知 a_1, d, n，求 a_n」題型的參數。
    邏輯:
        隨機生成首項 a1 (整數，範圍 [-20, 20])。
        隨機生成公差 d (非零整數，範圍 [-7, -2] U [2, 7])。
        隨機生成項數 n_term (整數，範圍 [5, 18])，確保 n_term > 1。
        計算 an = a1 + (n_term - 1) * d。
    回傳: (a1, d, n_term, an) (所有值皆為 int)。
    """
    a1 = random.randint(-20, 20)
    d = random.choice(list(range(-7, -1)) + list(range(2, 8))) # [-7, -2] U [2, 7]
    n_term = random.randint(5, 18)
    an = a1 + (n_term - 1) * d
    return a1, d, n_term, an

def _generate_arithmetic_sequence_params_for_type2():
    """
    用途: 生成用於「已知 a_1, a_n, n，求 d」題型的參數。
    邏輯:
        隨機生成首項 a1 (整數，範圍 [-20, 20])。
        隨機生成實際公差 d_actual (非零整數，範圍 [-7, -2] U [2, 7])。
        隨機生成項數 n_term (整數，範圍 [5, 18])，確保 n_term > 1。
        計算 an = a1 + (n_term - 1) * d_actual。
        此生成方式自然保證 (an - a1) 可被 (n_term - 1) 整除，且 d_actual 為整數。
    回傳: (a1, an, n_term, d_actual) (所有值皆為 int)。
    """
    a1 = random.randint(-20, 20)
    d_actual = random.choice(list(range(-7, -1)) + list(range(2, 8))) # [-7, -2] U [2, 7]
    n_term = random.randint(5, 18)
    an = a1 + (n_term - 1) * d_actual
    return a1, an, n_term, d_actual

def _generate_arithmetic_sequence_params_for_type3():
    """
    用途: 生成用於「已知 a_n, d, n，求 a_1」題型的參數。
    邏輯:
        隨機生成實際首項 a1_actual (整數，範圍 [-20, 20])。
        隨機生成公差 d (非零整數，範圍 [-7, -2] U [2, 7])。
        隨機生成項數 n_term (整數，範圍 [5, 18])，確保 n_term > 1。
        計算 an = a1_actual + (n_term - 1) * d。
    回傳: (an, d, n_term, a1_actual) (所有值皆為 int)。
    """
    a1_actual = random.randint(-20, 20)
    d = random.choice(list(range(-7, -1)) + list(range(2, 8))) # [-7, -2] U [2, 7]
    n_term = random.randint(5, 18)
    an = a1_actual + (n_term - 1) * d
    return an, d, n_term, a1_actual

def _generate_arithmetic_sequence_params_for_type4():
    """
    用途: 生成用於「已知 a_1, d, a_n，求 n」題型的參數。
    邏輯:
        隨機生成首項 a1 (整數，範圍 [-20, 20])。
        隨機生成公差 d (非零整數，範圍 [-7, -2] U [2, 7])。
        隨機生成實際項數 n_actual (整數，範圍 [5, 18])，確保 n_actual > 1。
        計算 an = a1 + (n_actual - 1) * d。
        此生成方式自然保證 (an - a1) 可被 d 整除，且 n_actual 為正整數。
    回傳: (a1, d, an, n_actual) (所有值皆為 int)。
    """
    a1 = random.randint(-20, 20)
    d = random.choice(list(range(-7, -1)) + list(range(2, 8))) # [-7, -2] U [2, 7]
    n_actual = random.randint(5, 18)
    an = a1 + (n_actual - 1) * d
    return a1, d, an, n_actual

def _generate_arithmetic_sequence_params_for_type5():
    """
    用途: 生成用於「已知 a_i, a_j，求 a_k」題型的參數。
    邏輯:
        隨機生成實際首項 a1_actual (整數，範圍 [-15, 15])。
        隨機生成實際公差 d_actual (非零整數，範圍 [-6, -2] U [2, 6])。
        從 [3, 18] 範圍內隨機選取三個不重複的整數作為 i, j, k，並進行排序以確保 i < j < k。
        計算 ai = a1_actual + (i - 1) * d_actual。
        計算 aj = a1_actual + (j - 1) * d_actual。
        計算 ak = a1_actual + (k - 1) * d_actual (此為答案)。
    回傳: (ai, aj, i, j, k, ak) (所有值皆為 int)。
    """
    a1_actual = random.randint(-15, 15)
    d_actual = random.choice(list(range(-6, -1)) + list(range(2, 7))) # [-6, -2] U [2, 6]
    terms = sorted(random.sample(range(3, 19), 3)) # Ensure i, j, k are distinct and ordered, range(3, 19) to include 18
    i, j, k = terms[0], terms[1], terms[2]
    
    ai = a1_actual + (i - 1) * d_actual
    aj = a1_actual + (j - 1) * d_actual
    ak = a1_actual + (k - 1) * d_actual
    
    return ai, aj, i, j, k, ak

def _generate_arithmetic_sequence_params_for_type6():
    """
    用途: 生成用於「等差數列應用題」題型的參數。
    邏輯:
        隨機生成起始值 s_start (整數，範圍 [10, 50])。
        隨機生成變化量 s_diff (非零整數，範圍 [-10, -2] U [2, 10])。
        隨機生成目標項數 n_term (整數，範圍 [5, 15])。
        計算 an = s_start + (n_term - 1) * s_diff。
    回傳: (s_start, s_diff, n_term, an) (所有值皆為 int)。
    """
    s_start = random.randint(10, 50)
    s_diff = random.choice(list(range(-10, -1)) + list(range(2, 11))) # [-10, -2] U [2, 10]
    n_term = random.randint(5, 15)
    an = s_start + (n_term - 1) * s_diff
    return s_start, s_diff, n_term, an

def _format_latex_string(template, replacements):
    """
    用途: 處理包含 LaTeX 語法的字串格式化，避免 f-string 導致的衝突。
    邏輯: 接收一個模板字串和一個字典 ({"{placeholder}": value})，將模板中的佔位符替換為 str(value)。
    回傳: 格式化後的字串。
    """
    formatted_string = template
    for key, value in replacements.items():
        formatted_string = formatted_string.replace(key, str(value))
    return formatted_string

def generate(level=1):
    # [題型鏡射] 隨機選擇題型，對應 RAG 例題
    problem_type = random.choice([1, 2, 3, 4, 5, 6]) 

    question_text = ""
    correct_answer = ""
    image_base64 = None # 等差數列題目不涉及圖形

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 4, 5): 已知 a_1, d, n，求 a_n
        a1, d, n_term, an = _generate_arithmetic_sequence_params_for_type1()
        
        template = r"已知一個等差數列的首項 $a_1 = {a1}$，公差 $d = {d}$。求其第 {n_term} 項 $a_{n_term}$ 的值。"
        replacements = {"{a1}": a1, "{d}": d, "{n_term}": n_term}
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(an) # [CRITICAL RULE: Answer Data Purity]

    elif problem_type == 2:
        # Type 2 (Variation of a_n = a_1 + (n-1)d): 已知 a_1, a_n, n，求 d
        a1, an, n_term, d_actual = _generate_arithmetic_sequence_params_for_type2()
        
        template = r"已知一個等差數列的首項 $a_1 = {a1}$，第 {n_term} 項 $a_{n_term} = {an}$。求其公差 $d$ 的值。"
        replacements = {"{a1}": a1, "{an}": an, "{n_term}": n_term}
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(d_actual) # [CRITICAL RULE: Answer Data Purity]

    elif problem_type == 3:
        # Type 3 (Variation of a_n = a_1 + (n-1)d): 已知 a_n, d, n，求 a_1
        an, d, n_term, a1_actual = _generate_arithmetic_sequence_params_for_type3()
        
        template = r"已知一個等差數列的第 {n_term} 項 $a_{n_term} = {an}$，公差 $d = {d}$。求其首項 $a_1$ 的值。"
        replacements = {"{an}": an, "{d}": d, "{n_term}": n_term}
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(a1_actual) # [CRITICAL RULE: Answer Data Purity]

    elif problem_type == 4:
        # Type 4 (Maps to Example 2): 已知 a_1, d, a_n，求 n
        a1, d, an, n_actual = _generate_arithmetic_sequence_params_for_type4()
        
        template = r"已知一個等差數列的首項 $a_1 = {a1}$，公差 $d = {d}$。若某項的值為 {an}，求該項是第幾項 (即 $n$ 的值)？"
        replacements = {"{a1}": a1, "{d}": d, "{an}": an}
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(n_actual) # [CRITICAL RULE: Answer Data Purity]

    elif problem_type == 5:
        # Type 5 (Variation of a_n = a_1 + (n-1)d): 已知 a_i, a_j，求 a_k
        ai, aj, i, j, k, ak = _generate_arithmetic_sequence_params_for_type5()
        
        template = r"已知一個等差數列的第 {i} 項 $a_{i} = {ai}$，第 {j} 項 $a_{j} = {aj}$。求其第 {k} 項 $a_{k}$ 的值。"
        replacements = {"{i}": i, "{ai}": ai, "{j}": j, "{aj}": aj, "{k}": k}
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(ak) # [CRITICAL RULE: Answer Data Purity]

    elif problem_type == 6:
        # Type 6 (Maps to Example 3): 等差數列應用題 (Find an)
        s_start, s_diff, n_term, an = _generate_arithmetic_sequence_params_for_type6()
        
        item_names = ["積木", "書籍", "蘋果", "硬幣", "球", "玩具", "鉛筆"]
        item = random.choice(item_names)
        
        if s_diff > 0:
            verb = "增加"
        else:
            verb = "減少"
        
        template = r"某商店的 {item} 庫存量第一天有 {s_start} 個。如果每天的庫存量會比前一天 {verb} {abs_s_diff} 個，那麼第 {n_term} 天的庫存量會是多少個？"
        replacements = {
            "{item}": item,
            "{s_start}": s_start,
            "{verb}": verb,
            "{abs_s_diff}": abs(s_diff),
            "{n_term}": n_term
        }
        question_text = _format_latex_string(template, replacements)
        correct_answer = str(an) # [CRITICAL RULE: Answer Data Purity]

    # [數據與欄位] 鎖死回傳字典欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 內部使用，可與 correct_answer 相同
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # [時間戳記]
        "version": "1.0"
    }


    """
    [CRITICAL CODING STANDARDS: Verification & Stability]
    2. 通用 Check 函式模板 (Universal Check Template)：
    此函數已根據系統底層鐵律的「通用 Check 函式模板」進行實作，並遵循「閱卷與反饋」規範回傳 True/False。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, Ans= 等變數前綴
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        # 移除常見的中文單位
        s = s.replace("項", "").replace("根", "").replace("個", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                if d == 0: # 避免除以零
                    raise ValueError("Denominator cannot be zero")
                return n / d
            return float(val_str)
        
        user_num = parse_val(u)
        correct_num = parse_val(c)
        
        # 使用 math.isclose 進行浮點數比較，考慮精度問題
        # rel_tol=1e-5 允許相對誤差，abs_tol=0.0 確保小數點後精確度
        return math.isclose(user_num, correct_num, rel_tol=1e-5, abs_tol=0.0)
    except ValueError:
        # 如果轉換失敗 (例如使用者輸入非數字字串、除以零)，則視為錯誤，降級到字串比對
        pass
    except Exception: # 捕捉其他未預期的錯誤
        pass
        
    # 3. 降級為字串比對
    # 作為最終的備用方案，處理非數值或特殊格式的答案
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
