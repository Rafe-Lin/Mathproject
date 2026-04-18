# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfIntegers
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 25.68s | RAG: 5 examples
# Created At: 2026-01-14 13:43:00
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
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{rem}}{{den}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{rem}", str(rem_num)).replace("{den}", str(abs_num.denominator))
        return r"\frac{{num}}{{den}}".replace("{num}", str(num.numerator)).replace("{den}", str(num.denominator))
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
        return r" - {v}".replace("{v}", abs_val) if is_neg else r" + {v}".replace("{v}", abs_val)
    
    if signed:
        # e.g., "+3", "-3"
        return r"-{v}".replace("{v}", abs_val) if is_neg else r"+{v}".replace("{v}", abs_val)
        
    # Default behavior (parentheses for negative)
    if is_neg: return r"({v})".replace("{v}", latex_val)
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



import datetime
 # For abs() if needed, but direct comparison abs(num) is fine
import base64 # Required for image_base64, even if empty

# --- 輔助函式 (Helper Functions) ---

# 規範 4: 必須回傳結果, 規範 3: LaTeX 安全排版
# 確保負數在 LaTeX 環境中被括號包圍，如 $(-5)$
def _format_num_latex_safe(num):
    """
    將數字格式化為 LaTeX 安全的字串。
    負數會被括號包圍，例如 -5 會變成 `( -5 )`。
    正數和零則直接轉換為字串。
    嚴格遵循規範 3，使用 .replace() 避免 f-string 衝突。
    """
    if num < 0:
        # 規範 3: 嚴禁 f-string，必須使用 .replace()
        formatted_str = r"( {val} )".replace("{val}", str(num))
        return formatted_str
    # 規範 4: 回傳值強制轉為字串
    return str(num)

# --- 頂層函式 (Top-Level Functions) ---

# 規範 1: 嚴禁使用 class 封裝，必須直接定義於模組最外層
def generate(level=1):
    """
    根據「整數的四則運算」技能，生成一道數學題目。
    包含多種題型變體，並嚴格遵守 LaTeX 排版和數據規範。

    Args:
        level (int): 題目難度等級 (此版本中暫未實作等級差異，預設為1)。

    Returns:
        dict: 包含題目文本、正確答案、答案字串、圖片Base64等資訊的字典。
              規範 5: 欄位鎖死。
    """
    # 規範 2: 隨機分流，至少 3 種不同的題型變體
    problem_type = random.choice([
        "direct_calculation",      # 直接計算
        "inverse_solving",         # 逆向求解
        "contextual_application"   # 情境應用
    ])

    question_text = ""
    correct_answer = None
    
    # 規範 5: image_base64 欄位必須存在，即使為空字串
    # 規範 4: 防洩漏原則，視覺化函式僅能接收「題目已知數據」，嚴禁傳入「答案數據」
    # 此技能目前沒有複雜的視覺化需求，故為空字串。
    image_base64 = ""

    if problem_type == "direct_calculation":
        # 題型變體 1: 直接計算 (Direct Calculation)
        # 例如：計算 $(-5) + 3 \times (-2) - 10 \div 2$ 的值。
        
        # 初始化起始值
        current_val = random.randint(-20, 20)
        
        # 規範 3: 所有數學式一律使用 $...$
        # 規範 3: 嚴格執行 .replace() 模板
        expression_display_parts = [_format_num_latex_safe(current_val)]
        
        num_operations = random.randint(2, 3) # 增加 2 到 3 個運算
        
        for _ in range(num_operations):
            op = random.choice(['+', '-', '*', '/'])
            next_val = random.randint(-15, 15) # 潛在的下一個運算數
            
            # 確保除法結果為整數，並避免除以零
            if op == '/':
                # 策略：如果 current_val 是 0，除數可以是任何非零數。
                # 如果 current_val 不是 0，則尋找其因數作為除數。
                if current_val == 0:
                    while next_val == 0:
                        next_val = random.randint(-15, 15)
                else:
                    # 尋找 current_val 的非零因數
                    # 考慮到 next_val 範圍是 -15 到 15，因此只尋找此範圍內的因數
                    divisors = [d for d in range(-15, 16) if d != 0 and current_val % d == 0]
                    if not divisors:
                        # 備用方案：如果範圍內沒有合適的整數因數，則改變運算符
                        # 為了簡化，直接將運算符改為非除法
                        op = random.choice(['+', '-', '*']) 
                        next_val = random.randint(-15, 15) # 重新選擇 next_val
                    else:
                        next_val = random.choice(divisors) # 從因數中隨機選擇一個作為除數
            
            # 規範 3: 數學符號的 LaTeX 顯示，並使用 .replace()
            op_display = op
            if op == '*':
                op_display = r"\times"
            elif op == '/':
                op_display = r"\div"
            
            # 規範 3: 嚴格執行 .replace() 模板來構建顯示部分
            display_part = r" {op_display} {operand_str} ".replace("{op_display}", op_display) \
                                                          .replace("{operand_str}", _format_num_latex_safe(next_val))
            expression_display_parts.append(display_part)
            
            # 根據運算符更新 current_val
            if op == '+':
                current_val += next_val
            elif op == '-':
                current_val -= next_val
            elif op == '*':
                current_val *= next_val
            elif op == '/':
                current_val //= next_val # 使用整數除法

        correct_answer = current_val # 最終計算結果
        
        # 規範 3: 構建完整的題目文本，所有數學式一律使用 $...$
        # 規範 3: 嚴格執行 .replace() 模板
        question_text_base = r"計算下列各式的值："
        question_expr = r"$ {expression} $".replace("{expression}", "".join(expression_display_parts))
        question_text = r"{intro} {expr}".replace("{intro}", question_text_base).replace("{expr}", question_expr)

    elif problem_type == "inverse_solving":
        # 題型變體 2: 逆向求解 (Inverse Solving)
        # 例如：「某數 $x$ 加上 $( -7 )$ 後得到 $15$，求此數 $x$。」
        
        x = random.randint(-20, 20) # 待求的未知數 x
        op = random.choice(['+', '-', '*']) # 選擇加、減、乘運算
        
        operand_b = random.randint(-15, 15)
        
        result_val = 0
        question_template = ""

        if op == '+':
            result_val = x + operand_b
            # x + B = R => x = R - B
            question_template = r"某數 $x$ 加上 {operand_b_str} 後得到 {result_str}，求此數 $x$。"
            
        elif op == '-':
            result_val = x - operand_b
            # x - B = R => x = R + B
            question_template = r"某數 $x$ 減去 {operand_b_str} 後得到 {result_str}，求此數 $x$。"
            
        elif op == '*':
            # 確保乘法逆向求解時，結果能被 operand_b 整除，以得到整數 x
            operand_b = random.randint(-5, 5)
            while operand_b == 0: # 避免乘數為零
                operand_b = random.randint(-5, 5)
            
            x = random.randint(-10, 10) # 重新生成未知數 x
            result_val = x * operand_b
            
            # x * B = R => x = R / B
            question_template = r"某數 $x$ 乘以 {operand_b_str} 後得到 {result_str}，求此數 $x$。"
            
        # 規範 3: 嚴格執行 .replace() 模板來構建題目文本
        question_text = question_template \
            .replace("{operand_b_str}", _format_num_latex_safe(operand_b)) \
            .replace("{result_str}", _format_num_latex_safe(result_val))
            
        correct_answer = x

    elif problem_type == "contextual_application":
        # 題型變體 3: 情境應用 (Contextual Application)
        # 例如：氣溫變化、海拔高度、銀行帳戶餘額等。
        
        scenario = random.choice(["temperature", "elevation", "money"])
        
        if scenario == "temperature":
            initial_temp = random.randint(-10, 10) # 清晨氣溫
            change1_val = random.randint(-15, 15) # 第一次變化 (可升可降)
            change2_val = random.randint(-15, 15) # 第二次變化
            
            final_temp = initial_temp + change1_val + change2_val
            
            # 規範 3: 嚴格執行 .replace() 模板
            question_template = r"某城市清晨的氣溫是 {initial_temp_str} 度。中午時 {change1_action} 了 {change1_abs_str} 度，傍晚又 {change2_action} 了 {change2_abs_str} 度。請問傍晚的氣溫是多少度？"
            
            change1_action = r"上升" if change1_val >= 0 else r"下降"
            change2_action = r"上升" if change2_val >= 0 else r"下降"
            
            change1_abs_str = str(abs(change1_val))
            change2_abs_str = str(abs(change2_val))

            question_text = question_template \
                .replace("{initial_temp_str}", _format_num_latex_safe(initial_temp)) \
                .replace("{change1_action}", change1_action) \
                .replace("{change1_abs_str}", change1_abs_str) \
                .replace("{change2_action}", change2_action) \
                .replace("{change2_abs_str}", change2_abs_str)
            
            correct_answer = final_temp
        
        elif scenario == "elevation":
            initial_elevation = random.randint(-50, 50) # 初始海拔 (海平面以上/下)
            climb_val = random.randint(10, 30) # 上升距離
            descend_val = random.randint(10, 30) # 下潛距離
            
            # 隨機決定上升/下潛的順序
            if random.choice([True, False]):
                final_elevation = initial_elevation + climb_val - descend_val
                question_template = r"某潛水艇一開始在海平面 {initial_elevation_str} 公尺處。它先上升 {climb_str} 公尺，然後又下潛 {descend_str} 公尺。請問潛水艇最終在海平面多少公尺處？"
            else:
                final_elevation = initial_elevation - descend_val + climb_val
                question_template = r"某潛水艇一開始在海平面 {initial_elevation_str} 公尺處。它先下潛 {descend_str} 公尺，然後又上升 {climb_str} 公尺。請問潛水艇最終在海平面多少公尺處？"
            
            # 規範 3: 嚴格執行 .replace() 模板
            question_text = question_template \
                .replace("{initial_elevation_str}", _format_num_latex_safe(initial_elevation)) \
                .replace("{climb_str}", str(climb_val)) \
                .replace("{descend_str}", str(descend_val))
            
            correct_answer = final_elevation

        elif scenario == "money":
            initial_balance = random.randint(100, 500) # 初始餘額
            deposit1_val = random.randint(50, 200) # 第一次存入
            withdrawal1_val = random.randint(20, 100) # 第一次提領
            deposit2_val = random.randint(30, 150) # 第二次存入
            
            final_balance = initial_balance + deposit1_val - withdrawal1_val + deposit2_val
            
            # 規範 3: 嚴格執行 .replace() 模板
            question_template = r"小明銀行帳戶裡原有 {initial_balance_str} 元。他先存入 {deposit1_str} 元，然後提領 {withdrawal1_str} 元，最後又存入 {deposit2_str} 元。請問小明帳戶裡現在有多少元？"
            
            question_text = question_template \
                .replace("{initial_balance_str}", str(initial_balance)) \
                .replace("{deposit1_str}", str(deposit1_val)) \
                .replace("{withdrawal1_str}", str(withdrawal1_val)) \
                .replace("{deposit2_str}", str(deposit2_val))
            
            correct_answer = final_balance

    # 確保 correct_answer 是整數 (此技能為整數運算)
    if not isinstance(correct_answer, int):
        correct_answer = int(correct_answer)

    # 規範 5: 返回字典必須且僅能包含指定欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": str(correct_answer), # 規範 5: 答案的字串表示
        "image_base64": image_base64, # 規範 5: 圖片 Base64 (此處為空)
        "created_at": datetime.datetime.now().isoformat(), # 規範 5: 時間戳記
        "version": "9.6" # 規範 5: 版本號
    }

# 規範 1: 嚴禁使用 class 封裝，必須直接定義於模組最外層
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    u = str(user_answer).strip().replace(" ", "").replace("，", ",")

    # 處理「商,餘數」格式 (針對 IntegerDivision)
    if isinstance(correct_answer, dict) and "quotient" in correct_answer:
        ans_display = r"{q},{r}".replace("{q}", str(correct_answer["quotient"])).replace("{r}", str(correct_answer["remainder"]))
        try:
            u_q_r = u.replace("商", "").replace("餘", ",").split(",")
            if int(u_q_r[0]) == int(correct_answer["quotient"]) and int(u_q_r[1]) == int(correct_answer["remainder"]):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(correct_answer).strip()
    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", ans_display)} 

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤。'}
        if isinstance(res, dict):
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤。'
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
