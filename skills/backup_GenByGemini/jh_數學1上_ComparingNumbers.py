import random
from fractions import Fraction

# Helper function to format numbers into LaTeX strings
def _to_latex(num):
    """
    Converts a number (int, float, Fraction) into a proper LaTeX string.
    Handles mixed numbers and proper fractions.
    """
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        
        sign = ""
        if num < 0:
            sign = "-"
            num = -num

        integer_part = num.numerator // num.denominator
        frac_num = num.numerator % num.denominator
        frac_den = num.denominator

        if integer_part == 0:
            return f"{sign}\\frac{{{frac_num}}}{{{frac_den}}}"
        else:
            if frac_num == 0:
                 return f"{sign}{integer_part}"
            else:
                 return f"{sign}{integer_part}\\frac{{{frac_num}}}{{{frac_den}}}"

    elif isinstance(num, float):
        if num == int(num):
            return str(int(num))
        else:
            return f"{num:.10g}" # Use general format to keep it clean and avoid trailing zeros
    else: # int
        return str(num)

def generate(level=1):
    """
    生成「比較數的大小」相關題目 (國中數學1上)。
    包含：
    1. 兩數直接比較大小
    2. 三一律應用題
    3. 遞移律應用題
    """
    problem_type = random.choice(['direct_comparison', 'trichotomy', 'transitive'])
    
    if problem_type == 'direct_comparison':
        return generate_direct_comparison()
    elif problem_type == 'trichotomy':
        return generate_trichotomy_problem()
    else: # transitive
        return generate_transitive_problem()

def generate_direct_comparison():
    """
    題型：直接比較兩個數的大小，填入 >、< 或 =。
    對應課本例題 1。
    """
    num_types = [random.randint(-10, 10), round(random.uniform(-10, 10), 1), Fraction(random.randint(-20, 20), random.randint(2, 5))]
    num1_val = random.choice(num_types)
    num2_val = random.choice(num_types)

    # 80% chance to ensure they are not equal
    if random.random() < 0.8:
        while num1_val == num2_val:
            num2_val = random.choice([random.randint(-10, 10), round(random.uniform(-10, 10), 1)])
    else:
        num2_val = num1_val

    num1_str = _to_latex(num1_val)
    num2_str = _to_latex(num2_val)

    if num1_val < num2_val:
        correct_answer = '<'
    elif num1_val > num2_val:
        correct_answer = '>'
    else:
        correct_answer = '='
    
    question_text = f"請在 __ 中填入 $ > $、$ < $ 或 $ = $：\n\n${num1_str}$ __ ${num2_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_trichotomy_problem():
    """
    題型：利用三一律，從「不比 a 大」且「不比 a 小」推斷出「等於 a」。
    對應課本例題 2。
    """
    type_choice = random.choice(['int', 'decimal', 'fraction'])
    
    if type_choice == 'int':
        val = random.randint(-20, 20)
        val_str = _to_latex(val)
        correct_answer = str(val)
    elif type_choice == 'decimal':
        val = round(random.randint(-19, 19) + random.choice([i/10 for i in range(1,10)]), 1)
        val_str = _to_latex(val)
        correct_answer = str(val)
    else: # fraction
        den = random.randint(3, 9)
        num = random.randint(1, den - 1) * random.choice([-1, 1])
        val = Fraction(num, den)
        val_str = _to_latex(val)
        correct_answer = f"{num}/{den}"

    question_text = f"老師心中想了一個數 $a$，小翊猜說：「這個數比 ${val_str}$ 大。」小妍猜說：「這個數比 ${val_str}$ 小。」結果老師說兩個人都猜錯了，那麼 $a$ 應該是多少呢？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_transitive_problem():
    """
    題型：利用遞移律，從 a < m 且 m < b 推斷出 a < b。
    對應課本例題 3。
    """
    m = random.randint(-10, 10)
    var1, var2 = random.sample(['a', 'b'], 2)

    if random.random() < 0.5:
        # Case: var1 < m < var2  (implies var1 < var2)
        stmt1 = f"{var1} < {m}"
        stmt2 = f"{m} < {var2}"
        larger = var2
        smaller = var1
    else:
        # Case: var1 > m > var2  (implies var1 > var2)
        stmt1 = f"{var1} > {m}"
        stmt2 = f"{m} > {var2}"
        larger = var1
        smaller = var2

    target_word, correct_answer = random.choice([('較大', larger), ('較小', smaller)])
    statements = random.sample([stmt1, stmt2], 2)
    
    question_text = f"已知 $a$ 和 $b$ 分別代表一個數，若 ${statements[0]}$ 且 ${statements[1]}$，則 $a$ 和 $b$ 何者{target_word}？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer_str = str(correct_answer).strip()
    is_correct = False

    # Case 1: Comparison operators
    if correct_answer_str in ['<', '>', '=']:
        user_answer = user_answer.replace('＞', '>').replace('＜', '<').replace('＝', '=')
        is_correct = (user_answer == correct_answer_str)
        display_answer = correct_answer_str
        result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：{display_answer}"

    # Case 2: Alphabetic answer (e.g., 'a', 'b')
    elif correct_answer_str.isalpha() and len(correct_answer_str) == 1:
        is_correct = (user_answer.lower() == correct_answer_str.lower())
        display_answer = f"${correct_answer_str}$"
        result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：{display_answer}"

    # Case 3: Numerical answer
    else:
        try:
            # Robust comparison using Fraction for inputs like '0.5' vs '1/2'
            if Fraction(user_answer) == Fraction(correct_answer_str):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # Fallback to string comparison if conversion fails
            if user_answer == correct_answer_str:
                is_correct = True
        
        # Format correct answer for display using LaTeX
        try:
            display_answer = _to_latex(Fraction(correct_answer_str))
        except (ValueError, ZeroDivisionError):
            display_answer = correct_answer_str
        
        display_answer = f"${display_answer}$"
        result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：{display_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}