import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「正整數指數與指數律」相關題目。
    """
    problem_types_l1 = [
        '_generate_product_same_base',
        '_generate_power_of_power',
        '_generate_product_same_exponent',
    ]
    
    problem_types_l2_plus = [
        '_generate_product_same_base',
        '_generate_power_of_power',
        '_generate_product_same_exponent',
        '_generate_quotient_same_base',
        '_generate_fill_in_blank_base',
        '_generate_fill_in_blank_exponent',
    ]

    if level == 1:
        chosen_type_name = random.choice(problem_types_l1)
    else: # level 2 and above
        chosen_type_name = random.choice(problem_types_l2_plus)
    
    # Call the chosen helper function
    return globals()[chosen_type_name](level)


def _get_base_range(level):
    if level == 1:
        return [2, 5] # Positive bases only for level 1
    elif level == 2:
        return [-5, 5] # Allow negative bases, exclude 0, 1, -1 for meaningful problems
    else: # level >= 3
        return [-10, 10]

def _get_exponent_range(level):
    if level == 1:
        return [2, 5]
    elif level == 2:
        return [2, 7]
    else: # level >= 3
        return [2, 10]

def _get_random_base(level):
    base_range = _get_base_range(level)
    base = 0
    # Avoid trivial bases 0, 1, -1 which simplify exponent laws too much
    while base in [0, 1, -1]:
        base = random.randint(min(base_range), max(base_range))
    return base

def _get_random_exponent(level, min_exp=2):
    exp_range = _get_exponent_range(level)
    # Ensure generated exponent is at least min_exp and within the level's range
    return random.randint(max(min_exp, min(exp_range)), max(exp_range))

def _format_base(base):
    # Use parentheses for negative bases for clarity in LaTeX
    if base < 0:
        return f"({base})"
    return str(base)

def _generate_product_same_base(level):
    # Law: a^m * a^n = a^(m+n)
    a = _get_random_base(level)
    m = _get_random_exponent(level)
    n = _get_random_exponent(level)

    question_text = f"利用指數律求下列各式的值：<br>$\\quad {_format_base(a)}^{{ {m} }} \\times {_format_base(a)}^{{ {n} }}$"
    correct_value = a**(m+n)
    correct_answer = str(correct_value)

    explanation = f"$\\quad {_format_base(a)}^{{ {m} }} \\times {_format_base(a)}^{{ {n} }} = {_format_base(a)}^{{ {m} }} + {{ {n} }} = {_format_base(a)}^{{ {m+n} }} = {correct_value}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def _generate_power_of_power(level):
    # Law: (a^m)^n = a^(mn)
    a = _get_random_base(level)
    m = _get_random_exponent(level)
    n = _get_random_exponent(level)

    question_text = f"利用指數律求下列各式的值：<br>$\\quad ( {_format_base(a)}^{{ {m} }} )^{{ {n} }}$"
    correct_value = a**(m*n)
    correct_answer = str(correct_value)

    explanation = f"$\\quad ( {_format_base(a)}^{{ {m} }} )^{{ {n} }} = {_format_base(a)}^{{ {m} }} \\times {{ {n} }} = {_format_base(a)}^{{ {m*n} }} = {correct_value}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def _generate_product_same_exponent(level):
    # Law: a^n * b^n = (ab)^n
    a = _get_random_base(level)
    b = _get_random_base(level)
    while a == b: # Ensure different bases for a more varied problem
        b = _get_random_base(level)
    
    n = _get_random_exponent(level)

    # Limit exponents to prevent excessively large numbers if a*b is large
    # For a*b, if level is 1 or 2, limit n such that (a*b)^n is not too big.
    # Max value of abs(a*b) for level 2 is abs(-5 * 5) = 25. 25^7 is huge.
    # So if abs(a*b) > 6, reduce max n.
    max_n_limit = _get_exponent_range(level)[1]
    if level <= 2 and abs(a * b) > 6: # E.g., if a*b = 10, then 10^7 is very large
        max_n_limit = min(max_n_limit, 4) # Reduce max exponent to avoid huge results
    
    # Regenerate n with the adjusted max_n_limit
    n = random.randint(2, max_n_limit) 
    if n < 2: n = 2 # Ensure minimum exponent is 2, just in case

    question_text = f"利用指數律求下列各式的值：<br>$\\quad {_format_base(a)}^{{ {n} }} \\times {_format_base(b)}^{{ {n} }}$"
    correct_value = (a*b)**n
    correct_answer = str(correct_value)

    explanation = f"$\\quad {_format_base(a)}^{{ {n} }} \\times {_format_base(b)}^{{ {n} }} = ( {_format_base(a)} \\times {_format_base(b)} )^{{ {n} }} = ( {a*b} )^{{ {n} }} = {correct_value}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def _generate_quotient_same_base(level):
    # Law: a^m / a^n = a^(m-n) (where m > n for positive integer exponent result)
    a = _get_random_base(level)
    
    # Ensure m is large enough so m-1 >= 2 (i.e., m >= 3).
    # The minimum exponent for 'n' should be 2.
    m = _get_random_exponent(level, min_exp=3) # m must be at least 3 for n=2 to be possible
    n = random.randint(2, m - 1) # Now m-1 is guaranteed to be >= 2

    question_text = f"利用指數律求下列各式的值：<br>$\\quad \\frac{{ {_format_base(a)}^{{ {m} }} }}{{ {_format_base(a)}^{{ {n} }} }}$"
    correct_value = a**(m-n)
    correct_answer = str(correct_value)

    explanation = f"$\\quad \\frac{{ {_format_base(a)}^{{ {m} }} }}{{ {_format_base(a)}^{{ {n} }} }} = {_format_base(a)}^{{ {m} }} - {{ {n} }} = {_format_base(a)}^{{ {m-n} }} = {correct_value}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def _generate_fill_in_blank_exponent(level):
    # Law: a^m * a^n = a^□ or (a^m)^n = a^□ or a^m / a^n = a^□
    a = _get_random_base(level)
    
    choice = random.choice([1, 2, 3])
    if choice == 1: # a^m * a^n = a^□
        m = _get_random_exponent(level)
        n = _get_random_exponent(level)
        question_text = f"利用指數律完成下列填空：<br>$\\quad {_format_base(a)}^{{ {m} }} \\times {_format_base(a)}^{{ {n} }} = {_format_base(a)}^{{ \\square }}$"
        correct_answer = str(m + n)
        explanation = f"$\\quad {_format_base(a)}^{{ {m} }} \\times {_format_base(a)}^{{ {n} }} = {_format_base(a)}^{{ {m} }} + {{ {n} }} = {_format_base(a)}^{{ {m+n} }}$"
    elif choice == 2: # (a^m)^n = a^□
        m = _get_random_exponent(level)
        n = _get_random_exponent(level)
        question_text = f"利用指數律完成下列填空：<br>$\\quad ( {_format_base(a)}^{{ {m} }} )^{{ {n} }} = {_format_base(a)}^{{ \\square }}$"
        correct_answer = str(m * n)
        explanation = f"$\\quad ( {_format_base(a)}^{{ {m} }} )^{{ {n} }} = {_format_base(a)}^{{ {m} }} \\times {{ {n} }} = {_format_base(a)}^{{ {m*n} }}$"
    else: # a^m / a^n = a^□
        m = _get_random_exponent(level, min_exp=3) # m must be at least 3
        n = random.randint(2, m - 1) # Now m-1 is guaranteed to be >= 2
        question_text = f"利用指數律完成下列填空：<br>$\\quad \\frac{{ {_format_base(a)}^{{ {m} }} }}{{ {_format_base(a)}^{{ {n} }} }} = {_format_base(a)}^{{ \\square }}$"
        correct_answer = str(m - n)
        explanation = f"$\\quad \\frac{{ {_format_base(a)}^{{ {m} }} }}{{ {_format_base(a)}^{{ {n} }} }} = {_format_base(a)}^{{ {m} }} - {{ {n} }} = {_format_base(a)}^{{ {m-n} }}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def _generate_fill_in_blank_base(level):
    # Law: a^n * b^n = (□)^n
    a = _get_random_base(level)
    b = _get_random_base(level)
    while a == b: # Ensure different bases
        b = _get_random_base(level)
    
    n = _get_random_exponent(level)

    # Same logic as _generate_product_same_exponent to limit huge results
    max_n_limit = _get_exponent_range(level)[1]
    if level <= 2 and abs(a * b) > 6:
        max_n_limit = min(max_n_limit, 4)
    
    # Regenerate n with the adjusted max_n_limit
    n = random.randint(2, max_n_limit) 
    if n < 2: n = 2 # Ensure minimum exponent is 2, just in case

    question_text = f"利用指數律完成下列填空：<br>$\\quad {_format_base(a)}^{{ {n} }} \\times {_format_base(b)}^{{ {n} }} = ( \\square )^{{ {n} }}$"
    correct_answer = str(a * b)
    explanation = f"$\\quad {_format_base(a)}^{{ {n} }} \\times {_format_base(b)}^{{ {n} }} = ( {_format_base(a)} \\times {_format_base(b)} )^{{ {n} }} = ( {a*b} )^{{ {n} }}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        # Try comparing as floats to handle '1024' vs '1024.0'
        if float(user_answer) == float(correct_answer):
            is_correct = True
    except ValueError:
        # If conversion to float fails, compare as strings (e.g., if answer is non-numeric, though not expected here)
        is_correct = (user_answer == correct_answer)

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}