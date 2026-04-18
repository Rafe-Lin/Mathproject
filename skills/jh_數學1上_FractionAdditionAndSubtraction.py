# ==============================================================================
# ID: jh_數學1上_FractionAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 29.87s | RAG: 5 examples
# Created At: 2026-01-14 19:04:21
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
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
    if n <= 1: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    if n <= 3: return {'correct': True, 'result': '正確！'}
    if n % 2 == 0 or n % 3 == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
        i += 6
    return {'correct': True, 'result': '正確！'}
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
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}



import base64
 # 使用 fractions 模組確保分數運算的精確性

# --- 輔助函式 (Helper Functions) ---
# 遵循通用規範：必須回傳結果，若用於 question_text 則強制轉為字串。
# 防洩漏原則：視覺化函式僅能接收題目已知數據 (此技能暫無複雜視覺化)。

def _gcd(a, b):
    """
    計算兩個整數的最大公因數 (GCD)。
    回傳 int。
    """
    while b:
        a, b = b, a % b
    return a

def _simplify_fraction(numerator, denominator):
    """
    簡化分數至最簡形式。
    回傳簡化後的 (numerator, denominator) tuple。
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    if numerator == 0:
        return (0, 1) # 0/X 簡化為 0/1

    common = _gcd(abs(int(numerator)), abs(int(denominator)))
    return (numerator // common, denominator // common)

def _format_fraction_latex(numerator, denominator, mixed_number=False):
    """
    將分數格式化為 LaTeX 字串，考慮真分數、假分數、整數和帶分數。
    【排版與 LaTeX 安全】強制使用 replace 避免 f-string 與 LaTeX 衝突。
    回傳 str。
    """
    if denominator == 0:
        return r"\text{錯誤}" # 理論上不應發生

    # 處理負號
    sign = ""
    if numerator * denominator < 0:
        sign = "-"
        numerator = abs(numerator)
        denominator = abs(denominator)
    elif numerator == 0: # 如果分子是0，則不顯示負號
        sign = ""
        numerator = 0
        denominator = 1 # 簡化為 0/1

    simplified_num, simplified_den = _simplify_fraction(numerator, denominator)

    if simplified_den == 1:
        # 整數情況
        return sign + str(simplified_num)
    elif mixed_number and simplified_num >= simplified_den:
        # 帶分數情況 (僅當 mixed_number=True 且為假分數時)
        whole_part = simplified_num // simplified_den
        remainder = simplified_num % simplified_den
        if remainder == 0: # 若餘數為0，則實際為整數
            return sign + str(whole_part)
        else:
            # 嚴格遵循 replace 模板
            mixed_str_template = r"{sign}{whole}\frac{{{num}}}{{{den}}}"
            mixed_str = mixed_str_template.replace("{sign}", sign)
            mixed_str = mixed_str.replace("{whole}", str(whole_part))
            mixed_str = mixed_str.replace("{num}", str(remainder))
            mixed_str = mixed_str.replace("{den}", str(simplified_den))
            return mixed_str
    else:
        # 真分數或未轉換為帶分數的假分數
        # 嚴格遵循 replace 模板
        frac_str_template = r"{sign}\frac{{{num}}}{{{den}}}"
        frac_str = frac_str_template.replace("{sign}", sign)
        frac_str = frac_str.replace("{num}", str(simplified_num))
        frac_str = frac_str.replace("{den}", str(simplified_den))
        return frac_str

# --- 頂層函式 (Top-level Functions) ---
# 嚴禁使用 class 封裝，自動重載兼容。

def generate(level=1):
    """
    生成 K12 數學「分數的加減」技能的題目。
    根據 level 參數 (目前未使用，預留擴展) 和隨機選擇生成不同題型。
    """
    # 題型多樣性：隨機分流實現至少 3 種不同題型變體
    problem_type_choice = random.choice([
        "direct_calculation_simple",    # 直接計算：真分數加減
        "direct_calculation_mixed",     # 直接計算：包含帶分數的加減
        "inverse_problem",              # 逆向求解：尋找未知數
        "word_problem_add",             # 情境應用：加法應用題
        "word_problem_subtract"         # 情境應用：減法應用題
    ])

    question_text = ""
    correct_answer_frac = None # 內部計算使用 Fraction 物件，確保精確度
    display_answer = ""
    image_base64 = "" # 此技能通常不需圖片，留空。

    # 題型變體 1: 直接計算 (真分數加減)
    if problem_type_choice == "direct_calculation_simple":
        op = random.choice(['+', '-'])
        
        # 生成分母，避免過大或過小
        den1 = random.randint(2, 12)
        den2 = random.randint(2, 12)
        
        # 生成分子，確保為真分數 (分子 < 分母)
        num1 = random.randint(1, den1 - 1)
        num2 = random.randint(1, den2 - 1)

        frac1 = Fraction(num1, den1)
        frac2 = Fraction(num2, den2)

        # 格式化為 LaTeX 字串，遵循排版規範
        frac1_str = _format_fraction_latex(num1, den1)
        frac2_str = _format_fraction_latex(num2, den2)

        if op == '+':
            correct_answer_frac = frac1 + frac2
            question_template = r"計算：${f1} + {f2} = ?$"
            question_text = question_template.replace("{f1}", frac1_str).replace("{f2}", frac2_str)
        else: # op == '-'
            # 確保減法結果非負，若第一個分數較小則交換
            if frac1 < frac2:
                frac1, frac2 = frac2, frac1
                frac1_str, frac2_str = frac2_str, frac1_str
            correct_answer_frac = frac1 - frac2
            question_template = r"計算：${f1} - {f2} = ?$"
            question_text = question_template.replace("{f1}", frac1_str).replace("{f2}", frac2_str)

    # 題型變體 2: 直接計算 (包含帶分數的加減)
    elif problem_type_choice == "direct_calculation_mixed":
        op = random.choice(['+', '-'])
        
        # 生成帶分數的整數部分和分數部分
        whole1 = random.randint(1, 3)
        den1 = random.randint(2, 8)
        num1 = random.randint(1, den1 - 1)

        whole2 = random.randint(1, 3)
        den2 = random.randint(2, 8)
        num2 = random.randint(1, den2 - 1)
        
        # 將帶分數轉換為假分數以便 Fraction 物件計算
        frac1 = Fraction(whole1 * den1 + num1, den1)
        frac2 = Fraction(whole2 * den2 + num2, den2)

        # 格式化為 LaTeX 字串 (帶分數形式)
        frac1_str = _format_fraction_latex(frac1.numerator, frac1.denominator, mixed_number=True)
        frac2_str = _format_fraction_latex(frac2.numerator, frac2.denominator, mixed_number=True)

        if op == '+':
            correct_answer_frac = frac1 + frac2
            question_template = r"計算：${f1} + {f2} = ?$"
            question_text = question_template.replace("{f1}", frac1_str).replace("{f2}", frac2_str)
        else: # op == '-'
            # 確保減法結果非負，若第一個分數較小則交換
            if frac1 < frac2:
                frac1, frac2 = frac2, frac1
                frac1_str, frac2_str = frac2_str, frac1_str
            correct_answer_frac = frac1 - frac2
            question_template = r"計算：${f1} - {f2} = ?$"
            question_text = question_template.replace("{f1}", frac1_str).replace("{f2}", frac2_str)
            
    # 題型變體 3: 逆向求解 (Find Missing Part)
    elif problem_type_choice == "inverse_problem":
        op_type = random.choice(['add_missing_rhs', 'subtract_missing_rhs', 'subtract_missing_lhs']) # A + X = B, A - X = B, X - A = B

        den_a = random.randint(2, 10)
        num_a = random.randint(1, den_a - 1)
        frac_a = Fraction(num_a, den_a)
        frac_a_str = _format_fraction_latex(num_a, den_a)

        # 生成一個用於構成答案的輔助分數 X
        den_x = random.randint(2, 10)
        num_x = random.randint(1, den_x - 1)
        frac_x = Fraction(num_x, den_x)
        
        if op_type == 'add_missing_rhs': # A + ? = B  =>  ? = B - A
            frac_b = frac_a + frac_x
            correct_answer_frac = frac_x
            question_template = r"請找出 $?$ 的值：${f_a} + ? = {f_b}$"
            question_text = question_template.replace("{f_a}", frac_a_str)
            question_text = question_text.replace("{f_b}", _format_fraction_latex(frac_b.numerator, frac_b.denominator, mixed_number=True))
        elif op_type == 'subtract_missing_rhs': # A - ? = B  =>  ? = A - B
            # 確保 A > B 使得 ? 為正數
            if frac_a < frac_x: # 如果 frac_a 比 frac_x 小，則交換，使結果為正
                frac_a, frac_x = frac_x, frac_a
                frac_a_str = _format_fraction_latex(frac_a.numerator, frac_a.denominator)
            frac_b = frac_a - frac_x
            correct_answer_frac = frac_x
            question_template = r"請找出 $?$ 的值：${f_a} - ? = {f_b}$"
            question_text = question_template.replace("{f_a}", frac_a_str)
            question_text = question_text.replace("{f_b}", _format_fraction_latex(frac_b.numerator, frac_b.denominator, mixed_number=True))
        elif op_type == 'subtract_missing_lhs': # ? - A = B  =>  ? = B + A
            frac_b = frac_x # 讓 frac_x 作為結果 B
            correct_answer_frac = frac_a + frac_b
            question_template = r"請找出 $?$ 的值：$? - {f_a} = {f_b}$"
            question_text = question_template.replace("{f_a}", frac_a_str)
            question_text = question_text.replace("{f_b}", _format_fraction_latex(frac_b.numerator, frac_b.denominator, mixed_number=True))

    # 題型變體 4: 情境應用 (加法)
    elif problem_type_choice == "word_problem_add":
        item1 = random.choice(["蛋糕", "披薩", "果汁", "一塊地"])
        unit1 = random.choice(["份", "塊", "公升", "公頃"])
        person1 = random.choice(["小明", "小華", "老師", "媽媽"])
        person2 = random.choice(["小美", "小芳", "同學", "爸爸"])

        den1 = random.randint(2, 6)
        num1 = random.randint(1, den1 - 1)
        frac1 = Fraction(num1, den1)
        frac1_str = _format_fraction_latex(num1, den1)

        den2 = random.randint(2, 6)
        num2 = random.randint(1, den2 - 1)
        frac2 = Fraction(num2, den2)
        frac2_str = _format_fraction_latex(num2, den2)

        correct_answer_frac = frac1 + frac2

        # 嚴格遵循 replace 模板
        question_template = r"{p1} 吃了 {item} 的 ${f1}$ {unit}，{p2} 吃了 {item} 的 ${f2}$ {unit}。請問他們一共吃了多少 {item}{unit}？"
        question_text = question_template.replace("{p1}", person1).replace("{item}", item1)
        question_text = question_text.replace("{f1}", frac1_str).replace("{unit}", unit1)
        question_text = question_text.replace("{p2}", person2).replace("{f2}", frac2_str)

    # 題型變體 5: 情境應用 (減法)
    elif problem_type_choice == "word_problem_subtract":
        item1 = random.choice(["蛋糕", "披薩", "果汁", "一塊布"])
        unit1 = random.choice(["份", "塊", "公升", "公尺"])
        person1 = random.choice(["小明", "小華", "老師", "媽媽"])

        # 生成一個可能為假分數或帶分數的總量
        den_total = random.randint(2, 6)
        num_total = random.randint(den_total + 1, den_total * 2) # 確保總量通常大於1
        frac_total = Fraction(num_total, den_total)
        frac_total_str = _format_fraction_latex(num_total, den_total, mixed_number=True)

        den_eaten = random.randint(2, 6)
        num_eaten = random.randint(1, den_eaten - 1)
        frac_eaten = Fraction(num_eaten, den_eaten)
        frac_eaten_str = _format_fraction_latex(num_eaten, den_eaten)
        
        # 確保總量大於吃掉的量
        if frac_total < frac_eaten:
            # 如果總量小於吃掉的量，則交換，使結果為正
            frac_total, frac_eaten = frac_eaten, frac_total
            frac_total_str = _format_fraction_latex(frac_total.numerator, frac_total.denominator, mixed_number=True)
            frac_eaten_str = _format_fraction_latex(frac_eaten.numerator, frac_eaten.denominator)

        correct_answer_frac = frac_total - frac_eaten

        # 嚴格遵循 replace 模板
        question_template = r"原本有 ${f_total}$ {unit} 的 {item}，{p1} 吃了 ${f_eaten}$ {unit}。請問還剩下多少 {item}{unit}？"
        question_text = question_template.replace("{f_total}", frac_total_str).replace("{unit}", unit1)
        question_text = question_text.replace("{item}", item1).replace("{p1}", person1).replace("{f_eaten}", frac_eaten_str)

    # 將 Fraction 對象轉換為 display_answer 和 correct_answer 的標準格式
    if correct_answer_frac is not None:
        # answer (顯示給用戶的答案) 通常為帶分數或最簡分數
        display_answer = _format_fraction_latex(correct_answer_frac.numerator, correct_answer_frac.denominator, mixed_number=True)
        # correct_answer (用於系統判斷的標準答案) 建議為 "numerator/denominator" 字串
        correct_answer = f"{correct_answer_frac.numerator}/{correct_answer_frac.denominator}"
    else:
        correct_answer = ""
        display_answer = ""

    # 數據與欄位：返回字典必須且僅能包含指定欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": display_answer,
        "image_base64": image_base64,
        # created_at 和 version 應由系統層面管理，不在此處返回字典中。
    }


# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # 2. [V10.3] 解決 r-string 導致的 \n 換行失效問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\']
            if (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers) and "手寫" not in res.get('question_text', ''):
                res['question_text'] += "\n(請在手寫區作答!)"

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
