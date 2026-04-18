import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「對數運算性質與換底公式」相關題目。
    包含：
    1. 對數加減運算 (log A + log B - log C)
    2. 對數冪次法則 (n log A + m log B)
    3. 特定底數對數求值 (log_a b = k)
    4. 換底公式的乘積應用 (log_a b * log_b c)
    """
    
    # 根據難度等級選擇題目類型
    # Level 1: 基本對數加減、特定底數求值（整數指數）
    # Level 2: 包含冪次法則、特定底數求值（分數指數）
    # Level 3: 包含換底公式的乘積運算
    
    problem_choice = random.randint(1, 100) 

    if level == 1:
        if problem_choice <= 60:
            return _generate_simple_laws_problem()
        else:
            return _generate_specific_base_log_problem(exponent_type='integer')
    elif level == 2:
        if problem_choice <= 35:
            return _generate_simple_laws_problem()
        elif problem_choice <= 70:
            return _generate_power_rule_problem()
        else:
            return _generate_specific_base_log_problem(exponent_type='fractional')
    else: # level 3 and higher
        if problem_choice <= 25:
            return _generate_simple_laws_problem()
        elif problem_choice <= 50:
            return _generate_power_rule_problem()
        elif problem_choice <= 75:
            return _generate_specific_base_log_problem(exponent_type=random.choice(['integer', 'fractional']))
        else:
            return _generate_change_of_base_product_problem()

def _generate_simple_laws_problem():
    """
    生成形如 log A + log B - log C 的題目，其中對數通常為常用對數 (log)。
    答案會是整數。
    """
    
    # 預設多個會簡化為整數的常用對數運算式
    patterns = [
        (r"log4 + log25", 2),
        (r"log2 + log5", 1),
        (r"log20 + log5", 2),
        (r"log100 - log10", 1),
        (r"log400 - log4", 2),
        (r"log20 - log200", -1),
        (r"log2 + log0.2 + log5 + log0.5", 0), # log(2 * 0.2 * 5 * 0.5) = log(1) = 0
    ]
    
    question_str, answer = random.choice(patterns)
    
    question_text = f"求下列各式的值：<br>${question_str}$"
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def _generate_power_rule_problem():
    """
    生成形如 n log A + m log B - p log C 的題目，可能包含不同底數。
    答案會是整數。
    """
    
    # 預設多個會簡化為整數的對數冪次法則與加減運算式
    patterns = [
        (r"3log2 + log5 - 2log20", -1), # log8 + log5 - log400 = log(40/400) = log(1/10) = -1
        (r"2log_6 2 + log_6 45 - log_6 5", 2), # log_6 4 + log_6 45 - log_6 5 = log_6(4*45/5) = log_6 36 = 2
        (r"log3 + 2log10 - log30", 1), # log3 + log100 - log30 = log(300/30) = log10 = 1
        (r"3log5 - log125", 0), # log 125 - log 125 = 0
        (r"log4 + 2log5", 2), # log4 + log25 = log100 = 2
        (r"log27 - 3log3", 0) # log27 - log27 = 0
    ]
    
    question_str, answer = random.choice(patterns)
    
    question_text = f"求下列各式的值：<br>${question_str}$"
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def _generate_specific_base_log_problem(exponent_type='integer'):
    """
    生成形如 log_a b 的題目，其中 b 是 a 的 k 次方，答案為 k。
    k 可以是整數或分數。
    """
    
    base = random.choice([2, 3, 4, 5, 8, 9, 10]) # 避免底數為1
    
    if exponent_type == 'integer':
        exponent = random.randint(-3, 3)
        # 避免 log_b 1 = 0 頻繁出現，使其為隨機選擇
        while exponent == 0 and random.random() < 0.5: 
             exponent = random.randint(-3, 3)
        
        val_b = base**exponent
        
        if val_b == 1:
            val_b_str = "1"
        elif isinstance(val_b, float) and val_b < 1: 
            val_b_frac = Fraction(val_b).limit_denominator(100)
            if val_b_frac.denominator == 1: # 例如 0.5 應顯示為 1/2
                val_b_str = str(val_b_frac.numerator)
            else:
                val_b_str = r"\\frac{{{}}}{{{}}}".format(val_b_frac.numerator, val_b_frac.denominator)
        else:
            val_b_str = str(int(val_b)) # 將浮點數轉為整數，若無小數部分
            
        correct_answer = str(exponent)

    else: # fractional exponent (例如 log_8 sqrt(2) = 1/6)
        num = random.choice([1, -1])
        den = random.choice([2, 3, 4]) # 限制分母為2, 3, 4以產生常見根號
        exponent = Fraction(num, den)
        
        val_b = base**float(exponent)
        
        # 依分數指數顯示成根號或指數形式
        if exponent.denominator == 2: # 平方根
            if exponent.numerator == 1:
                val_b_str = r"\\sqrt{{{base}}}"
            else: # numerator == -1
                val_b_str = r"\\frac{{1}}{{\\sqrt{{{base}}}}}"
        elif exponent.denominator == 3: # 立方根
            if exponent.numerator == 1:
                val_b_str = r"\\sqrt[3]{{{base}}}"
            else: # numerator == -1
                val_b_str = r"\\frac{{1}}{{\\sqrt[3]{{{base}}}}}"
        else: # 一般分數指數，顯示為 X^(n/d)
            val_b_str = f"{base}^{{({exponent.numerator}/{exponent.denominator})}}"
        
        correct_answer = str(exponent) # Fraction 物件可以直接轉為字串
        
    question_text = f"求下列各式的值：<br>$log_{{{base}}} {{{val_b_str}}}$"
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_change_of_base_product_problem():
    """
    生成換底公式的乘積應用題目，例如 log_a b * log_b c = log_a c，或 log_4 9 * log_3 8。
    答案可以是整數或分數。
    """
    
    problem_type = random.choice(['chain', 'cancellation'])
    
    if problem_type == 'chain':
        # 類型: log_a b * log_b c = log_a c
        base1 = random.choice([2, 3, 5])
        mid_base = random.choice([4, 6, 7, 8, 9, 11, 13]) # 選擇一個不那麼明顯是 base1 乘冪的底數
        
        # 讓 log_base1 c 的結果為整數
        final_answer_exp = random.randint(1, 3) 
        final_val_c = base1**final_answer_exp
        
        question_text = f"求下列各式的值：<br>$log_{{{base1}}} {{{mid_base}}} \\times log_{{{mid_base}}} {{{final_val_c}}}$"
        correct_answer = str(final_answer_exp)
        
    else: # 類型: cancellation (例如 log_4 9 * log_3 8 = 3)
        # 選擇兩個不同的質數作為底數和真數的因子
        prime1 = random.choice([2, 3])
        prime2 = random.choice([3, 5])
        while prime2 == prime1: # 確保兩個質數不同
            prime2 = random.choice([3, 5])
        
        # 對第一個對數: log_{prime1^x} (prime2^y)
        # 對第二個對數: log_{prime2^z} (prime1^w)
        
        x = random.randint(1, 3) # 第一個對數底數的指數
        y = random.randint(1, 3) # 第一個對數真數的指數
        z = random.randint(1, 3) # 第二個對數底數的指數
        w = random.randint(1, 3) # 第二個對數真數的指數
        
        base_A = prime1**x
        val_B = prime2**y
        base_C = prime2**z
        val_D = prime1**w
        
        # 答案將是 (y/x) * (w/z)
        answer_fraction = Fraction(y, x) * Fraction(w, z)
        
        question_text = (
            f"求下列各式的值：<br>"
            f"$log_{{{base_A}}} {{{val_B}}} \\times log_{{{base_C}}} {{{val_D}}}$"
        )
        correct_answer = str(answer_fraction)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援整數、浮點數（帶容錯）和分數的比較。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False

    try:
        # 嘗試將答案解析為分數，以處理整數、小數和分數
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        
        if user_frac == correct_frac:
            is_correct = True
        else:
            # 如果分數比較不相等，再考慮浮點數的微小誤差
            user_float = float(user_answer)
            correct_float = float(correct_answer)
            if abs(user_float - correct_float) < 1e-9: # 浮點數比較容錯
                is_correct = True
    except ValueError:
        pass # 如果解析失敗 (非數字輸入), 則為不正確

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}