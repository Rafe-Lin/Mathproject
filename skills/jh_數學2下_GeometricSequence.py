# ==============================================================================
# ID: jh_數學2下_GeometricSequence
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 57.09s | RAG: 5 examples
# Created At: 2026-01-19 15:56:28
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
import base64

def generate(level=1):
    """
    生成等比數列相關題目
    """
    # 根據 MANDATORY MIRRORING RULES,嚴格映射 RAG 範例的數學模型
    # Type 1, 4, 5 均對應「判斷等比數列並寫出公比」的數學模型
    # Type 2 對應「已知首項和公比,求特定項」的數學模型
    # Type 3 對應「插入數使其成為等比數列」的數學模型
    problem_type_key = random.choice([1, 2, 3, 4, 5])

    question_text = ""
    correct_answer_raw = ""  # 純數據答案
    answer_display = ""      # 供前端顯示的格式化答案
    image_base64 = ""        # 無圖片，為空字串

    # 隨機生成基礎數據,確保不為 0,且公比不為 1 或 -1 (增加變化性)
    a1 = random.randint(1, 10) * random.choice([-1, 1])
    r_abs = random.randint(2, 5)
    r = r_abs * random.choice([-1, 1])
    n = random.randint(3, 7) # 項數,用於求特定項或數列長度

    # --- Type 1: (Maps to RAG Ex 1: 判斷等比數列,寫出公比) ---
    if problem_type_key == 1:
        is_geometric = random.choice([True, False])
        
        if is_geometric:
            # 生成等比數列
            r_geo = random.randint(2, 5) * random.choice([-1, 1]) # 確保公比不為 0, 1, -1
            term1 = a1
            term2 = a1 * r_geo
            term3 = a1 * r_geo * r_geo
            
            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = f"是,{r_geo}"
            answer_display = f"是，公比為 {r_geo}"
        else:
            # 生成非等比數列
            term1 = a1
            # 嘗試生成類等差數列或隨機數列,確保其非等比
            term2 = a1 + random.randint(1, 5) * random.choice([-1, 1])
            term3 = term2 + random.randint(1, 5) * random.choice([-1, 1])
            
            # 再次檢查確保非等比,避免極端情況
            # 避免除以零,並檢查比值是否相等
            if term1 != 0 and term2 != 0 and term3 != 0:
                if math.isclose(term2 / term1, term3 / term2, rel_tol=1e-9):
                    # 如果意外地等比了,調整第三項使其非等比
                    term3 += random.randint(1, 2) * random.choice([-1, 1])
                    if term3 == term2: # 避免調整後又變成一樣
                        term3 += 1
            elif term1 == 0: # 如果首項為0,則等比數列所有項都為0。確保非等比時不是全0
                if term2 == 0 and term3 == 0:
                    term3 = random.randint(1, 5) * random.choice([-1, 1])

            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = "否"
            answer_display = "否"

    # --- Type 2: (Maps to RAG Ex 2: 已知首項和公比,求特定項) ---
    elif problem_type_key == 2:
        # 題目: 等比數列的首項為 A,公比為 R,求此數列的第 N 項
        # 公式: a_n = a_1 * r^(n-1)
        an = a1 * (r**(n-1))
        
        question_text_template = r"一個等比數列的首項為 ${a_1}$，公比為 ${r}$，則此數列的第 ${n}$ 項為何？"
        question_text = question_text_template.replace("{a_1}", str(a1)).replace("{r}", str(r)).replace("{n}", str(n))
        
        correct_answer_raw = str(an)
        answer_display = str(an)

    # --- Type 3: (Maps to RAG Ex 3: 插入數使其成為等比數列) ---
    elif problem_type_key == 3:
        # 題目: 在 A 與 B 之間插入 K 個數,使其成為一個等比數列,求插入的第一個數
        # 假設原始數列為 start_term, ..., end_term。插入 k 個數後,總項數為 k+2
        # end_term = start_term * r^(k+1)
        
        # 為了使數字不至於過大,公比 r 範圍可以小一點
        r_insert = random.randint(2, 4) * random.choice([-1, 1])
        k = random.randint(1, 3) # 插入 1 到 3 個數
        
        start_term = random.randint(1, 10) * random.choice([-1, 1])
        end_term = start_term * (r_insert**(k+1))
        
        # 插入的第一個數為 start_term * r_insert
        first_inserted_term = start_term * r_insert
        
        question_text_template = r"在 ${start_term}$ 與 ${end_term}$ 之間插入 ${k}$ 個數，使其成為一個等比數列，則插入的第一個數為何？"
        question_text = question_text_template.replace("{start_term}", str(start_term)).replace("{end_term}", str(end_term)).replace("{k}", str(k))

        correct_answer_raw = str(first_inserted_term)
        answer_display = str(first_inserted_term)

    # --- Type 4: (Maps to RAG Ex 4: 判斷等比數列,寫出公比) - 與 Type 1 數學模型相同 ---
    elif problem_type_key == 4:
        is_geometric = random.choice([True, False])
        
        if is_geometric:
            r_geo = random.randint(2, 5) * random.choice([-1, 1])
            term1 = a1
            term2 = a1 * r_geo
            term3 = a1 * r_geo * r_geo
            
            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = f"是,{r_geo}"
            answer_display = f"是，公比為 {r_geo}"
        else:
            term1 = a1
            term2 = a1 + random.randint(1, 5) * random.choice([-1, 1])
            term3 = term2 + random.randint(1, 5) * random.choice([-1, 1])
            if term1 != 0 and term2 != 0 and term3 != 0:
                if math.isclose(term2 / term1, term3 / term2, rel_tol=1e-9):
                    term3 += random.randint(1, 2) * random.choice([-1, 1])
                    if term3 == term2: term3 += 1
            elif term1 == 0:
                if term2 == 0 and term3 == 0:
                    term3 = random.randint(1, 5) * random.choice([-1, 1])
            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = "否"
            answer_display = "否"

    # --- Type 5: (Maps to RAG Ex 5: 判斷等比數列,寫出公比) - 與 Type 1 數學模型相同 ---
    elif problem_type_key == 5:
        is_geometric = random.choice([True, False])
        
        if is_geometric:
            r_geo = random.randint(2, 5) * random.choice([-1, 1])
            term1 = a1
            term2 = a1 * r_geo
            term3 = a1 * r_geo * r_geo
            
            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = f"是,{r_geo}"
            answer_display = f"是，公比為 {r_geo}"
        else:
            term1 = a1
            term2 = a1 + random.randint(1, 5) * random.choice([-1, 1])
            term3 = term2 + random.randint(1, 5) * random.choice([-1, 1])
            if term1 != 0 and term2 != 0 and term3 != 0:
                if math.isclose(term2 / term1, term3 / term2, rel_tol=1e-9):
                    term3 += random.randint(1, 2) * random.choice([-1, 1])
                    if term3 == term2: term3 += 1
            elif term1 == 0:
                if term2 == 0 and term3 == 0:
                    term3 = random.randint(1, 5) * random.choice([-1, 1])
            question_text_template = r"判斷數列 ${t1}, {t2}, {t3}$ 是否為等比數列？若是，其公比為何？（請回答：是/否, 公比）"
            question_text = question_text_template.replace("{t1}", str(term1)).replace("{t2}", str(term2)).replace("{t3}", str(term3))
            
            correct_answer_raw = "否"
            answer_display = "否"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_raw,
        "answer": answer_display,
        "image_base64": image_base64,
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
