# ==============================================================================
# ID: jh_數學2下_FunctionValue
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 96.71s | RAG: 5 examples
# Created At: 2026-01-20 19:12:32
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

# 輔助函式定義區 (Helper Functions)
# -----------------------------------------------------------------------------
def _generate_integer(min_val, max_val, exclude_zero=False):
    """生成指定範圍的隨機整數，可排除零。"""
    val = random.randint(min_val, max_val)
    if exclude_zero and val == 0:
        while val == 0:
            val = random.randint(min_val, max_val)
    return val

def _format_coefficient(coeff, var='x', is_first=False):
    """
    格式化係數，處理 1, -1, 0 的顯示。
    is_first: 如果是表達式的第一項，不顯示 '+' 號。
    """
    if coeff == 0:
        return ""
    elif coeff == 1:
        return f"{var}" if is_first else f"+{var}"
    elif coeff == -1:
        return f"-{var}"
    else:
        sign = "+" if coeff > 0 and not is_first else ""
        return f"{sign}{coeff}{var}"

def _format_constant(const, is_first=False):
    """
    格式化常數項。
    is_first: 如果是表達式的第一項，不顯示 '+' 號。
    """
    if const == 0:
        return ""
    sign = "+" if const > 0 and not is_first else ""
    return f"{sign}{const}"

def _format_linear_expression(a, b, var='x'):
    """
    格式化線性函數表達式 ax + b。
    遵循「方程式生成鎖死」規範，手動組合字串片段。
    """
    x_term_str = _format_coefficient(a, var, is_first=True)
    const_term_str = _format_constant(b, is_first=(x_term_str == ""))
    
    parts = []
    if x_term_str:
        parts.append(x_term_str)
    if const_term_str:
        parts.append(const_term_str)
    
    expr = "".join(parts)
    
    # 如果表達式為空 (a=0, b=0), 則顯示 "0"
    if not expr:
        expr = "0"
    
    return expr

# -----------------------------------------------------------------------------

def generate(level=1):
    problem_type = random.choice([
        "Type 1", "Type 2", "Type 3", "Type 4", "Type 5"
    ])
    
    question_text = ""
    correct_answer = ""
    image_base64 = None # 本技能不涉及圖形繪製，設為 None

    # V11.8: 嚴格遵循隨機生成與公式計算，禁絕硬編碼
    # V13.0: 座標選取控制 (不適用於此技能，但規範已鎖定)
    # V13.1: 禁絕假分數 (不適用於此技能，但規範已鎖定)
    # V13.5: 整數優先 (結果可能為浮點數，但會確保整數結果以整數呈現)

    if problem_type == "Type 1": # Type 1 (Maps to RAG Example 1): 線性函數求值 f(k)
        # 1. 隨機數據生成: f(x) = ax + b, find f(k)
        # RAG Ex 1 包含 y=100+2x (線性函數) 和 y=25 (常數函數)
        a = _generate_integer(-5, 5) # 允許 a=0 以生成常數函數
        b = _generate_integer(-10, 10)
        k = _generate_integer(-5, 5)

        # 避免生成 f(x) = 0 的平凡情況
        if a == 0 and b == 0:
            a = _generate_integer(-5, 5, exclude_zero=True) # 確保不是 f(x)=0

        # 2. 題目文字建構
        func_expr = _format_linear_expression(a, b, 'x')
        
        question_text_template = r"設函數 $f(x) = {func_expr}$，求 $f({k})$ 的值。"
        question_text = question_text_template.replace("{func_expr}", func_expr).replace("{k}", str(k))

        # 3. 計算正確答案
        result = a * k + b
        correct_answer = str(result)

    elif problem_type == "Type 2": # Type 2 (Maps to RAG Example 2): a1x + b1 = a2x + b2, find x
        # 1. 隨機數據生成
        # f1(x) = a1x + b1, f2(x) = a2x + b2. 求 x 使 f1(x) = f2(x).
        a1 = _generate_integer(-5, 5, exclude_zero=True)
        b1 = _generate_integer(-10, 10)
        a2 = _generate_integer(-5, 5) # a2 可以為 0 (常數函數)
        b2 = _generate_integer(-10, 10)

        # 確保 a1 != a2 以保證唯一解
        while a1 == a2:
            a2 = _generate_integer(-5, 5)
        
        # 為了確保 x 是整數解: (a1 - a2)x = b2 - b1
        # 設定一個整數 x_true, 然後調整 b1 使得該 x_true 為解
        x_true = _generate_integer(-5, 5)
        
        # 計算所需的 b1 值
        b1_target = b2 - (a1 - a2) * x_true
        b1 = b1_target 

        # 2. 題目文字建構
        func_expr1 = _format_linear_expression(a1, b1, 'x')
        func_expr2 = _format_linear_expression(a2, b2, 'x')
        
        question_text_template = r"若一次函數 $y={func_expr1}$ 與一次函數 $y={func_expr2}$ 在 $x=a$ 時的函數值相等，則 $a$ 為多少？"
        question_text = question_text_template \
            .replace("{func_expr1}", func_expr1) \
            .replace("{func_expr2}", func_expr2)

        # 3. 計算正確答案
        # a1*x + b1 = a2*x + b2  =>  (a1 - a2)x = b2 - b1  =>  x = (b2 - b1) / (a1 - a2)
        result = (b2 - b1) / (a1 - a2)
        correct_answer = str(int(result)) if result.is_integer() else str(result) # V13.5: 整數優先

    elif problem_type == "Type 3": # Type 3 (Maps to RAG Example 3): (x-k)/d = C, find x
        # 1. 隨機數據生成
        # 模型: y = (x - k) / d  和 y = C (常數函數)
        k_val = _generate_integer(-5, 5) # 類似 RAG Ex 3 中 (x-3)/2 的 -3
        d_val = _generate_integer(2, 5) # 分母，類似 RAG Ex 3 中 (x-3)/2 的 2
        
        # 生成一個目標整數解 'a' (題目中的未知數 x)
        a_true = _generate_integer(-5, 5)
        
        # 計算常數函數值 C，並確保 C 為整數
        # (a_true - k_val) 必須是 d_val 的倍數
        remainder = (a_true - k_val) % d_val
        if remainder != 0:
            # 調整 k_val 使得 (a_true - k_val) 成為 d_val 的倍數
            # 例如: k_val_new = a_true - (某個整數倍數 * d_val)
            k_val = a_true - (random.randint(-2, 2) * d_val) 

        C_val = (a_true - k_val) / d_val # 此時 C_val 保證為整數

        # 2. 題目文字建構
        # 格式化分數形式的線性表達式 y = (x - k) / d
        k_sign = "+" if k_val < 0 else "-"
        k_abs = abs(k_val)
        
        # 處理 k_val = 0 的情況: (x-0)/d 應顯示為 x/d
        if k_abs == 0:
            func_expr = r"\frac{x}{" + str(d_val) + "}"
        else:
            func_expr = r"\frac{x {k_sign} {k_abs}}{" + str(d_val) + "}"
            func_expr = func_expr.replace("{k_sign}", k_sign).replace("{k_abs}", str(k_abs))

        question_text_template = r"若一次函數 $y={func_expr}$ 與常數函數 $y={c_val}$ 在 $x=a$ 時的函數值相等，則 $a$ 為多少？"
        question_text = question_text_template \
            .replace("{func_expr}", func_expr) \
            .replace("{c_val}", str(int(C_val)))

        # 3. 計算正確答案
        # (x - k_val) / d_val = C_val  =>  x - k_val = C_val * d_val  =>  x = C_val * d_val + k_val
        result = C_val * d_val + k_val
        correct_answer = str(int(result)) # 結果保證為整數

    elif problem_type == "Type 4": # Type 4 (Maps to RAG Example 4): y=ax+b, given f(x1)=y1, f(x2)=y2. Find y=ax+b
        # 1. 隨機數據生成
        # 先生成真實的係數 a 和 b
        a_true = _generate_integer(-5, 5, exclude_zero=True)
        b_true = _generate_integer(-10, 10)

        # 生成兩個不同的 x 座標
        x1 = _generate_integer(-5, 5)
        x2 = _generate_integer(-5, 5)
        while x1 == x2:
            x2 = _generate_integer(-5, 5)
        
        # 計算對應的 y 座標
        y1 = a_true * x1 + b_true
        y2 = a_true * x2 + b_true

        # 2. 題目文字建構
        question_text_template = (
            r"若一次函數 $y=ax＋b$，在 $x={x1}$ 時的函數值是 ${y1}$，在 $x={x2}$ 時的函數值是 ${y2}$，"
            r"則此一次函數為何？"
        )
        question_text = question_text_template \
            .replace("{x1}", str(x1)) \
            .replace("{y1}", str(y1)) \
            .replace("{x2}", str(x2)) \
            .replace("{y2}", str(y2))

        # 3. 計算正確答案 (a_true 和 b_true 已經是正確答案)
        correct_answer_expr = _format_linear_expression(a_true, b_true, 'x')
        correct_answer = f"y={correct_answer_expr}"

    elif problem_type == "Type 5": # Type 5 (Maps to RAG Example 5): y=cx+d, given f(x1)=y1, f(x2)=y2. Find y=cx+d
        # 此題型的數學模型與 Type 4 完全相同，僅係數變數名稱不同 (c, d 而非 a, b)。
        # 1. 隨機數據生成
        c_true = _generate_integer(-5, 5, exclude_zero=True)
        d_true = _generate_integer(-10, 10)

        x1 = _generate_integer(-5, 5)
        x2 = _generate_integer(-5, 5)
        while x1 == x2:
            x2 = _generate_integer(-5, 5)
        
        y1 = c_true * x1 + d_true
        y2 = c_true * x2 + d_true

        # 2. 題目文字建構
        question_text_template = (
            r"若一次函數 $y=cx＋d$，在 $x={x1}$ 時的函數值是 ${y1}$，在 $x={x2}$ 時的函數值是 ${y2}$，"
            r"則此一次函數為何？"
        )
        question_text = question_text_template \
            .replace("{x1}", str(x1)) \
            .replace("{y1}", str(y1)) \
            .replace("{x2}", str(x2)) \
            .replace("{y2}", str(y2))

        # 3. 計算正確答案 (c_true 和 d_true 已經是正確答案)
        correct_answer_expr = _format_linear_expression(c_true, d_true, 'x')
        correct_answer = f"y={correct_answer_expr}"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # V11.8: answer 欄位也鎖定為純數據
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    V11.8: 強韌閱卷邏輯 (Robust Check Logic)
    V12.6: 結構鎖死 - 數值序列比對 (此處為單一數值比對)
    V13.5: 禁絕複雜比對 - 統一使用數字序列比對 (此處為單一數值)
    遵循「系統底層鐵律」中的「通用 Check 函式模板」與「閱卷與反饋」規範。
    """
    # 1. 清洗雙方輸入 (Input Sanitization)
    def clean(s):
        s = str(s).strip().lower()
        # 移除 LaTeX 符號、變數前綴、所有空白字元
        s = s.replace("$", "").replace("\\", "").replace(" ", "")
        
        # 移除常見答案前綴 (e.g., y=, f(x)=, a=, x=, ans:)
        s = re.sub(r'^(y=|f\(x\)=|a=|x=|ans:)', '', s)
        
        # 正規化係數 1 (e.g., +1x -> +x, 1x -> x)
        s = re.sub(r'([+\-])1([a-z])', r'\1\2', s) # -1x -> -x, +1y -> +y
        s = re.sub(r'^1([a-z])', r'\1', s)        # 1x -> x (開頭)
        
        # 正規化常數項為 0 的情況 (e.g., x+0 -> x)
        s = re.sub(r'\+0$', '', s)
        s = re.sub(r'-0$', '', s)
        
        # 處理 "0+x" -> "x", "0-x" -> "-x"
        s = re.sub(r'^0\+', '', s) # 0+x -> x
        s = re.sub(r'^0-', '-', s) # 0-x -> -x
        
        # 處理 "0x" 成為 "0" 的情況 (如果它是唯一項或開頭項)
        s = re.sub(r'^0x([+\-])?', '0', s) # 0x+3 -> 0+3 -> 3. 0x -> 0
        
        # 如果表達式在清洗後變為空 (例如 "y=0" 清洗後為空字串)，應視為 "0"
        if not s: 
            s = "0"
        
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n / d
            return float(val_str)
        
        # 判斷使用者答案和正確答案是否都能解析為數字 (適用於 Type 1, 2, 3)
        u_is_num = False
        c_is_num = False
        u_parsed_val = None
        c_parsed_val = None
        
        try:
            u_parsed_val = parse_val(u)
            u_is_num = True
        except ValueError:
            pass

        try:
            c_parsed_val = parse_val(c)
            c_is_num = True
        except ValueError:
            pass

        if u_is_num and c_is_num:
            # 對於數值答案，使用浮點數比較並允許誤差
            if math.isclose(u_parsed_val, c_parsed_val, rel_tol=1e-5):
                return True
    except Exception:
        # 捕獲數值解析或比較過程中可能發生的任何異常
        pass
        
    # 3. 降級為字串比對 (適用於代數表達式如 y=ax+b，或數值比較失敗的情況)
    # 由於 `_format_linear_expression` 產生的是標準化格式，且 `clean` 函式
    # 盡力將使用者輸入正規化，因此直接的字串比對在此應足夠。
    if u == c:
        return True
    
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
