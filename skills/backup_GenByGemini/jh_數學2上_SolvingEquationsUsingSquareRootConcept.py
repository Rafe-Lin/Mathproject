import random
from fractions import Fraction
import math

def gcd(a, b):
    """Computes the greatest common divisor of a and b."""
    return math.gcd(a, b)

def simplify_sqrt(n):
    """
    Simplifies a square root.
    Returns a tuple (coefficient, radicand).
    e.g., simplify_sqrt(12) returns (2, 3) for 2√3.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return (1, 0)
    if n == 1:
        return (1, 1)

    i = int(math.sqrt(n))
    while i > 1:
        if n % (i * i) == 0:
            return (i, n // (i * i))
        i -= 1
    return (1, n)

def format_sqrt(coeff, radicand, pm=False):
    """Formats a simplified square root into a LaTeX string."""
    pm_str = "\\pm" if pm else ""
    if radicand == 0:
        return "0"
    if radicand == 1:
        return f"{pm_str}{coeff}"
    if coeff == 1:
        return f"{pm_str}\\sqrt{{{radicand}}}"
    return f"{pm_str}{coeff}\\sqrt{{{radicand}}}"

def format_fraction(f):
    """Formats a Fraction object into a LaTeX string, handling integers."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def generate_type1_simple_square():
    """
    Generates a problem of the form x² = k.
    """
    if random.random() < 0.6:  # k is a perfect square
        n = random.randint(2, 15)
        k = n * n
        answer = f"x=\\pm{n}"
    else:  # k is not a perfect square
        while True:
            k = random.randint(2, 50)
            if int(math.sqrt(k)) ** 2 != k:
                break
        coeff, rad = simplify_sqrt(k)
        answer = f"x={format_sqrt(coeff, rad, pm=True)}"

    # 修正：移除 \n，改用 <br> 並放在 $ 外面
    question_text = f"解下列一元二次方程式：<br>$x^2 = {k}$"
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_type2_shifted_square():
    """
    Generates a problem of the form (x+b)² = c.
    """
    b = random.randint(1, 10) * random.choice([-1, 1])
    b_op = '+' if b > 0 else '-'
    b_val = abs(b)
    lhs_str = f"(x {b_op} {b_val})^2"

    if random.random() < 0.6:  # c is a perfect square
        n = random.randint(2, 12)
        c = n * n
        sol1 = -b + n
        sol2 = -b - n
        # Order the solutions, larger one first
        if sol1 < sol2:
            sol1, sol2 = sol2, sol1
        answer = f"x={sol1} 或 x={sol2}"
    else:  # c is not a perfect square
        while True:
            c = random.randint(2, 30)
            if int(math.sqrt(c)) ** 2 != c:
                break
        coeff, rad = simplify_sqrt(c)
        sqrt_c_str = format_sqrt(coeff, rad)
        neg_b = -b
        answer = f"x={neg_b}\\pm{sqrt_c_str}"

    # 修正：移除 \n，改用 <br> 並放在 $ 外面
    question_text = f"解下列一元二次方程式：<br>${lhs_str} = {c}$"
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_type3_rearrange_square():
    """
    Generates a problem of the form (ax+b)² + d = f, requiring rearrangement.
    """
    a = random.choice([1, 1, 1, 2, 3, 4, 5])
    b = random.randint(1, 9) * random.choice([-1, 1])
    b_op = '+' if b > 0 else '-'
    b_val = abs(b)

    if a == 1:
        lhs_str = f"(x {b_op} {b_val})^2"
    else:
        lhs_str = f"({a}x {b_op} {b_val})^2"

    term_to_move = random.randint(1, 25)
    op_move = random.choice(['+', '-'])

    # 修正：移除 \n，改用 <br> 並放在 $ 外面
    if op_move == '+':  # (ax+b)² + term = c_rhs
        c_rhs = random.randint(term_to_move + 2, 60)
        c = c_rhs - term_to_move
        question_text = f"解下列一元二次方程式：<br>${lhs_str} + {term_to_move} = {c_rhs}$"
    else:  # (ax+b)² - term = c_rhs
        c_rhs = random.randint(1, 40)
        c = c_rhs + term_to_move
        question_text = f"解下列一元二次方程式：<br>${lhs_str} - {term_to_move} = {c_rhs}$"

    is_c_perfect = (int(math.sqrt(c)) ** 2 == c)

    if is_c_perfect:
        n = int(math.sqrt(c))
        sol1 = Fraction(-b + n, a)
        sol2 = Fraction(-b - n, a)
        
        # Order the solutions
        if sol1 < sol2:
            sol1, sol2 = sol2, sol1

        sol1_str = format_fraction(sol1)
        sol2_str = format_fraction(sol2)
        answer = f"x={sol1_str} 或 x={sol2_str}"
    else:
        coeff, rad = simplify_sqrt(c)
        sqrt_c_str = format_sqrt(coeff, rad)
        neg_b = -b
        
        if a == 1:
            answer = f"x={neg_b}\\pm{sqrt_c_str}"
        else:
            answer = f"x=\\frac{{{neg_b}\\pm{sqrt_c_str}}}{{{a}}}"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate(level=1):
    """
    Generates a problem for solving quadratic equations using the square root concept.
    
    Skill ID: jh_數學2上_SolvingEquationsUsingSquareRootConcept
    Topic: 當一元二次方程式可整理成 x²=k 或 (ax+b)²=c (c≥0) 的形式時，可直接利用平方根的概念求解。
    """
    # Choose a problem type based on increasing complexity
    problem_type = random.choice(['type1', 'type2', 'type2', 'type3', 'type3'])
    
    if problem_type == 'type1':
        return generate_type1_simple_square()
    elif problem_type == 'type2':
        return generate_type2_shifted_square()
    else: # type3
        return generate_type3_rearrange_square()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles different orderings for answers with '或'.
    """
    # Normalize by removing spaces and the leading "x="
    norm_user = user_answer.strip().replace(" ", "").replace("x=", "")
    norm_correct = correct_answer.strip().replace(" ", "").replace("x=", "")

    is_correct = False
    
    # Handle answers with two distinct solutions like "a 或 b"
    if "或" in norm_correct:
        try:
            # Split and sort to handle order differences
            parts_correct = sorted(norm_correct.split("或"))
            parts_user = sorted(norm_user.split("或"))
            if parts_correct == parts_user:
                is_correct = True
        except:
            # Fallback if user input is not as expected
            is_correct = (norm_user == norm_correct)
    else:
        # Direct comparison for answers like x=±5 or x=2±√3
        if norm_user == norm_correct:
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}