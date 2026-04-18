# ==============================================================================
# ID: jh_數學1上_IntegerExponentiation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 32.64s | RAG: 5 examples
# Created At: 2026-01-14 16:23:44
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
#==============================================================================


import random
import math
import matplotlib
# [Fix] Font injection for Traditional Chinese support
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
matplotlib.rcParams['axes.unicode_minus'] = False
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{rem_num}}{{abs_num.denominator}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    if n <= 3: return {'correct': True, 'result': '正確！'}
    if n % 2 == 0 or n % 3 == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
        i += 6
    return {'correct': True, 'result': '正確！'}
def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
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

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

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

# --- 4. High-Level Math Objects (Vector/Matrix/Calculus) ---
class Vector3:
    """Simple 3D Vector Class for Geometry."""
    def __init__(self, x, y, z=0): self.x, self.y, self.z = x, y, z
    def __add__(self, o): return Vector3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vector3(self.x-o.x, self.y-o.y, self.z-o.z)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o): return Vector3(self.y*o.z-self.z*o.y, self.z*o.x-self.x*o.z, self.x*o.y-self.y*o.x)
    def mag(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def __repr__(self): return f"({self.x}, {self.y}, {self.z})"

class Matrix:
    """Simple Matrix (2x2 or 3x3) for transformations."""
    def __init__(self, rows): self.rows = rows
    def det(self):
        if len(self.rows) == 2: return self.rows[0][0]*self.rows[1][1] - self.rows[0][1]*self.rows[1][0]
        return 0 # Placeholder for 3x3
    def mv(self, v): # Matrix-Vector multiplication
        return Vector3(
            self.rows[0][0]*v.x + self.rows[0][1]*v.y,
            self.rows[1][0]*v.x + self.rows[1][1]*v.y, 0
        )

def draw_integral_area(func_lambda, x_range, color='blue', alpha=0.3):
    """
    [Visual] Helper to plot area under curve. 
    Usage: In generate(), ax.fill_between(x, y, ...).
    Actually, this is just a placeholder to remind AI to use fill_between.
    """
    pass

# --- 5. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案 (No answer)"}
    
    # 1. Normalize strings (字串正規化)
    def normalize(s):
        s = str(s).strip()
        # 移除空格、LaTeX間距
        s = s.replace(" ", "").replace("\\,", "").replace("\\;", "")
        # [Fix] 支援中文全形逗號，轉為半形，避免判錯
        s = s.replace("，", ",") 
        return s
    
    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    # 2. Exact Match Strategy (精確比對)
    if user_norm == correct_norm:
        return {"correct": True, "result": "正確！"}
        
    # 3. Float Match Strategy (數值容錯比對)
    try:
        # 嘗試將兩者都轉為浮點數，如果誤差極小則算對
        if abs(float(user_norm) - float(correct_norm)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError:
        pass # 無法轉為數字，可能是代數式或座標，維持字串比對結果
        
    # [Fix] 錯誤訊息優化：中文、換行顯示，去除不必要的符號
    # 這裡回傳的 result 會直接顯示在前端 Result 區域
    return {"correct": False, "result": f"答案錯誤。正確答案為：\n{correct_answer}"}



import datetime
import base64
from io import BytesIO

# 為了確保代碼不依賴全域狀態，所有輔助函式將以底線開頭。

# --- 輔助函式 (Helper Functions) ---
# 視覺化函式僅能接收「題目已知數據」，嚴禁將「答案數據」傳入。
# 若函式結果用於拼接 question_text，回傳值必須強制轉為字串 (str)。

def _format_latex_power(base, exponent):
    """
    將底數和指數格式化為 LaTeX 數學式字串。
    處理負數底數時，會用括號包起來以符合 LaTeX 語法。
    範例： _format_latex_power(-3, 2) 會回傳 r"(-3)^{2}"
    """
    if base < 0:
        base_str = r"({b})".replace("{b}", str(base))
    else:
        base_str = str(base)
    
    if exponent == 1: # 指數為 1 時通常不寫出
        return base_str
    elif exponent == 0: # 指數為 0 時，如 $a^0$
        return r"{b}^{{{e}}}".replace("{b}", base_str).replace("{e}", str(exponent))
    else:
        return r"{b}^{{{e}}}".replace("{b}", base_str).replace("{e}", str(exponent))


def _generate_random_integer(min_val, max_val, exclude=None):
    """
    在指定範圍內生成一個隨機整數，可選排除特定值。
    """
    if exclude is None:
        return random.randint(min_val, max_val)
    
    while True:
        num = random.randint(min_val, max_val)
        if num != exclude:
            return num


# --- 頂層函式 (Top-level Functions) ---
# 嚴禁使用 class 封裝。必須直接定義。

def generate(level=1):
    """
    根據指定的難度等級 (level) 生成一道整數乘方的數學題目。
    確保題型多樣性，包含至少 3 種不同的題型變體。
    """
    # 隨機分流：實作至少 3 種不同的題型變體
    problem_type = random.choice([1, 2, 3])
    
    question_text = ""
    correct_answer = ""
    answer_display = "" # 這是提供給使用者顯示的答案格式
    
    # image_base64 欄位鎖死，若無圖片則回傳空字串
    image_base64 = ""

    # --- 題型變體 1: 直接計算 (Basic Calculation) ---
    if problem_type == 1:
        type_variant = random.randint(1, 3) # 細分 3 種基本計算題型
        
        if type_variant == 1: # 直接計算單一乘方，含正負底數、零指數
            base = _generate_random_integer(-5, 5, exclude=0)
            exponent = _generate_random_integer(0, 4) # 指數範圍 0 到 4
            
            ans_val = base ** exponent
            
            # 排版與 LaTeX 安全：嚴禁 f-string，必須使用 .replace()
            power_str = _format_latex_power(base, exponent)
            template = r"請計算 $P$ 的值： $P = {power_val}$"
            question_text = template.replace("{power_val}", power_str)
            
            correct_answer = str(ans_val)
            answer_display = str(ans_val)

        elif type_variant == 2: # 計算含有負號在乘方外的情況，如 $-a^n$
            base = _generate_random_integer(2, 5)
            exponent = _generate_random_integer(2, 3) # 指數範圍 2 或 3
            
            ans_val = -(base ** exponent)
            
            # 排版與 LaTeX 安全
            power_str = r"-{b}^{{{e}}}".replace("{b}", str(base)).replace("{e}", str(exponent))
            template = r"請計算 $P$ 的值： $P = {power_val}$"
            question_text = template.replace("{power_val}", power_str)
            
            correct_answer = str(ans_val)
            answer_display = str(ans_val)

        elif type_variant == 3: # 計算多個乘方的加減運算
            base1 = _generate_random_integer(-4, 4, exclude=0)
            exp1 = _generate_random_integer(0, 3)
            base2 = _generate_random_integer(-4, 4, exclude=0)
            exp2 = _generate_random_integer(0, 3)

            # 確保兩個乘方的值不完全相同，增加題目多樣性
            while (base1 ** exp1) == (base2 ** exp2) and base1 != base2:
                 base2 = _generate_random_integer(-4, 4, exclude=0)
                 exp2 = _generate_random_integer(0, 3)
            
            op = random.choice(['+', '-'])
            
            val1 = base1 ** exp1
            val2 = base2 ** exp2
            
            if op == '+':
                ans_val = val1 + val2
            else:
                ans_val = val1 - val2
            
            # 排版與 LaTeX 安全
            power_str1 = _format_latex_power(base1, exp1)
            power_str2 = _format_latex_power(base2, exp2)
            
            template = r"請計算 $P$ 的值： $P = {power1} {op} {power2}$"
            question_text = template.replace("{power1}", power_str1)\
                                     .replace("{op}", op)\
                                     .replace("{power2}", power_str2)
            correct_answer = str(ans_val)
            answer_display = str(ans_val)

    # --- 題型變體 2: 逆向求解與比較 (Reverse Deduction & Comparison) ---
    elif problem_type == 2:
        type_variant = random.randint(1, 3)

        if type_variant == 1: # 已知乘方結果，求底數 (如 $x^2 = 36$)
            exponent = random.choice([2, 3]) # 常用指數 2 或 3
            
            if exponent == 2: # $x^2 = K$，可能有多個解 (正負)
                base_abs = _generate_random_integer(2, 6) # 底數的絕對值
                ans_val = base_abs ** exponent
                
                # 排版與 LaTeX 安全
                eq_str = r"x^{{{e}}} = {val}".replace("{e}", str(exponent)).replace("{val}", str(ans_val))
                template = r"若 ${eq_expr}$，則 $x$ 的所有可能整數值為何？"
                question_text = template.replace("{eq_expr}", eq_str)
                
                correct_answer = f"{base_abs}, -{base_abs}" # 以逗號分隔表示多個答案
                answer_display = r"${p}, {m}$".replace("{p}", str(base_abs)).replace("{m}", str(-base_abs))

            elif exponent == 3: # $x^3 = K$，只有一個解
                base = _generate_random_integer(-4, 4, exclude=0)
                ans_val = base ** exponent
                
                # 排版與 LaTeX 安全
                eq_str = r"x^{{{e}}} = {val}".replace("{e}", str(exponent)).replace("{val}", str(ans_val))
                template = r"若 ${eq_expr}$，則 $x$ 的整數值為何？"
                question_text = template.replace("{eq_expr}", eq_str)
                
                correct_answer = str(base)
                answer_display = str(base)
        
        elif type_variant == 2: # 已知底數和乘方結果，求指數 (如 $2^x = 32$)
            base = random.choice([2, 3, 4, 5])
            exponent = _generate_random_integer(2, 5)
            ans_val_power = base ** exponent
            
            # 排版與 LaTeX 安全
            eq_str = r"{b}^{{x}} = {val}".replace("{b}", str(base)).replace("{val}", str(ans_val_power))
            template = r"若 ${eq_expr}$，則 $x$ 的值為何？"
            question_text = template.replace("{eq_expr}", eq_str)
            correct_answer = str(exponent)
            answer_display = str(exponent)

        elif type_variant == 3: # 比較不同乘方的大小
            base1 = _generate_random_integer(2, 5)
            exp1 = _generate_random_integer(2, 4)
            base2 = _generate_random_integer(2, 5)
            exp2 = _generate_random_integer(2, 4)

            # 確保兩個乘方的值不相等，以進行比較
            while (base1 ** exp1) == (base2 ** exp2):
                base2 = _generate_random_integer(2, 5)
                exp2 = _generate_random_integer(2, 4)
            
            val1 = base1 ** exp1
            val2 = base2 ** exp2
            
            comparison_op = ""
            if val1 > val2:
                comparison_op = r">"
            elif val1 < val2:
                comparison_op = r"<"
            
            # 排版與 LaTeX 安全
            power_str1 = _format_latex_power(base1, exp1)
            power_str2 = _format_latex_power(base2, exp2)
            
            template = r"比較 $A = {power1}$ 和 $B = {power2}$ 的大小關係。請填入 $A > B$, $A < B$ 或 $A = B$。"
            question_text = template.replace("{power1}", power_str1)\
                                    .replace("{power2}", power_str2)
            
            correct_answer = f"A {comparison_op} B"
            answer_display = f"A {comparison_op} B"


    # --- 題型變體 3: 情境應用 (Word Problems) ---
    elif problem_type == 3:
        type_variant = random.randint(1, 3)

        if type_variant == 1: # 正方形面積 / 正方體體積
            side = _generate_random_integer(3, 10)
            
            if random.choice([True, False]): # 正方形面積
                ans_val = side ** 2
                
                # 排版與 LaTeX 安全
                template = r"一個正方形的邊長為 ${side_val}$ 公分，請問其面積是多少平方公分？"
                question_text = template.replace("{side_val}", str(side))
                correct_answer = str(ans_val)
                answer_display = str(ans_val) + " 平方公分"
            else: # 正方體體積
                ans_val = side ** 3
                
                # 排版與 LaTeX 安全
                template = r"一個正方體的邊長為 ${side_val}$ 公分，請問其體積是多少立方公分？"
                question_text = template.replace("{side_val}", str(side))
                correct_answer = str(ans_val)
                answer_display = str(ans_val) + " 立方公分"

        elif type_variant == 2: # 細菌生長 / 數量倍增問題
            initial_count = random.choice([1, 2, 5, 10])
            hours = _generate_random_integer(2, 4)
            
            ans_val = initial_count * (2 ** hours)
            
            # 排版與 LaTeX 安全
            template = r"某種細菌每小時數量會增為原來的 2 倍。如果一開始有 ${init_count}$ 隻細菌，"\
                       r"那麼 ${hours_val}$ 小時後會有多少隻細菌？"
            question_text = template.replace("{init_count}", str(initial_count))\
                                    .replace("{hours_val}", str(hours))
            correct_answer = str(ans_val)
            answer_display = str(ans_val) + " 隻"

        elif type_variant == 3: # 重複對摺 / 分割問題
            # 選擇能被 2^folds 整除的初始長度，確保結果為整數
            possible_initial_lengths = [16, 32, 64, 128, 256, 512]
            folds = _generate_random_integer(2, 4) # 對摺次數
            
            # 確保 initial_length 可以被 2^folds 整除
            initial_length = random.choice([l for l in possible_initial_lengths if l % (2 ** folds) == 0])

            ans_val = initial_length / (2 ** folds)
            
            # 排版與 LaTeX 安全
            template = r"一張長度為 ${init_len}$ 公分的紙條，每次對摺後長度會變成原來的一半。"\
                       r"如果對摺 ${folds_val}$ 次，請問紙條的長度會變成多少公分？"
            question_text = template.replace("{init_len}", str(initial_length))\
                                    .replace("{folds_val}", str(folds))
            correct_answer = str(int(ans_val)) # 強制轉為整數的字串
            answer_display = str(int(ans_val)) + " 公分"

    # --- 數據與欄位 (Standard Fields) ---
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # 提供給前端顯示的答案
        "image_base64": image_base64, # 若無圖片，則為空字串
        "created_at": datetime.datetime.now().isoformat(), # 時間戳記
        "version": "9.6", # 版本號
    }


def check(user_answer, correct_answer):
    """
    [V10.6 Standard] 支援指數題型可能出現的多重答案 (如 6, -6)
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    u = str(user_answer).strip().replace(" ", "").replace("，", ",")
    c = str(correct_answer).strip().replace(" ", "").replace("，", ",")
    
    # 處理多個答案 (例如 6,-6)
    u_list = sorted(u.split(","))
    c_list = sorted(c.split(","))
    
    if u_list == c_list:
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", str(correct_answer))}

# --- 內部測試用程式碼 (不會被納入最終系統) ---
if __name__ == '__main__':
    print("--- 正在生成整數乘方題目範例 ---")
    for i in range(10):
        problem = generate()
        print(f"--- 題目 {i+1} ---")
        print(f"  問題: {problem['question_text']}")
        print(f"  參考答案 (用於顯示): {problem['answer']}")
        print(f"  正確答案 (用於檢查): {problem['correct_answer']}")
        print(f"  建立時間: {problem['created_at']}")
        print(f"  版本: {problem['version']}")
        
        # 測試 check 函式
        test_user_answer_correct = problem['correct_answer']
        check_result = check(test_user_answer_correct, problem['correct_answer'])
        print(f"  使用正確答案 '{test_user_answer_correct}' 檢查: {check_result['is_correct']} ({check_result['result']})")

        if "," in problem['correct_answer']:
            # 測試多個答案，順序顛倒的情況
            parts = problem['correct_answer'].split(',')
            if len(parts) == 2:
                reversed_answer = f"{parts[1].strip()}, {parts[0].strip()}"
                check_result_reversed = check(reversed_answer, problem['correct_answer'])
                print(f"  使用顛倒順序答案 '{reversed_answer}' 檢查: {check_result_reversed['is_correct']} ({check_result_reversed['result']})")
            
            # 測試錯誤答案
            incorrect_answer = "99"
            check_result_incorrect = check(incorrect_answer, problem['correct_answer'])
            print(f"  使用錯誤答案 '{incorrect_answer}' 檢查: {check_result_incorrect['is_correct']} ({check_result_incorrect['result']})")
        
        print("-" * 60)

# [Auto-Injected Patch v10.3.1] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝，並強制使用中文
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # 2. [V10.3 核心修復] 解決 r-string 導致的 \n 換行失效問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            
            # 3. 確保反饋訊息也是中文 (針對 AI 可能寫出的英文進行覆蓋)
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
