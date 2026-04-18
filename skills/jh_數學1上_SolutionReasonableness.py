# ==============================================================================
# ID: jh_數學1上_SolutionReasonableness
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 88.44s | RAG: 2 examples
# Created At: 2026-01-14 21:58:09
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


import random
import math
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from fractions import Fraction
from functools import reduce
import ast

# [V10.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. Formatting Helpers (V10.6 No-F-String LaTeX) ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX using .replace() to avoid f-string conflicts.
    """
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
    """
    Format number for LaTeX (Safe Mode).
    """
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

# Alias
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def is_prime(n):
    """Check primality (Standard Boolean Return)."""
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
# --- 3. Fraction Generator ---
def simplify_fraction(n, d):
    """[V11.3 Standard Helper] 強力化簡分數並回傳 (分子, 分母)"""
    common = math.gcd(n, d)
    return n // common, d // common


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
    
def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result

# --- 4. Answer Checker (V10.6 Hardcoded Golden Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    # [V11.0] 暴力清理 LaTeX 冗餘符號 ($, \) 與空格
    u = str(user_answer).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "")
    
    # 強制還原字典格式 (針對商餘題)
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try: import ast; c_raw = ast.literal_eval(c_raw)
        except: pass

    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q, r = str(c_raw.get("quotient", "")), str(c_raw.get("remainder", ""))
        ans_display = r"{q},{r}".replace("{q}", q).replace("{r}", r)
        try:
            u_parts = u.replace("商", "").replace("餘", ",").split(",")
            if int(u_parts[0]) == int(q) and int(u_parts[1]) == int(r):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(c_raw).strip()

    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        import math
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    # [V11.1] 科學記號自動比對 (1.23*10^4 vs 1.23e4)
    # 支援 *10^, x10^, e 格式
    if "*" in str(ans_display) or "^" in str(ans_display) or "e" in str(ans_display):
        try:
            # 正規化：將常見乘號與次方符號轉為 E-notation
            norm_ans = str(ans_display).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            norm_user = str(u).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            if math.isclose(float(norm_ans), float(norm_user), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
        except: pass

    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}


import datetime
import base64
import io
# --- CRITICAL CHANGE: Use Figure for thread-safety ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import matplotlib # Import matplotlib to access rcParams

# --- GLOBAL FONT SETTING (V10.2 Visual Style) ---
# Set font for Traditional Chinese (Taiwan) characters.
# This must be done using matplotlib.rcParams as `matplotlib.pyplot` is forbidden.
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'sans-serif'] # Add a fallback font
matplotlib.rcParams['axes.unicode_minus'] = False # To display minus sign correctly in plots

# --- 視覺化與輔助函式通用規範 (Generic Helper Rules) ---

def _generate_simple_bar_chart_base64(values, labels, title="數量比較", ylabel="數量"):
    """
    Generates a simple bar chart as a base64 encoded PNG image.
    This function strictly adheres to the '防洩漏原則' by only receiving '題目已知數據'.
    It does not receive or process '答案數據' to prevent direct answer leakage.
    Args:
        values (list): Numeric values for the bars.
        labels (list): Labels for each bar.
        title (str): Title of the chart.
        ylabel (str): Label for the y-axis.
    Returns:
        str: Base64 encoded PNG image string.
    """
    # CRITICAL CHANGE: Use Figure instead of plt.subplots for thread-safety
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    bars = ax.bar(labels, values, color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'lightgray', 'salmon'])

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=0)
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom', fontsize=9)

    # CRITICAL CHANGE: Use fig.tight_layout()
    fig.tight_layout()
    buf = io.BytesIO()
    # CRITICAL CHANGE: Use fig.savefig()
    fig.savefig(buf, format='png', bbox_inches='tight')
    # CRITICAL CHANGE: Explicitly delete the figure object to free memory, as plt.close(fig) is forbidden
    del fig 
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _generate_simple_number_line_base64(points_data, title="數字線示意圖", start=0, end=10):
    """
    Generates a simple number line with labeled points as a base64 encoded PNG image.
    Points are tuples (value, label). This function adheres to '防洩漏原則'.
    Args:
        points_data (list): A list of tuples, where each tuple is (value, label_string).
        title (str): Title of the number line.
        start (int): Starting value of the number line.
        end (int): Ending value of the number line.
    Returns:
        str: Base64 encoded PNG image string.
    """
    # CRITICAL CHANGE: Use Figure instead of plt.subplots for thread-safety
    fig = Figure(figsize=(8, 1))
    ax = fig.add_subplot(111)

    ax.set_xlim(start, end)
    ax.set_ylim(0, 1)
    ax.axhline(0.5, color='black', linewidth=1) # The line itself

    # CRITICAL CHANGE: Number line ONLY shows origin '0' with fontsize 18.
    ax.set_xticks([0]) # Only show 0 as a major tick
    ax.set_xticklabels(['0'], fontsize=18) # Label 0 with specified fontsize
    ax.tick_params(axis='y', left=False, labelleft=False) # Remove y-axis ticks and labels

    # Plot points
    for value, label in points_data:
        ax.plot(value, 0.5, 'o', color='red', markersize=8) # Point marker
        # CRITICAL CHANGE: Point labels (like '小麗', '媽媽') set to 16+.
        ax.text(value, 0.65, label, ha='center', va='bottom', fontsize=16, color='blue') # Updated fontsize

    ax.set_title(title, fontsize=12)
    # CRITICAL CHANGE: Use fig.tight_layout()
    fig.tight_layout()

    buf = io.BytesIO()
    # CRITICAL CHANGE: Use fig.savefig()
    fig.savefig(buf, format='png', bbox_inches='tight')
    # CRITICAL CHANGE: Explicitly delete the figure object to free memory, as plt.close(fig) is forbidden
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 程式結構 (Structure Hardening) ---
# [頂層函式]: 嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# [自動重載]: 確保代碼不依賴全域狀態。
def _generate_type_1_direct_calculation(level):
    """題型 1：水族館買魚情境 (對齊 RAG 例題：整數限制)"""
    tank_price = 110
    fish_price = 20
    # 隨機決定是否要產生不合理的情境
    is_reasonable = random.choice([True, False])
    if is_reasonable:
        fish_count = random.randint(5, 12)
        total_price = tank_price + fish_price * fish_count
    else:
        # 故意加上 5, 10, 15 元，導致算出 0.25, 0.5, 0.75 隻魚
        total_price = tank_price + fish_price * random.randint(5, 12) + random.choice([5, 10, 15])
    
    question_template = r"巴奈去水族館買孔雀魚：魚缸 {tp} 元/個，孔雀魚 {fp} 元/隻。巴奈買了 1 個魚缸與數隻孔雀魚，結帳時老闆收了 {total} 元。請問收費是否合理？(請填「合理」或「不合理」)"
    question_text = question_template.replace("{tp}", str(tank_price)).replace("{fp}", str(fish_price)).replace("{total}", str(total_price))
    
    # 邏輯判斷：總價扣除魚缸後，必須能被單價整除
    correct_ans = "合理" if (total_price - tank_price) % fish_price == 0 else "不合理"
    return question_text, correct_ans, correct_ans, ""

def _generate_type_2_unreasonable_scenario(level):
    """題型 2：游泳池門票情境 (對齊 RAG 例題：正整數解)"""
    full_price = 120
    discount_price = 80 # 120 - 40
    num_full = 4
    # 設定一個會算出 3.75 張票的不合理總價
    total_paid = 780 
    
    question_template = r"琦瑋一家去游泳，買了 {nf} 張全票與若干張優待票。全票一張 {fp} 元，比優待票貴 40 元。琦瑋計算後認為應付 {total} 元，請問此金額是否合理？(請填「合理」或「不合理」)"
    question_text = question_template.replace("{nf}", str(num_full)).replace("{fp}", str(full_price)).replace("{total}", str(total_paid))
    
    is_int = (total_paid - (num_full * full_price)) % discount_price == 0
    correct_ans = "合理" if is_int else "不合理"
    return question_text, correct_ans, correct_ans, ""

def _generate_type_3_choose_reasonable_answer(level):
    """題型 3：人數與比例限制 (解題後檢查實際情境)"""
    # 情境：男女生比例與總人數
    # 設女生 x 人，男生為 2/3x 人，總人數 = 5/3x
    total_students = random.choice([30, 31, 32, 33])
    
    question_template = r"某班級男生人數是女生人數的 $\frac{2}{3}$ 倍，若小明算得全班總人數為 {total} 人，請問這個結果是否合理？(請填「合理」或「不合理」)"
    question_text = question_template.replace("{total}", str(total_students))
    
    # 總人數必須是 (1 + 2/3) = 5/3 的倍數，即總人數必須能被 5 整除
    is_reasonable = (total_students % 5 == 0)
    correct_ans = "合理" if is_reasonable else "不合理"
    return question_text, correct_ans, correct_ans, ""
def generate(level=1):
    """
    Generates a math problem related to "Solution Reasonableness" based on the specified level.
    Ensures problem variety, LaTeX safety, and adheres to the standard output structure.

    Args:
        level (int): Difficulty level of the problem (e.g., 1 for K12 Math 1st grade).

    Returns:
        dict: A dictionary containing problem details, including question text, correct answer,
              display answer, image (base64), creation timestamp, and version.
    """
    problem_types = [
        _generate_type_1_direct_calculation,
        _generate_type_2_unreasonable_scenario,
        _generate_type_3_choose_reasonable_answer,
    ]
    
    # [隨機分流]: 根據該技能的教科書例題，實作至少 3 種不同的題型變體。
    chosen_problem_func = random.choice(problem_types)
    
    # Generate the problem using the selected function.
    # Each helper function returns (question_text, correct_answer, answer, image_base64).
    question_text, correct_answer, answer_display, image_b64 = chosen_problem_func(level)

    # [數據與欄位]: 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    # [時間戳記]: 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    result = {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_b64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "9.6.0" # Specified version
    }
    
    return result



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
                # 解決 r-string 導致的 \\n 問題
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\\n(請在手寫區作答!)"

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
