# ==============================================================================
# ID: jh_數學1上_IntegerMultiplication
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 25.54s | RAG: 5 examples
# Created At: 2026-01-14 09:45:10
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
#==============================================================================


import random
import math
import matplotlib
# [Fix] Font injection for Traditional Chinese support
matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
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
    if n <= 1: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
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
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}


import datetime
#  # Not strictly needed for this skill, as noted, so can be removed for minimal imports.

# --- 輔助函式通用規範 (Generic Helper Rules) ---
# 此輔助函式已在原始規範中提供，並符合「程式結構」中不使用 class 封裝的要求。
# 根據「FINAL CHECK: NO help functions definition」的嚴格解讀，如果這意味著除了 generate 和 check 之外
# 任何其他函式都不能存在，那麼此函式應該被內聯。
# 然而，它被明確定義為「輔助函式通用規範」的一部分，且「程式結構」部分也允許模組級別的函式。
# 我將其視為允許的通用輔助函式，因為它減少了 generate 內部重複的邏輯並提高了可讀性。
# 如果「NO help functions definition」是絕對的，則此函式需被移除並將邏輯內聯。
# 考量到原始規範提供了此函式，我將保留它。

def _format_number_for_latex(num: int) -> str:
    """
    將整數格式化為 LaTeX 字串，負數會加上括號。
    例如：-5 轉換為 (-5)，3 轉換為 3。
    """
    if num < 0:
        return r"({})".format(str(num))
    return str(num)

# --- 程式結構 (Structure Hardening) ---
# 嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# 確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level: int = 1) -> dict:
    """
    根據指定難度等級生成一道整數乘法運算題目。

    Args:
        level (int): 難度等級，1 表示基礎，數字越大難度越高。

    Returns:
        dict: 包含題目文本、正確答案、答案格式、Base64 圖片（如果有的話）的字典。
        遵循 {'question_text': str, 'answer': str, 'correct_answer': str, 'image_base64': str} 嚴格格式。
    """
    # 根據難度設定數字範圍
    if level == 1:
        num_range_min = -10
        num_range_max = 10
        # 避免過於簡單的 0 乘法在基礎題中頻繁出現
        non_zero_range = [-10, -1] + [1, 10]
    elif level == 2:
        num_range_min = -20
        num_range_max = 20
        non_zero_range = [-20, -1] + [1, 20]
    else: # level >= 3
        num_range_min = -30
        num_range_max = 30
        non_zero_range = [-30, -1] + [1, 30]

    problem_type = random.choice(["direct_calculation", "inverse_problem", "contextual_application"])

    question_text = ""
    correct_answer_int = None # 內部計算使用 int
    answer_display = ""

    # 題型多樣性 (Problem Variety)
    if problem_type == "direct_calculation":
        # 題型1: 直接計算
        num1 = random.randint(num_range_min, num_range_max)
        num2 = random.randint(num_range_min, num_range_max)

        # 確保不會出現 0 * 0 的情況，除非是高難度或特殊設計
        if num1 == 0 and num2 == 0:
            num1 = random.choice(non_zero_range)
        elif num1 == 0: # 確保至少有一個非零數在非零範圍內
            num2 = random.choice(non_zero_range)
        elif num2 == 0:
            num1 = random.choice(non_zero_range)

        correct_answer_int = num1 * num2
        
        # 排版與 LaTeX 安全 (Elite Guardrails) - 強制語法零修復 (Regex=0)
        # 嚴禁使用 f-string 或 % 格式化。必須嚴格執行以下模板。
        formatted_num1 = _format_number_for_latex(num1)
        formatted_num2 = _format_number_for_latex(num2)
        
        question_template = r"${a} \times {b} = ?$"
        question_text = question_template.replace("{a}", formatted_num1).replace("{b}", formatted_num2)
        answer_display = str(correct_answer_int)

    elif problem_type == "inverse_problem":
        # 題型2: 逆向求解（已知積與一個因數，求另一個因數）
        # 確保因數不為 0，避免除以 0
        factor1 = random.choice(non_zero_range)
        factor2 = random.choice(non_zero_range)
        
        product = factor1 * factor2
        
        # 隨機決定哪個因數是未知數 x
        if random.choice([True, False]): # x * factor2 = product
            known_factor = factor2
            correct_answer_int = factor1
            
            formatted_known_factor = _format_number_for_latex(known_factor)
            formatted_product = str(product)
            
            question_template = r"$x \times {b} = {c}$"
            question_text = question_template.replace("{b}", formatted_known_factor).replace("{c}", formatted_product)
        else: # factor1 * x = product
            known_factor = factor1
            correct_answer_int = factor2
            
            formatted_known_factor = _format_number_for_latex(known_factor)
            formatted_product = str(product)
            
            question_template = r"${a} \times x = {c}$"
            question_text = question_template.replace("{a}", formatted_known_factor).replace("{c}", formatted_product)
        
        answer_display = str(correct_answer_int)

    else: # contextual_application
        # 題型3: 情境應用（如移動點、溫度變化、資產變動等）
        scenario_type = random.choice([
            "temperature",
            "elevation",
            "money_loss",
            "score_change"
        ])

        if scenario_type == "temperature":
            change_per_unit = random.randint(num_range_min // 2, num_range_max // 2) # 溫度變化量較小
            if change_per_unit == 0: change_per_unit = random.choice([-2, 2]) # 避免變化為0
            
            num_units = random.randint(2, 7) # 例如天數或小時數

            if change_per_unit > 0:
                action = "上升"
            else:
                action = "下降"
            
            # 使用 .replace() 模板
            text_template = r"某城市氣溫每天{action} {change} 攝氏度。請問 {units} 天後，氣溫總共會變化多少攝氏度？"
            question_text = text_template.replace("{action}", action).replace("{change}", str(abs(change_per_unit))).replace("{units}", str(num_units))
            
            correct_answer_int = change_per_unit * num_units
            answer_display = str(correct_answer_int) + r" 攝氏度"

        elif scenario_type == "elevation":
            change_per_unit = random.randint(num_range_min * 2, num_range_max * 2) # 變化量可能較大
            if change_per_unit == 0: change_per_unit = random.choice([-5, 5])
            
            num_units = random.randint(3, 10) # 例如分鐘數

            if change_per_unit > 0:
                action = "上升"
            else:
                action = "下降"
            
            text_template = r"一潛水艇以每分鐘 {change} 公尺的速度{action}。請問 {units} 分鐘後，它的位置會變化多少公尺？"
            question_text = text_template.replace("{action}", action).replace("{change}", str(abs(change_per_unit))).replace("{units}", str(num_units))
            
            correct_answer_int = change_per_unit * num_units
            answer_display = str(correct_answer_int) + r" 公尺"

        elif scenario_type == "money_loss":
            loss_per_item = random.randint(5, 20) * -1 # 損失為負數
            num_items = random.randint(5, 15)

            text_template = r"某公司每賣出一件商品虧損 {loss} 元。如果賣出 {items} 件商品，總共會虧損多少元？"
            question_text = text_template.replace("{loss}", str(abs(loss_per_item))).replace("{items}", str(num_items))
            
            correct_answer_int = loss_per_item * num_items
            answer_display = str(correct_answer_int) + r" 元"

        elif scenario_type == "score_change":
            change_per_round = random.randint(-10, 10)
            if change_per_round == 0: change_per_round = random.choice([-3, 3])
            
            num_rounds = random.randint(3, 8)

            if change_per_round > 0:
                action_word = "增加"
            else:
                action_word = "減少"
            
            text_template = r"小明在一個遊戲中，每回合得分 {action} {points} 分。如果他玩了 {rounds} 回合，他的總得分會變化多少分？"
            question_text = text_template.replace("{action}", action_word).replace("{points}", str(abs(change_per_round))).replace("{rounds}", str(num_rounds))
            
            correct_answer_int = change_per_round * num_rounds
            answer_display = str(correct_answer_int) + r" 分"

    # 視覺化與輔助函式通用規範 - 防洩漏原則：視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
    # 對於整數乘法，通常不需要複雜的視覺化圖形，因此 image_base64 留空。
    # 嚴格遵循 INFRASTRUCTURE RULES: NO matplotlib.pyplot, image_base64 留空。
    image_base64 = ""

    # 數據與欄位 (Standard Fields)
    # 遵循 INFRASTRUCTURE RULES Return Format (NO EXCEPTIONS):
    # generate() MUST return a dict: {'question_text': str, 'answer': str, 'correct_answer': str, 'image_base64': str}.
    # correct_answer 必須是 str。
    return {
        "question_text": question_text,
        "correct_answer": str(correct_answer_int), # 轉換為 str
        "answer": answer_display,
        "image_base64": image_base64,
        # 移除 'created_at' 和 'version' 欄位，以嚴格符合 generate() 的回傳格式規範。
    }

def check(user_answer: str, correct_answer: str) -> dict:
    """
    檢查用戶答案是否正確。

    Args:
        user_answer (str): 用戶提交的答案字串。
        correct_answer (str): 系統計算的正確答案字串。

    Returns:
        dict: 遵循 {'correct': bool, 'result': str} 嚴格格式。
    """
    try:
        # 清理用戶答案，移除可能的情境題單位，只留下數字部分進行比較。
        # 這裡假設用戶在情境題中只輸入數字，或系統會預處理。
        # 如果用戶輸入如 "10 攝氏度"，則需要更複雜的解析。
        # 目前的 check 僅處理純數字字串。
        user_answer_cleaned = user_answer.strip()
        
        # 嘗試從 correct_answer 中提取數字部分，以處理情境題中的單位
        # 例如 "10 攝氏度" -> "10"
        correct_answer_num_str = correct_answer.split(' ')[0]

        user_answer_int = int(user_answer_cleaned)
        correct_answer_int = int(correct_answer_num_str)

        if user_answer_int == correct_answer_int:
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
    except ValueError:
        return {"correct": False, "result": "格式錯誤，請輸入整數。"}

# 為了測試方便，可以在此添加一些調試代碼
if __name__ == '__main__':
    print("--- 整數的乘法運算題目生成測試 ---")
    for i in range(1, 4):
        print(f"\n--- Level {i} ---")
        for _ in range(5): # 生成5道題目
            problem = generate(level=i)
            print(f"題目: {problem['question_text']}")
            print(f"正確答案: {problem['correct_answer']} (顯示: {problem['answer']})")
            
            # 模擬檢查答案
            # 為了符合 check 函式預期，從 problem['correct_answer'] 中提取數字部分
            # 這是因為 generate 的 'correct_answer' 是一個純數字字串，而 'answer' 可能是帶單位的。
            # check 函式現在內部會處理從 'correct_answer' 中提取數字。
            test_user_answer_correct = problem['correct_answer']
            
            # 模擬一個錯誤答案，例如在正確答案上加 1
            # 注意：如果 correct_answer 是 "10 攝氏度"，這裡需要更複雜的處理
            try:
                wrong_answer_int = int(problem['correct_answer']) + 1
                test_user_answer_wrong = str(wrong_answer_int)
            except ValueError:
                # 如果 correct_answer 帶單位，我們就簡單給一個明顯錯誤的數字
                test_user_answer_wrong = "9999" 
            
            print(f"檢查 (正確): {check(test_user_answer_correct, problem['correct_answer'])}")
            print(f"檢查 (錯誤): {check(test_user_answer_wrong, problem['correct_answer'])}")
            print("-" * 20)

    print("\n--- 邊緣案例測試 ---")
    problem_zero_mult = generate(level=1)
    # 嘗試生成一個包含 0 的乘法，確保不是 0*0
    problem_zero_mult['question_text'] = r"$0 \times 5 = ?$"
    problem_zero_mult['correct_answer'] = "0"
    problem_zero_mult['answer'] = "0"
    print(f"題目: {problem_zero_mult['question_text']}")
    print(f"正確答案: {problem_zero_mult['correct_answer']} (顯示: {problem_zero_mult['answer']})")
    print(f"檢查 (正確): {check('0', '0')}")
    print(f"檢查 (錯誤): {check('1', '0')}")
    print("-" * 20)

    problem_negative_latex = generate(level=1)
    problem_negative_latex['question_text'] = r"$(-5) \times 3 = ?$"
    problem_negative_latex['correct_answer'] = "-15"
    problem_negative_latex['answer'] = "-15"
    print(f"題目: {problem_negative_latex['question_text']}")
    print(f"正確答案: {problem_negative_latex['correct_answer']} (顯示: {problem_negative_latex['answer']})")
    print(f"檢查 (正確): {check('-15', '-15')}")
    print(f"檢查 (錯誤): {check('15', '-15')}")
    print("-" * 20)

    problem_context_with_unit = generate(level=3)
    problem_context_with_unit['question_text'] = r"一潛水艇以每分鐘 10 公尺的速度下降。請問 5 分鐘後，它的位置會變化多少公尺？"
    problem_context_with_unit['correct_answer'] = "-50"
    problem_context_with_unit['answer'] = "-50 公尺"
    print(f"題目: {problem_context_with_unit['question_text']}")
    print(f"正確答案: {problem_context_with_unit['correct_answer']} (顯示: {problem_context_with_unit['answer']})")
    print(f"檢查 (正確, 數字): {check('-50', problem_context_with_unit['correct_answer'])}")
    print(f"檢查 (錯誤, 數字): {check('50', problem_context_with_unit['correct_answer'])}")
    print(f"檢查 (錯誤, 帶單位): {check('-50 公尺', problem_context_with_unit['correct_answer'])}") # 根據目前的 check 邏輯，帶單位會因 int() 轉換失敗
    print(f"檢查 (錯誤, 無法轉換): {check('abc', problem_context_with_unit['correct_answer'])}")
    print("-" * 20)

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
