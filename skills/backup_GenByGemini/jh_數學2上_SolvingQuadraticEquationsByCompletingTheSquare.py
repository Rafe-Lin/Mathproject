import random
from fractions import Fraction
from math import gcd, isqrt

# --- Helper Functions ---

def format_term(coeff, var, is_leading=False):
    """Formats a single term in a polynomial."""
    if coeff == 0:
        return ""
    
    sign = ""
    if is_leading:
        if coeff < 0:
            sign = "-"
    else:
        sign = " + " if coeff > 0 else " - "
        
    abs_coeff = abs(coeff)
    
    if abs_coeff == 1 and var:
        coeff_str = ""
    else:
        coeff_str = str(abs_coeff)
        
    return f"{sign}{coeff_str}{var}"

def format_fraction_plain(f):
    """Formats a Fraction object as a plain string 'a/b' or 'a'."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def format_fraction_latex(f):
    """Formats a Fraction object as a LaTeX string."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def simplify_sqrt(n):
    """Simplifies a square root. Returns (coefficient, radicand). e.g., sqrt(20) -> (2, 5)."""
    if n < 0:
        raise ValueError("Input to simplify_sqrt must be non-negative")
    if n == 0:
        return 1, 0
    i = isqrt(n)
    if i * i == n:
        return i, 1
    largest_sq_factor = 1
    for j in range(i, 1, -1):
        if n % (j * j) == 0:
            largest_sq_factor = j * j
            break
    coeff = isqrt(largest_sq_factor)
    radicand = n // largest_sq_factor
    return coeff, radicand


# --- Problem Generation Functions ---

def generate_complete_the_square_expression():
    """
    Type 1: Given x²+bx+___, find the constant to make it a perfect square.
    e.g., x²＋12x＋____ = (x+____)²
    """
    b = random.choice(list(range(-15, 0)) + list(range(1, 16)))
    p = Fraction(b, 2)
    p_squared = p * p

    b_sign = "+" if b > 0 else "-"
    b_abs = abs(b)
    
    # Question text uses LaTeX for display
    question_text = f"在下列各空格中分別填入適當的數，使等式成為完全平方式：$x² {b_sign} {b_abs}x + \\_\\_\\_ = (x + \\_\\_\\_ )²$"

    # Answer uses plain text format (e.g., '49/4', '-7/2')
    answer_p_squared = format_fraction_plain(p_squared)
    answer_p = format_fraction_plain(p)
    correct_answer = f"{answer_p_squared},{answer_p}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_solve_a_is_1():
    """
    Type 2: Solve quadratic equations where a=1.
    e.g., x²+2x-2=0
    """
    if random.random() < 0.6: # Generate problem with integer solutions
        h = random.randint(-8, 8)
        k = random.randint(1, 15)
        # Ensure roots are distinct
        while k == 0:
            k = random.randint(1, 15)

        b = -2 * h
        c = h**2 - k**2
        x1 = h + k
        x2 = h - k
        correct_answer = f"{x1},{x2}"
    else: # Generate problem with irrational solutions
        h = random.randint(-6, 6)
        k_inner = random.choice([2, 3, 5, 6, 7, 10, 11, 13, 14, 15])

        b = -2 * h
        c = h**2 - k_inner
        
        h_str = "" if h == 0 else str(h)
        correct_answer = f"{h_str}+-sqrt({k_inner})"
        
    eq_x2_term = format_term(1, "x²", is_leading=True)
    eq_x_term = format_term(b, "x")
    eq_c_term = format_term(c, "")
    
    equation = f"{eq_x2_term}{eq_x_term}{eq_c_term} = 0".replace("  ", " ").strip()
    question_text = f"利用配方法解下列一元二次方程式：${equation}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_solve_a_is_not_1():
    """
    Type 3: Solve quadratic equations where a is not 1.
    Can result in two roots, one repeated root, or no solution.
    e.g., 2x²-8x+3=0
    """
    outcome = random.choice(['distinct', 'repeated', 'no_solution'])

    if outcome == 'repeated':
        h = random.randint(-8, 8)
        a = random.choice([-3, -2, 2, 3, 4])
        b = a * (-2 * h)
        c = a * (h**2)
        correct_answer = f"{h} (重根)"

    elif outcome == 'no_solution':
        h = random.randint(-5, 5)
        k = random.randint(1, 12) # This k becomes part of the positive constant term
        a = random.choice([-3, -2, 2, 3])
        b = a * (-2 * h)
        c = a * (h**2 + k)
        correct_answer = "無解"
        
    else: # 'distinct'
        # Construct from solution x = (num ± sqrt(D))/den
        den = random.randint(2, 4)
        num = random.randint(-5 * (den // 2), 5 * (den // 2))
        
        # Ensure D is not a perfect square and D > 0
        D_inner = random.choice([2, 3, 5, 6, 7, 10])
        s_coeff = random.randint(1, 3)
        D = D_inner * (s_coeff ** 2)
        
        a = den**2
        b = -2 * num * den
        c = num**2 - D
        
        common_divisor = gcd(abs(a), gcd(abs(b), abs(c)))
        a //= common_divisor
        b //= common_divisor
        c //= common_divisor

        if a < 0: # Conventionally, lead with a positive 'a'
            a, b, c = -a, -b, -c
        
        if a == 1: # Failsafe to ensure it's not a type 2 problem
            a *= random.randint(2,3)
            b *= a
            c *= a

        # Format the answer string (plain text)
        s_str = "" if s_coeff == 1 else str(s_coeff)
        if den == 1:
            num_str = "" if num == 0 else str(num)
            correct_answer = f"{num_str}+-{s_str}sqrt({D_inner})"
        else:
            # Simplify fraction if possible
            g = gcd(abs(num), gcd(s_coeff, den))
            num_s, s_coeff_s, den_s = num//g, s_coeff//g, den//g
            s_str_s = "" if s_coeff_s == 1 else str(s_coeff_s)
            
            if den_s == 1:
                num_str_s = "" if num_s == 0 else str(num_s)
                correct_answer = f"{num_str_s}+-{s_str_s}sqrt({D_inner})"
            else:
                 correct_answer = f"({num_s}+-{s_str_s}sqrt({D_inner}))/{den_s}"

    eq_x2_term = format_term(a, "x²", is_leading=True)
    eq_x_term = format_term(b, "x")
    eq_c_term = format_term(c, "")
    
    equation = f"{eq_x2_term}{eq_x_term}{eq_c_term} = 0".replace("  ", " ").strip()
    question_text = f"利用配方法解下列一元二次方程式：${equation}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_error_analysis():
    """
    Type 4: Find the error in a given solution process.
    """
    # Create an equation x² + bx - c = 0 where b is odd
    b = random.choice([-7, -5, -3, 3, 5, 7])
    D = -1
    c = 0
    # Ensure D = b² + 4c is positive and not a perfect square
    while D <= 0 or isqrt(D)**2 == D:
        c = random.randint(1, 15)
        D = b**2 + 4*c

    # Incorrect working
    b_sign = "+" if b > 0 else "-"
    b_abs = abs(b)
    c_rhs = c
    b_sq = b**2
    rhs = c + b_sq
    
    incorrect_steps = f"""$x² {b_sign} {b_abs}x - {c} = 0$
$x² {b_sign} {b_abs}x = {c_rhs}$
$x² {b_sign} {b_abs}x + {b_sq} = {c_rhs} + {b_sq}$
$(x {b_sign} {b})² = {rhs}$
$x {b_sign} {b} = \\pm\\sqrt{{{rhs}}}$
$x = {-b} \\pm \\sqrt{{{rhs}}}$"""
    
    question_text = f"小翊利用配方法解一元二次方程式 $x²{format_term(b, 'x')}{format_term(-c, '')} = 0$，他的過程如下：{incorrect_steps}\n"
    question_text += "判斷他的解法是否正確？若不正確，請直接寫出正確的解法。"

    # Correct solution
    s_coeff, D_inner = simplify_sqrt(D)
    den = 2
    num = -b
    
    g = gcd(abs(num), gcd(s_coeff, den))
    num_s, s_coeff_s, den_s = num//g, s_coeff//g, den//g
    
    s_str_s = "" if s_coeff_s == 1 else str(s_coeff_s)
    
    if den_s == 1:
        num_str_s = "" if num_s == 0 else str(num_s)
        correct_answer = f"{num_str_s}+-{s_str_s}sqrt({D_inner})"
    else:
        correct_answer = f"({num_s}+-{s_str_s}sqrt({D_inner}))/{den_s}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem for solving quadratic equations by completing the square.
    """
    # Adjust problem type distribution based on level if needed
    problem_type = random.choice([
        'complete_expression', 
        'solve_a_is_1', 
        'solve_a_is_not_1', 
        'error_analysis'
    ])
    
    if problem_type == 'complete_expression':
        return generate_complete_the_square_expression()
    elif problem_type == 'solve_a_is_1':
        return generate_solve_a_is_1()
    elif problem_type == 'solve_a_is_not_1':
        return generate_solve_a_is_not_1()
    else: # 'error_analysis'
        return generate_error_analysis()

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles different formats like 'a,b', 'b,a', and 'x (重根)'.
    """
    user_ans = user_answer.strip().replace(' ', '').replace('或', ',').lower()
    correct_ans = correct_answer.strip().replace(' ', '').lower()
    
    is_correct = False
    
    if "," in correct_ans:
        parts = correct_ans.split(',')
        if len(parts) == 2:
            rev_ans = f"{parts[1]},{parts[0]}"
            if user_ans == correct_ans or user_ans == rev_ans:
                is_correct = True
    elif "(重根)" in correct_ans:
        num_part = correct_ans.split("(重根)")[0]
        if user_ans == correct_ans or user_ans == num_part:
            is_correct = True
    else:
        # For answers like '2+-sqrt(3)' or '無解'
        # A simple string comparison is sufficient
        is_correct = (user_ans == correct_ans)

    # Re-format correct_answer with LaTeX for display
    # (This is a simplified version; a full implementation might need more context)
    display_answer = correct_answer.replace("+-", " \\pm ").replace("sqrt(", "\\sqrt{").replace(")", "}")
    
    if is_correct:
        result_text = f"完全正確！答案是 ${display_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}