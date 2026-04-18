import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「對數的定義」相關題目。
    包含：
    1. 求 log_a b 的值，其中 b 是 a 的整數次方。
    2. 求 log_a b 的值，其中 b 是 a 的負整數次方或 0 次方。
    3. 求 log_a b 的值，其中 b 是 a 的分數次方 (可能包含根號表示)。
    """
    
    # 目前僅專注於一種題型：求對數的值
    return generate_logarithm_value_problem(level)

def generate_logarithm_value_problem(level):
    base_choices = [2, 3, 4, 5, 7, 10]
    
    # Level 1: 結果為正整數指數
    if level == 1:
        base = random.choice([2, 3, 5]) # 選擇較小的底數
        exponent = random.randint(1, 4) # 正整數指數
        correct_answer_val = exponent
        b_val = base**exponent
        b_display = str(b_val)
        
    # Level 2: 結果包含負整數和零指數
    elif level == 2:
        base = random.choice(base_choices)
        exponent = random.randint(-3, 3) # 包含 -3, -2, -1, 0, 1, 2, 3
        correct_answer_val = exponent
        b_val = base**exponent
        
        if exponent < 0:
            # 負指數表示為分數形式，例如 1/9
            b_display = r"\\frac{{1}}{{{base}^{{{abs(exponent)}}}}}"
        elif exponent == 0:
            b_display = "1"
        else: # 正指數
            b_display = str(b_val)
            
    # Level 3: 結果為分數指數 (可能涉及根號)
    elif level == 3:
        # 題型選擇: 
        # 1. log_a K，其中 K 是 a 的某個分數次方，且 K 最終簡化為整數或簡單分數
        # 2. log_a (a^m * root(a))，b 直接以根號形式給出
        choice = random.choice(['integer_or_fraction_result', 'root_form'])
        
        if choice == 'integer_or_fraction_result':
            # 為了確保 b 值是整數或簡單分數，選擇一個底數是某個整數的平方或立方
            possible_roots = [2, 3, 4, 5]
            denominator = random.choice([2, 3]) # 僅考慮平方根或立方根
            
            if denominator == 2: # 底數為某數的平方
                root_base = random.choice(possible_roots)
                base = root_base**2 # 例如: 4, 9, 16, 25
            else: # 底數為某數的立方
                root_base = random.choice(possible_roots[:3]) # 例如: 2, 3, 4
                base = root_base**3 # 例如: 8, 27, 64
            
            numerator = random.randint(-3, 4)
            # 避免分子為0，因為 log_a 1 已經在 Level 2 處理，且此處通常需要非零分數指數
            if numerator == 0: 
                numerator = random.choice([-1, 1])
            
            # 簡化分數 (e.g., 2/4 -> 1/2)
            gcd_val = math.gcd(abs(numerator), denominator)
            numerator //= gcd_val
            denominator //= gcd_val
            
            correct_answer_val = Fraction(numerator, denominator)
            
            # 計算 b 的實際值，會是整數或簡單分數 (e.g., 8^(2/3) = 4, 4^(-3/2) = 1/8)
            actual_b_val_raw = root_base**numerator
            
            # 將結果轉換為合適的整數或分數表示
            if isinstance(actual_b_val_raw, float) and actual_b_val_raw.is_integer():
                actual_b_val = int(actual_b_val_raw)
            else:
                actual_b_val = actual_b_val_raw
            
            if actual_b_val < 1: # 如果 b 是分數 (e.g., 1/8)
                denominator_for_display = int(1 / actual_b_val)
                b_display = r"\\frac{{1}}{{{denominator_for_display}}}"
            else: # 如果 b 是整數 (e.g., 27, 4)
                b_display = str(actual_b_val)
            
        else: # 'root_form' type (例如: log_5 5sqrt(5))
            base = random.choice([2, 3, 5, 7]) # 常用質數底數
            
            root_type = random.choice([2, 3]) # 平方根或立方根
            
            m = random.randint(0, 2) # 整數部分的指數 (a^m)
            
            if root_type == 2: # 平方根 (a^(1/2))
                fractional_exponent_val = Fraction(1, 2)
                if m == 0:
                    b_display = r"\\sqrt{{{base}}}"
                else:
                    b_display = f"{base}^{{{m}}} " + r"\\sqrt{{{base}}}"
            else: # 立方根 (a^(1/3) 或 a^(2/3))
                fraction_numerator = random.choice([1, 2])
                fractional_exponent_val = Fraction(fraction_numerator, 3)
                if m == 0:
                    b_display = r"\\sqrt[3]{{{base}^{{{fraction_numerator}}}}}"
                else:
                    b_display = f"{base}^{{{m}}} " + r"\\sqrt[3]{{{base}^{{{fraction_numerator}}}}}"

            # 正確答案是整數部分指數與分數部分指數之和
            correct_answer_val = Fraction(m) + fractional_exponent_val
            
        # 確保分數答案簡化並正確轉換為字串 (例如 Fraction(3,1) 轉為 "3" 而不是 "3/1")
        if isinstance(correct_answer_val, Fraction) and correct_answer_val.denominator == 1:
            correct_answer_str = str(correct_answer_val.numerator)
        else:
            correct_answer_str = str(correct_answer_val)

    question_text = f"求下列對數的值：<br>$log_{{{base}}} {b_display}$"

    return {
        "question_text": question_text,
        "answer": correct_answer_str, # 將正確答案以字串形式儲存
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    try:
        # 嘗試將使用者答案和正確答案轉換為分數進行比較，確保精確性 (例如 "1/2" 與 "0.5")
        user_fraction = Fraction(user_answer)
        correct_fraction = Fraction(correct_answer)
        if user_fraction == correct_fraction:
            is_correct = True
    except ValueError:
        # 如果無法轉換為分數 (例如輸入非分數或不精確的小數)，則嘗試浮點數比較
        try:
            # 使用 float 比較時，引入一個小的容忍度來處理浮點數精度問題
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                is_correct = True
        except ValueError:
            pass # 使用者答案既不是有效分數也不是有效數字
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}