# ==============================================================================
# ID: jh_數學1上_FormulatingOneVariableLinearEquations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 43.55s | RAG: 2 examples
# Created At: 2026-01-14 20:58:45
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
import base64 # 即使圖片為空，也必須包含此模組以符合欄位規範

# --- 輔助函式 (Helper Functions) ---
# 確保所有輔助函式明確回傳結果，且若用於 question_text 則強制轉為字串。
# 視覺化函式在此技能中不適用，但若有，會遵循防洩漏原則。

def _generate_random_coefficient():
    """產生一個隨機的非零整數係數。"""
    val = random.randint(-10, 10)
    while val == 0: # 確保係數不為零，以形成一元一次方程式
        val = random.randint(-10, 10)
    return val

def _generate_random_constant():
    """產生一個隨機的整數常數項。"""
    return random.randint(-20, 20)

def _generate_positive_integer(min_val=1, max_val=15):
    """產生一個指定範圍內的正整數。"""
    return random.randint(min_val, max_val)

def _generate_random_name():
    """產生一個隨機的常見中文人名，用於情境題。"""
    names = ["小明", "小華", "小芳", "小麗", "老師", "媽媽", "爸爸", "哥哥", "妹妹"]
    return random.choice(names)

def _format_equation_from_terms(left_expr: str, right_expr: str) -> str:
    """
    將左右兩側的表達式組合成一個方程式字串。
    此函式內部使用 f-string 是安全的，因為 left_expr 和 right_expr
    在傳入時已是純文字或數字，不包含 LaTeX 指令。
    """
    return f"{left_expr} = {right_expr}"

# --- 頂層函式 (Top-Level Functions) ---

def generate(level: int = 1) -> dict:
    """
    生成一元一次方程式的列式題目。
    根據 `level` 參數（目前未使用，但保留擴展性），隨機選擇題型。
    """
    problem_type = random.choice([1, 2, 3]) # 隨機分流至至少 3 種題型變體
    question_text = ""
    correct_answer = ""
    answer_guidance = "" # 用於引導學生輸入格式的範例

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 2): 直接翻譯 verbal statement
        # 描述: 將一個數的倍數、加減常數等於另一個數的敘述，列出方程式。
        a_val = _generate_random_coefficient()
        b_val = _generate_random_constant()
        c_val = _generate_random_constant()

        # 為了題型多樣性，讓係數 a 盡量不是 1 或 -1，除非 b_val 為 0
        if b_val != 0:
            while a_val == 1 or a_val == -1:
                a_val = _generate_random_coefficient()
        
        # 構建題目敘述的各部分，嚴格遵守 LaTeX 安全規範 (Regex=0)
        a_text_part = ""
        if a_val == 1:
            a_text_part = r"一個數"
        elif a_val == -1:
            # 負一倍通常會寫成 -(一個數) 或 -x，這裡為了語意清晰，使用「-1 倍」
            a_text_part = r"一個數的 $({val})$ 倍".replace("{val}", str(a_val))
        else:
            a_text_part = r"一個數的 ${val}$ 倍".replace("{val}", str(a_val))
        
        b_text_part = ""
        if b_val > 0:
            b_text_part = r"加上 ${val}$".replace("{val}", str(b_val))
        elif b_val < 0:
            b_text_part = r"減去 ${val_abs}$".replace("{val_abs}", str(abs(b_val)))
        
        q_template = r"{a_term}{b_term} 等於 ${c}$。請列出方程式。"
        question_text = q_template.replace("{a_term}", a_text_part) \
                                  .replace("{b_term}", b_text_part) \
                                  .replace("{c}", str(c_val))
        
        # 構建正確答案的方程式字串
        left_expr = ""
        if a_val == 1:
            left_expr = "x"
        elif a_val == -1:
            left_expr = "-x"
        else:
            left_expr = f"{a_val}x"

        if b_val > 0:
            left_expr += f" + {b_val}"
        elif b_val < 0:
            left_expr += f" - {abs(b_val)}"
        
        right_expr = str(c_val)
        correct_answer = _format_equation_from_terms(left_expr, right_expr)
        answer_guidance = r"例如：$3x+5=10$"

    elif problem_type == 2:
        # Type 2 (Maps to Example 3, 4): 情境應用 (年齡、金錢、長度等)
        # 描述: 給定情境，例如年齡關係、金錢交易或物體長度，要求學生列出方程式。
        scenario = random.choice(["age", "money", "length"])
        name1 = _generate_random_name()
        name2 = _generate_random_name()
        while name1 == name2: # 確保人名不同
            name2 = _generate_random_name()

        if scenario == "age":
            diff_age = _generate_positive_integer(2, 10) # 年齡差
            total_age = _generate_positive_integer(20, 60) # 總年齡
            
            q_template = r"{name1}比{name2}大${diff}$歲，兩人年齡和是${total}$歲。若{name2}的年齡是$x$歲，請列出方程式。"
            question_text = q_template.replace("{name1}", name1) \
                                      .replace("{name2}", name2) \
                                      .replace("{diff}", str(diff_age)) \
                                      .replace("{total}", str(total_age))
            
            # 方程式: x + (x + diff_age) = total_age
            correct_answer = _format_equation_from_terms(f"x + (x + {diff_age})", str(total_age))
            answer_guidance = r"例如：$x+(x+3)=25$"

        elif scenario == "money":
            item_cost = _generate_positive_integer(50, 200) # 商品單價
            num_items = _generate_positive_integer(2, 5) # 購買數量
            remaining_money = _generate_positive_integer(10, 50) # 剩餘金額
            # 確保初始金額合理，可以購買商品並有剩餘 (雖然 x 是未知數，但確保題目情境合理)
            # 這裡不需要真的計算初始金額，因為 x 就是初始金額。
            # 但可以確保購買總價不會讓 remaining_money 變成負數 (如果 x 是正數)
            
            q_template = r"{name}有$x$元，他買了${num}$個單價為${cost}$元的商品後，還剩下${rem}$元。請列出方程式。"
            question_text = q_template.replace("{name}", name1) \
                                      .replace("{num}", str(num_items)) \
                                      .replace("{cost}", str(item_cost)) \
                                      .replace("{rem}", str(remaining_money))
            
            # 方程式: x - (num_items * item_cost) = remaining_money
            correct_answer = _format_equation_from_terms(f"x - {num_items * item_cost}", str(remaining_money))
            answer_guidance = r"例如：$x-150=20$"
        
        elif scenario == "length":
            total_length = _generate_positive_integer(30, 100) # 繩子總長
            part_diff = _generate_positive_integer(5, 15) # 兩段的長度差
            
            q_template = r"一條繩子長${total}$公分，分成兩段。若其中一段長$x$公分，另一段比這段短${diff}$公分。請列出方程式。"
            question_text = q_template.replace("{total}", str(total_length)) \
                                      .replace("{diff}", str(part_diff))
            
            # 方程式: x + (x - part_diff) = total_length
            correct_answer = _format_equation_from_terms(f"x + (x - {part_diff})", str(total_length))
            answer_guidance = r"例如：$x+(x-5)=50$"

    elif problem_type == 3:
        # Type 3 (Maps to Example 5): 幾何或比較問題
        # 描述: 涉及圖形周長或數量比較，要求學生列出方程式。
        shape_type = random.choice(["rectangle", "triangle"])

        if shape_type == "rectangle":
            diff_lw = _generate_positive_integer(2, 10) # 長寬差
            perimeter = _generate_positive_integer(20, 80) # 周長
            # 確保周長為偶數且足夠大，以形成有效長方形 (寬 x, 長 x+diff_lw, 2*(x + x+diff_lw) = p)
            # 2*(2x + diff_lw) = p => 4x + 2*diff_lw = p => p - 2*diff_lw = 4x
            # 所以 p - 2*diff_lw 必須是 4 的倍數，且 p - 2*diff_lw > 0
            # 簡化為 p 必須是偶數，且 p 必須大於 2*diff_lw (保證 x > 0)
            while perimeter % 2 != 0 or perimeter <= 2 * diff_lw: 
                perimeter = _generate_positive_integer(20, 80)
            
            q_template = r"一個長方形的長比寬多${diff}$公分，周長是${p}$公分。若寬是$x$公分，請列出方程式。"
            question_text = q_template.replace("{diff}", str(diff_lw)) \
                                      .replace("{p}", str(perimeter))
            
            # 方程式: 2 * (x + (x + diff_lw)) = perimeter
            correct_answer = _format_equation_from_terms(f"2 * (x + (x + {diff_lw}))", str(perimeter))
            answer_guidance = r"例如：$2(x+x+5)=30$"

        elif shape_type == "triangle":
            diff_x_a = _generate_positive_integer(2, 8) # 第二邊比 x 多
            # 確保 x-b 仍為正數，所以 b 必須小於 x。為了讓 x-b 作為邊長合理，b 必須小於 a
            # 且為了避免 x-b 變成非正數，這裡直接讓 diff_x_b 小於 diff_x_a
            diff_x_b = _generate_positive_integer(1, max(1, diff_x_a - 1)) 
            
            # 確保周長有意義且能形成三角形 (任意兩邊和大於第三邊)
            # 這裡簡化為確保三邊長為正，且周長足夠大。
            # 假設 x 至少為 1 + diff_x_b (讓 x - diff_x_b 至少為 1)
            min_x_val = diff_x_b + 1 
            min_possible_perimeter = min_x_val + (min_x_val + diff_x_a) + (min_x_val - diff_x_b) 
            perimeter = _generate_positive_integer(max(30, min_possible_perimeter + 5), 80) # 確保周長足夠大

            q_template = r"一個三角形的三邊長分別為$x$公分、$(x+{a})$公分，以及$(x-{b})$公分。若周長是${p}$公分，請列出方程式。"
            question_text = q_template.replace("{a}", str(diff_x_a)) \
                                      .replace("{b}", str(diff_x_b)) \
                                      .replace("{p}", str(perimeter))
            
            # 方程式: x + (x + diff_x_a) + (x - diff_x_b) = perimeter
            correct_answer = _format_equation_from_terms(f"x + (x + {diff_x_a}) + (x - {diff_x_b})", str(perimeter))
            answer_guidance = r"例如：$x+(x+2)+(x-1)=20$"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_guidance, # 提供學生輸入範例
        "image_base64": "", # 此技能不涉及圖片，故為空字串
        "created_at": datetime.datetime.now().isoformat(), # ISO 8601 格式時間戳
        "version": 1.0 # 版本號
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
