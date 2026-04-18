import random
from fractions import Fraction
import math # Not explicitly used for math functions, but Fraction might use it internally for gcd

def poly_to_string(coeffs):
    """
    Converts a list of polynomial coefficients to a string representation for LaTeX display.
    Coefficients are ordered from highest degree to constant term: [c_n, c_{n-1}, ..., c_1, c_0].
    Example: [1, -2, 3] -> "x^2 - 2x + 3"
    """
    if not coeffs:
        return "0"

    terms = []
    degree = len(coeffs) - 1
    first_term_found = False

    for i, coeff in enumerate(coeffs):
        current_degree = degree - i
        
        if coeff == 0:
            continue

        abs_coeff = abs(coeff)
        coeff_str = ""
        if current_degree == 0: # Constant term
            coeff_str = str(abs_coeff)
        elif abs_coeff == 1: # Coefficient is 1 or -1, don't show '1' explicitly for x terms
            coeff_str = ""
        else:
            coeff_str = str(abs_coeff)

        term_part = ""
        if current_degree == 1:
            term_part = f"{coeff_str}x"
        elif current_degree > 1:
            term_part = f"{coeff_str}x^{{{{ {current_degree} }}}}" # Double braces for LaTeX exponent
        elif current_degree == 0: # Constant term
            term_part = coeff_str

        # Determine sign and append to terms list
        if not first_term_found:
            if coeff < 0:
                terms.append(f"-{term_part}")
            else:
                terms.append(term_part)
            first_term_found = True
        else:
            if coeff < 0:
                terms.append(f"- {term_part}") # Add space for readability
            else:
                terms.append(f"+ {term_part}") # Add space for readability

    if not terms:
        return "0"
    
    return "".join(terms).strip()

def evaluate_poly(coeffs, x_val):
    """
    Evaluates a polynomial at a given x_val.
    coeffs: list of coefficients [c_n, c_{n-1}, ..., c_0]
    x_val: the value to substitute for x. Can be an integer or a Fraction.
    """
    result = Fraction(0)
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        current_degree = degree - i
        result += Fraction(coeff) * (x_val ** current_degree)
    return result

def generate_direct_remainder_by_linear():
    """
    Generates a problem: Given f(x) and a linear divisor (x-a) or (ax-b), find the remainder.
    """
    degree = random.randint(2, 4)
    coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
    # Ensure leading coefficient is not zero
    while coeffs[0] == 0:
        coeffs[0] = random.randint(-5, 5)
    
    # Ensure not all coeffs are zero
    if all(c == 0 for c in coeffs):
        coeffs[random.randint(0, degree)] = random.choice([-2, -1, 1, 2])

    f_x_str = poly_to_string(coeffs)

    # Choose divisor type: x-a or ax-b
    divisor_type = random.choice(['x_minus_a', 'ax_minus_b'])

    if divisor_type == 'x_minus_a':
        a_val = random.randint(-3, 3)
        while a_val == 0: # Avoid x-0 which is x
            a_val = random.randint(-3, 3)
        
        divisor_str = f"x - ({a_val})" if a_val < 0 else f"x - {a_val}"
        if a_val == 1: divisor_str = "x - 1"
        if a_val == -1: divisor_str = "x + 1"

        eval_point = Fraction(a_val)
        question_text = f"已知多項式 $f(x) = {f_x_str}$，求 $f(x)$ 除以 $({divisor_str})$ 的餘式。"
    else: # ax_minus_b
        a_div = random.randint(2, 4) # a for ax-b
        b_div = random.randint(-5, 5) # b for ax-b
        while b_div == 0: # Avoid ax
             b_div = random.randint(-5, 5)

        divisor_str = f"{a_div}x - ({b_div})" if b_div < 0 else f"{a_div}x - {b_div}"
        if b_div == 0: divisor_str = f"{a_div}x" 
        
        eval_point = Fraction(b_div, a_div)
        question_text = f"已知多項式 $f(x) = {f_x_str}$，求 $f(x)$ 除以 $({divisor_str})$ 的餘式。"

    correct_answer_frac = evaluate_poly(coeffs, eval_point)
    correct_answer = str(correct_answer_frac)
    if correct_answer_frac.denominator == 1:
        correct_answer = str(correct_answer_frac.numerator)

    # Solution LaTeX for this type
    eval_point_str_for_latex = str(eval_point)
    if eval_point.denominator == 1:
        eval_point_str_for_latex = str(eval_point.numerator)
    elif eval_point.numerator < 0: # for negative fractions, ensure parentheses
        eval_point_str_for_latex = f"\\left({eval_point_str_for_latex}\\right)"

    solution_latex = (
        f"由餘式定理知，當 $f(x)$ 除以 $({divisor_str})$ 時，餘式為 $f({eval_point_str_for_latex})$。"
        f"<br>$f({eval_point_str_for_latex}) = {f_x_str}$"
        f"<br>代入可得餘式為 ${correct_answer}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_latex": solution_latex
    }

def generate_evaluate_fa():
    """
    Generates a problem asking to evaluate f(a) for a given f(x) and a.
    This implicitly uses the Remainder Theorem (f(a) is the remainder when divided by x-a).
    """
    degree = random.randint(2, 4)
    coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
    while coeffs[0] == 0:
        coeffs[0] = random.randint(-5, 5)

    if all(c == 0 for c in coeffs):
        coeffs[random.randint(0, degree)] = random.choice([-2, -1, 1, 2])

    f_x_str = poly_to_string(coeffs)
    a_val = random.randint(-4, 4)

    question_text = f"已知多項式 $f(x) = {f_x_str}$，求 $f({a_val})$ 的值。"
    
    correct_answer_frac = evaluate_poly(coeffs, Fraction(a_val))
    correct_answer = str(correct_answer_frac)
    if correct_answer_frac.denominator == 1:
        correct_answer = str(correct_answer_frac.numerator)
    
    # Reconstruct f(x) with substitution for solution_latex
    substituted_terms = []
    current_degree = degree
    for coeff in coeffs:
        if coeff != 0:
            coeff_str = str(coeff)
            
            term_val_str = ""
            if current_degree == 0:
                term_val_str = coeff_str
            elif current_degree == 1:
                if coeff == 1:
                    term_val_str = f"({a_val})"
                elif coeff == -1:
                    term_val_str = f"-({a_val})"
                else:
                    term_val_str = f"{coeff_str}({a_val})"
            else: # current_degree > 1
                if coeff == 1:
                    term_val_str = f"({a_val})^{{{{ {current_degree} }}}}"
                elif coeff == -1:
                    term_val_str = f"-({a_val})^{{{{ {current_degree} }}}}"
                else:
                    term_val_str = f"{coeff_str}({a_val})^{{{{ {current_degree} }}}}"
            substituted_terms.append(term_val_str)
        current_degree -= 1
    
    # Join with appropriate signs for clarity in solution
    solution_substituted_str = ""
    first_term_substituted = True
    for term in substituted_terms:
        if first_term_substituted:
            solution_substituted_str += term
            first_term_substituted = False
        else:
            if term.startswith('-'):
                solution_substituted_str += f" {term}"
            else:
                solution_substituted_str += f" + {term}"
    
    solution_latex = (
        f"將 $x={a_val}$ 代入多項式 $f(x)$：<br>"
        f"$f({a_val}) = {solution_substituted_str}$<br>"
        f"計算得 ${correct_answer}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_latex": solution_latex
    }


def generate_quadratic_remainder():
    """
    Generates a problem: Given remainders for x-a and x-b, find remainder for (x-a)(x-b).
    """
    a = random.randint(-3, 3)
    b = random.randint(-3, 3)
    while a == b: # Ensure a and b are distinct
        b = random.randint(-3, 3)
    
    r1 = random.randint(-15, 15)
    r2 = random.randint(-15, 15)

    # f(x) = (x-a)(x-b)q(x) + mx + c
    # f(a) = ma + c = r1
    # f(b) = mb + c = r2

    # Solve for m and c
    # m(a-b) = r1 - r2  => m = (r1 - r2) / (a - b)
    # c = r1 - ma

    m_frac = Fraction(r1 - r2, a - b)
    c_frac = Fraction(r1) - m_frac * Fraction(a)

    remainder_str_parts = []
    
    m_frac_display = m_frac
    if m_frac_display.denominator == 1:
        m_frac_display = m_frac_display.numerator
    
    c_frac_display = c_frac
    if c_frac_display.denominator == 1:
        c_frac_display = c_frac_display.numerator

    if m_frac != 0:
        if m_frac == 1:
            remainder_str_parts.append("x")
        elif m_frac == -1:
            remainder_str_parts.append("-x")
        else:
            remainder_str_parts.append(str(m_frac_display) + "x")

    if c_frac != 0:
        if c_frac > 0:
            if remainder_str_parts:
                remainder_str_parts.append(f"+ {c_frac_display}")
            else:
                remainder_str_parts.append(str(c_frac_display))
        else: # c_frac < 0
            remainder_str_parts.append(f"- {abs(c_frac_display)}")

    correct_answer_display = "".join(remainder_str_parts)
    if not correct_answer_display:
        correct_answer_display = "0"


    # For solution LaTeX
    m_frac_str_latex = str(m_frac)
    if m_frac.denominator == 1:
        m_frac_str_latex = str(m_frac.numerator)
    else:
        m_frac_str_latex = r"\\frac{{{}}}{{{}}}".format(m_frac.numerator, m_frac.denominator)
    
    c_frac_str_latex = str(c_frac)
    if c_frac.denominator == 1:
        c_frac_str_latex = str(c_frac.numerator)
    else:
        c_frac_str_latex = r"\\frac{{{}}}{{{}}}".format(c_frac.numerator, c_frac.denominator)

    # Ensure negative fractions are wrapped in parentheses for clarity in LaTeX calculations
    if m_frac.numerator < 0 and m_frac.denominator != 1:
        m_frac_str_latex = r"\left(" + m_frac_str_latex + r"\right)"
    if c_frac.numerator < 0 and c_frac.denominator != 1:
        c_frac_str_latex = r"\left(" + c_frac_str_latex + r"\right)"

    question_text = (
        f"已知多項式 $f(x)$ 除以 $(x-{a})$ 的餘式為 ${r1}$，且除以 $(x-{b})$ 的餘式為 ${r2}$，"
        f"求 $f(x)$ 除以 $(x-{a})(x-{b})$ 的餘式。"
    )

    solution_latex = (
        r"因為除式 $(x-{a})(x-{b})$ 的次數為2，所以餘式可設為 $ax+b$。"
        r"<br>由除法原理知，恰有一多項式 $q(x)$ 使得 $f(x) = (x-{a})(x-{b})q(x) + (ax+b)$。"
        r"<br>由餘式定理知 $f({a})={r1}$ 且 $f({b})={r2}$。"
        r"<br>將 $x={a}, {b}$ 分別代入餘式 $ax+b$，得："
        r"<br>$a({a})+b = {r1}$ …… (1)"
        r"<br>$a({b})+b = {r2}$ …… (2)"
        r"<br>(1)-(2) 得 $a({a}-{b}) = {r1}-{r2}$"
        r"<br>$a({a-b}) = {r1-r2}$"
        r"<br>$a = \\frac{{{{ {r1-r2} }}}}{{{{ {a-b} }}}} = {m_frac_str_latex}$"
        r"<br>將 $a={m_frac_str_latex}$ 代入 (1) 得 $({m_frac_str_latex})({a})+b = {r1}$"
        r"<br>${str(m_frac * a)} + b = {r1}$"
        r"<br>$b = {r1} - { str(m_frac * a) } = {c_frac_str_latex}$"
        r"<br>故所求餘式為 ${correct_answer_display}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_display,
        "correct_answer": correct_answer_display,
        "solution_latex": solution_latex
    }


def generate(level=1):
    """
    Generates a remainder theorem problem.
    """
    problem_type = random.choice([
        'direct_remainder_linear',
        'evaluate_fa',
        'quadratic_remainder'
    ])

    if problem_type == 'direct_remainder_linear':
        return generate_direct_remainder_by_linear()
    elif problem_type == 'evaluate_fa':
        return generate_evaluate_fa()
    elif problem_type == 'quadratic_remainder':
        return generate_quadratic_remainder()


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles numerical and symbolic answers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Attempt numerical comparison first if possible
    try:
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        if user_frac == correct_frac:
            is_correct = True
    except ValueError:
        pass # Not a simple numerical fraction

    # If not numerical or not correct, try symbolic comparison
    # For symbolic, normalize by removing spaces and converting to lowercase for robust comparison
    if not is_correct:
        user_normalized = user_answer.replace(" ", "").lower().replace("-x", "-1x").replace("x", "1x")
        correct_normalized = correct_answer.replace(" ", "").lower().replace("-x", "-1x").replace("x", "1x")

        # Basic attempt to handle term reordering, only for linear expressions like ax+b
        # This is a simplification and might not cover all equivalent polynomial forms
        try:
            # Parse a simple linear polynomial string into (coefficient_of_x, constant_term)
            def parse_linear(poly_str):
                # Regex to find ax and b parts
                match_x = random.re.search(r'([+-]?\s*\d*(?:/\d+)?)\s*x', poly_str)
                match_const = random.re.search(r'([+-]?\s*\d+(?:/\d+)?)(?![x\d])', poly_str) # Ensure it's not a coefficient of x
                
                coeff_x = Fraction(0)
                const_term = Fraction(0)

                if match_x:
                    coeff_str = match_x.group(1).replace(" ", "")
                    if coeff_str == "+": coeff_x = Fraction(1)
                    elif coeff_str == "-": coeff_x = Fraction(-1)
                    elif coeff_str == "": coeff_x = Fraction(1) # x implies 1x
                    else: coeff_x = Fraction(coeff_str)
                
                # To find constant, temporarily remove x terms to avoid parsing them as constants
                poly_str_no_x_terms = random.re.sub(r'([+-]?\s*\d*(?:/\d+)?)\s*x', '', poly_str)
                
                match_const = random.re.search(r'([+-]?\s*\d+(?:/\d+)?)\s*$', poly_str_no_x_terms.strip()) # Look for a number at the end
                if match_const:
                    const_term = Fraction(match_const.group(1).replace(" ", ""))
                elif not match_x and poly_str.strip(): # If no x term, and string is not empty, it could be a constant
                     try:
                         const_term = Fraction(poly_str.strip())
                     except ValueError:
                         pass

                return (coeff_x, const_term)

            user_parsed = parse_linear(user_answer)
            correct_parsed = parse_linear(correct_answer)
            
            if user_parsed == correct_parsed:
                is_correct = True
        except Exception:
            # Fallback to direct normalized string comparison if parsing fails
            if user_normalized == correct_normalized:
                is_correct = True

    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}