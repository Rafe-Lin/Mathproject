# ==============================================================================
# ID: jh_數學1上_CostProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 30.39s | RAG: 2 examples
# Created At: 2026-01-14 20:55:56
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
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



from datetime import datetime
import base64 # 雖然此技能通常無需圖像，但依規範需導入

# --- 輔助函式通用規範 (Generic Helper Rules) ---
# 所有輔助函式皆以 '_' 開頭，表示內部使用，並明確 'return' 結果。
# 若結果用於拼接 question_text，則強制轉為字串 (str)。

def _generate_random_integer(min_val, max_val, step=1) -> int:
    """
    生成一個指定範圍和步長的隨機整數。
    - 必須回傳。
    """
    return random.randrange(min_val, max_val + 1, step)

def _generate_random_price(min_p=10, max_p=100, step=5) -> int:
    """
    生成一個隨機商品單價。
    - 必須回傳。
    """
    return _generate_random_integer(min_p, max_p, step)

def _generate_random_quantity(min_q=2, max_q=15) -> int:
    """
    生成一個隨機商品數量。
    - 必須回傳。
    """
    return _generate_random_integer(min_q, max_q)

def _generate_random_discount_factor() -> float:
    """
    生成一個常見的隨機折扣因子 (例如: 0.8, 0.85, 0.9, 0.95)。
    - 必須回傳。
    """
    return random.choice([0.8, 0.85, 0.9, 0.95])

def _format_discount_text(discount_factor: float) -> str:
    """
    將折扣因子轉換為顯示用的中文折扣字串 (例如: "八折", "九五折")。
    - 必須回傳。
    - 類型一致: 回傳值為 str，用於 question_text 拼接。
    """
    # 將浮點數轉換為整數百分比，然後再轉換為中文折扣
    discount_percent = int(discount_factor * 100)
    
    if discount_percent == 80:
        return "八折"
    elif discount_percent == 85:
        return "八五折"
    elif discount_percent == 90:
        return "九折"
    elif discount_percent == 95:
        return "九五折"
    else:
        # 應急處理，以防未來增加其他折扣因子，或生成器產生非預期值
        # 這裡假設折扣因子如0.75會顯示為"七五折"
        return str(discount_percent // 10) + str(discount_percent % 10) + "折" if discount_percent % 10 != 0 else str(discount_percent // 10) + "折"


def _calculate_total_cost(unit_price: int, quantity: int, discount_factor: float = 1.0) -> int:
    """
    計算總費用，並四捨五入到最接近的整數 (符合 K12 貨幣計算習慣)。
    - 必須回傳。
    - 防洩漏原則: 此函式僅根據已知數據計算，不涉及答案數據的洩漏。
    """
    cost = unit_price * quantity * discount_factor
    return round(cost)

# 視覺化函式: 對於費用問題，通常無需複雜的幾何圖形視覺化。
# 若未來需要，將遵循 'draw_' 開頭、僅接收已知數據、並回傳 base64 字串的規範。
# 目前 image_base64 預設為 None。

# --- 頂層函式 (程式結構: Structure Hardening) ---
# 嚴禁使用 class 封裝。直接定義函式於模組最外層。
# 確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level: int = 1) -> dict:
    """
    生成一個 K12 數學「費用問題」的題目。
    - 程式結構: 頂層函式。
    - 題型多樣性: 內部使用 random.choice 實作至少 3 種題型變體。
    - 排版與 LaTeX 安全: 嚴格使用 .replace() 模板，避免 f-string。
    - 數據與欄位: 返回字典必須且僅能包含指定欄位。
    """
    problem_type = random.choice([1, 2, 3]) # 隨機分流
    question_text = ""
    correct_answer = ""
    answer_value = None
    image_base64 = None # 此技能預設不生成圖像

    # 確保代碼不依賴全域狀態，所有變數皆為函式內部區域變數。
    unit_price = _generate_random_price()
    quantity = _generate_random_quantity()
    discount_factor = _generate_random_discount_factor()
    discount_text = _format_discount_text(discount_factor)

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 2): 直接計算 (Direct Calculation)
        # 描述: 給定單價、數量和折扣，計算總費用。
        
        final_cost = _calculate_total_cost(unit_price, quantity, discount_factor)
        answer_value = final_cost

        # 排版與 LaTeX 安全: 嚴格使用 .replace() 模板。
        q_template = r"某商品每個 {price} 元，小明購買了 {qty} 個。如果購買時享有 {discount_txt}，請問小明總共需要支付多少元？"
        question_text = q_template.replace("{price}", str(unit_price))
        question_text = question_text.replace("{qty}", str(quantity))
        question_text = question_text.replace("{discount_txt}", discount_text)
        
        correct_answer = str(answer_value)

    elif problem_type == 2:
        # Type 2 (Maps to Example 3, 4): 逆向求解 (Reverse Solving - 尋找數量或原始單價)
        # 描述: 給定總費用、折扣，以及單價或數量其中一個，要求找出另一個。
        
        sub_type = random.choice([1, 2]) # 隨機選擇逆向求解的子類型

        if sub_type == 1:
            # 逆向求解子類型 1: 尋找數量
            # 為了確保答案是整數，我們從已知的數量開始計算總價。
            base_quantity = _generate_random_quantity(min_q=3, max_q=10)
            # 確保 unit_price * discount_factor 能除盡 total_paid 以得到整數 quantity
            # 調整 unit_price 使 total_paid / (unit_price * discount_factor) 是整數
            
            # 先計算一個理論上的總價
            total_paid_raw = unit_price * base_quantity * discount_factor
            # 為了讓逆推的數量是整數，確保 total_paid_raw 能夠被 (unit_price * discount_factor) 整除
            # 如果 discount_factor 是小數，這會複雜。最簡單的方式是確保 unit_price 乘以 discount_factor 後是整數
            # 為了簡化，我們直接讓 _calculate_total_cost 處理，並假設 round() 造成的誤差在逆推時可忽略
            # 或者，更嚴謹的做法是調整 unit_price 或 discount_factor 讓 `unit_price * discount_factor` 為整數
            
            # 方法一：讓 unit_price * discount_factor 為整數
            # 選擇 unit_price 讓 unit_price * discount_factor 是一個方便的數
            # 例如，如果 discount_factor 是 0.8，則 unit_price 選擇 10 的倍數
            # 如果 discount_factor 是 0.85，則 unit_price 選擇 20 的倍數 (0.85 = 17/20)
            
            # 重新生成 unit_price 和 discount_factor，確保 product 是整數
            # 考慮 discount_factor 可能是 0.8, 0.85, 0.9, 0.95 (即 4/5, 17/20, 9/10, 19/20)
            # 最小公倍數是 20。所以讓 unit_price 是 20 的倍數會比較保險。
            adjusted_unit_price = _generate_random_price(min_p=20, max_p=120, step=20)
            adjusted_discount_factor = _generate_random_discount_factor()
            adjusted_discount_text = _format_discount_text(adjusted_discount_factor)

            total_paid = _calculate_total_cost(adjusted_unit_price, base_quantity, adjusted_discount_factor)
            
            # 檢查逆推是否為整數
            # 由於 _calculate_total_cost 做了 round，直接逆推可能會不精確
            # 為了保證答案精確為 base_quantity，我們需要確保 total_paid / (adjusted_unit_price * adjusted_discount_factor) 是整數
            # 最佳方式是讓 (adjusted_unit_price * adjusted_discount_factor) 乘積為整數
            
            # 確保 adjusted_unit_price * adjusted_discount_factor 是一個整數
            # 例如，如果 discount_factor 是 0.85 (17/20)，unit_price 必須是 20 的倍數
            # 如果 discount_factor 是 0.9 (9/10)，unit_price 必須是 10 的倍數
            
            # Let's adjust the generation for robustness
            while True:
                temp_unit_price = _generate_random_price(min_p=20, max_p=120, step=10) # 10的倍數
                temp_discount_factor = _generate_random_discount_factor()
                
                # 檢查 temp_unit_price * temp_discount_factor 是否接近整數
                effective_unit_price_raw = temp_unit_price * temp_discount_factor
                if abs(effective_unit_price_raw - round(effective_unit_price_raw)) < 1e-6:
                    unit_price = temp_unit_price
                    discount_factor = temp_discount_factor
                    discount_text = _format_discount_text(discount_factor)
                    break

            total_paid = _calculate_total_cost(unit_price, base_quantity, discount_factor)
            answer_value = base_quantity # 這是學生需要找出的答案

            q_template = r"某商品每個 {price} 元。小華購買了若干個，並享有 {discount_txt}。他總共支付了 {paid_amount} 元，請問小華購買了多少個商品？"
            question_text = q_template.replace("{price}", str(unit_price))
            question_text = question_text.replace("{discount_txt}", discount_text)
            question_text = question_text.replace("{paid_amount}", str(total_paid))
            
            correct_answer = str(answer_value)

        elif sub_type == 2:
            # 逆向求解子類型 2: 尋找原始單價
            # 同樣為確保答案是整數，從已知的單價開始計算總價。
            
            # 確保 base_unit_price * discount_factor * quantity 是整數 (或 round 後是整數)
            # 同樣調整 unit_price 和 discount_factor
            while True:
                temp_base_unit_price = _generate_random_price(min_p=20, max_p=150, step=10) # 10的倍數
                temp_quantity = _generate_random_quantity(min_q=2, max_q=10)
                temp_discount_factor = _generate_random_discount_factor()
                
                # 檢查 temp_base_unit_price * temp_discount_factor 是否接近整數
                effective_unit_price_raw = temp_base_unit_price * temp_discount_factor
                if abs(effective_unit_price_raw - round(effective_unit_price_raw)) < 1e-6:
                    base_unit_price = temp_base_unit_price
                    quantity = temp_quantity
                    discount_factor = temp_discount_factor
                    discount_text = _format_discount_text(discount_factor)
                    break

            total_paid = _calculate_total_cost(base_unit_price, quantity, discount_factor)
            answer_value = base_unit_price # 這是學生需要找出的答案

            q_template = r"小李購買了 {qty} 個商品，並享有 {discount_txt}。他總共支付了 {paid_amount} 元，請問每個商品的原始價格是多少元？"
            question_text = q_template.replace("{qty}", str(quantity))
            question_text = question_text.replace("{discount_txt}", discount_text)
            question_text = question_text.replace("{paid_amount}", str(total_paid))
            
            correct_answer = str(answer_value)

    elif problem_type == 3:
        # Type 3 (Maps to Example 5, 6): 情境應用 (Contextual Application - 比較不同方案)
        # 描述: 比較兩種不同的購買方案或商店的費用，找出最便宜的或費用差異。
        
        shop_a_unit_price = _generate_random_price(min_p=50, max_p=200, step=10)
        shop_a_discount_factor = _generate_random_discount_factor()
        shop_a_discount_text = _format_discount_text(shop_a_discount_factor)

        # 確保 Shop B 的折扣與 Shop A 不同，以增加比較性。
        possible_b_discounts = [df for df in [0.8, 0.85, 0.9, 0.95] if df != shop_a_discount_factor]
        if not possible_b_discounts: # 如果只剩一種折扣因子，則隨機選一個不同的值 (極少發生)
            # 為了確保不同，可以稍微調整折扣因子，但要確保 _format_discount_text 能夠處理
            # 這裡簡單隨機選一個，並假設 _format_discount_text 處理非標準值
            shop_b_discount_factor = random.choice([0.7, 0.75, 0.82, 0.92, 0.98]) 
        else:
            shop_b_discount_factor = random.choice(possible_b_discounts)
        
        shop_b_unit_price = shop_a_unit_price # 為公平比較，兩家店單價相同
        shop_b_discount_text = _format_discount_text(shop_b_discount_factor)

        compare_quantity = _generate_random_quantity(min_q=5, max_q=20) # 學生購買的數量

        cost_a = _calculate_total_cost(shop_a_unit_price, compare_quantity, shop_a_discount_factor)
        cost_b = _calculate_total_cost(shop_b_unit_price, compare_quantity, shop_b_discount_factor)

        # 問題要求: "在A店購買會比在B店購買便宜多少元？ (若B店便宜，則為負數)"
        # 這樣答案為數值，符合 correct_answer 的常見格式。
        answer_value = cost_b - cost_a 

        q_template = r"小芳想購買 {qty} 個相同的商品。A店每個商品 {price_a} 元，並享有 {discount_txt_a}。B店每個商品 {price_b} 元，並享有 {discount_txt_b}。請問在A店購買會比在B店購買便宜多少元？(請填寫數值，若B店較便宜請填寫負數)"
        question_text = q_template.replace("{qty}", str(compare_quantity))
        question_text = question_text.replace("{price_a}", str(shop_a_unit_price))
        question_text = question_text.replace("{discount_txt_a}", shop_a_discount_text)
        question_text = question_text.replace("{price_b}", str(shop_b_unit_price))
        question_text = question_text.replace("{discount_txt_b}", shop_b_discount_text)
        
        correct_answer = str(answer_value)

    # --- 數據與欄位 (Standard Fields) ---
    # 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    # created_at 設為 datetime.now() 並遞增 version。
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_value, # 原始數值答案
        "image_base64": image_base64, # 目前為 None
        "created_at": datetime.now().isoformat(), # 時間戳記
        "version": "1.0", # 版本號
    }

# check 函數根據規範【絕對禁令】嚴禁自定義，系統會自動注入 V10.6 鎖死版工具庫。

# --- 測試案例 (僅供開發驗證，不屬於最終部署程式碼) ---
if __name__ == "__main__":
    print("--- 費用問題 Coder Spec 測試執行 ---")
    for i in range(5):
        problem_data = generate(level=1)
        print(f"\n--- 問題 {i+1} ---")
        print(f"問題文本: {problem_data['question_text']}")
        print(f"正確答案 (字串): {problem_data['correct_answer']}")
        print(f"正確答案 (數值): {problem_data['answer']}")
        print(f"建立時間: {problem_data['created_at']}")
        print(f"版本: {problem_data['version']}")
        print(f"圖像 Base64: {problem_data['image_base64']}")
        print("-" * 30)

    # 模擬 LaTeX 安全檢查的嚴格性 (此技能問題本身不含複雜 LaTeX，但仍需遵守規範)
    ans_val_example = 10
    # 錯誤範例 (嚴禁): expr_bad = f"求 $x$ 的值: $x = \\frac{{ans_val_example}}{2}$"
    expr_template_good = r"求 $x$ 的值: $x = \frac{{{a}}}{2}$"
    expr_good = expr_template_good.replace("{a}", str(ans_val_example))
    print(f"\nLaTeX 安全排版範例 (正確): {expr_good}")
    # 嚴禁使用 \par 或 \[...\]，所有數學式一律使用 $...$
    print(r"數學式一律使用 $A = \pi r^2$ 而非 \[ A = \pi r^2 \]")


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
