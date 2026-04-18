import random
from fractions import Fraction

# --- Helper functions for polynomial manipulation ---

def term_to_string(exp, coeff, is_first, var='x'):
    """Converts a single term (exponent, coefficient) to a string."""
    # 1. Sign
    sign_str = ""
    if is_first:
        if coeff < 0:
            sign_str = "-"
    else:
        sign_str = " - " if coeff < 0 else " + "
    
    abs_coeff = abs(coeff)
    
    # 2. Coefficient
    coeff_str = ""
    if isinstance(abs_coeff, Fraction):
        if abs_coeff.denominator == 1:
            # It's an integer after simplification
            if abs_coeff.numerator != 1 or exp == 0:
                coeff_str = str(abs_coeff.numerator)
        else:
            # It's a proper fraction
            coeff_str = f"\\frac{{{abs_coeff.numerator}}}{{{abs_coeff.denominator}}}"
    else:  # It's an integer
        if abs_coeff != 1 or exp == 0:
            coeff_str = str(abs_coeff)

    # 3. Variable
    var_str = ""
    if exp > 0:
        var_str = var
        if exp > 1:
             var_str += f"^{exp}" # No curly braces for single digits, as per examples
    
    return f"{sign_str}{coeff_str}{var_str}"

def poly_to_string(poly, var='x'):
    """Converts a polynomial dictionary {power: coeff} to a string in canonical form."""
    if not poly or all(c == 0 for c in poly.values()):
        return "0"

    # Filter out zero-coefficient terms
    non_zero_poly = {exp: coeff for exp, coeff in poly.items() if coeff != 0}
    if not non_zero_poly:
        return "0"
        
    terms = []
    sorted_exponents = sorted(non_zero_poly.keys(), reverse=True)

    # First term
    first_exp = sorted_exponents[0]
    first_coeff = non_zero_poly[first_exp]
    terms.append(term_to_string(first_exp, first_coeff, is_first=True, var=var))
    
    # Subsequent terms
    for exp in sorted_exponents[1:]:
        coeff = non_zero_poly[exp]
        terms.append(term_to_string(exp, coeff, is_first=False, var=var))

    return "".join(terms).strip()

def multiply_polys(p1, p2):
    """Multiplies two polynomial dictionaries."""
    result = {}
    if not p1 or not p2:
        return {}
        
    for exp1, coeff1 in p1.items():
        for exp2, coeff2 in p2.items():
            new_exp = exp1 + exp2
            new_coeff = coeff1 * coeff2
            result[new_exp] = result.get(new_exp, 0) + new_coeff
    return result

# --- Generator for problem types ---

def generate_mono_x_mono():
    """Generates a Monomial × Monomial problem."""
    if random.random() < 0.3:  # (ax^n)^2
        c1 = random.randint(-9, 9)
        while c1 == 0: c1 = random.randint(-9, 9)
        e1 = random.randint(1, 3)
        p1 = {e1: c1}
        
        term1_str = poly_to_string(p1)
        # Add parentheses for clarity
        question_text = f"計算 $({term1_str})^2$。"
            
        result_poly = multiply_polys(p1, p1)
    else:  # (ax^n) * (bx^m)
        use_fractions = random.random() < 0.2
        if use_fractions:
            d1 = random.randint(2, 5)
            n1 = random.randint(1, d1 - 1) * random.choice([-1, 1])
            c1 = Fraction(n1, d1)
            
            d2 = random.randint(2, 5)
            n2 = random.randint(1, d2 - 1) * random.choice([-1, 1])
            c2 = Fraction(n2, d2)
        else:  # Integers
            c1 = random.randint(-9, 9)
            while c1 == 0: c1 = random.randint(-9, 9)
            c2 = random.randint(-9, 9)
            while c2 == 0: c2 = random.randint(-9, 9)

        e1 = random.randint(1, 2)
        e2 = random.randint(1, 2)
        p1 = {e1: c1}
        p2 = {e2: c2}
        
        term1_str = poly_to_string(p1)
        term2_str = poly_to_string(p2)
        
        term1_str = f"({term1_str})" if c1 < 0 or isinstance(c1, Fraction) else term1_str
        term2_str = f"({term2_str})" if c2 < 0 or isinstance(c2, Fraction) else term2_str
            
        question_text = f"計算 ${term1_str} \\cdot {term2_str}$。"
        result_poly = multiply_polys(p1, p2)

    correct_answer = poly_to_string(result_poly)
    return question_text, correct_answer

def generate_mono_x_poly():
    """Generates a Monomial × Polynomial problem."""
    c1 = random.randint(-5, 5)
    while c1 == 0: c1 = random.randint(-5, 5)
    e1 = random.randint(1, 2)
    mono_poly = {e1: c1}
    
    c2 = random.randint(-9, 9)
    while c2 == 0: c2 = random.randint(-9, 9)
    e2 = random.randint(1, 2)
    
    c3 = random.randint(-9, 9)
    while c3 == 0: c3 = random.randint(-9, 9)
    e3 = 0 if e2 > 0 else 1
    
    poly_poly = {e2: c2, e3: c3}
    
    mono_str = poly_to_string(mono_poly)
    poly_str = poly_to_string(poly_poly)
    
    if random.choice([True, False]):
        question_text = f"計算 ${mono_str}({poly_str})$。"
        result_poly = multiply_polys(mono_poly, poly_poly)
    else:
        question_text = f"計算 $({poly_str})({mono_str})$。"
        result_poly = multiply_polys(poly_poly, mono_poly)
        
    correct_answer = poly_to_string(result_poly)
    return question_text, correct_answer

def generate_poly_x_poly():
    """Generates a Polynomial × Polynomial problem, possibly with missing terms."""
    deg1 = random.choice([1, 2])
    p1 = {}
    c1 = random.randint(-5, 5)
    while c1 == 0: c1 = random.randint(-5, 5)
    p1[deg1] = c1
    
    if deg1 == 2:
        if random.random() > 0.3: # 70% chance to have x term
             c_mid = random.randint(-7, 7)
             if c_mid != 0: p1[1] = c_mid
    if random.random() > 0.2: # 80% chance to have constant term
        c_low = random.randint(-9, 9)
        if c_low != 0: p1[0] = c_low

    deg2 = 1
    p2 = {}
    c2 = random.randint(-5, 5)
    while c2 == 0: c2 = random.randint(-5, 5)
    p2[deg2] = c2
    c_low2 = random.randint(-9, 9)
    if c_low2 != 0: p2[0] = c_low2
    
    if len(p1) < 2: p1[0] = random.randint(1, 5) * random.choice([-1, 1])
    if len(p2) < 2: p2[0] = random.randint(1, 5) * random.choice([-1, 1])
    
    p1_str = poly_to_string(p1)
    p2_str = poly_to_string(p2)
    
    question_text = f"計算 $({p1_str})({p2_str})$。"
    result_poly = multiply_polys(p1, p2)
    correct_answer = poly_to_string(result_poly)
    
    return question_text, correct_answer

def generate_formula():
    """Generates a problem solvable by multiplication formulas."""
    formula_type = random.choice(['sum_sq', 'diff_sq', 'prod_sum_diff'])
    
    c1 = random.randint(2, 9)
    c2 = random.randint(2, 9)
    
    if formula_type == 'sum_sq':  # (ax+b)^2
        p1 = {1: c1, 0: c2}
        p1_str = poly_to_string(p1)
        question_text = f"利用乘法公式，計算 $({p1_str})^2$。"
        result_poly = multiply_polys(p1, p1)
        
    elif formula_type == 'diff_sq':  # (ax-b)^2 or (b-ax)^2
        if random.choice([True, False]):  # (ax-b)^2
            p1 = {1: c1, 0: -c2}
        else:  # (b-ax)^2
            p1 = {1: -c1, 0: c2}
        p1_str = poly_to_string(p1)
        question_text = f"利用乘法公式，計算 $({p1_str})^2$。"
        result_poly = multiply_polys(p1, p1)

    else:  # 'prod_sum_diff', (ax+b)(ax-b)
        if random.choice([True, False]):
            p1 = {1: c1, 0: c2}
            p2 = {1: c1, 0: -c2}
        else:
            p1 = {1: c1, 0: -c2}
            p2 = {1: c1, 0: c2}

        p1_str = poly_to_string(p1)
        p2_str = poly_to_string(p2)
        question_text = f"利用乘法公式，計算 $({p1_str})({p2_str})$。"
        result_poly = multiply_polys(p1, p2)
    
    correct_answer = poly_to_string(result_poly)
    return question_text, correct_answer

def generate(level=1):
    """
    生成「多項式乘法」相關題目。
    """
    problem_type = random.choices(
        ['mono_x_mono', 'mono_x_poly', 'poly_x_poly', 'formula'],
        weights=[15, 25, 35, 25],
        k=1
    )[0]
    
    if problem_type == 'mono_x_mono':
        q_text, ans = generate_mono_x_mono()
    elif problem_type == 'mono_x_poly':
        q_text, ans = generate_mono_x_poly()
    elif problem_type == 'poly_x_poly':
        q_text, ans = generate_poly_x_poly()
    else:  # 'formula'
        q_text, ans = generate_formula()

    q_text += "\n(請將答案依 $x$ 的次數由高至低排列作答)"

    return {
        "question_text": q_text,
        "answer": ans,
        "correct_answer": ans
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize by removing all spaces and using standard + and -
    normalized_user = user_answer.strip().replace(" ", "").replace("＋", "+").replace("－", "-")
    normalized_correct = correct_answer.strip().replace(" ", "")

    is_correct = (normalized_user == normalized_correct)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}