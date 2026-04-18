# ==============================================================================
# ID: jh_數學2上_WordProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 34.51s | RAG: 5 examples
# Created At: 2026-01-19 12:26:44
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
# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格, 中文標籤)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'長=|寬=|高=|邊長=|兩個數=|三個數=|數=|answer:|ans:', '', s) 
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
        s = s.replace("，", ",").replace("、", ",")
        # 移除單位
        s = re.sub(r'公分|公尺|cm|m|元|歲|號', '', s)
        # 移除括號 (如果是座標或數對)
        s = s.replace("(", "").replace(")", "")
        return s
    
    u_cleaned = clean(user_answer)
    c_cleaned = clean(correct_answer)

    # 處理多重答案 (以逗號分隔)
    u_parts = sorted([x for x in re.split(r'[,;]+', u_cleaned) if x])
    c_parts = sorted([x for x in re.split(r'[,;]+', c_cleaned) if x])

    if len(u_parts) != len(c_parts):
        return {"correct": False, "result": "答案數量不符。"}

    # 逐一比對
    is_correct = True
    for u, c in zip(u_parts, c_parts):
        try:
            if not math.isclose(float(u), float(c), rel_tol=1e-5):
                is_correct = False
                break
        except ValueError:
            # 非數值比對 (fallback)
            if u != c:
                is_correct = False
                break
    
    if is_correct:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", str(correct_answer))}


import re
from datetime import datetime

def generate(level: int = 1) -> dict:
    """
    生成國中二年級上學期「一元二次方程式應用問題」題目。
    包含四種典型題型：數值問題、幾何面積、路寬問題、連續整數。
    """
    problem_type = random.choice([1, 2, 3, 4])
    
    question_text = ""
    correct_answer = ""
    answer_display = ""
    image_base64 = None

    if problem_type == 1:
        # Type 1: 數值問題 (兩正整數之和為 S，積為 P)
        while True:
            a = random.randint(3, 20)
            b = random.randint(a + 1, a + 15) # Ensure distinct
            if a != b: break
        
        S_val = a + b
        P_val = a * b
        
        question_text = r"兩正整數之和為 {S}，積為 {P}，求此兩數。".replace("{S}", str(S_val)).replace("{P}", str(P_val))
        correct_answer = f"{a},{b}"
        answer_display = r"此兩數為 ${a}, {b}$。".replace("{a}", str(a)).replace("{b}", str(b))

    elif problem_type == 2:
        # Type 2: 幾何面積 (長方形長比寬多 k)
        width = random.randint(5, 20)
        diff_k = random.randint(2, 10)
        length = width + diff_k
        area = length * width
        
        question_text = r"一長方形的長比寬多 {k} 公分，面積為 {A} 平方公分，求長的長度與寬的長度。"\
                        .replace("{k}", str(diff_k)).replace("{A}", str(area))
        
        correct_answer = f"{length},{width}"
        answer_display = r"長為 ${L}$ 公分，寬為 ${W}$ 公分。".replace("{L}", str(length)).replace("{W}", str(width))
        
        if random.random() < 0.5:
             # 簡單示意圖
             polygons = [[(0, 0), (length, 0), (length, width), (0, width)]]
             labels = {f"Area={area}": (length/2, width/2)}
             image_base64 = draw_geometry_composite(polygons, labels)

    elif problem_type == 3:
        # Type 3: 路寬問題 (外圍道路)
        # 原矩形 L, W，外圍路寬 x，總面積 A_total = (L+2x)(W+2x)
        L = random.randint(10, 30)
        W = random.randint(5, 20) # W <= L
        x = random.randint(1, 5) # 路寬
        
        A_total = (L + 2*x) * (W + 2*x)
        
        question_text = r"有一長 {L} 公尺、寬 {W} 公尺的矩形花圃，今在其周圍開闢一條等寬的道路，若道路與花圃的總面積為 {A} 平方公尺，求道路的寬度。"\
                        .replace("{L}", str(L)).replace("{W}", str(W)).replace("{A}", str(A_total))
        
        correct_answer = str(x)
        answer_display = r"道路寬度為 ${x}$ 公尺。".replace("{x}", str(x))

    elif problem_type == 4:
        # Type 4: 連續整數平方和
        # 三個連續正整數 x-1, x, x+1 或 x, x+1, x+2
        start_n = random.randint(5, 20)
        nums = [start_n, start_n + 1, start_n + 2]
        sum_sq = sum(n*n for n in nums)
        
        question_text = r"三個連續正整數的平方和為 {S}，求這三個數。".replace("{S}", str(sum_sq))
        correct_answer = f"{nums[0]},{nums[1]},{nums[2]}"
        answer_display = r"這三個數為 ${n1}, {n2}, {n3}$。".replace("{n1}", str(nums[0]))\
                         .replace("{n2}", str(nums[1])).replace("{n3}", str(nums[2]))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
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
