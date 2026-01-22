# ==============================================================================
# ID: jh_數學2上_FourOperationsOfRadicals
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 52.75s | RAG: 5 examples
# Created At: 2026-01-18 21:05:25
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
import base64 # Required by spec, though not used for image generation in this skill

# 頂層函式定義
def generate(level=1):
    """
    根據指定難度等級 (level) 生成一道關於根式四則運算的題目。
    Level 參數在此版本中暫未細分具體難度，所有題型均為基礎至中等難度。
    """
    problem_data = _select_and_generate_problem()
    
    # 鎖死欄位與時間戳記
    problem_data["created_at"] = datetime.now().isoformat()
    problem_data["version"] = "1.0"
    
    return problem_data

def check(user_answer, correct_answer_raw):
    """
    強韌閱卷邏輯 (Robust Check Logic)：
    比對使用者答案與正確答案。支援整數、小數、分數以及 a*sqrt(b) 形式。
    - correct_answer_raw 格式:
      - "整數" (e.g., "10")
      - "分數" (e.g., "1/2")
      - "a,b" (e.g., "2,3" 代表 2*sqrt(3))
      - "a/b,c" (e.g., "2/3,3" 代表 (2/3)*sqrt(3))
    
    遵照 [系統底層鐵律] check(u, c) 僅限回傳 True/False。
    """
    
    # 1. 清洗雙方輸入 (Input Sanitization)
    def clean_input(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, ans= 等前綴
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        s = s.replace("sqrt", "s").replace("根號", "s").replace("root", "s") # 標準化根號表示
        return s

    user_answer_sanitized = clean_input(user_answer)
    
    correct_parts = correct_answer_raw.split(',')
    
    # 2. 嘗試數值比對 (支援純有理數: 整數或分數/小數)
    if len(correct_parts) == 1:
        try:
            def parse_val(val_str):
                # 處理分數形式 "1/2"
                if "/" in val_str:
                    n, d = map(float, val_str.split("/"))
                    return n / d
                return float(val_str)
            
            correct_val = parse_val(correct_parts[0])
            user_val = parse_val(user_answer_sanitized)
            return math.isclose(user_val, correct_val, rel_tol=1e-9)
        except (ValueError, SyntaxError, TypeError):
            # 若無法解析為純數字，則繼續嘗試根式比對或返回 False
            pass
    
    # 3. 嘗試根式比對 (支援 a*sqrt(b) 或 (a/b)*sqrt(c) 形式)
    if len(correct_parts) == 2:
        correct_coeff_str = correct_parts[0]
        correct_radicand_str = correct_parts[1]
        
        try:
            correct_coeff = float(eval(correct_coeff_str))
            correct_radicand = int(correct_radicand_str)
        except (ValueError, SyntaxError, TypeError):
            return False # 正確答案格式錯誤 (應由 generate 確保)

        # 解析使用者輸入的 a*sqrt(b) 形式
        # 預期使用者輸入格式: "2s3", "2*s3", "2s(3)", "2/3s5", "-s7"
        match = re.match(r'^(-?\d+(/\d+)?)\*?s(\d+)$', user_answer_sanitized, re.IGNORECASE)
        
        # 處理使用者只輸入數字 (例如: "5", 對應正確答案 radicand == 1)
        if not match and correct_radicand == 1:
            try:
                user_val = float(eval(user_answer_sanitized))
                return math.isclose(user_val, correct_coeff, rel_tol=1e-9)
            except (ValueError, SyntaxError, TypeError):
                pass # 不是純數字，繼續嘗試其他解析方式
        
        # 處理使用者輸入只有根號 (例如: "s3" 對應 coeff == 1, "-s7" 對應 coeff == -1)
        if not match:
            match_sqrt_only = re.match(r'^(-?)\s*s(\d+)$', user_answer_sanitized, re.IGNORECASE)
            if match_sqrt_only:
                user_sign = -1 if match_sqrt_only.group(1) == '-' else 1
                user_radicand = int(match_sqrt_only.group(2))
                # 檢查係數是否為 1 或 -1，且根號內數字匹配
                if math.isclose(user_sign, correct_coeff, rel_tol=1e-9):
                    return user_radicand == correct_radicand
            
            return False # 無法解析為 a*sqrt(b) 形式

        # 如果匹配到 a*sqrt(b) 形式
        if match:
            user_coeff_str = match.group(1)
            user_radicand_str = match.group(3)
            
            try:
                user_coeff = float(eval(user_coeff_str))
                user_radicand = int(user_radicand_str)
            except (ValueError, SyntaxError, TypeError):
                return False

            # 比較簡化後的根式形式
            # generate 函式已確保 correct_answer 是最簡形式。
            # 閱卷時需將使用者輸入的 radicand 也簡化，再進行比對。
            user_simp_coeff, user_simp_radicand = _simplify_radical(user_radicand)
            user_final_coeff = user_coeff * user_simp_coeff

            # correct_answer_raw 已經是簡化後的 radicand
            # correct_simp_coeff, correct_simp_radicand = _simplify_radical(correct_radicand) # 不需再次簡化
            # correct_final_coeff = correct_coeff * correct_simp_coeff # 也不需再次乘上簡化係數

            return (math.isclose(user_final_coeff, correct_coeff, rel_tol=1e-9) and
                    user_simp_radicand == correct_radicand)
    
    return False # 無效的 correct_answer_raw 格式或無法匹配

# --- 輔助函式通用規範 ---
# 所有輔助函式最後一行必須明確使用 'return' 語句回傳結果。
# 若函式結果會用於拼接 question_text，回傳值必須強制轉為字串 (str)。
# 視覺化函式僅能接收「題目已知數據」，嚴禁將「答案數據」傳入繪圖函式。

def _simplify_radical(n):
    """
    將根號內的數字 n 簡化為 a*sqrt(b) 形式。
    回傳 (係數 a, 根號內數字 b)。
    例如: _simplify_radical(12) 應回傳 (2, 3) 代表 2*sqrt(3)。
    """
    if not isinstance(n, (int, float)) or n < 0:
        if n == 0: return (0, 0)
        raise ValueError("根號內數字必須是非負整數或浮點數。")
    if n == 0:
        return (0, 0)
    
    coeff = 1
    radicand = int(n) # 確保處理為整數
    
    # 從 2 開始尋找平方因子
    for i in range(2, int(math.sqrt(radicand)) + 1):
        while radicand % (i * i) == 0:
            coeff *= i
            radicand //= (i * i)
    return (coeff, radicand)

def _get_random_prime_radicand(min_val=2, max_val=15):
    """
    生成一個隨機的質數，作為最簡根式中的根號內數字。
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29] # 常用質數
    valid_primes = [p for p in primes if min_val <= p <= max_val]
    if not valid_primes: 
        # 如果範圍內沒有質數，則退而求其次選擇隨機數，但確保不是1
        return random.randint(max(2, min_val), max_val)
    return random.choice(valid_primes)

def _generate_simplifiable_number(base_radicand, max_val=100):
    """
    生成一個數字 N，使其可簡化為 `perfect_square * base_radicand` 的形式。
    確保 N 在合理範圍內。
    """
    perfect_squares = [4, 9, 16, 25, 36, 49, 64, 81]
    
    # 過濾出不會使 num 超過 max_val 的 perfect_squares
    possible_ps = [ps for ps in perfect_squares if ps * base_radicand <= max_val]
    
    if not possible_ps: # 如果沒有合適的平方數，則直接使用 base_radicand 或其小倍數
        return base_radicand * random.randint(1, 3) # 至少乘以1
    
    ps = random.choice(possible_ps)
    num = ps * base_radicand
    
    # 確保生成的數字不等於 base_radicand，使其確實可簡化
    if num == base_radicand and len(possible_ps) > 1:
        possible_ps.remove(ps) # 移除當前選擇，再選一次
        if possible_ps:
            ps = random.choice(possible_ps)
            num = ps * base_radicand
    
    # 如果簡化後還是等於 base_radicand (例如 base_radicand=5, ps=1, num=5)，
    # 則確保至少在視覺上是不同的數字，除非沒有其他選擇
    if num == base_radicand and base_radicand * 4 <= max_val: # 確保有可簡化的空間
        num = base_radicand * random.choice([4, 9]) # 至少乘以一個平方數
        if num > max_val: # 如果超出了，則退回 base_radicand
            num = base_radicand
    elif num == base_radicand: # 如果沒有簡化空間，就直接用 base_radicand
        pass

    return num

def _fmt_radical_term(coeff, radicand):
    """
    Format a radical term a*sqrt(b) for use INSIDE a LaTeX math block.
    Does NOT include surrounding $...$.
    Handles coefficient 1 suppression.
    """
    if radicand == 0: return "0"
    if radicand == 1: return str(coeff)
    
    parts = []
    if coeff == 1:
        pass # Omit 1
    elif coeff == -1:
        parts.append("-") # Omit 1, keep minus
    else:
        parts.append(str(coeff))
    
    parts.append(r"\sqrt{{{r}}}".replace("{r}", str(radicand)))
    return "".join(parts)


def _format_radical_answer(coeff, radicand):
    """
    將根式答案格式化為顯示用的 LaTeX 字串和純數據字串。
    純數據字串遵循 "a,b" (代表 a*sqrt(b)) 或 "a" (代表純數字) 格式。
    """
    if radicand == 0:
        return "0", "0"
    if radicand == 1:
        return str(coeff), str(coeff) # 例如 5*sqrt(1) = 5
    
    if coeff == 1:
        display_str = r"$\sqrt{{{r}}}$".replace("{r}", str(radicand))
        pure_data_str = f"1,{radicand}"
    elif coeff == -1:
        display_str = r"$-\sqrt{{{r}}}$".replace("{r}", str(radicand))
        pure_data_str = f"-1,{radicand}"
    else:
        display_str = r"${c}\sqrt{{{r}}}$".replace("{c}", str(coeff)).replace("{r}", str(radicand))
        pure_data_str = f"{coeff},{radicand}"
    return display_str, pure_data_str

def _format_fraction_radical_answer(num_coeff, den_coeff, radicand):
    """
    將分數形式的根式答案 (例如 (2/3)*sqrt(3)) 格式化為顯示用的 LaTeX 字串和純數據字串。
    純數據字串遵循 "a/b,c" (代表 (a/b)*sqrt(c)) 或 "a" (代表純數字) 格式。
    """
    if radicand == 0:
        return "0", "0"
    if num_coeff == 0:
        return "0", "0"

    # 先簡化分數部分
    gcd_val = math.gcd(abs(num_coeff), abs(den_coeff))
    num_coeff //= gcd_val
    den_coeff //= gcd_val
    
    # 處理符號：將負號統一放在分子
    if den_coeff < 0:
        num_coeff *= -1
        den_coeff *= -1

    if radicand == 1: # 如果根號內是 1，則為純分數或整數
        if den_coeff == 1:
            return str(num_coeff), str(num_coeff)
        else:
            display_str = r"$\frac{{{n}}}{{{d}}}$".replace("{n}", str(num_coeff)).replace("{d}", str(den_coeff))
            pure_data_str = f"{num_coeff}/{den_coeff}"
            return display_str, pure_data_str

    if den_coeff == 1: # 如果分數分母是 1，則為整數係數根式
        return _format_radical_answer(num_coeff, radicand)
    
    # 正常分數係數根式
    display_str = r"$\frac{{{nc}}\sqrt{{{r}}}}{{{dc}}}$".replace("{nc}", str(num_coeff)).replace("{r}", str(radicand)).replace("{dc}", str(den_coeff))
    pure_data_str = f"{num_coeff}/{den_coeff},{radicand}"
    return display_str, pure_data_str


# --- 題型生成函式 ---
# 嚴格遵循 [禁絕原創] 原則，所有題型皆映射至 RAG 中常見的例題模式。
# 數據禁絕常數 (Hardcode)，所有數值皆隨機生成並反向計算答案。

def _generate_type1_simplification_add_sub():
    """
    Type 1 (映射 RAG Ex 1, 2, 3): 根式化簡與加減 (Simplification and Addition/Subtraction of Radicals)
    描述: 題目包含兩個或多個根式，需要先化簡再進行加減運算。確保化簡後能合併成同類方根。
    """
    op = random.choice(['+', '-'])
    
    base_radicand = _get_random_prime_radicand(2, 7) # 例如 2, 3, 5, 7
    
    c1 = random.randint(1, 5)
    c2 = random.randint(1, 5)
    
    n1 = _generate_simplifiable_number(base_radicand, max_val=75)
    n2 = _generate_simplifiable_number(base_radicand, max_val=75)

    # 確保 n1 和 n2 至少有一個是可簡化的，且簡化後能與 base_radicand 匹配
    # 如果 n1 和 n2 相同，則重新生成 n2，避免題目過於單調
    attempts = 0
    while n1 == n2 and attempts < 5: 
        n2 = _generate_simplifiable_number(base_radicand, max_val=75)
        attempts += 1
    
    # 計算簡化後的係數和根號內數字
    s_c1, s_r1 = _simplify_radical(n1)
    s_c2, s_r2 = _simplify_radical(n2)

    # 題目顯示為未簡化形式
    term1 = _fmt_radical_term(c1, n1)
    term2 = _fmt_radical_term(c2, n2)
    
    question_text = r"計算並化簡： ${t1} {op} {t2}$".replace("{t1}", term1).replace("{op}", op).replace("{t2}", term2)

    # 計算結果
    if op == '+':
        result_coeff = c1 * s_c1 + c2 * s_c2
    else: # '-'
        result_coeff = c1 * s_c1 - c2 * s_c2
    
    # 最終答案的根號內數字應為 base_radicand (因為是同類方根合併)
    answer_display, correct_answer = _format_radical_answer(result_coeff, base_radicand)
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": None,
    }

def _generate_type2_multiplication():
    """
    Type 2 (映射 RAG Ex 4 隱含的乘法公式應用): 根式乘法 (Multiplication of Radicals)
    描述: 題目包含兩個根式的乘法，可能是單項乘單項，或單項乘多項，確保最終答案為有理數或單一簡化根式。
    """
    sub_type = random.choice(['simple', 'binomial_rational']) # 確保答案為有理數或單一簡化根式

    if sub_type == 'simple': # 單項乘單項: c1*sqrt(r1) * c2*sqrt(r2)
        c1 = random.randint(1, 5)
        c2 = random.randint(1, 5)
        
        # 生成兩個根號內數字，使其乘積可簡化為單一根式
        base_r = _get_random_prime_radicand(2, 10)
        
        # r1 和 r2 至少一個是 base_r 的倍數，或兩者相乘後能簡化
        choice = random.choice([1, 2, 3])
        if choice == 1: # r1 和 r2 都與 base_r 相關，但可簡化
            r1 = _generate_simplifiable_number(base_r, max_val=50)
            r2 = base_r
        elif choice == 2: # 讓乘積包含平方因子
            r1 = random.choice([2, 3, 5, 7])
            r2 = random.choice([2, 3, 5, 7])
            if r1 != r2 and r1 * r2 <= 50 and random.random() < 0.6: # 引入平方因子讓它能簡化
                r1 *= random.choice([4, 9])
            if r1 * r2 > 75: # 防止數字過大
                r1 = random.choice([2,3])
                r2 = random.choice([2,3])
        else: # 簡單乘法，結果可能需要簡化
            r1 = random.randint(2, 10)
            r2 = random.randint(2, 10)
            if r1*r2 > 100:
                r1, r2 = random.randint(2,5), random.randint(2,5)

        term1 = _fmt_radical_term(c1, r1)
        term2 = _fmt_radical_term(c2, r2)
        
        question_text = r"計算並化簡： ${t1} \times {t2}$".replace("{t1}", term1).replace("{t2}", term2)
        
        product_coeff = c1 * c2
        product_radicand = r1 * r2
        
        final_coeff_simp, final_radicand_simp = _simplify_radical(product_radicand)
        final_coeff = product_coeff * final_coeff_simp
        
        answer_display, correct_answer = _format_radical_answer(final_coeff, final_radicand_simp)

    else: # binomial_rational: (A+sqrt(B))(A-sqrt(B)) = A^2-B (結果為有理數)
        a = random.randint(2, 7)
        b = _get_random_prime_radicand(2, 10)
        # 確保 a^2 - b > 0，避免結果為負數或 0 (根號內)
        while a*a <= b:
            a = random.randint(2, 7)
            b = _get_random_prime_radicand(2, 10)
        
        question_text = r"計算並化簡： $({a}+\sqrt{{{b}}})({a}-\sqrt{{{b}}})$".replace("{a}", str(a)).replace("{b}", str(b))
        correct_answer = str(a*a - b)
        answer_display = correct_answer
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": None,
    }

def _generate_type3_rationalization():
    """
    Type 3 (映射 RAG Ex 4 part 3, Ex 5 part 2): 分母有理化 (Rationalizing the Denominator)
    描述: 題目要求對分母進行有理化。本類型嚴格限制為最終答案為有理數或單一簡化根式。
    """
    sub_type = random.choice(['single_term', 'conjugate_rational_result'])

    if sub_type == 'single_term': # 單項分母有理化: N/sqrt(R)
        numerator = random.randint(2, 20)
        radicand = _get_random_prime_radicand(2, 10)
        
        question_text = r"計算並化簡： $\frac{{{n}}}{\sqrt{{{r}}}}$".replace("{n}", str(numerator)).replace("{r}", str(radicand))
        
        # 計算結果: (numerator * sqrt(radicand)) / radicand
        # 簡化分數部分
        final_num_coeff = numerator
        final_den_coeff = radicand

        answer_display, correct_answer = _format_fraction_radical_answer(final_num_coeff, final_den_coeff, radicand)

    else: # conjugate_rational_result: 分母共軛化，確保最終結果為有理數
        # 使用特殊形式: $\frac{A+\sqrt{B}}{A-\sqrt{B}} + \frac{A-\sqrt{B}}{A+\sqrt{B}}$
        # 其結果為 $\frac{2A^2+2B}{A^2-B}$ (純有理數)
        a = random.randint(2, 7)
        b_base = _get_random_prime_radicand(2, 10)
        
        # 確保 a*a != b_base，避免分母為零
        while a*a == b_base:
            a = random.randint(2, 7)
        
        question_text = r"計算並化簡： $\frac{{{a}}+\sqrt{{{b}}}}{{{a}}-\sqrt{{{b}}}} + \frac{{{a}}-\sqrt{{{b}}}}{{{a}}+\sqrt{{{b}}}}$".replace("{a}", str(a)).replace("{b}", str(b_base))
        
        numerator_ans = 2 * (a*a + b_base)
        denominator_ans = a*a - b_base
        
        # 簡化分數
        gcd_val = math.gcd(abs(numerator_ans), abs(denominator_ans))
        final_num = numerator_ans // gcd_val
        final_den = denominator_ans // gcd_val
        
        # 處理負號
        if final_den < 0:
            final_num *= -1
            final_den *= -1

        if final_den == 1:
            correct_answer = str(final_num)
            answer_display = correct_answer
        else:
            correct_answer = f"{final_num}/{final_den}"
            answer_display = r"$\frac{{{n}}}{{{d}}}$".replace("{n}", str(final_num)).replace("{d}", str(final_den))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": None,
    }

def _generate_type4_mixed_operations():
    """
    Type 4 (映射 RAG Ex 4, 5 的綜合運算): 綜合運算 (Mixed Operations)
    描述: 結合根式的加減乘除，可能包含乘法公式的應用。嚴格限制為最終答案為有理數或單一簡化根式。
    """
    sub_type = random.choice(['binomial_square_rational', 'combined_add_sub_rationalized'])

    if sub_type == 'binomial_square_rational': # (A*sqrt(R1) +- B*sqrt(R2))^2 簡化為有理數
        op = random.choice(['+', '-'])
        c1 = random.randint(1, 3)
        c2 = random.randint(1, 3)
        
        # 確保 r2 是 r1 的倍數，且倍數為平方數，以便簡化後可合併
        r1_base = _get_random_prime_radicand(2, 7)
        ps = random.choice([4, 9, 16]) # 平方數因子
        r2_val = ps * r1_base
        
        
        t1 = _fmt_radical_term(c1, r1_base)
        t2 = _fmt_radical_term(c2, r2_val)
        
        question_text = r"計算並化簡： $({t1} {op} {t2})^2$".replace("{t1}", t1).replace("{op}", op).replace("{t2}", t2)
        
        # 先計算括號內: c1*sqrt(r1_base) op c2*sqrt(ps*r1_base)
        # = c1*sqrt(r1_base) op c2*sqrt(ps)*sqrt(r1_base)
        # = (c1 op c2*sqrt(ps)) * sqrt(r1_base)
        
        inner_coeff = c1
        if op == '+':
            inner_coeff += c2 * int(math.sqrt(ps))
        else: # '-'
            inner_coeff -= c2 * int(math.sqrt(ps))
            
        # 再平方: (inner_coeff * sqrt(r1_base))^2 = inner_coeff^2 * r1_base
        final_answer = inner_coeff * inner_coeff * r1_base
        
        correct_answer = str(final_answer)
        answer_display = correct_answer

    else: # combined_add_sub_rationalized: $\frac{N_1}{\sqrt{R_1}} \pm \frac{N_2}{\sqrt{R_2}}$ 簡化為單一根式或有理數
        op = random.choice(['+', '-'])
        
        # 確保兩個項都能簡化為同類方根
        base_radicand_common = _get_random_prime_radicand(2, 7)
        
        # 第一項: $\frac{N_1}{\sqrt{R_1}}$
        n1_val = random.randint(2, 10)
        r1_val = base_radicand_common
        
        # 第二項: $\frac{N_2}{\sqrt{R_2}}$
        n2_val = random.randint(2, 10)
        r2_val = base_radicand_common # 確保與第一項為同類方根
        
        expr1_str = r"\frac{{{n1}}}{{\sqrt{{{r1}}}}}".replace("{n1}", str(n1_val)).replace("{r1}", str(r1_val))
        expr2_str = r"\frac{{{n2}}}{{\sqrt{{{r2}}}}}".replace("{n2}", str(n2_val)).replace("{r2}", str(r2_val))
        
        question_text = r"計算並化簡： ${e1} {op} {e2}$".replace("{e1}", expr1_str).replace("{op}", op).replace("{e2}", expr2_str)
        
        # 計算第一項簡化結果: (n1 / r1_val) * sqrt(r1_val)
        term1_num_coeff = n1_val
        term1_den_coeff = r1_val
        
        # 計算第二項簡化結果: (n2 / r2_val) * sqrt(r2_val)
        term2_num_coeff = n2_val
        term2_den_coeff = r2_val
        
        # 合併係數: ((AD op BC) / BD) * sqrt(R)
        final_num_combined_coeff = term1_num_coeff * term2_den_coeff
        if op == '+':
            final_num_combined_coeff += term2_num_coeff * term1_den_coeff
        else: # '-'
            final_num_combined_coeff -= term2_num_coeff * term1_den_coeff
        
        final_den_combined_coeff = term1_den_coeff * term2_den_coeff
        
        # 簡化分數係數
        answer_display, correct_answer = _format_fraction_radical_answer(final_num_combined_coeff, final_den_combined_coeff, base_radicand_common)
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": None,
    }


def _select_and_generate_problem():
    """
    內部函式，用於隨機選擇一個題型並生成題目。
    [隨機分流]：使用 random.choice 明確對應到 RAG 中的例題。
    """
    problem_types = [
        _generate_type1_simplification_add_sub,
        _generate_type2_multiplication,
        _generate_type3_rationalization,
        _generate_type4_mixed_operations,
    ]
    
    selected_type_generator = random.choice(problem_types)
    return selected_type_generator()


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
