import random
from fractions import Fraction

# --- Helper Functions ---

def _get_random_fraction(is_divisor=False):
    """
    生成一個隨機分數，可以是整數、真分數或帶分數/假分數。
    is_divisor: 若為 True，確保分母不為零 (此邏輯下恆為真)。
    """
    # 1: integer, 2: proper fraction, 3: mixed/improper fraction
    frac_type = random.choice([1, 2, 3])

    if frac_type == 1:  # Integer
        val = random.randint(1, 9)
        if val == 1 and random.random() < 0.5: # -1 is a special case from examples
             f = Fraction(-1)
        else:
             f = Fraction(val)
    elif frac_type == 2:  # Proper fraction
        den = random.randint(2, 9)
        num = random.randint(1, den - 1)
        f = Fraction(num, den)
    else:  # Mixed / Improper fraction
        den = random.randint(2, 9)
        integer_part = random.randint(1, 3)
        num_part = random.randint(1, den - 1)
        f = Fraction(integer_part * den + num_part, den)

    # Randomly assign a negative sign
    if random.random() < 0.4 and f != -1:
        f = -f

    return f

def _fraction_to_latex(f: Fraction, use_mixed=False, add_paren_if_neg=False):
    """
    將 Fraction 物件轉換為 LaTeX 字串 (不含 $ 符號)。
    use_mixed: 是否將假分數顯示為帶分數。
    add_paren_if_neg: 是否在負數時加上括號。
    """
    is_negative = f.numerator < 0
    sign = "-" if is_negative else ""
    num = abs(f.numerator)
    den = f.denominator

    core_str = ""
    if den == 1:
        core_str = str(num)
    elif use_mixed and num >= den:
        integer_part = num // den
        rem_num = num % den
        if rem_num == 0:
            core_str = str(integer_part)
        else:
            core_str = f"{integer_part}\\frac{{{rem_num}}}{{{den}}}"
    else:
        core_str = f"\\frac{{{num}}}{{{den}}}"

    final_str = f"{sign}{core_str}"

    if is_negative and add_paren_if_neg:
        return f"\\left( {final_str} \\right)"
    else:
        return final_str

def _fraction_to_answer_string(f: Fraction):
    """
    將 Fraction 物件轉換為標準答案格式的字串 (例如 "-7/4" 或 "-1")。
    """
    if f.denominator == 1:
        return str(f.numerator)
    else:
        return f"{f.numerator}/{f.denominator}"

# --- Problem Type Generators ---

def generate_reciprocal_problem():
    """
    生成求倒數的題目 (對應例題 1)。
    """
    f = _get_random_fraction()
    if f == 0:
        f = Fraction(random.randint(1, 5)) # Avoid 0 for reciprocal
    
    reciprocal = 1 / f

    f_latex = _fraction_to_latex(f, use_mixed=True)
    
    question_text = f"寫出 ${f_latex}$ 的倒數。"
    correct_answer = _fraction_to_answer_string(reciprocal)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_two_term_division_problem():
    """
    生成兩項分數除法的題目 (對應例題 2, 3 的第一部分)。
    """
    f1 = _get_random_fraction()
    f2 = _get_random_fraction(is_divisor=True)
    
    # Ensure the problem is not too simple, e.g., 4 / 2
    if f1.denominator == 1 and f2.denominator == 1 and f1 % f2 == 0 and abs(f2.numerator) > 1:
        f1 = _get_random_fraction()
        f2 = _get_random_fraction(is_divisor=True)

    ans = f1 / f2

    f1_latex = _fraction_to_latex(f1, use_mixed=True)
    f2_latex = _fraction_to_latex(f2, use_mixed=True, add_paren_if_neg=True)

    question_text = f"計算下列式子的值：${f1_latex} \\div {f2_latex}$"
    correct_answer = _fraction_to_answer_string(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_three_term_division_problem():
    """
    生成三項分數連除的題目 (對應例題 2, 3 的第二部分)。
    """
    f1 = _get_random_fraction()
    f2 = _get_random_fraction(is_divisor=True)
    f3 = _get_random_fraction(is_divisor=True)
    
    # To make it simpler, let's limit the complexity of the third fraction
    if random.random() < 0.5:
         f3 = Fraction(random.choice([-1, 1]) * random.randint(1,5), random.randint(2,7))

    ans = f1 / f2 / f3

    f1_latex = _fraction_to_latex(f1, use_mixed=True, add_paren_if_neg=True if f1<0 else False)
    f2_latex = _fraction_to_latex(f2, use_mixed=True, add_paren_if_neg=True)
    f3_latex = _fraction_to_latex(f3, use_mixed=True, add_paren_if_neg=True)

    question_text = f"計算下列式子的值：${f1_latex} \\div {f2_latex} \\div {f3_latex}$"
    correct_answer = _fraction_to_answer_string(ans)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    生成「分數除法」相關題目。
    包含：
    1. 求倒數
    2. 兩項分數除法
    3. 三項分數除法
    """
    problem_type = random.choice([
        'reciprocal', 
        'two_term_division', 
        'three_term_division'
    ])
    
    if problem_type == 'reciprocal':
        return generate_reciprocal_problem()
    elif problem_type == 'two_term_division':
        return generate_two_term_division_problem()
    else:
        return generate_three_term_division_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    能處理整數、分數 (a/b)、帶分數 (a b/c) 等格式。
    """
    try:
        correct_f = Fraction(correct_answer)
    except (ValueError, TypeError):
        return {"correct": False, "result": "內部錯誤：標準答案格式無效。", "next_question": True}

    user_answer = user_answer.strip()
    user_f = None
    
    try:
        # Case 1: Simple fraction "a/b" or integer "a" or decimal "a.b"
        user_f = Fraction(user_answer)
    except (ValueError, TypeError):
        # Case 2: Mixed number "a b/c"
        try:
            parts = user_answer.split()
            if len(parts) == 2 and '/' in parts[1]:
                integer_part = int(parts[0])
                frac_part = Fraction(parts[1])
                if integer_part < 0:
                    user_f = integer_part - frac_part
                else:
                    user_f = integer_part + frac_part
        except (ValueError, IndexError, TypeError):
            pass
    
    is_correct = (user_f is not None) and (user_f == correct_f)

    # Format the correct answer for display, showing both improper and mixed forms if applicable.
    num = correct_f.numerator
    den = correct_f.denominator
    
    answer_display = ""
    if den == 1:
        answer_display = str(num)
    elif abs(num) < den:
        answer_display = f"\\frac{{{num}}}{{{den}}}"
    else: # Improper fraction
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        improper_latex = f"{sign}\\frac{{{abs_num}}}{{{den}}}"
        
        integer_part = abs_num // den
        rem_num = abs_num % den
        
        if rem_num == 0: # was actually an integer
            answer_display = str(correct_f.numerator)
        else:
            mixed_latex = f"{sign}{integer_part}\\frac{{{rem_num}}}{{{den}}}"
            answer_display = f"{improper_latex} \\; (\\text{{或}} \\; {mixed_latex})"

    result_text = f"完全正確！答案是 ${answer_display}$。" if is_correct else f"答案不正確。正確答案應為：${answer_display}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
