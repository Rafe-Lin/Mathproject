# ==============================================================================
# ID: jh_數學2上_FactoringQuadraticsWithLeadingCoefficientNotOne
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 41.67s | RAG: 5 examples
# Created At: 2026-01-19 10:59:56
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


import re
from datetime import datetime

# 頂層函式:generate()

# 頂層函式:generate()
def generate(level=1):
    # 1. 設定係數範圍 (確保二次項係數 a*c != 1)
    # 模型：(ax + b)(cx + d)
    while True:
        a = random.randint(1, 5)
        c = random.randint(1, 5)
        if a * c > 1: # 確保 leading coefficient 不為 1
            break
    
    # b, d 為非零整數
    b = random.choice([x for x in range(-9, 10) if x != 0])
    d = random.choice([x for x in range(-9, 10) if x != 0])
    
    # 2. 展開多項式 P = (ac)x^2 + (ad+bc)x + bd
    A = a * c
    B = a * d + b * c
    C = b * d
    
    # 3. 格式化題目字串 (處理正負號)
    # 使用 fmt_num 輔助函式 (若有定義) 或手動處理
    term_B = f"+ {B}" if B >= 0 else f"- {abs(B)}"
    term_C = f"+ {C}" if C >= 0 else f"- {abs(C)}"
    
    # 若 B 或 C 為 0，則省略該項 (雖然本題設定不易為0，但加上判斷較安全)
    poly_str = f"{A}x^2"
    if B != 0: poly_str += f" {term_B}x"
    if C != 0: poly_str += f" {term_C}"
        
    question_text = f"因式分解下列各式： $${poly_str}$$"
    
    # 4. 設定正確答案
    # 格式：(ax+b)(cx+d)
    # 處理括號內的符號
    def fmt_poly(coef, const):
        op = "+" if const >= 0 else "-"
        return f"({coef}x {op} {abs(const)})"
        
    ans_part1 = fmt_poly(a, b)
    ans_part2 = fmt_poly(c, d)
    correct_answer = f"{ans_part1}{ans_part2}"
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": ""
    }

# 頂層函式:check()
def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確，支援交換律。
    格式: (ax+b)(cx+d)
    """
    if not user_answer: return {"correct": False, "result": "未提供答案"}

    # 正規化函式：將 "(ax+b)" 字串解析為 (a, b) tuple
    def parse_factor(s):
        s = s.strip().replace(" ", "").lower()
        if not s.startswith("(") or not s.endswith(")"): return None
        inner = s[1:-1] # 去掉括號
        # 預期格式 ax+b 或 ax-b
        # 簡單解析：找 x 的位置
        if 'x' not in inner: return None
        
        # 處理係數 a
        x_idx = inner.find('x')
        a_str = inner[:x_idx]
        if a_str == "" or a_str == "+": a = 1
        elif a_str == "-": a = -1
        else: 
            try: a = int(a_str)
            except: return None
            
        # 處理常數 b
        rest = inner[x_idx+1:]
        if rest == "": b = 0
        else:
            try: b = int(rest)
            except: return None
            
        return (a, b)

    # 分割兩個括號 (ax+b)(cx+d)
    def parse_factors(ans_str):
        # 簡單分割：用 ")(" 分割，或是正則
        ans_str = ans_str.strip().replace(" ", "").lower()
        # 補上中間的乘號如果有的話 (雖不常見)
        # 這裡假設標準格式 (..)(..)
        # 使用正則擷取所有 (...) 的區塊
        factors = re.findall(r'\(([^)]+)\)', ans_str)
        if len(factors) != 2: return None
        
        parsed = []
        for f in factors:
            # 重構回 (content) 丟給 parse_factor logic
            # 其實可以直接解析 content
            # let's reuse logic inline or adapt
            inner = f
            if 'x' not in inner: return None
            x_idx = inner.find('x')
            a_str = inner[:x_idx]
            if a_str == "" or a_str == "+": a = 1
            elif a_str == "-": a = -1
            else: 
                try: a = int(a_str)
                except: return None
            
            rest = inner[x_idx+1:]
            if rest == "": b = 0
            else:
                try: b = int(rest)
                except: return None
            parsed.append((a, b))
        return parsed

    u_factors = parse_factors(user_answer)
    c_factors = parse_factors(correct_answer)
    
    if not u_factors or not c_factors:
        return {"correct": False, "result": "答案格式錯誤，請依照 (ax+b)(cx+d) 格式輸入"}

    # 比對邏輯：(f1, f2) == (g1, g2) 或 (g2, g1)
    # 考慮負號提出嗎？ 暫不考慮，假設使用者寫標準形式。
    # e.g. (-2x-3) vs (2x+3) -> 通常因式分解首項係數為正
    
    # 簡單比對: set comparison
    # 注意 list of tuple 用 set 比較
    u_set = sorted(u_factors)
    c_set = sorted(c_factors)
    
    if u_set == c_set:
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}


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
                import re
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 ---
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '|', '[', '{', '\\']
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
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
