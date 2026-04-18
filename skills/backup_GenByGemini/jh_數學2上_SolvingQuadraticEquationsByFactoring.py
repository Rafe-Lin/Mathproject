import random
from fractions import Fraction
import re
import math

# --- Helper Functions for Formatting ---

def _format_polynomial(coeffs, var='x'):
    """Formats a list of coefficients [a, b, c] into a LaTeX string like 'ax^2 + bx + c'."""
    terms = []
    # Iterate in reverse to handle powers correctly
    for i, c in enumerate(reversed(coeffs)):
        power = i
        if c == 0:
            continue
        
        # Coefficient part
        if power > 0: # x^n term
            if c == 1:
                coeff_str = ""
            elif c == -1:
                coeff_str = "-"
            else:
                coeff_str = str(c)
        else: # constant term
            coeff_str = str(c)
            
        # Variable part
        if power == 0:
            var_str = ""
        elif power == 1:
            var_str = var
        else:
            var_str = f"{var}^{{{power}}}"
            
        terms.append(f"{coeff_str}{var_str}")
        
    if not terms:
        return "0"
        
    # Join with signs, from highest power to lowest
    result = terms[-1]
    for term in reversed(terms[:-1]):
        if str(term).startswith('-'):
            result += f" - {str(term)[1:]}"
        else:
            result += f" + {term}"
            
    return result

def _format_linear_term(a, b, var='x'):
    """Formats (ax+b) into a string, without parentheses if simple."""
    if a == 0:
        return str(b)
    
    term_a_str = ""
    if a == 1:
        term_a_str = var
    elif a == -1:
        term_a_str = f"-{var}"
    else:
        term_a_str = f"{a}{var}"
        
    if b == 0:
        return term_a_str
    
    op = "+" if b > 0 else "-"
    return f"{term_a_str} {op} {abs(b)}"

def _format_fraction_display(f):
    """Formats a Fraction object for display."""
    if f.denominator == 1:
        return str(f.numerator)
    else:
        return f"{f.numerator}/{f.denominator}"

def _format_answer(roots):
    """Formats a list of roots into the final answer string."""
    if len(roots) == 2 and roots[0] == roots[1]:
        return f"${_format_fraction_display(roots[0])}$ (重根)"
    
    # Sort roots numerically for consistent answer format
    sorted_roots = sorted(roots)
    
    formatted_roots = [f"${_format_fraction_display(r)}$" for r in sorted_roots]
    return " 和 ".join(formatted_roots)

# --- Generator Functions for Different Problem Types ---

def generate_pre_factored():
    """Generates a problem that is already in factored form."""
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(1, 3)
    d = random.randint(-5, 5)
    
    # Ensure the two factors are different to avoid accidental repeated roots
    while a * d == b * c:
        d = random.randint(-5, 5)

    factor1 = f"({_format_linear_term(a, b)})"
    if a == 1 and b == 0:
        factor1 = "x"
    
    factor2 = f"({_format_linear_term(c, d)})"
    if c == 1 and d == 0:
        factor2 = "x"
        
    question_text = f"找出下列方程式的解：${factor1}{factor2}=0$"
    
    root1 = Fraction(-b, a)
    root2 = Fraction(-d, c)
    
    answer = _format_answer([root1, root2])
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_common_factor():
    """Generates a problem solvable by taking out a common factor."""
    # Type 1: ax^2 + bx = 0
    if random.random() < 0.6:
        a = random.randint(1, 5)
        b = random.randint(-7, 7)
        while b == 0:
            b = random.randint(-7, 7)
            
        poly_str = _format_polynomial([b, a]) # coeffs are [c, b, a] for ax^2+bx+c
        question_text = f"解下列一元二次方程式：${poly_str}=0$"
        
        root1 = Fraction(0)
        root2 = Fraction(-b, a)
        
        answer = _format_answer([root1, root2])

    # Type 2: (x-k)(ax+b) = (x-k)(cx+d)
    else:
        k = random.randint(-5, 5)
        a = random.randint(1, 4)
        b = random.randint(-5, 5)
        c = random.randint(1, 4)
        d = random.randint(-5, 5)
        
        # Ensure it remains a quadratic equation after simplification (a != c)
        while a == c:
            c = random.randint(1, 4)
            
        common_factor = f"({_format_linear_term(1, -k)})"
        side1_factor = f"({_format_linear_term(a, b)})"
        side2_factor = f"({_format_linear_term(c, d)})"
        
        question_text = f"解下列一元二次方程式：${common_factor}{side1_factor} = {common_factor}{side2_factor}$"

        root1 = Fraction(k)
        root2 = Fraction(d - b, a - c)
        
        answer = _format_answer([root1, root2])

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_formula_factoring():
    """Generates a problem solvable using perfect square or difference of squares formulas."""
    # Type 1: Difference of Squares, (ax)^2 - b^2 = 0
    if random.random() < 0.5:
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        
        A = a * a
        C = -b * b
        
        # Randomly swap terms
        if random.choice([True, False]):
            poly_str = _format_polynomial([C, 0, A])
            question_text = f"解下列一元二次方程式：${poly_str}=0$"
        else:
            poly_str = _format_polynomial([0, 0, A])
            question_text = f"解下列一元二次方程式：${poly_str}={-C}$"

        root1 = Fraction(b, a)
        root2 = Fraction(-b, a)
        answer = _format_answer([root1, root2])
        
    # Type 2: Perfect Square, (ax +/- b)^2 = 0
    else:
        a = random.randint(1, 4)
        b = random.randint(1, 5)
        sign = random.choice([-1, 1])
        
        b_signed = b * sign
        
        A = a * a
        B = 2 * a * b_signed
        C = b * b
        
        poly_str = _format_polynomial([C, B, A])
        question_text = f"解下列一元二次方程式：${poly_str}=0$"
        
        root = Fraction(-b_signed, a)
        answer = _format_answer([root, root])
        
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_cross_multiplication():
    """Generates a problem solvable by cross-multiplication."""
    r1_den = random.randint(1, 3)
    r1_num = random.randint(-5, 5)
    r1 = Fraction(r1_num, r1_den)
    
    r2_den = random.randint(1, 3)
    r2_num = random.randint(-5, 5)
    r2 = Fraction(r2_num, r2_den)
    
    # Ensure roots are not zero, not equal, and not opposites
    while r1 == 0 or r2 == 0 or r1 == r2 or r1 == -r2:
        r2_den = random.randint(1, 3)
        r2_num = random.randint(-5, 5)
        r2 = Fraction(r2_num, r2_den)
        
    a, b = r1.denominator, -r1.numerator
    c, d = r2.denominator, -r2.numerator
    
    A, B, C = a * c, a * d + b * c, b * d
    
    multiplier = random.choice([-2, -1, 1, 2, 3])
    if multiplier == 0: multiplier = 1
    A, B, C = A * multiplier, B * multiplier, C * multiplier
    
    form_type = random.choice(['std', 'moved_c', 'moved_b'])
    if form_type == 'std':
        poly_str = _format_polynomial([C, B, A])
        question_text = f"利用十字交乘法，解一元二次方程式 ${poly_str}=0$。"
    elif form_type == 'moved_c':
        poly_str = _format_polynomial([0, B, A])
        question_text = f"利用十字交乘法，解一元二次方程式 ${poly_str}={-C}$。"
    else:
        poly_str = _format_polynomial([C, 0, A])
        question_text = f"利用十字交乘法，解一元二次方程式 ${poly_str}={-B}x$。"
        
    answer = _format_answer([r1, r2])
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }


def generate(level=1):
    """
    生成「利用因式分解解一元二次方程式」相關題目。
    涵蓋：
    1. 已因式分解
    2. 提公因式法
    3. 乘法公式（平方差、和的平方、差的平方）
    4. 十字交乘法
    """
    problem_generators = {
        'pre_factored': generate_pre_factored,
        'common_factor': generate_common_factor,
        'formula_factoring': generate_formula_factoring,
        'cross_multiplication': generate_cross_multiplication
    }
    
    problem_type = random.choices(
        list(problem_generators.keys()), 
        weights=[0.15, 0.25, 0.25, 0.35], 
        k=1
    )[0]
    
    return problem_generators[problem_type]()


def _parse_roots(answer_str):
    """Parses a string answer into a sorted list of Fraction objects."""
    answer_str = answer_str.strip()
    is_repeated = "重根" in answer_str
    
    numbers_str = re.findall(r'-?\d+(?:/\d+)?', answer_str)
    
    if not numbers_str:
        return []
        
    roots = []
    for s in numbers_str:
        try:
            roots.append(Fraction(s))
        except (ValueError, ZeroDivisionError):
            pass
            
    if is_repeated and len(roots) == 1:
        roots.append(roots[0])
        
    return sorted(roots)

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    此函數能處理不同順序、不同格式的答案。
    """
    user_roots = _parse_roots(user_answer)
    correct_roots = _parse_roots(correct_answer)
    
    is_correct = (user_roots == correct_roots) and (len(user_roots) > 0)
    
    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}