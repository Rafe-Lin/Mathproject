# ==============================================================================
# ID: jh_數學1上_PrimeNumbersAndPrimeFactorization
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 27.01s | RAG: 5 examples
# Created At: 2026-01-14 20:13:46
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
import base64 # Required for 'image_base64' field, even if empty

# --- 輔助函式 (Helper Functions) ---

def _is_prime(n):
    """
    檢查一個數是否為質數。
    Args:
        n (int): 待檢查的整數。
    Returns:
        bool: 如果 n 是質數則回傳 True，否則回傳 False。
    """
    if n < 2:
        return False
    # 從 2 到 sqrt(n) 檢查是否有因數
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def _get_prime_factors_dict(n):
    """
    取得一個數的質因數及其指數的字典。
    Args:
        n (int): 待分解的整數。
    Returns:
        dict: 質因數為鍵，指數為值的字典。例如：_get_prime_factors_dict(120) -> {2: 3, 3: 1, 5: 1}
    """
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1: # 處理剩餘的質因數 (如果 temp 本身是質數)
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def _format_prime_factorization(factors_dict):
    """
    將質因數分解的字典格式化為 LaTeX 安全的字串。
    Args:
        factors_dict (dict): 質因數及其指數的字典。
    Returns:
        str: 格式化後的質因數分解字串。例如：{2: 3, 3: 1, 5: 1} -> "2^3 \\times 3 \\times 5"
    """
    if not factors_dict:
        return "1" # 理論上對於大於 1 的正整數不會發生

    parts = []
    # 確保質因數按大小排序
    sorted_factors = sorted(factors_dict.items())

    for prime, exponent in sorted_factors:
        if exponent == 1:
            parts.append(str(prime))
        else:
            # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
            # 必須使用 .replace() 模板，避免 LaTeX 大括號與 Python 衝突
            part_str_template = r"{prime}^{exponent}"
            part_str = part_str_template.replace("{prime}", str(prime)).replace("{exponent}", str(exponent))
            parts.append(part_str)
            
    # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
    # 必須使用 .replace() 模板，避免 LaTeX 大括號與 Python 衝突 (此處為拼接，但仍需注意)
    result_str = r" \times ".join(parts)
    return result_str

def _generate_random_prime(min_val, max_val):
    """
    在指定範圍內生成一個隨機質數。
    Args:
        min_val (int): 範圍最小值。
        max_val (int): 範圍最大值。
    Returns:
        int: 一個隨機質數。
    Raises:
        ValueError: 如果範圍內沒有質數。
    """
    primes = [i for i in range(min_val, max_val + 1) if _is_prime(i)]
    if not primes:
        raise ValueError(f"在 {min_val} 到 {max_val} 之間沒有找到質數。")
    return random.choice(primes)

def _generate_random_composite(min_val, max_val):
    """
    在指定範圍內生成一個隨機合數。
    Args:
        min_val (int): 範圍最小值。
        max_val (int): 範圍最大值。
    Returns:
        int: 一個隨機合數。
    Raises:
        ValueError: 如果範圍內沒有合數。
    """
    # 合數定義為大於1且不是質數的整數
    composites = [i for i in range(min_val, max_val + 1) if not _is_prime(i) and i > 1]
    if not composites:
        raise ValueError(f"在 {min_val} 到 {max_val} 之間沒有找到合數。")
    return random.choice(composites)

# --- 模組版本控制 ---
# 注意：此為模組級別變數，用於追蹤代碼版本，每次調用 generate 會遞增。
# importlib.reload 會將其重置為初始值，符合無全域狀態依賴的規範。
_MODULE_VERSION = 1.0

# --- 頂層函式 (Top-level Functions) ---

def generate(level=1):
    """
    生成 K12 數學「質數與質因數分解」技能的題目。

    Args:
        level (int): 題目難度等級，目前未使用，預設為 1。
    
    Returns:
        dict: 包含題目文本、正確答案、顯示答案、圖片base64、創建時間和版本的字典。
    """
    global _MODULE_VERSION
    _MODULE_VERSION += 0.01 # 每次生成題目，模組版本號微幅遞增

    problem_type = random.choice([1, 2, 3]) # 隨機選擇 3 種題型變體
    question_text = ""
    correct_answer = ""
    answer_display = "" # 用於顯示給用戶的答案格式

    if problem_type == 1:
        # 題型變體 1: 直接計算 - 質因數分解
        # 範例：「將 120 進行質因數分解。」
        
        num = _generate_random_composite(50, 300) # 生成一個 50 到 300 之間的合數

        # 【強制】LaTeX 安全排版：凡字串包含 LaTeX 指令，嚴禁 f-string
        # 必須使用 .replace() 模板
        question_text_template = r"請將 {num} 進行質因數分解。答案請以 $p_1^{a_1} \times p_2^{a_2} \times \dots$ 的形式表示。"
        question_text = question_text_template.replace("{num}", str(num))
        
        factors_dict = _get_prime_factors_dict(num)
        correct_answer_formatted = _format_prime_factorization(factors_dict)
        
        # correct_answer 為機器可讀取的標準格式，answer_display 為用戶顯示格式
        correct_answer = correct_answer_formatted
        # 【強制】LaTeX 安全排版：所有數學式一律使用 $...$
        answer_display_template = r"${ans}$"
        answer_display = answer_display_template.replace("{ans}", correct_answer_formatted)

    elif problem_type == 2:
        # 題型變體 2: 情境應用 - 識別質數或找出所有質因數
        # 範例：「下列哪個數是質數？」或「找出 72 的所有質因數。」

        sub_type = random.choice([1, 2])
        if sub_type == 1:
            # 子題型 2.1: 從選項中識別質數
            num_options = 4
            num_primes_in_options = random.randint(1, 2) # 選項中包含 1 或 2 個質數
            
            prime_candidates = []
            while len(prime_candidates) < num_primes_in_options:
                p = _generate_random_prime(10, 80) # 生成 10 到 80 之間的質數
                if p not in prime_candidates:
                    prime_candidates.append(p)
            
            composite_candidates = []
            while len(composite_candidates) < (num_options - num_primes_in_options):
                c = _generate_random_composite(10, 80) # 生成 10 到 80 之間的合數
                if c not in composite_candidates and c not in prime_candidates:
                    composite_candidates.append(c)
            
            all_numbers = prime_candidates + composite_candidates
            random.shuffle(all_numbers) # 打亂選項順序
            
            options_text = []
            correct_prime_options = []
            for i, n in enumerate(all_numbers):
                option_char = chr(65 + i) # 'A', 'B', 'C', 'D'
                # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
                option_template = r"({char}) {num}"
                options_text.append(option_template.replace("{char}", option_char).replace("{num}", str(n)))
                if _is_prime(n):
                    correct_prime_options.append(option_char)
            
            # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
            question_text_template = r"下列哪個（些）數是質數？請選出所有正確的選項。{options_list}"
            question_text = question_text_template.replace("{options_list}", " ".join(options_text))
            
            correct_answer = ",".join(sorted(correct_prime_options)) # 例如 "A,C"
            answer_display = correct_answer

        else:
            # 子題型 2.2: 找出一個數的所有質因數 (僅列出不重複的質因數)
            num = _generate_random_composite(70, 250)
            
            # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
            question_text_template = r"找出 {num} 的所有質因數。"
            question_text = question_text_template.replace("{num}", str(num))
            
            factors_dict = _get_prime_factors_dict(num)
            distinct_prime_factors = sorted(list(factors_dict.keys()))
            
            correct_answer = ",".join(map(str, distinct_prime_factors))
            # 【強制】LaTeX 安全排版：所有數學式一律使用 $...$
            answer_display_template = r"${ans}$"
            answer_display = answer_display_template.replace("{ans}", correct_answer)

    else: # problem_type == 3
        # 題型變體 3: 逆向求解 / 情境應用 - 從質因數分解求原數 或 找出範圍內的質數
        # 範例：「已知一個數的質因數分解為 $2^2 \times 3 \times 5$，請問這個數是多少？」

        sub_type = random.choice([1, 2])
        if sub_type == 1:
            # 子題型 3.1: 已知質因數分解，求原數
            primes_pool = [2, 3, 5, 7, 11, 13]
            num_distinct_primes = random.randint(2, 3) # 選擇 2 或 3 個不同的質因數
            selected_primes = random.sample(primes_pool, num_distinct_primes)
            
            factors_dict = {}
            original_num = 1
            for p in selected_primes:
                exp = random.randint(1, 2) # 指數為 1 或 2
                factors_dict[p] = exp
                original_num *= (p ** exp)
            
            # 確保生成的數值在合理範圍內 (例如 30 到 500)
            while original_num < 30 or original_num > 500:
                factors_dict = {}
                original_num = 1
                selected_primes = random.sample(primes_pool, num_distinct_primes)
                for p in selected_primes:
                    exp = random.randint(1, 2)
                    factors_dict[p] = exp
                    original_num *= (p ** exp)

            factorization_str = _format_prime_factorization(factors_dict)
            
            # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
            question_text_template = r"已知一個正整數 N 的質因數分解為 ${factors_str}$，請問這個數 N 是多少？"
            question_text = question_text_template.replace("{factors_str}", factorization_str)
            
            correct_answer = str(original_num)
            answer_display = correct_answer
            
        else:
            # 子題型 3.2: 找出指定範圍內的所有質數
            start_range = random.randint(10, 60)
            end_range = start_range + random.randint(15, 40) # 範圍寬度 15 到 40
            
            primes_in_range = [p for p in range(start_range, end_range + 1) if _is_prime(p)]
            
            # 【強制】LaTeX 安全排版：嚴禁 f-string 或 % 格式化
            question_text_template = r"找出介於 {start} 到 {end} 之間（包含 {start} 和 {end}）的所有質數，並由小到大排列，以逗號分隔。"
            question_text = question_text_template.replace("{start}", str(start_range)).replace("{end}", str(end_range))
            
            correct_answer = ",".join(map(str, primes_in_range))
            # 【強制】LaTeX 安全排版：所有數學式一律使用 $...$
            answer_display_template = r"${ans}$"
            answer_display = answer_display_template.replace("{ans}", correct_answer)

    # 返回字典必須且僅能包含指定欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": "", # 此技能目前無需圖片，回傳空字串
        "created_at": datetime.datetime.now().isoformat(), # 更新時間戳記
        "version": _MODULE_VERSION, # 遞增版本
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
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['question_text'] += "\\n(請在手寫區作答!)"

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
