import random
import math
from fractions import Fraction

def _format_equation(a, b, c):
    """Formats a quadratic equation into a LaTeX string."""
    if a == 1:
        term_a = "x^2"
    elif a == -1:
        term_a = "-x^2"
    else:
        term_a = f"{a}x^2"

    if b != 0:
        if b == 1:
            term_b = " + x"
        elif b == -1:
            term_b = " - x"
        elif b > 0:
            term_b = f" + {b}x"
        else:
            term_b = f" - {-b}x"
    else:
        term_b = ""

    if c != 0:
        if c > 0:
            term_c = f" + {c}"
        else:
            term_c = f" - {-c}"
    else:
        term_c = ""
    
    equation = f"{term_a}{term_b}{term_c} = 0"
    return f"${equation}$"

def _is_perfect_square(n):
    if n < 0:
        return False
    if n == 0:
        return True
    x = int(math.sqrt(n))
    return x * x == n

def _simplify_sqrt(n):
    """Simplifies sqrt(n) to a * sqrt(b). Returns (a, b)."""
    if n <= 0:
        return (1, n)
    for i in range(int(math.sqrt(n)), 1, -1):
        if n % (i * i) == 0:
            return (i, n // (i * i))
    return (1, n)

def generate_solve_formula(level=1):
    """
    Generates a problem that requires solving a quadratic equation using the formula.
    Covers D>0 (perfect square and non-perfect square), D=0, and D<0.
    """
    d_type = random.choice(['perfect_square', 'surd', 'zero', 'negative'])
    
    a, b, c = 1, 2, 3

    if d_type == 'perfect_square':
        r1 = Fraction(random.randint(-6, 6), random.randint(1, 3))
        r2 = Fraction(random.randint(-6, 6), random.randint(1, 3))
        if r1 == r2: r2 += 1

        common_mult = r1.denominator * r2.denominator
        a = common_mult
        b = int(-common_mult * (r1 + r2))
        c = int(common_mult * (r1 * r2))
        
        roots = sorted([r1, r2])
        r_strs = [(str(r) if r.denominator != 1 else str(r.numerator)) for r in roots]
        answer = f"x={r_strs[0]} 或 x={r_strs[1]}"
        correct_answer = f"{r_strs[0]},{r_strs[1]}"
        
    elif d_type == 'surd':
        while True:
            a = random.randint(1, 5)
            b = random.randint(-13, 13)
            c = random.randint(-13, 13)
            if c == 0 or b == 0: continue
            D = b**2 - 4*a*c
            if D > 0 and not _is_perfect_square(D):
                break
        
        neg_b = -b
        two_a = 2*a
        coeff, rad = _simplify_sqrt(D)
        
        g = math.gcd(math.gcd(neg_b, coeff), two_a)
        
        neg_b //= g
        coeff //= g
        two_a //= g
        
        sqrt_latex = f"\\sqrt{{{rad}}}" if coeff == 1 else f"{coeff}\\sqrt{{{rad}}}"
        num_latex = f"{neg_b} \\pm {sqrt_latex}"
        if two_a == 1 or two_a == -1:
             answer = f"x = {num_latex}" if two_a == 1 else f"x = -({num_latex})"
        else:
             answer = f"x = \\frac{{{num_latex}}}{{{two_a}}}"

        sqrt_ans = f"√{rad}" if coeff == 1 else f"{coeff}√{rad}"
        r1 = f"({neg_b}+{sqrt_ans})/{two_a}"
        r2 = f"({neg_b}-{sqrt_ans})/{two_a}"
        correct_answer = f"{r1},{r2}"

    elif d_type == 'zero':
        k = random.randint(1, 4)
        m = random.randint(-7, 7)
        if m == 0: m = 1
        a, b, c = k*k, 2*k*m, m*m
        root = Fraction(-m, k)
        root_str = str(root) if root.denominator != 1 else str(root.numerator)
        answer = f"x={root_str} (重根)"
        correct_answer = answer
        
    else: # negative
        while True:
            a = random.randint(1, 5)
            b = random.randint(-8, 8)
            c = random.randint(1, 8)
            if b**2 - 4*a*c < 0:
                break
        answer = "無實數解"
        correct_answer = answer
        
    if random.random() < 0.2 and a > 0:
        a, b, c = -a, -b, -c
        
    question_text = f"利用公式解，求一元二次方程式 {_format_equation(a, b, c)} 的解。"
    if d_type == 'negative':
        question_text = f"解一元二次方程式 {_format_equation(a, b, c)}。"
        
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": correct_answer
    }

def generate_determine_nature(level=1):
    """Generates a problem asking to determine the nature of the roots."""
    temp_problem = generate_solve_formula()
    # Extract the equation part from the generated question
    equation_str = temp_problem['question_text'].split('方程式')[1].split('的')[0].strip()
    
    answer_key = temp_problem['correct_answer']
    
    if "無實數解" in answer_key:
        correct_answer = "無實數解"
    elif "(重根)" in answer_key:
        correct_answer = "重根"
    else:
        correct_answer = "兩相異實根"
        
    question_text = f"判斷下列方程式解的情形： {equation_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_coefficient(level=1):
    """
    Generates a problem where the student must find a coefficient `m`
    given that the equation has a repeated root.
    """
    r = random.randint(-9, 9)
    if r == 0: r = 10
    
    b_val = -2 * r
    c_val = r * r
    
    k = random.randint(2, 5)
    m = random.randint(-5, 5)
    d = c_val - k * m
    
    c_expr = f"{k}m"
    if d > 0:
        c_expr += f" + {d}"
    elif d < 0:
        c_expr += f" - {-d}"

    equation = _format_equation(1, b_val, 0).replace("= 0", f" + ({c_expr}) = 0")
        
    question_text = f"已知 $x$ 的一元二次方程式 {equation} 有重根，求 $m$ 的值及此方程式的解。(請以 m=...,x=... 的格式作答)"
    
    answer_x = f"x={r} (重根)"
    answer_m = f"m={m}"
    answer = f"{answer_m}, {answer_x}"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate(level=1):
    """
    Generates a question related to the quadratic formula.
    """
    problem_type = random.choice([
        'solve', 'solve', 'solve', 'solve', 
        'determine', 'determine',
        'find_coeff'
    ])
    
    if problem_type == 'solve':
        return generate_solve_formula(level)
    elif problem_type == 'determine':
        return generate_determine_nature(level)
    else:
        return generate_find_coefficient(level)

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct one.
    Handles different formats and orders for roots.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    # Normalize some common variations
    user_answer_norm = user_answer.replace(" ", "").replace("x=", "").replace("，", ",").replace("或", ",")
    correct_answer_norm = correct_answer.replace(" ", "").replace("x=", "").replace("，", ",")

    # Type 1: Classification answers
    if correct_answer in ["兩相異實根", "重根", "無實數解"]:
        if correct_answer == "兩相異實根":
            is_correct = "異" in user_answer
        elif correct_answer == "重根":
            is_correct = "重" in user_answer or "相等" in user_answer
        elif correct_answer == "無實數解":
            is_correct = "無" in user_answer
    # Type 2: Answers with text like "(重根)" or "m="
    elif "(重根)" in correct_answer or "m=" in correct_answer:
        if "," in correct_answer_norm: # For "m=...,x=..." case, order doesn't matter
            is_correct = sorted(user_answer_norm.split(',')) == sorted(correct_answer_norm.split(','))
        else: # For "x=... (重根)" case
            is_correct = user_answer_norm == correct_answer_norm
    # Type 3: Numeric or formulaic roots
    else:
        try:
            # Attempt to parse as fractions (for rational roots)
            user_parts = user_answer_norm.split(',')
            correct_parts = correct_answer_norm.split(',')
            if len(user_parts) == len(correct_parts):
                user_fractions = sorted([Fraction(p) for p in user_parts])
                correct_fractions = sorted([Fraction(p) for p in correct_parts])
                is_correct = user_fractions == correct_fractions
        except (ValueError, ZeroDivisionError):
            # Fallback for irrational roots (e.g., contains '√')
            user_parts_str = sorted(user_answer_norm.replace("sqrt", "√").split(','))
            correct_parts_str = sorted(correct_answer_norm.split(','))
            is_correct = user_parts_str == correct_parts_str

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}