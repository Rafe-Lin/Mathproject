import random
from fractions import Fraction
import math

def format_fraction(num_or_frac, den=None):
    """
    Formats a number or Fraction object into a string suitable for LaTeX display.
    If num_or_frac is a Fraction, den should be None.
    If num_or_frac is int and den is int, it constructs a Fraction.
    """
    if isinstance(num_or_frac, Fraction):
        frac = num_or_frac
    elif den is not None:
        frac = Fraction(num_or_frac, den)
    else:
        frac = Fraction(num_or_frac)

    if frac.denominator == 1:
        return str(frac.numerator)
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

def generate(level=1):
    """
    生成「級數」相關題目。
    包含：
    1. 等差級數：已知首項、項數、和，求公差。
    2. 等差級數：已知首項、第二項、末項，求和。
    3. 等比級數：已知首項、公比、項數，求和。
    4. 等比級數：已知首項、第二項、末項，求和。
    """
    problem_type = random.choice([
        'arithmetic_d',         # Find common difference
        'arithmetic_sum_terms', # Find sum given a_1, a_n, d
        'geometric_sum_a1rn',   # Find sum given a_1, r, n
        'geometric_sum_terms'   # Find sum given a_1, a_n, r
    ])

    if problem_type == 'arithmetic_d':
        return generate_arithmetic_d_problem()
    elif problem_type == 'arithmetic_sum_terms':
        return generate_arithmetic_sum_terms_problem()
    elif problem_type == 'geometric_sum_a1rn':
        return generate_geometric_sum_a1rn_problem()
    elif problem_type == 'geometric_sum_terms':
        return generate_geometric_sum_terms_problem()

def generate_arithmetic_d_problem():
    """
    生成等差數列問題：已知首項、項數、和，求公差。
    """
    a1 = random.randint(-20, 20)
    d = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
    n = random.randint(5, 12)

    # Calculate Sn = n/2 * (2*a1 + (n-1)*d)
    sn_val = Fraction(n * (2 * a1 + (n - 1) * d), 2)
    
    question_text = f"求首項為 ${a1}$，前 ${n}$ 項和為 ${format_fraction(sn_val)}$ 的等差數列之公差。"
    correct_answer = str(d)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_arithmetic_sum_terms_problem():
    """
    生成等差級數問題：已知首項、第二項、末項，求和。
    """
    a1 = random.randint(-15, 15)
    d = random.choice([-4, -3, -2, 2, 3, 4])
    
    # n should be at least 3 for "..." to make sense, but series_str only shows a1, a1+d, ..., an.
    n = random.randint(5, 13) 

    an = a1 + (n - 1) * d
    
    # Generate the series string with a_1, a_2, ..., a_n
    term1_str = format_fraction(a1)
    term2_str = format_fraction(a1 + d)
    an_str = format_fraction(an)

    series_str = f"{term1_str} + {term2_str} + ... + {an_str}"

    # Calculate Sn = n/2 * (a1 + an)
    sn_val = Fraction(n * (a1 + an), 2)
    
    question_text = f"求等差級數 ${series_str}$ 的和。"
    correct_answer = str(sn_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_sum_a1rn_problem():
    """
    生成等比級數問題：已知首項、公比、項數，求和。
    """
    a1 = random.choice([-3, -2, 2, 3])
    r_int = random.choice([-3, -2, 2, 3])
    r_frac_num = random.choice([1]) # Numerator of 1 for simple fractions
    r_frac_den = random.choice([2, 3]) # Denominator for simple fractions
    r_frac_sign = random.choice([1, -1])

    r_choices = [Fraction(r_int)]
    if r_frac_den != 0: 
        r_choices.append(Fraction(r_frac_num * r_frac_sign, r_frac_den))

    r = random.choice(r_choices)

    # Ensure r != 1
    # For safety, if r happens to be 1, re-pick from the pool until not 1.
    while r == 1:
        r = random.choice(r_choices)

    n = random.randint(4, 7) # Keep n small to avoid huge numbers

    # Calculate Sn = a1 * (r^n - 1) / (r - 1)
    # Cast a1 to Fraction for consistent arithmetic
    sn_val = Fraction(a1) * ( (r**n) - 1 ) / (r - 1)
    
    question_text = f"求首項為 ${a1}$，公比為 ${format_fraction(r)}$ 的等比數列前 ${n}$ 項的和。"
    correct_answer = str(sn_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_sum_terms_problem():
    """
    生成等比級數問題：已知首項、第二項、末項，求和。
    """
    a1 = random.choice([-3, -2, 2, 3])
    r_int = random.choice([-3, -2, 2, 3])
    r_frac_num = random.choice([1])
    r_frac_den = random.choice([2, 3])
    r_frac_sign = random.choice([1, -1])

    r_choices = [Fraction(r_int)]
    if r_frac_den != 0:
        r_choices.append(Fraction(r_frac_num * r_frac_sign, r_frac_den))
    
    r = random.choice(r_choices)
    
    # Ensure r != 1
    while r == 1:
        r = random.choice(r_choices)

    n = random.randint(4, 7) # Keep n small

    # Calculate an
    an_val = Fraction(a1) * (r ** (n - 1))
    
    # Generate the series string: a_1, a_1*r, ..., a_n
    term1_str = format_fraction(a1)
    term2_str = format_fraction(Fraction(a1) * r)
    an_str = format_fraction(an_val)

    series_str = f"{term1_str} + {term2_str} + ... + {an_str}"

    # Calculate Sn
    sn_val = Fraction(a1) * ( (r**n) - 1 ) / (r - 1)
    
    question_text = f"求等比級數 ${series_str}$ 的和。"
    correct_answer = str(sn_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援整數、小數、分數形式的答案。
    """
    try:
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        is_correct = (user_frac == correct_frac)
    except ValueError:
        is_correct = False
    
    if is_correct:
        result_text = f"完全正確！答案是 ${format_fraction(Fraction(correct_answer))}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${format_fraction(Fraction(correct_answer))}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}