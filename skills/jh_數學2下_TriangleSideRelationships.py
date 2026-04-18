# ==============================================================================
# ID: jh_數學2下_TriangleSideRelationships
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 66.55s | RAG: 4 examples
# Created At: 2026-01-23 14:46:59
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

    # 0. 選項集合比對 (Option Set Matching)
    import re
    if re.search(r'[A-C]', str(correct_answer)) or "無" in str(correct_answer):
        # 提取使用者與正確答案中的所有 A-C 字母 (忽略大小寫、順序)
        u_vals = re.findall(r'[a-cA-C]', str(user_answer))
        c_vals = re.findall(r'[a-cA-C]', str(correct_answer))
        u_set = {x.upper() for x in u_vals}
        c_set = {x.upper() for x in c_vals}
        
        # 處理 "無" 的情況
        if "無" in str(correct_answer) and ("無" in str(user_answer) or "none" in str(user_answer).lower()):
            return {"correct": True, "result": "正確！"}

        if u_set == c_set:
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": f"答案錯誤。正確選項為：{correct_answer}"}
    
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


import datetime

import re

# Helper Functions
def _generate_positive_integer_side(min_val, max_val):
    """Generates a positive integer side length within the specified range."""
    return random.randint(min_val, max_val)

def _is_triangle_valid(a, b, c):
    """
    Determines if three side lengths can form a valid triangle.
    Returns True if a valid triangle can be formed, False otherwise.
    """
    # Ensure all sides are positive
    if a <= 0 or b <= 0 or c <= 0:
        return False
    return (a + b > c) and (a + c > b) and (b + c > a)

def generate(level=1):
    """
    Generates a K12 math problem about triangle side relationships.
    """
    problem_type = random.choice([1, 2, 3])
    
    # Initialize variables to avoid potential UnboundLocalError
    side1, side2, side3 = 0, 0, 0 
    question_text = ""
    correct_answer = ""
    solution_text = ""
    
    min_side_val = 3
    max_side_val = 15

    if problem_type == 1:
        # Type 1: 多重選項判斷 (Which sets form a triangle?)
        labels = ['A', 'B', 'C']
        options_text = []
        valid_labels = []
        solution_lines = []
        
        for lbl in labels:
            # 隨機生成一組邊長 (保持整數)
            s1 = random.randint(3, 15)
            s2 = random.randint(3, 15)
            
            # 50% 機率生成合法，50% 非法
            if random.random() < 0.5: 
                # 合法: 第三邊在 (diff, sum) 之間
                min_s3, max_s3 = abs(s1-s2)+1, s1+s2-1
                if min_s3 <= max_s3:
                    s3 = random.randint(min_s3, max_s3)
                else: 
                    # 邊際情況：無法構成三角形 (如 3,3 -> 1~5, 必有解; 除非 s1+s2 太小?)
                    s3 = s1 + s2 # Fallback invalid
            else:
                # 非法: 第三邊太長或太短
                if random.random() < 0.5: # Too large or equal sum
                    s3 = random.randint(s1+s2, s1+s2+5)
                else: # Too small or equal diff
                    # 確保不為負
                    diff = abs(s1-s2)
                    s3 = random.randint(1, diff) if diff > 0 else 1
                    
            # 檢查是否構成三角形
            is_valid = _is_triangle_valid(s1, s2, s3)
            if is_valid:
                valid_labels.append(lbl)
                
            options_text.append(f"({lbl}) {s1}、{s2}、{s3}")
            
            # Solution logic check
            sides = sorted([s1, s2, s3])
            shortest_two_sum = sides[0] + sides[1]
            longest = sides[2]
            
            if is_valid:
                 solution_lines.append(f"({lbl}) {s1}、{s2}、{s3}：因為 {sides[0]} + {sides[1]} = {shortest_two_sum} > {longest}，所以能構成三角形。")
            else:
                 solution_lines.append(f"({lbl}) {s1}、{s2}、{s3}：因為 {sides[0]} + {sides[1]} = {shortest_two_sum} $\\le$ {longest}，所以不能構成三角形。")

        question_text = "下列各組的 3 個數分別代表三線段的長度，哪幾組數可以構成三角形？\n" + "\n".join(options_text)
        correct_answer = ", ".join(valid_labels) if valid_labels else "無"
        
        solution_text = (
            "根據三角形三邊關係：任意兩邊之和必大於第三邊 (或兩短邊之和 > 最長邊)。\n" + 
            "\n".join(solution_lines) + 
            f"\n\n正確答案為：{correct_answer}"
        )

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 給定兩邊長，求第三邊長的範圍。
        s1 = _generate_positive_integer_side(min_side_val, max_side_val)
        s2 = _generate_positive_integer_side(min_side_val, max_side_val)
        
        side1, side2 = s1, s2

        abs_diff = abs(side1 - side2)
        sum_sides = side1 + side2

        # For integer side x, the range is (abs_diff, sum_sides) exclusive.
        # So, x must be an integer such that abs_diff < x < sum_sides.
        min_x = abs_diff + 1
        max_x = sum_sides - 1

        # Ensure there's a valid range for integer sides, otherwise regenerate.
        # This handles cases like (3,3) where abs_diff=0, sum_sides=6, so min_x=1, max_x=5.
        # If (1,10), abs_diff=9, sum_sides=11, so min_x=10, max_x=10. This is a valid range (x=10).
        # But if min_x >= max_x, it means no valid integer side exists.
        while min_x >= max_x:
            s1 = _generate_positive_integer_side(min_side_val, max_side_val)
            s2 = _generate_positive_integer_side(min_side_val, max_side_val)
            side1, side2 = s1, s2
            abs_diff = abs(side1 - side2)
            sum_sides = side1 + side2
            min_x = abs_diff + 1
            max_x = sum_sides - 1


        correct_answer = f"{min_x},{max_x}" # Pure data format: "min_x,max_x"

        question_text_template = "已知有長 {s1} 公分、{s2} 公分的兩線段，若另有一長為 x 公分的線段，則此三線段可構成三角形，請列出 x 的範圍。"
        question_text = question_text_template.replace("{s1}", str(side1)).replace("{s2}", str(side2))
        solution_text = (
            "根據三角形三邊關係，第三邊長 x 必須滿足：\n"
            f"$|{side1} - {side2}| < x < {side1} + {side2}$\n"
            f"即 ${abs_diff} < x < {sum_sides}$\n"
            f"因此，x 的整數範圍是 ${min_x} \\leq x \\leq {max_x}$。\n"
            "答案應為範圍的最小值與最大值，用逗號分隔。"
        )

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): 給定兩邊長，求第三邊可能整數值的數量。
        s1 = _generate_positive_integer_side(min_side_val, max_side_val)
        s2 = _generate_positive_integer_side(min_side_val, max_side_val)

        side1, side2 = s1, s2
        
        abs_diff = abs(side1 - side2)
        sum_sides = side1 + s2

        min_x = abs_diff + 1
        max_x = sum_sides - 1
        
        # Ensure there's a valid range for integer sides, otherwise count would be 0 or negative.
        # Regenerate s1, s2 until a valid range exists.
        while min_x >= max_x:
            s1 = _generate_positive_integer_side(min_side_val, max_side_val)
            s2 = _generate_positive_integer_side(min_side_val, max_side_val)
            side1, side2 = s1, s2
            abs_diff = abs(side1 - side2)
            sum_sides = side1 + side2
            min_x = abs_diff + 1
            max_x = sum_sides - 1

        count = max_x - min_x + 1
        correct_answer = str(count) # Pure data format: "count"

        question_text_template = "若 {s1}、{s2} 是一個三角形的兩邊長，且第三邊的邊長是整數，列出符合條件的三角形數量。"
        question_text = question_text_template.replace("{s1}", str(side1)).replace("{s2}", str(side2))
        solution_text = (
            "根據三角形三邊關係，第三邊長 x 必須滿足：\n"
            f"$|{side1} - {side2}| < x < {side1} + {side2}$\n"
            f"即 ${abs_diff} < x < {sum_sides}$\n"
            f"因此，x 的整數值範圍是從 ${min_x}$ 到 ${max_x}$。\n"
            f"總共有 ${max_x} - {min_x} + 1 = {count}$ 種可能的整數邊長。"
        )

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": None,
        "version": "1.0",
        "created_at": datetime.datetime.now().isoformat(),
    }


    """
    Checks the user's answer against the correct answer.
    Supports Type 1 (Yes/No), Type 2 (Range), and Type 3 (Count).
    """
    import re, math

    def clean_input_string(s):
        """Cleans user input by removing LaTeX, variables, units, and spaces."""
        s = str(s).strip().lower()
        s = re.sub(r'^[a-z]+=', '', s)  # Remove k=, x=, y=, etc.
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
        s = s.replace("公分", "").replace("cm", "")
        s = re.sub(r'\s+', '', s) # Remove all whitespace
        return s

    # Determine problem type based on correct_answer format
    if correct_answer == "是" or correct_answer == "否":
        # Type 1: Yes/No question
        u_cleaned = clean_input_string(user_answer)
        # Further clean for keyword matching: keep only Chinese characters and English letters
        u_for_keywords = re.sub(r'[^a-z\u4e00-\u9fa5]', '', u_cleaned)

        yes_keywords = {"是", "對", "yes", "true", "可以", "能", "可以構成", "能構成", "成立"}
        no_keywords = {"否", "不", "no", "false", "不能", "無法", "不能構成", "無法構成", "不成立"}
        
        if u_for_keywords in yes_keywords and correct_answer == "是":
            return {"correct": True, "result": "正確！"}
        if u_for_keywords in no_keywords and correct_answer == "否":
            return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": f"答案錯誤。"}

    # For Type 2 and Type 3, correct_answer will be numeric string(s)
    # Extract numbers from user_answer
    u_raw_numbers = re.findall(r'-?\d+\.?\d*', clean_input_string(user_answer))
    u_numbers = [float(n) for n in u_raw_numbers if n.strip()]

    # Extract numbers from correct_answer (it's pure data, so just parse)
    c_raw_numbers = re.findall(r'-?\d+\.?\d*', correct_answer)
    c_numbers = [float(n) for n in c_raw_numbers if n.strip()]

    # Type 2: Range (e.g., "3,7") - expects two numbers in correct_answer
    if len(c_numbers) == 2:
        if len(u_numbers) == 2:
            u_sorted = sorted(u_numbers)
            c_sorted = sorted(c_numbers) # Ensure correct_answer numbers are also sorted for comparison
            
            if math.isclose(u_sorted[0], c_sorted[0], rel_tol=1e-5) and \
               math.isclose(u_sorted[1], c_sorted[1], rel_tol=1e-5):
                return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": f"答案錯誤。"}

    # Type 3: Count (e.g., "5") - expects one number in correct_answer
    elif len(c_numbers) == 1:
        if len(u_numbers) == 1:
            if math.isclose(u_numbers[0], c_numbers[0], rel_tol=1e-5):
                return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": f"答案錯誤。"}
    
    # Fallback for unexpected correct_answer format or if user_answer couldn't be parsed correctly for numeric types
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
