# ==============================================================================
# ID: jh_數學1上_FractionDivision
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 23.00s | RAG: 3 examples
# Created At: 2026-01-14 19:04:44
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



from datetime import datetime
import base64 # Required for image_base64 field, even if empty

# --- 輔助函式 (Helper Functions) ---

def _gcd(a, b):
    """
    計算兩個整數的最大公因數。
    回傳值型別: int
    """
    return math.gcd(a, b)

def _simplify_fraction(numerator, denominator):
    """
    簡化分數 (分子, 分母)，並確保分母為正數。
    例如: (4, 8) -> (1, 2); (-4, 8) -> (-1, 2); (4, -8) -> (-1, 2); (0, 5) -> (0, 1)。
    回傳值型別: tuple (int, int)
    """
    if denominator == 0:
        raise ValueError("分母不能為零。")
    if numerator == 0:
        return (0, 1)

    common_divisor = _gcd(abs(numerator), abs(denominator))
    simplified_num = numerator // common_divisor
    simplified_den = denominator // common_divisor

    # 確保分母始終為正數
    if simplified_den < 0:
        simplified_num = -simplified_num
        simplified_den = -simplified_den

    return (simplified_num, simplified_den)

def _format_fraction_latex(numerator, denominator):
    """
    將分數格式化為 LaTeX 字串。處理整數和簡化分數。
    例如: (5, 1) -> "5"; (1, 2) -> "$\frac{1}{2}$"。
    【強制】嚴格執行 Regex=0 規範，凡字串包含 LaTeX 指令，嚴禁使用 f-string。
    回傳值型別: str
    """
    if denominator == 1:
        return str(numerator)
    if numerator == 0:
        return str(0)
    
    # 嚴格遵循 Regex=0 模板: replace("{placeholder}", value)
    # 使用 NUM 和 DEN 作為佔位符以避免與 LaTeX 自身的 {} 衝突。
    latex_str_template = r"$\frac{NUM}{DEN}$"
    formatted_str = latex_str_template.replace("NUM", str(numerator)).replace("DEN", str(denominator))
    return formatted_str

def _format_fraction_string(numerator, denominator):
    """
    將簡化分數 (分子, 分母) 格式化為字串，如 "3/4" 或 "5"。
    此函式用於 `correct_answer` 欄位，不含 LaTeX，故可使用 f-string。
    回傳值型別: str
    """
    if denominator == 1:
        return str(numerator)
    return f"{numerator}/{denominator}"

def _calculate_fraction_division(n1, d1, n2, d2):
    """
    執行分數除法運算 (n1/d1) / (n2/d2)，並回傳簡化後的結果 (分子, 分母)。
    回傳值型別: tuple (int, int)
    """
    if n2 == 0: # 除數的分子不能為零
        raise ValueError("除數不能為零。")
    
    result_num = n1 * d2
    result_den = d1 * n2
    
    return _simplify_fraction(result_num, result_den)

def _parse_fraction_string(fraction_str):
    """
    將 "3/4" 或 "5" 等字串解析為簡化後的 (分子, 分母) tuple。
    回傳值型別: tuple (int, int) 或 None (解析失敗時)
    """
    try:
        if '/' in fraction_str:
            parts = fraction_str.split('/')
            numerator = int(parts[0])
            denominator = int(parts[1])
            if denominator == 0:
                raise ValueError("分母不能為零。")
        else:
            numerator = int(fraction_str)
            denominator = 1
        return _simplify_fraction(numerator, denominator)
    except (ValueError, IndexError):
        return None # 解析失敗

# --- 頂層函式 (Top-level Functions) ---

def generate(level=1):
    """
    根據指定難度等級 (level) 生成分數除法運算題目。
    嚴禁使用 class 封裝。
    回傳值型別: dict
    """
    problem_types = [
        "direct_calculation",   # 直接計算
        "inverse_problem",      # 逆向求解
        "word_problem"          # 情境應用
    ]
    problem_type = random.choice(problem_types)

    # 根據難度等級調整數字範圍
    if level == 1:
        num_range = (1, 10) # 分子範圍
        den_range = (2, 10) # 分母範圍 (從2開始確保是真分數或假分數)
    elif level == 2:
        num_range = (1, 15)
        den_range = (2, 15)
    else: # level 3+
        num_range = (1, 20)
        den_range = (2, 20)
    
    def _get_non_zero_num(r):
        """生成非零的分子，以避免除數為零或結果為零的特殊情況。"""
        num = 0
        while num == 0:
            num = random.randint(*r)
        return num

    # 初始化題目所需變數
    question_text = ""
    result_num, result_den = (0, 1) # 預設答案

    if problem_type == "direct_calculation":
        # 題型1: 直接計算 (e.g., 計算 A/B ÷ C/D 的值)
        
        n1 = random.randint(*num_range)
        d1 = random.randint(*den_range)
        n2 = _get_non_zero_num(num_range) # 除數分子不能為零
        d2 = random.randint(*den_range)
        
        s_n1, s_d1 = _simplify_fraction(n1, d1)
        s_n2, s_d2 = _simplify_fraction(n2, d2)

        result_num, result_den = _calculate_fraction_division(n1, d1, n2, d2)
        
        frac1_latex = _format_fraction_latex(s_n1, s_d1)
        frac2_latex = _format_fraction_latex(s_n2, s_d2)
        
        # 使用 replace 模板來構建 question_text，確保 LaTeX 安全
        question_text_template = r"計算 {frac1} $\div$ {frac2} 的值。"
        question_text = question_text_template.replace("{frac1}", frac1_latex).replace("{frac2}", frac2_latex)

    elif problem_type == "inverse_problem":
        # 題型2: 逆向求解 (e.g., 已知 A/B ÷ X = C/D，求 X 的值)
        # 則 X = (A/B) ÷ (C/D)
        
        n_A = random.randint(*num_range)
        d_A = random.randint(*den_range)
        n_C = _get_non_zero_num(num_range) # 結果的分子不能為零
        d_D = random.randint(*den_range)
        
        s_n_A, s_d_A = _simplify_fraction(n_A, d_A)
        s_n_C, s_d_D = _simplify_fraction(n_C, d_D)

        result_num, result_den = _calculate_fraction_division(n_A, d_A, n_C, d_D)
        
        fracA_latex = _format_fraction_latex(s_n_A, s_d_A)
        fracC_latex = _format_fraction_latex(s_n_C, s_d_D)
        
        question_text_template = r"已知 {fracA} $\div X =$ {fracC}，求 $X$ 的值。"
        question_text = question_text_template.replace("{fracA}", fracA_latex).replace("{fracC}", fracC_latex)

    else: # problem_type == "word_problem"
        # 題型3: 情境應用 (e.g., 一條繩子總長度為 ...，每段長度為 ...，可以剪成幾段？)
        
        # 為了使情境題答案更符合 K12 習慣 (通常為整數段數)，我們反向生成題目
        num_pieces = random.randint(2, 12) # 預設結果為整數段數 (2到12段)
        
        # 生成每段的長度 (分數)
        n_piece = _get_non_zero_num(num_range)
        d_piece = random.randint(*den_range)
        s_n_piece, s_d_piece = _simplify_fraction(n_piece, d_piece)

        # 計算總長度 = 段數 * 每段長度
        # 注意：這裡的乘法可能導致分子分母很大，但 _simplify_fraction 會處理
        n_total_length = num_pieces * n_piece
        d_total_length = d_piece
        s_n_total_length, s_d_total_length = _simplify_fraction(n_total_length, d_total_length)

        # 答案就是預設的段數
        result_num, result_den = (num_pieces, 1)

        total_length_latex = _format_fraction_latex(s_n_total_length, s_d_total_length)
        piece_length_latex = _format_fraction_latex(s_n_piece, s_d_piece)
        
        question_text_template = r"有一條長 {total_len} 公尺的繩子，每 {piece_len} 公尺剪成一段，請問總共可以剪成幾段？"
        question_text = question_text_template.replace("{total_len}", total_length_latex).replace("{piece_len}", piece_length_latex)

    # 格式化正確答案為字串
    correct_answer_str = _format_fraction_string(result_num, result_den)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str, # 初始答案與正確答案相同
        "image_base64": "", # 此技能無需圖片，回傳空字串
        "created_at": datetime.now().isoformat(), # ISO 8601 格式時間戳記
        "version": "1.0" # 版本號
    }


# 以下為內部測試用，實際提交時不會執行

if __name__ == '__main__':
    print("--- 執行 generate 測試 ---")
    for level in [1, 2, 3]:
        print(f"\n--- Level {level} ---")
        for _ in range(3): # 為每個難度生成3個題目
            problem = generate(level)
            print(f"題目: {problem['question_text']}")
            print(f"正確答案: {problem['correct_answer']}")
            # print(f"完整題目: {problem}")

    print("\n--- 執行 check 測試 ---")
    test_cases = [
        ("1/2", "1/2", True),
        ("2/4", "1/2", True), # 簡化後應相等
        ("3", "3/1", True),   # 整數與分數表示應相等
        ("3/1", "3", True),
        ("5/2", "2/1", False),
        ("0/1", "0", True),
        ("0", "0/5", True),
        ("abcd", "1/2", False), # 無效輸入
        ("1/0", "1/2", False), # 無效分母
        ("1/2", "abcd", False), # 無效答案
        ("-1/2", "1/-2", True), # 分母為負數應簡化為分子為負
        ("-1/2", "-2/4", True),
        ("1", "1", True)
    ]

    for user_ans, correct_ans, expected in test_cases:
        result = check(user_ans, correct_ans)
        print(f"使用者答案: '{user_ans}', 正確答案: '{correct_ans}', 檢查結果: {result} (預期: {expected}) {'✅' if result == expected else '❌'}")

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
