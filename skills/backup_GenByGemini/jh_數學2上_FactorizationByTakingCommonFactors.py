import random

# --- Helper Functions ---

def format_poly(coeff_x, const, var='x'):
    """Formats a linear polynomial ax+b into a string."""
    parts = []
    # Handle x term
    if coeff_x != 0:
        if coeff_x == 1:
            parts.append(f"{var}")
        elif coeff_x == -1:
            parts.append(f"-{var}")
        else:
            parts.append(f"{coeff_x}{var}")

    # Handle constant term
    if const != 0:
        if const > 0:
            if parts:  # if there was an x term
                parts.append(f" + {const}")
            else:
                parts.append(f"{const}")
        else:  # const < 0
            parts.append(f" - {abs(const)}")
    
    if not parts:
        return "0"
        
    return "".join(parts)

# --- Problem Type Generators ---

def generate_monomial_common_factor():
    """
    Generates a problem like 2x^2 + 6x = 2x(x+3).
    Form: a*b*x^2 + a*c*x = ax(bx+c)
    """
    var = 'x'
    a = random.randint(2, 6)  # common coefficient
    b = random.randint(1, 5)
    c = random.randint(-9, 9)
    if c == 0: c = random.choice([-1, 1]) * random.randint(1, 5)

    coeff1 = a * b
    coeff2 = a * c

    term1_str = f"{coeff1}{var}^2"
    term2_sign = "+" if coeff2 > 0 else "-"
    term2_str = f" {term2_sign} {abs(coeff2)}{var}"
    question_latex = f"{term1_str}{term2_str}"
    
    factor1 = f"{a}{var}"
    factor2 = f"({format_poly(b, c, var)})"
    
    return {"question_latex": question_latex, "factor1": factor1, "factor2": factor2}

def generate_poly_common_factor_simple():
    """
    Generates a problem like x(2x-1) - x(x+3) = x(x-4).
    Form: M*P1 +/- M*P2 = M(P1 +/- P2), where M is a monomial.
    """
    var = 'x'
    # Common factor M = ax
    a = random.randint(1, 4)
    M_str = f"{a}{var}" if a > 1 else var
    
    # P1 = (bx+c), P2 = (dx+e)
    b, d = random.randint(1, 4), random.randint(1, 4)
    c, e = random.randint(-5, 5), random.randint(-5, 5)
    
    op_char = random.choice(['+', '-'])
    
    # Calculate result and check for trivial cases before forming the question
    if op_char == '+':
        final_x_coeff = b + d
        final_const = c + e
    else:
        final_x_coeff = b - d
        final_const = c - e
        
    # Retry if polynomials are identical and op is '-', or if result is trivial
    if (op_char == '-' and b == d and c == e) or \
       (final_x_coeff == 0 and final_const == 0) or \
       (final_x_coeff == 0 and abs(final_const) == 1):
        return generate_poly_common_factor_simple()

    P1_str = f"({format_poly(b, c, var)})"
    P2_str = f"({format_poly(d, e, var)})"
    question_latex = f"{M_str}{P1_str} {op_char} {M_str}{P2_str}"
    
    factor1 = M_str
    factor2 = f"({format_poly(final_x_coeff, final_const, var)})"
    
    return {"question_latex": question_latex, "factor1": factor1, "factor2": factor2}

def generate_poly_common_factor_advanced():
    """
    Generates a problem like 2(3x-1)^2 + (3x-1) = (3x-1)(6x-1).
    Form: c*P^2 + d*P = P(c*P + d), where P is a polynomial.
    """
    var = 'x'
    # Common factor P = (ax+b)
    a = random.randint(1, 4)
    b = random.randint(-5, 5)
    if b == 0: b = random.choice([-1, 1]) * random.randint(1, 5)
    
    c = random.randint(2, 5)
    d = random.randint(-5, 5)
    if d == 0: d = random.choice([-1, 1]) * random.randint(1, 5)

    # Calculate result and check for trivial cases
    # c*P + d = c(ax+b)+d = (ca)x + (cb+d)
    final_x_coeff = c * a
    final_const = c * b + d
    if final_x_coeff == 0 and (final_const == 0 or abs(final_const) == 1):
        return generate_poly_common_factor_advanced()

    P_str = f"({format_poly(a, b, var)})"
    op_char = '+' if d > 0 else '-'
    abs_d = abs(d)
    term2 = f"{P_str}" if abs_d == 1 else f"{abs_d}{P_str}"
    question_latex = f"{c}{P_str}^2 {op_char} {term2}"
    
    factor1 = P_str
    factor2 = f"({format_poly(final_x_coeff, final_const, var)})"
    
    return {"question_latex": question_latex, "factor1": factor1, "factor2": factor2}

def generate_hidden_factor_linear():
    """
    Generates a problem like (x-5)(x+1) - (5-x)(x-2) = (x-5)(2x-1).
    Form: Q1*P - Q2*(-P) = P*(Q1+Q2)
    """
    var = 'x'
    c = random.randint(1, 9)
    
    d, f = random.randint(1, 3), random.randint(1, 3)
    e, g = random.randint(-5, 5), random.randint(-5, 5)
    
    op_char = random.choice(['+', '-'])

    # Calculate result and check for trivial cases
    if op_char == '+': # P(Q1 - Q2)
        final_x_coeff = d - f
        final_const = e - g
    else: # P(Q1 + Q2)
        final_x_coeff = d + f
        final_const = e + g

    if (final_x_coeff == 0 and final_const == 0) or \
       (final_x_coeff == 0 and abs(final_const) == 1):
        return generate_hidden_factor_linear()

    P1_str = f"({var}-{c})"
    P_hidden_str = f"({c}-{var})"
    Q1_str = f"({format_poly(d, e, var)})"
    Q2_str = f"({format_poly(f, g, var)})"
    
    question_latex = f"{Q1_str}{P1_str} {op_char} {Q2_str}{P_hidden_str}"

    factor1 = P1_str
    factor2 = f"({format_poly(final_x_coeff, final_const, var)})"
    
    return {"question_latex": question_latex, "factor1": factor1, "factor2": factor2}

def generate_hidden_factor_squared():
    """
    Generates a problem like (x-4)(2x+5) - (4-x)^2 = (x-4)(x+9).
    Form: Q*P - (-P)^2 = P*(Q-P)
    """
    var = 'x'
    c = random.randint(1, 9)
    d = random.randint(2, 4) # d>=2 to ensure (d-1)x is not zero
    e = random.randint(-5, 5)
    
    op_char = random.choice(['+', '-'])
    
    # Calculate result and check for trivial cases
    if op_char == '+': # P(Q+P) = P((dx+e)+(x-c))
        final_x_coeff = d + 1
        final_const = e - c
    else: # P(Q-P) = P((dx+e)-(x-c))
        final_x_coeff = d - 1
        final_const = e + c
            
    if (final_x_coeff == 0 and final_const == 0) or \
       (final_x_coeff == 0 and abs(final_const) == 1):
        return generate_hidden_factor_squared()

    P_str = f"({var}-{c})"
    P_hidden_sq_str = f"({c}-{var})^2"
    Q_str = f"({format_poly(d, e, var)})"
    
    question_latex = f"{Q_str}{P_str} {op_char} {P_hidden_sq_str}"
            
    factor1 = P_str
    factor2 = f"({format_poly(final_x_coeff, final_const, var)})"
    
    return {"question_latex": question_latex, "factor1": factor1, "factor2": factor2}

def generate(level=1):
    """
    Generates a question for factorization by taking out common factors.
    """
    problem_generators = [
        generate_monomial_common_factor,
        generate_poly_common_factor_simple,
        generate_poly_common_factor_advanced,
        generate_hidden_factor_linear,
        generate_hidden_factor_squared
    ]
    
    generator = random.choice(problem_generators)
    problem = generator()
    
    question_text = f"因式分解下列各式。\n$ {problem['question_latex']} $"
    
    # Create canonical and alternative answers
    f1 = problem['factor1']
    f2 = problem['factor2']
    
    # Handle trivial factor (1)
    if f2 == "(1)":
        ans1 = f1
        ans2 = f1
    elif f1 == "(1)":
        ans1 = f2
        ans2 = f2
    else:
        ans1 = f"{f1}{f2}"
        ans2 = f"{f2}{f1}"

    # Use a pipe separator for check function
    # Only add alternative if it's different
    if ans1 == ans2:
        correct_answer_for_check = ans1
    else:
        correct_answer_for_check = f"{ans1}|{ans2}"
        
    return {
        "question_text": question_text,
        "answer": ans1,  # The canonical answer to display
        "correct_answer": correct_answer_for_check # For the check function
    }

def check(user_answer, correct_answer):
    """
    Checks the user's answer for factorization problems.
    Allows for different order of factors.
    """
    correct_options = correct_answer.split('|')
    
    # Normalize user answer: remove spaces and optional multiplication signs
    user_ans_norm = user_answer.replace(" ", "").replace("*", "")

    # Normalize correct options for comparison
    correct_options_norm = [opt.replace(" ", "").replace("*", "") for opt in correct_options]

    is_correct = user_ans_norm in correct_options_norm
    
    # The display answer should be the first option, which is the canonical one.
    display_answer = correct_options[0]

    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}