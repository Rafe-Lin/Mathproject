# ==============================================================================
# ID: jh_數學1上_ApplicationProblems_v2
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 30.80s | RAG: 1 examples
# Created At: 2026-01-14 20:55:25
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

# Helper Functions (輔助函式)
# -----------------------------------------------------------------------------
def _generate_random_int(min_val: int, max_val: int) -> int:
    """
    生成指定範圍內的隨機整數。
    Args:
        min_val (int): 最小值 (包含)。
        max_val (int): 最大值 (包含)。
    Returns:
        int: 生成的隨機整數。
    """
    return random.randint(min_val, max_val)

# Top-level Functions (頂層函式)
# -----------------------------------------------------------------------------
def generate(level: int = 1) -> dict:
    """
    根據指定的難度等級生成 K12 應用問題。
    嚴禁使用 class 封裝，所有邏輯直接定義在模組最外層。
    確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

    Args:
        level (int): 難度等級 (預設為 1)。

    Returns:
        dict: 包含問題文本、正確答案、顯示答案、圖片數據等信息的字典。
              字典結構強制包含且僅包含 'question_text', 'correct_answer',
              'answer', 'image_base64', 'created_at', 'version' 欄位。
    """
    problem_type_choices = [
        'type_1_direct_calc',
        'type_2_inverse_solve',
        'type_3_contextual_app'
    ]
    problem_type = random.choice(problem_type_choices)

    question_text = ""
    correct_answer = ""
    answer = ""
    image_base64 = None # 應用問題通常不需要複雜圖形，保持為 None

    # 題型多樣性 (Problem Variety) - 至少 3 種不同的題型變體
    # -------------------------------------------------------------------------

    if problem_type == 'type_1_direct_calc':
        # Type 1 (Maps to Example 1, 3): 直接計算 - 兩數之和與差
        # 描述：給定兩個數的和與差，求其中一個數。
        # 目標：測試學生建立線性方程組並求解的能力 (雖然在 K12 1上常規為單一未知數)。
        
        diff = _generate_random_int(5, 15)  # 兩數的差
        
        # 設甲數為 A, 乙數為 B。
        # A + B = total
        # A - B = diff  (假設 A > B)
        # (A + B) - (A - B) = total - diff => 2B = total - diff => B = (total - diff) / 2
        # 為確保乙數 (B) 為正整數，(total - diff) 必須是正偶數。
        
        # 最小的 total 應使 B 至少為 1。
        # 當 B=1 時，total - diff = 2 => total = diff + 2。
        min_total_for_b_positive = diff + 2
        total = _generate_random_int(min_total_for_b_positive, min_total_for_b_positive + 40)
        
        # 調整 total 確保 (total - diff) 為偶數
        if (total - diff) % 2 != 0:
            total += 1 # 如果是奇數，加 1 後會變成偶數
        
        correct_ans_val = (total - diff) // 2 # 乙數
        
        question_text_template = r"甲數與乙數之和為 {total}，且甲數比乙數大 {diff}。請問乙數為何？"
        question_text = question_text_template.replace("{total}", str(total)).replace("{diff}", str(diff))
        
        correct_answer = str(correct_ans_val)
        answer = correct_answer # 顯示答案與正確答案相同

    elif problem_type == 'type_2_inverse_solve':
        # Type 2 (Maps to Example 2, 4): 逆向求解 - 財產變化問題
        # 描述：給定一系列支出和收入後的最終金額，要求學生計算最初的金額。
        # 目標：測試學生逆向思考及建立和解單一未知數線性方程的能力。

        # 確保各階段金額為正數，符合 K12 應用題情境
        initial_money_min = 200
        initial_money_max = 800
        spent1_min = 50
        spent1_max = 150
        earned_min = 30
        earned_max = 100
        spent2_min = 20
        spent2_max = 80

        while True:
            initial_money = _generate_random_int(initial_money_min, initial_money_max)
            spent1 = _generate_random_int(spent1_min, spent1_max)
            earned = _generate_random_int(earned_min, earned_max)
            spent2 = _generate_random_int(spent2_min, spent2_max)

            # 確保中間金額不會為負
            if initial_money - spent1 <= 0:
                continue
            if (initial_money - spent1 + earned) - spent2 <= 0:
                continue
            
            final_money = initial_money - spent1 + earned - spent2
            break # 條件滿足，跳出迴圈

        question_text_template = r"小明有一些錢。他先花了 {s1} 元，然後賺了 {e} 元，最後又花了 {s2} 元。如果他現在有 {f} 元，請問小明最初有多少錢？"
        question_text = question_text_template.replace("{s1}", str(spent1))\
                                                .replace("{e}", str(earned))\
                                                .replace("{s2}", str(spent2))\
                                                .replace("{f}", str(final_money))
        
        correct_ans_val = initial_money
        correct_answer = str(correct_ans_val)
        answer = correct_answer

    elif problem_type == 'type_3_contextual_app':
        # Type 3 (Maps to Example 5, 6): 情境應用 - 三人分錢問題
        # 描述：三人共有固定金額，且各人之間有相對金額關係，求其中一人的金額。
        # 目標：測試學生將實際情境轉化為代數表達式，並求解線性方程的能力。

        diff_bc = _generate_random_int(3, 10)  # 乙比丙多
        diff_ab = _generate_random_int(5, 15)  # 甲比乙多

        # 設丙為 x 元
        # 乙 = x + diff_bc
        # 甲 = 乙 + diff_ab = (x + diff_bc) + diff_ab = x + diff_bc + diff_ab
        # 總和 = 丙 + 乙 + 甲 = x + (x + diff_bc) + (x + diff_bc + diff_ab)
        # 總和 = 3x + 2*diff_bc + diff_ab

        required_sum_for_3x = 2 * diff_bc + diff_ab
        
        # 確保 x (丙的金額) 至少為 1。
        # 3x 至少為 3，所以 total_items - required_sum_for_3x 至少為 3。
        # 最小的 total_items = required_sum_for_3x + 3
        min_total_items_for_positive_x = required_sum_for_3x + 3 
        total_items = _generate_random_int(min_total_items_for_positive_x, min_total_items_for_positive_x + 60)
        
        # 調整 total_items 確保 (total_items - required_sum_for_3x) 能被 3 整除
        while (total_items - required_sum_for_3x) % 3 != 0:
            total_items += 1

        correct_ans_val = (total_items - required_sum_for_3x) // 3 # 丙的金額
        
        question_text_template = r"甲、乙、丙三人共有 {total} 元。若甲比乙多 {diff_ab} 元，乙比丙多 {diff_bc} 元。請問丙有多少元？"
        question_text = question_text_template.replace("{total}", str(total_items))\
                                                .replace("{diff_ab}", str(diff_ab))\
                                                .replace("{diff_bc}", str(diff_bc))
        
        correct_answer = str(correct_ans_val)
        answer = correct_answer

    # 數據與欄位 (Standard Fields)
    # -------------------------------------------------------------------------
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0" # 初始版本
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
