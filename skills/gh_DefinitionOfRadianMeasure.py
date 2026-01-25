# ==============================================================================
# ID: gh_DefinitionOfRadianMeasure
# Model: gemini-2.5-flash | Strategy: V18.10 Single Dollar Fix
# Fix Status: [Repaired]
# Fixes: Format($$->$)=Fixed, Scope(import)=Fixed
#==============================================================================

import random
import math
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
from datetime import datetime
from fractions import Fraction

# [V11.6 Elite Font & Style]
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

def simplify_fraction_pi(numerator, denominator):
    """
    將分數化簡並附加 \pi 字串。例如 (2, 4) -> "\frac{\pi}{2}"
    """
    common = math.gcd(numerator, denominator)
    num = numerator // common
    den = denominator // common
    
    if den == 1:
        if num == 1: return r"\pi"
        if num == -1: return r"-\pi"
        return fr"{num}\pi"
    
    if num == 1: return fr"\frac{{\pi}}{{{den}}}"
    if num == -1: return fr"-\frac{{\pi}}{{{den}}}"
    return fr"\frac{{{num}\pi}}{{{den}}}"

# --- 繪圖函式：繪製扇形 ---
def draw_sector(radius, angle_deg, label_r="r", label_theta=r"\theta", highlight_arc=False):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 限制繪圖範圍
    limit = radius * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # 圓心
    center = (0, 0)
    
    # 繪製半徑線 (0度 與 angle_deg)
    import numpy as np
    theta_rad = math.radians(angle_deg)
    
    # P1 (on x-axis)
    p1_x, p1_y = radius, 0
    # P2 (rotated)
    p2_x, p2_y = radius * math.cos(theta_rad), radius * math.sin(theta_rad)
    
    ax.plot([0, p1_x], [0, p1_y], 'k-', lw=2)
    ax.plot([0, p2_x], [0, p2_y], 'k-', lw=2)
    
    # 繪製弧線
    from matplotlib.patches import Arc
    arc = Arc(center, radius*2, radius*2, angle=0, theta1=0, theta2=angle_deg, color='blue', lw=2)
    ax.add_patch(arc)
    
    # 標示半徑 r
    mid_r_x, mid_r_y = radius/2 * math.cos(theta_rad/2), radius/2 * math.sin(theta_rad/2)
    offset_x, offset_y = mid_r_x * 0.2, mid_r_y * 0.2
    ax.text(radius/2, -radius*0.1, f"${label_r}$", ha='center', fontsize=12)
    
    # 標示角度 theta
    arc_label_r = radius * 0.3
    label_x = arc_label_r * math.cos(theta_rad/2)
    label_y = arc_label_r * math.sin(theta_rad/2)
    ax.text(label_x, label_y, f"${label_theta}$", ha='center', va='center', fontsize=12, color='red')

    if highlight_arc:
        arc_mid_x = radius * 1.1 * math.cos(theta_rad/2)
        arc_mid_y = radius * 1.1 * math.sin(theta_rad/2)
        ax.text(arc_mid_x, arc_mid_y, "S?", ha='center', va='center', fontsize=12, color='blue')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4])
    
    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    if problem_type == 1:
        # Type 1: 度數 -> 弧度
        special_angles = [30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
        deg = random.choice(special_angles)
        rad_latex = simplify_fraction_pi(deg, 180)
        
        question_text = f"試將角度 ${deg}^\circ$ 化為弧度。"
        correct_answer = rad_latex

    elif problem_type == 2:
        # Type 2: 弧度 -> 度數
        denominators = [2, 3, 4, 6]
        d = random.choice(denominators)
        n = random.choice([x for x in range(1, 2*d) if math.gcd(x, d) == 1])
        
        rad_latex = simplify_fraction_pi(n, d)
        deg_val = int(n * 180 / d)
        
        question_text = f"試將弧度 ${rad_latex}$ 化為度數 (以度為單位)。"
        correct_answer = str(deg_val)

    elif problem_type == 3:
        # Type 3: 扇形弧長
        r = random.randint(2, 10)
        denominators = [3, 4, 6]
        d = random.choice(denominators)
        n = random.choice([1, 2, 3, 4, 5])
        if n >= d * 2: n = 1
        
        theta_latex = simplify_fraction_pi(n, d)
        theta_val = n * math.pi / d
        
        num_s = r * n
        den_s = d
        s_latex = simplify_fraction_pi(num_s, den_s)
        
        question_text = f"已知一扇形的半徑為 ${r}$，圓心角為 ${theta_latex}$ 弧度，求此扇形的弧長。"
        correct_answer = s_latex
        image_base64 = draw_sector(r, int(theta_val * 180 / math.pi), label_r=str(r), label_theta=theta_latex, highlight_arc=True)

    elif problem_type == 4:
        # Type 4: 扇形面積
        r = random.randint(2, 8)
        denominators = [3, 4, 6]
        d = random.choice(denominators)
        n = random.choice([1, 2, 3, 4, 5])
        if n >= d * 2: n = 1
        
        theta_latex = simplify_fraction_pi(n, d)
        theta_val = n * math.pi / d
        
        num_a = r * r * n
        den_a = 2 * d
        a_latex = simplify_fraction_pi(num_a, den_a)
        
        question_text = f"已知一扇形的半徑為 ${r}$，圓心角為 ${theta_latex}$ 弧度，求此扇形的面積。"
        correct_answer = a_latex
        image_base64 = draw_sector(r, int(theta_val * 180 / math.pi), label_r=str(r), label_theta=theta_latex)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def check(user_answer, correct_answer):
    import math, re
    from fractions import Fraction

    if user_answer is None: return {"correct": False, "result": "未提供答案。"}

    def clean(s):
        s = str(s).strip().lower()
        s = s.replace(" ", "").replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
        s = s.replace("cdot", "*").replace("times", "*")
        s = s.replace("circ", "").replace("°", "")
        s = s.replace("pi", "p").replace("π", "p")
        return s

    u = clean(user_answer)
    c = clean(correct_answer)

    def parse_pi_expression(s):
        try:
            if 'p' in s:
                val_part = s.replace('p', '')
                if val_part == "" or val_part == "-": 
                    coeff = 1.0 if val_part == "" else -1.0
                elif val_part == "/": 
                     return None
                elif "/" in val_part:
                    n, d = map(float, val_part.split('/'))
                    coeff = n / d
                else:
                    coeff = float(val_part)
                return coeff * math.pi
            else:
                if "/" in s:
                    n, d = map(float, s.split('/'))
                    return n / d
                return float(s)
        except:
            return None

    val_u = parse_pi_expression(u)
    val_c = parse_pi_expression(c)

    if val_u is not None and val_c is not None:
        if math.isclose(val_u, val_c, rel_tol=1e-3):
            return {"correct": True, "result": "正確！"}

    if u == c:
        return {"correct": True, "result": "正確！"}

    return {"correct": False, "result": f"答案錯誤。正確答案為：${correct_answer}$"}

# [Auto-Injected Patch v11.0]
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        if isinstance(res, dict):
            # [V18.10 Fix] Force remove double dollars
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("$$", "$").replace(r"\\n", "\n")
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
