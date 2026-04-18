import random
from fractions import Fraction

# --- Helper functions for formatting ---

def format_term(coeff, var, is_leading=False):
    """Formats a single term of a polynomial (e.g., '+ 5x', '- 3')."""
    if coeff == 0:
        return ""
    
    # Determine the sign
    if is_leading:
        sign = "-" if coeff < 0 else ""
    else:
        sign = " - " if coeff < 0 else " + "
    
    abs_coeff = abs(coeff)
    
    # Determine the coefficient string (hide 1 for variables)
    if abs_coeff == 1 and var:
        coeff_str = ""
    else:
        coeff_str = str(abs_coeff)
        
    return f"{sign}{coeff_str}{var}"

def format_polynomial(a, b, c):
    """Formats a quadratic polynomial ax^2+bx+c into a string."""
    poly_a = format_term(a, "x^2", is_leading=True)
    poly_b = format_term(b, "x")
    poly_c = format_term(c, "")
    return f"{poly_a}{poly_b}{poly_c}".strip()

def format_factor(p, r):
    """Formats a linear factor (px+r) into a string."""
    if p == 1:
        p_str = "x"
    elif p == -1:
        p_str = "-x"
    else:
        p_str = f"{p}x"

    if r == 0:
        return f"({p_str})"
    
    sign = "+" if r > 0 else "-"
    abs_r = abs(r)
    
    return f"({p_str} {sign} {abs_r})"

# --- Problem generation functions ---

def generate_direct_factor_problem():
    """Generates a direct factoring problem: Factor ax^2+bx+c."""
    while True:
        p = random.randint(1, 8)
        q = random.randint(2, 8)
        # Randomly swap to avoid patterns where the first coefficient is always smaller
        if random.random() < 0.5: 
            p, q = q, p
        
        r = random.randint(-10, 10)
        s = random.randint(-10, 10)
        
        # Ensure coefficients are non-zero and reasonable
        if r == 0 or s == 0: continue
        if p * q > 80: continue # Keep the leading coefficient manageable
        
        b = p * s + q * r
        if b == 0: continue # Avoid difference of squares or common factor cases
        
        break

    a = p * q
    c = r * s
    
    poly_str = format_polynomial(a, b, c)
    
    question_text = f"因式分解下列多項式：${poly_str}$"
    
    factor1 = format_factor(p, r)
    factor2 = format_factor(q, s)
    
    # Create two acceptable answer formats for the check function
    answer1 = f"{factor1}{factor2}"
    answer2 = f"{factor2}{factor1}"
    
    return {
        "question_text": question_text,
        "answer": answer1,
        "correct_answer": f"{answer1}|{answer2}"
    }

def generate_find_coeffs_problem():
    """
    Generates a problem where the user must factor and find coefficients.
    e.g., Factor 39x^2+5x-14 into (3x+a)(bx+c) and find a+2c.
    """
    while True:
        # One factor must have a coefficient > 1
        p_choices = [1, 2, 3, 5, 7, 11, 13]
        q_choices = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        p = random.choice(p_choices)
        q = random.choice(q_choices)
        
        # Randomly assign p and q to the two factors
        if random.random() < 0.5:
             p, q = q, p
        if p == 1 and q == 1: continue # Ensure a != 1
        
        r = random.randint(-12, 12)
        s = random.randint(-12, 12)
        
        if r == 0 or s == 0: continue
        
        b = p * s + q * r
        if b == 0: continue
        
        break

    a = p * q
    c = r * s
    
    poly_str = format_polynomial(a, b, c)
    
    # These are the actual values for the variables in the question
    # The problem template is (px + a)(bx + c)
    a_val = r
    b_val = q
    c_val = s
    
    # Choose a random expression to evaluate
    expressions = [
        {"str": "a + c", "func": lambda a,b,c: a + c},
        {"str": "a + b + c", "func": lambda a,b,c: a + b + c},
        {"str": "a - c", "func": lambda a,b,c: a - c},
        {"str": "b - a", "func": lambda a,b,c: b - a},
        {"str": "a + 2c", "func": lambda a,b,c: a + 2*c},
        {"str": "b + 2a", "func": lambda a,b,c: b + 2*a},
        {"str": "a - b + c", "func": lambda a,b,c: a - b + c},
    ]
    chosen_expr = random.choice(expressions)
    expr_str = chosen_expr["str"]
    correct_value = chosen_expr["func"](a_val, b_val, c_val)

    # Format the factor with variables for the question
    p_revealed_str = "x" if p == 1 else f"{p}x"
    factor_template = f"({p_revealed_str} + a)(bx + c)"

    question_text = (
        f"若多項式 ${poly_str}$ 可因式分解成 ${factor_template}$，"
        f"其中 a、b、c 均為整數，則 ${expr_str}$ 之值為何？"
    )
    
    return {
        "question_text": question_text,
        "answer": str(correct_value),
        "correct_answer": str(correct_value)
    }

def generate(level=1):
    """
    Generates a problem for factoring quadratics with a leading coefficient not equal to one.
    
    Two types of problems are generated:
    1. Direct Factoring: Given ax^2+bx+c, provide the factored form.
    2. Find Coefficients: Given ax^2+bx+c and a template like (px+a)(bx+c), find the value of an expression involving a, b, and c.
    """
    # Give a higher chance to the more complex 'find_coeffs' type
    if random.random() < 0.6:
        return generate_find_coeffs_problem()
    else:
        return generate_direct_factor_problem()

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct one.
    Handles two types of answers:
    1. Factored form (e.g., "(x+2)(3x-1)"): Checks for commutative equivalence.
    2. Numerical value: Checks for numerical equality.
    """
    # Check for factoring problems, which use '|' to separate valid answers
    if '|' in correct_answer:
        norm_user_answer = user_answer.strip().lower().replace(" ", "").replace("*", "")
        possible_answers = correct_answer.split('|')
        
        is_correct = False
        for ans in possible_answers:
            norm_ans = ans.strip().lower().replace(" ", "")
            if norm_user_answer == norm_ans:
                is_correct = True
                break
        display_answer = possible_answers[0]
    else: # Check for numerical problems
        user_answer_clean = user_answer.strip()
        correct_answer_clean = correct_answer.strip()
        is_correct = False
        try:
            # Compare as floats to handle answers like '7.0' vs '7'
            if float(user_answer_clean) == float(correct_answer_clean):
                is_correct = True
        except (ValueError, TypeError):
             # Fallback to string comparison if not a number
             is_correct = (user_answer_clean.upper() == correct_answer_clean.upper())
        display_answer = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 ${display_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}