# ==============================================================================
# ID: jh_數學2下_ArithmeticSequences
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 73.40s | RAG: 5 examples
# Created At: 2026-01-19 15:03:40
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


from datetime import datetime
import re

import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

# --- 輔助函式定義 ---

# V13.5 & V13.0 & V13.1: 處理數字顯示格式,確保整數顯示為整數,小數點後為零的浮點數顯示為整數
def _format_number_for_display(val):
    """
    格式化數字,如果為整數則顯示為整數,否則保留浮點數
    """
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)

# V13.1 & V10.2 C: 格式化分數,確保為帶分數形式且真分數部分分子小於分母
def _format_fraction(numerator, denominator):
    """
    將分數格式化為 LaTeX 字串,處理負數、整數和帶分數
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    if numerator == 0:
        return "0"
    
    sign = ""
    if numerator < 0:
        sign = "-"
        numerator = abs(numerator)
    
    # 簡化分數
    common_divisor = math.gcd(numerator, denominator)
    numerator //= common_divisor
    denominator //= common_divisor

    if numerator % denominator == 0:
        return f"{sign}{numerator // denominator}"
    
    integer_part = numerator // denominator
    fraction_numerator = numerator % denominator

    # V13.1: 確保真分數部分分子小於分母
    if fraction_numerator == 0:
        return f"{sign}{integer_part}"
    else:
        # V10.2 C: LaTeX 模板規範,使用單層大括號並搭配 replace
        if integer_part == 0:
            template = r"{sign}\frac{{{num}}}{{{den}}}"
            return template.replace("{sign}", sign).replace("{num}", str(fraction_numerator)).replace("{den}", str(denominator))
        else:
            template = r"{sign}{int_part}\frac{{{num}}}{{{den}}}"
            return template.replace("{sign}", sign).replace("{int_part}", str(integer_part)).replace("{num}", str(fraction_numerator)).replace("{den}", str(denominator))

# V17/V13.6: 繪製數線的輔助函式 (本技能暫不啟用圖片,但保留規範參考)
def _draw_number_line_base64(points_to_label=None, x_range=(-10, 10)):
    """
    繪製數線,並在指定範圍內標示主要刻度
    V17 CRITICAL: 必須有主要刻度數字標示
    V13.6: 嚴禁在 axhline/axvline 使用 arrowprops,必須使用 ax.plot 繪製箭頭
    V13.0: 座標軸範圍必須是對稱整數,xticks 間隔必須固定為 1
    V10.2 D: 原點 '0' 需加粗，點標籤需加白色光暈
    """
    fig, ax = plt.subplots(figsize=(8, 2))
    
    ax.axhline(0, color='black', linewidth=1)

    # V13.6: 繪製箭頭
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8) # 右箭頭
    ax.plot(x_range[0], 0, "<k", clip_on=False, markersize=8) # 左箭頭

    ax.set_xlim(x_range[0], x_range[1])
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # V17 CRITICAL: 確保 X 軸顯示主要整數刻度
    # V13.0: xticks 間隔必須固定為 1
    major_ticks = np.arange(math.floor(x_range[0]), math.ceil(x_range[1]) + 1, 1)
    ax.set_xticks(major_ticks)
    ax.set_xticklabels([str(int(t)) if t == int(t) else '' for t in major_ticks])
    
    # V10.2 D: 標註原點 '0' (18號加粗)
    ax.text(0, -0.5, '0', fontsize=18, fontweight='bold', ha='center', va='top')

    # V13.5 & V13.1: 標籤隔離,ax.text 只能標註點的名稱 (Label),不能包含座標值
    if points_to_label:
        for val, label in points_to_label:
            ax.plot(val, 0, 'o', color='red', markersize=6)
            # V10.2 D: 點標籤需加白色光暈 (bbox)
            ax.text(val, 0.2, label, ha='center', va='bottom', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate(level=1):
    # V4. 題型鏡射 (Problem Mirroring): 隨機分流到不同的等差數列題型
    # 根據「最高權限指令」MANDATORY MIRRORING RULES 嚴格映射
    # Type 1 -> RAG Ex 1, Ex 4 (尋找第 N 項)
    # Type 2 -> RAG Ex 2 (給定兩項,求公差或首項)
    # Type 3 -> RAG Ex 3, Ex 5 (判斷是否為等差數列)
    problem_type = random.choice([1, 2, 3]) 

    question_text = ""
    correct_answer = ""
    image_base64 = None # V3. 幾何/圖形題的特殊規範: 預設為 None,避免不必要圖片或洩漏答案軌跡
    
    # V18. Grade & Semantic Alignment: 確保題目符合國二下學期等差數列的學習內容

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 4): 尋找第 N 項
        # 數學模型: an = a1 + (n-1)d
        
        a1 = random.randint(-15, 15) # V10. 數據禁絕常數: 隨機生成首項
        d = random.randint(-7, 7)    # V10. 數據禁絕常數: 隨機生成公差
        while d == 0: # 公差不能為零,否則數列無意義,除非是全同數列 (但此題型通常要求非零公差)
            d = random.randint(-7, 7)

        n_to_find = random.randint(5, 18) # V10. 數據禁絕常數: 隨機生成要找的項數

        an = a1 + (n_to_find - 1) * d # V10. 數據禁絕常數: 答案透過公式計算得出

        # V5. 排版與 LaTeX 安全: 嚴格使用 .replace() 進行字串替換,嚴禁 f-string 處理 LaTeX
        question_text_template = r"一個等差數列的首項為 ${a_1}$，公差為 ${d}$。請問此數列的第 ${n}$ 項為何？"
        question_text = question_text_template.replace("{a_1}", _format_number_for_display(a1)).replace("{d}", _format_number_for_display(d)).replace("{n}", str(n_to_find))
        
        # V3. CRITICAL RULE: Answer Data Purity: correct_answer 必須是純數據
        correct_answer = _format_number_for_display(an) 

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 給定兩項,求公差或首項
        # 數學模型: am - an = (m-n)d
        
        idx1 = random.randint(2, 7) # V10. 隨機生成項數索引 1
        idx2 = random.randint(idx1 + 2, idx1 + 8) # V10. 隨機生成項數索引 2,確保 idx2 > idx1
        
        d_val = random.randint(-6, 6) # V10. 隨機生成公差
        while d_val == 0: # 公差不能為零
            d_val = random.randint(-6, 6)
        
        a1_temp = random.randint(-20, 20) # V10. 隨機生成首項
        term1 = a1_temp + (idx1 - 1) * d_val
        term2 = a1_temp + (idx2 - 1) * d_val

        if random.choice([True, False]): # 隨機決定問公差還是首項
            # V5. 排版與 LaTeX 安全
            question_text_template = r"一個等差數列的第 ${idx1}$ 項為 ${term1}$，第 ${idx2}$ 項為 ${term2}$。請問此數列的公差為何？"
            question_text = question_text_template.replace("{idx1}", str(idx1)).replace("{term1}", _format_number_for_display(term1)).replace("{idx2}", str(idx2)).replace("{term2}", _format_number_for_display(term2))
            # V3. Answer Data Purity
            correct_answer = _format_number_for_display(d_val) 
        else:
            # V5. 排版與 LaTeX 安全
            question_text_template = r"一個等差數列的第 ${idx1}$ 項為 ${term1}$，第 ${idx2}$ 項為 ${term2}$。請問此數列的首項為何？"
            question_text = question_text_template.replace("{idx1}", str(idx1)).replace("{term1}", _format_number_for_display(term1)).replace("{idx2}", str(idx2)).replace("{term2}", _format_number_for_display(term2))
            # V3. Answer Data Purity
            correct_answer = _format_number_for_display(a1_temp) 

    elif problem_type == 3:
        # Type 3 (Maps to Example 3, 5): 判斷是否為等差數列,並寫出公差
        # 數學模型: 檢查 a_n+1 - a_n 是否為常數
        
        is_arithmetic = random.choice([True, False])
        num_terms = random.randint(4, 6) # 序列長度
        sequence_terms = []
        common_difference = None

        if is_arithmetic:
            a1_val = random.randint(-10, 10)
            d_val = random.choice([random.randint(-5, 5), random.uniform(-2.5, 2.5)]) # 允許浮點數公差
            
            # 確保公差不會太小或為零 (除非是常數數列)
            if isinstance(d_val, float):
                d_val = round(d_val * 2) / 2 # 確保公差是整數或 X.5
                if abs(d_val) < 0.1 and random.random() < 0.5: # 避免過小的非零浮點數,偶爾允許0
                    d_val = 0.5 if random.random() < 0.5 else -0.5
                elif d_val == 0: # 允許常數數列
                    pass
            else: # 整數公差
                if d_val == 0 and random.random() < 0.5: # 偶爾允許整數0公差
                    pass
                while d_val == 0: d_val = random.randint(-5, 5) # 否則確保非零

            # 30% 機率使用分數作為首項或公差
            if random.random() < 0.3:
                denominator_choice = random.choice([2, 3, 4])
                a1_val = random.randint(-10 * denominator_choice, 10 * denominator_choice) / denominator_choice
                d_val_num = random.randint(-5 * denominator_choice, 5 * denominator_choice)
                while d_val_num == 0: d_val_num = random.randint(-5 * denominator_choice, 5 * denominator_choice)
                d_val = d_val_num / denominator_choice
            
            common_difference = d_val
            for i in range(num_terms):
                sequence_terms.append(a1_val + i * common_difference)
            
            # 格式化序列中的每個項,確保分數或整數顯示正確
            formatted_terms = []
            for term_val in sequence_terms:
                if isinstance(term_val, float) and not term_val.is_integer():
                    # 嘗試將浮點數轉換為分數,如果它是簡單分數 (例如 X.5, X.25, X.75, X.33, X.66)
                    # 這裡使用一個簡化的邏輯,更精確的應使用分數類或更複雜的判斷
                    # 例如 0.5 -> 1/2, 0.25 -> 1/4, 0.333... -> 1/3 (近似)
                    if abs(term_val * 100 - round(term_val * 100)) < 1e-9: # 檢查是否為兩位小數點
                        temp_num = int(round(term_val * 100))
                        temp_den = 100
                        formatted_terms.append(_format_fraction(temp_num, temp_den))
                    elif abs(term_val * 3 - round(term_val * 3)) < 1e-9: # 檢查是否為1/3相關
                        temp_num = int(round(term_val * 3))
                        temp_den = 3
                        formatted_terms.append(_format_fraction(temp_num, temp_den))
                    else:
                        formatted_terms.append(_format_number_for_display(term_val))
                else:
                    formatted_terms.append(_format_number_for_display(term_val))
            
            sequence_str = " , ".join([f"{t}" for t in formatted_terms])
            question_text_template = r"判斷下列何者是等差數列。如果是等差數列，寫出它的公差。$${sequence}$$"
            question_text = question_text_template.replace("{sequence}", sequence_str)
            
            # 格式化公差用於答案顯示
            if isinstance(common_difference, float) and not common_difference.is_integer():
                # 嘗試將浮點數公差轉換為分數,與序列項處理方式類似
                if abs(common_difference * 100 - round(common_difference * 100)) < 1e-9:
                    num = int(round(common_difference * 100))
                    den = 100
                    formatted_d = _format_fraction(num, den)
                elif abs(common_difference * 3 - round(common_difference * 3)) < 1e-9:
                    num = int(round(common_difference * 3))
                    den = 3
                    formatted_d = _format_fraction(num, den)
                else:
                    formatted_d = _format_number_for_display(common_difference)
            else:
                formatted_d = _format_number_for_display(common_difference)

            correct_answer = f"是，公差為 ${formatted_d}$"

        else: # 不是等差數列
            a1_val = random.randint(-10, 10)
            d1 = random.randint(-5, 5)
            while d1 == 0: d1 = random.randint(-5, 5)
            d2 = random.randint(-5, 5)
            while d2 == 0 or d2 == d1: d2 = random.randint(-5, 5) # 確保至少有一個不同的公差

            sequence_terms.append(a1_val)
            sequence_terms.append(a1_val + d1)
            sequence_terms.append(a1_val + d1 + d2) # 引入不同的公差

            # 對剩餘的項,使其明顯不是等差數列
            for i in range(3, num_terms):
                if random.random() < 0.5: # 繼續使用 d2 或引入新的隨機差異
                    sequence_terms.append(sequence_terms[-1] + d2 + random.choice([-1, 1]) * random.randint(1, 2))
                else:
                    sequence_terms.append(random.randint(int(sequence_terms[-1] - 5), int(sequence_terms[-1] + 5)))
            
            # 確保確實不是等差數列 (防止隨機生成巧合)
            diffs = [sequence_terms[i+1] - sequence_terms[i] for i in range(len(sequence_terms)-1)]
            if len(set(diffs)) <= 1: # 如果偶然變成了等差數列,強制修改一個項
                idx_to_change = random.randint(2, num_terms - 1)
                sequence_terms[idx_to_change] += random.choice([-1, 1]) * random.randint(1, 3)
            
            # 格式化序列項用於顯示
            formatted_terms = [_format_number_for_display(term) for term in sequence_terms]
            sequence_str = " , ".join([f"{t}" for t in formatted_terms])
            question_text_template = r"判斷下列何者是等差數列。如果是等差數列，寫出它的公差。$${sequence}$$"
            question_text = question_text_template.replace("{sequence}", sequence_str)
            correct_answer = "不是"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # V3. CRITICAL RULE: Answer Data Purity
        "answer": correct_answer, # 開發環境顯示用
        "image_base64": image_base64, # V3. 幾何/圖形題的特殊規範: 本題型不需圖片，設為 None
        "created_at": datetime.now().isoformat(), # V7. 數據與欄位
        "version": "1.0", # V7. 數據與欄位
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
