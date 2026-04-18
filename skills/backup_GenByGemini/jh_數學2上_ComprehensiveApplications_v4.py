import random
from fractions import Fraction
import math
import re

# --- Helper Functions ---

def _format_fraction(f: Fraction) -> str:
    """Formats a Fraction object into a string, omitting the denominator if it's 1."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def _is_perfect_square(n: int) -> bool:
    """Checks if a non-negative integer is a perfect square."""
    if n < 0:
        return False
    if n == 0:
        return True
    x = int(math.sqrt(n))
    return x * x == n

# --- Problem Type Generators ---

def _generate_expand_and_solve():
    """
    Type 1: Generates an equation of the form (ax+b)(cx+d)=e that needs to be solved.
    The equation is guaranteed to have rational roots.
    """
    while True:
        a = random.choice([1, 2])
        c = 1
        b = random.randint(-7, 7)
        d = random.randint(-7, 7)
        e = random.randint(-20, 20)

        # Ensure a non-trivial problem
        if b == 0 or d == 0 or e == 0 or b == d or a*d + b*c == 0:
            continue

        # The simplified equation is Ax^2 + Bx + C = 0
        A = a * c
        B = a * d + b * c
        C = b * d - e

        if C == 0:
            continue

        # The discriminant must be a perfect square for the roots to be rational.
        discriminant = B**2 - 4 * A * C
        if _is_perfect_square(discriminant):
            sqrt_d = int(math.sqrt(discriminant))
            sol1 = Fraction(-B + sqrt_d, 2 * A)
            sol2 = Fraction(-B - sqrt_d, 2 * A)

            if sol1 != sol2:
                break

    # Format the question string for display
    term1_x = f"{a}x" if a != 1 else "x"
    term1 = f"({term1_x} + {b})" if b > 0 else f"({term1_x} - {-b})"
    term2_x = "x"  # c is always 1
    term2 = f"({term2_x} + {d})" if d > 0 else f"({term2_x} - {-d})"
    
    question_text = f"解一元二次方程式 ${term1}{term2}={e}$。"

    # Format the answer string, with roots sorted numerically
    roots = sorted([sol1, sol2])
    answer_str1 = _format_fraction(roots[0])
    answer_str2 = _format_fraction(roots[1])
    correct_answer = f"{answer_str1} 和 {answer_str2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_find_other_root():
    """
    Type 2: Generates a problem where one root is given, and the student must find the other.
    The equation contains an unknown parameter 'm'.
    """
    while True:
        # Based on (r1+k)(r2+k) = k^2, where k is the ratio of the coefficients of m.
        k = random.choice([-4, -3, -2, 2, 3, 4])
        
        # Find integer factors of k^2
        factors_k_sq = []
        for i in range(1, abs(k) + 1):
            if (k*k) % i == 0:
                factors_k_sq.append((i, k*k // i))
                factors_k_sq.append((-i, -(k*k // i)))
        
        if not factors_k_sq: continue
        
        u, v = random.choice(factors_k_sq)
        if u == v: continue

        r1 = u - k
        r2 = v - k

        if r1 == 0 or r2 == 0 or r1 == r2:
            continue
        
        # Define the structure of the equation, e.g., x^2 - mx - 4m = 0
        p = random.choice([-1, 1])
        q = k * p

        # Calculate m from the roots: m = -(r1+r2)/p
        m_val = -(r1 + r2) / p
        if m_val == int(m_val) and m_val != 0:
            m = int(m_val)
            break
    
    # Construct the equation string with the parameter 'm'
    def format_m_term(coeff, var):
        if coeff == 0: return ""
        sign = "+ " if coeff > 0 else "- "
        abs_coeff = abs(coeff)
        if abs_coeff == 1:
            return f"{sign}{var}"
        return f"{sign}{abs_coeff}{var}"

    x_term_str = format_m_term(p, "mx")
    c_term_str = format_m_term(q, "m")

    eq_str = f"x^2 {x_term_str}{c_term_str}"
    eq_str = eq_str.replace(" + -", " - ")

    # Randomly choose which root to give
    given_root = random.choice([r1, r2])
    other_root = r2 if given_root == r1 else r1

    question_text = f"若 x 的一元二次方程式 ${eq_str}=0$ 的一根為 ${given_root}$，則此一元二次方程式的另一根為多少？"
    correct_answer = str(other_root)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_find_coeffs_from_roots():
    """
    Type 3: Generates a problem where two roots are given, and the student must find
    the unknown coefficients 'a' and 'b'.
    """
    while True:
        # Generate two distinct non-zero rational roots
        n1, d1 = random.randint(-5, 5), random.randint(1, 2)
        n2, d2 = random.randint(-5, 5), random.randint(1, 3)
        if n1 == 0 or n2 == 0: continue
        
        r1 = Fraction(n1, d1)
        r2 = Fraction(n2, d2)

        if r1 != r2:
            break

    # Get simplified numerators and denominators for the roots
    n1, d1 = r1.numerator, r1.denominator
    n2, d2 = r2.numerator, r2.denominator

    # Determine coefficients from the factored form: (d1*x - n1)(d2*x - n2) = 0
    # which expands to: d1*d2*x^2 - (d1*n2 + d2*n1)*x + n1*n2 = 0
    A = d1 * d2
    B = -(d1 * n2 + d2 * n1)
    C = n1 * n2
    
    # Ensure the coefficients are in their simplest integer form
    common_divisor = math.gcd(math.gcd(A, B), C)
    A //= common_divisor
    B //= common_divisor
    C //= common_divisor

    # The problem will be of the form ax^2 + bx + C = 0, where C is known
    # and a, b are to be found.
    if C == 0: # Ensure the known part is non-zero to avoid ambiguity
        return _generate_find_coeffs_from_roots()

    eq_parts = ["ax^2", "+ bx"]
    if C > 0:
        eq_parts.append(f"+ {C}")
    else:
        eq_parts.append(f"- {-C}")
    
    eq_str = ' '.join(eq_parts).replace('+ -', '-')
    
    r1_str = _format_fraction(r1)
    r2_str = _format_fraction(r2)
    
    question_text = f"若 x 的一元二次方程式 ${eq_str}=0$ 的兩個解為 ${r1_str}$ 和 ${r2_str}$，則 a、b 的值為多少？"
    correct_answer = f"a={A}、b={B}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    Generates a question for the 'Comprehensive Applications' of quadratic equations skill.
    
    Three types of problems are included:
    1. Solving equations requiring expansion and simplification.
    2. Finding the other root given one root and an equation with a parameter.
    3. Finding unknown coefficients given the two roots of an equation.
    """
    problem_type = random.choice(['expand_and_solve', 'find_other_root', 'find_coeffs_from_roots'])
    
    if problem_type == 'expand_and_solve':
        return _generate_expand_and_solve()
    elif problem_type == 'find_other_root':
        return _generate_find_other_root()
    else: # find_coeffs_from_roots
        return _generate_find_coeffs_from_roots()

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer for all problem types.
    Handles multiple roots (order-insensitive) and coefficient-value pairs.
    """
    user_answer = user_answer.strip()
    is_correct = False

    # Type 3 check: Handles answers like "a=1、b=-3"
    if '=' in correct_answer:
        try:
            correct_pairs = re.findall(r'([a-zA-Z])\s*=\s*(-?\d+)', correct_answer)
            user_pairs = re.findall(r'([a-zA-Z])\s*=\s*(-?\d+)', user_answer)
            correct_dict = {k.lower(): int(v) for k, v in correct_pairs}
            user_dict = {k.lower(): int(v) for k, v in user_pairs}
            if correct_dict and user_dict: # Ensure parsing was successful
                is_correct = (correct_dict == user_dict)
        except (ValueError, IndexError):
            is_correct = False

    # Type 1 check: Handles answers with two roots, e.g., "-6 和 -1/2"
    elif '和' in correct_answer:
        try:
            # Find all numbers and fractions in both strings
            correct_nums_str = re.findall(r'-?\d+(?:/\d+)?', correct_answer)
            user_nums_str = re.findall(r'-?\d+(?:/\d+)?', user_answer)
            
            # Compare the sets of roots to ignore order
            if len(correct_nums_str) == len(user_nums_str) and len(user_nums_str) > 0:
                correct_set = set(Fraction(n) for n in correct_nums_str)
                user_set = set(Fraction(n) for n in user_nums_str)
                is_correct = (correct_set == user_set)
        except (ValueError, IndexError):
            is_correct = False

    # Type 2 check: Handles a single numerical answer
    else:
        try:
            is_correct = (Fraction(user_answer) == Fraction(correct_answer))
        except (ValueError, ZeroDivisionError):
            is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}