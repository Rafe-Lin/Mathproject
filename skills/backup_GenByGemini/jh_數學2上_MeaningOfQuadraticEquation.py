import random

def _format_term(coeff, var='x', power=1, is_first=False):
    """
    Formats a single term of a polynomial, e.g., -3x^2 or +5.
    Internal helper function.
    """
    if coeff == 0:
        return ""

    # Determine the sign for the term
    if is_first:
        sign = "-" if coeff < 0 else ""
    else:
        sign = " - " if coeff < 0 else " + "
    
    coeff = abs(coeff)

    # Format the coefficient part
    if coeff == 1 and power != 0:
        coeff_str = ""
    else:
        coeff_str = str(coeff)

    # Format the variable and its power
    if power == 0:
        var_str = ""
    elif power == 1:
        var_str = var
    else:
        var_str = f"{var}^{{{power}}}"
    
    # Handle specific edge cases for clean output
    if coeff_str == "1" and var_str == "": # Constant term of 1
        return f"{sign}1"
    if coeff_str == "" and var_str != "": # Variable with coefficient 1
        return f"{sign}{var_str}"

    return f"{sign}{coeff_str}{var_str}"

def generate_identify_equation_problem():
    """
    Generates a problem asking to identify if a given expression is a quadratic equation.
    """
    sub_type = random.choice([
        'is_quadratic_std', 'is_quadratic_rearranged', 'is_quadratic_factored',
        'not_linear_simple', 'not_linear_cancel_expanded', 'not_linear_cancel_factored',
        'not_polynomial', 'not_cubic', 'not_two_vars'
    ])

    expression = ""
    is_quadratic = False

    if sub_type in ['is_quadratic_std', 'is_quadratic_rearranged', 'is_quadratic_factored']:
        is_quadratic = True

    if sub_type == 'is_quadratic_std':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(-9, 9)
        c = random.randint(-9, 9)
        terms = [
            _format_term(a, 'x', 2, is_first=True),
            _format_term(b, 'x', 1),
            _format_term(c, '', 0)
        ]
        expression = "".join(filter(None, terms)).strip() + " = 0"

    elif sub_type == 'is_quadratic_rearranged':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(-9, 9)
        c = random.randint(-9, 9)
        if c == 0: c = random.randint(1, 5)
        lhs_terms = [_format_term(a, 'x', 2, is_first=True), _format_term(b, 'x', 1)]
        lhs = "".join(filter(None, lhs_terms)).strip()
        expression = f"{lhs} = {c}"

    elif sub_type == 'is_quadratic_factored':
        r1_val = -random.randint(-9, 9)
        r2_val = -random.randint(-9, 9)
        
        def format_factor(val):
            if val == 0: return "x"
            sign = "+" if val > 0 else "-"
            return f"(x {sign} {abs(val)})"

        factors = [format_factor(r1_val), format_factor(r2_val)]
        if random.random() < 0.5: factors.reverse()
        expression = f"{factors[0]}{factors[1]} = 0"

    elif sub_type == 'not_linear_simple':
        a = random.randint(1, 9) * random.choice([-1, 1])
        b = random.randint(-9, 9)
        term1 = _format_term(a, 'x', 1, is_first=True)
        term2 = _format_term(b, '', 0)
        expression = f"{term1}{term2} = 0"

    elif sub_type == 'not_linear_cancel_expanded':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b, c = random.randint(-9, 9), random.randint(-9, 9)
        d, e = random.randint(-9, 9), random.randint(-9, 9)
        while b == d and c == e:
            d = random.randint(-9, 9)
        
        lhs_terms = [_format_term(a, 'x', 2, is_first=True), _format_term(b, 'x', 1), _format_term(c, '', 0)]
        rhs_terms = [_format_term(a, 'x', 2, is_first=True), _format_term(d, 'x', 1), _format_term(e, '', 0)]
        lhs = "".join(filter(None, lhs_terms)).strip()
        rhs = "".join(filter(None, rhs_terms)).strip()
        expression = f"{lhs} = {rhs}"
        
    elif sub_type == 'not_linear_cancel_factored':
        a, c = random.randint(1, 3), random.randint(1, 3)
        b, d = random.randint(-5, 5), random.randint(-5, 5)
        
        coeff_x_rhs = a * d + b * c
        const_rhs = b * d
        
        e = coeff_x_rhs + random.randint(1, 5) * random.choice([-1, 1])
        f = const_rhs + random.randint(1, 5) * random.choice([-1, 1])
        
        lhs_terms = [_format_term(a*c, 'x', 2, is_first=True), _format_term(e, 'x', 1), _format_term(f, '', 0)]
        lhs = "".join(filter(None, lhs_terms)).strip()

        def format_linear_factor(coeff, const):
            const_part = ""
            if const > 0: const_part = f"+ {const}"
            elif const < 0: const_part = f"- {abs(const)}"
            
            coeff_part = "x" if abs(coeff) == 1 else f"{abs(coeff)}x"
            if coeff < 0: coeff_part = "-" + coeff_part

            return f"({coeff_part} {const_part})".replace("  ", " ").strip()
        
        rhs = f"{format_linear_factor(a, b)}{format_linear_factor(c, d)}"
        expression = f"{lhs} = {rhs}"

    elif sub_type == 'not_polynomial':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(-9, 9)
        c = random.randint(-9, 9)
        terms = [
            _format_term(a, 'x', 2, is_first=True),
            _format_term(b, 'x', 1),
            _format_term(c, '', 0)
        ]
        expression = "".join(filter(None, terms)).strip()

    elif sub_type == 'not_cubic':
        a = random.randint(1, 3) * random.choice([-1, 1])
        b, c, d = [random.randint(-5, 5) for _ in range(3)]
        terms = [
            _format_term(a, 'x', 3, is_first=True), _format_term(b, 'x', 2),
            _format_term(c, 'x', 1), _format_term(d, '', 0)
        ]
        expression = "".join(filter(None, terms)).strip() + " = 0"
        
    elif sub_type == 'not_two_vars':
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 5) * random.choice([-1, 1])
        c = random.randint(-9, 9)
        terms = [
            _format_term(a, 'x', 2, is_first=True),
            _format_term(b, 'y', 1),
            _format_term(c, '', 0)
        ]
        expression = "".join(filter(None, terms)).strip() + " = 0"

    expression = expression.replace(" + -", " - ").replace("  ", " ").strip()
    if expression.startswith("+ "):
        expression = expression[2:]
        
    correct_answer = "是" if is_quadratic else "否"
    question_text = f"判斷下列式子是否為一元二次方程式？\n$ {expression} $\n(請回答「是」或「否」)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_verify_root_problem():
    """
    Generates a problem asking to verify if a number is a root of an equation.
    """
    is_a_root = random.choice([True, False])
    
    r1 = random.randint(-7, 7)
    r2 = random.randint(-7, 7)
    while r1 == r2:
        r2 = random.randint(-7, 7)
    
    if is_a_root:
        val_to_test = random.choice([r1, r2])
    else:
        val_to_test = r1 + random.choice([-2, -1, 1, 2])
        while val_to_test == r1 or val_to_test == r2:
            val_to_test = random.randint(-10, 10)

    correct_answer = "是" if is_a_root else "否"
    
    equation_string = ""
    eq_format = random.choice(['std', 'rearranged', 'sides', 'factored'])

    if eq_format == 'factored' and abs(r1) < 10 and abs(r2) < 10 and r1 != 0 and r2 != 0:
        def format_factor(root_val):
            val = -root_val
            sign = "+" if val > 0 else "-"
            return f"(x {sign} {abs(val)})"
        factors = [format_factor(r1), format_factor(r2)]
        if random.random() < 0.5: factors.reverse()
        equation_string = f"{factors[0]}{factors[1]} = 0"
    else:
        a = random.choice([1, 1, 2, -1])
        b_prime = -a * (r1 + r2)
        c_prime = a * r1 * r2
        
        term2 = _format_term(a, 'x', 2, is_first=True)
        term1 = _format_term(b_prime, 'x', 1)
        term0 = _format_term(c_prime, '', 0)
        
        eq_format_expanded = random.choice(['std', 'rearranged', 'sides'])
        
        if eq_format_expanded == 'std':
            all_terms = [term2, term1, term0]
            expression = "".join(filter(None, all_terms)).strip()
            equation_string = f"{expression} = 0"
        elif eq_format_expanded == 'rearranged':
            lhs_terms = [term2, term1]
            lhs = "".join(filter(None, lhs_terms)).strip()
            rhs = str(-c_prime)
            equation_string = f"{lhs} = {rhs}"
        else: # 'sides'
            lhs_terms = [term2, term0]
            lhs = "".join(filter(None, lhs_terms)).strip()
            rhs_term = _format_term(-b_prime, 'x', 1, is_first=True)
            equation_string = f"{lhs} = {rhs_term}"

    equation_string = equation_string.replace(" + -", " - ").replace("  ", " ").strip()
    if equation_string.startswith("+ "):
        equation_string = equation_string[2:]
        
    question_text = f"判別 ${val_to_test}$ 是否為方程式 $ {equation_string} $ 的解？\n(請回答「是」或「否」)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem related to the meaning of quadratic equations.
    It can be one of two types:
    1. Identifying if an expression is a quadratic equation.
    2. Verifying if a given number is a root of a quadratic equation.
    """
    problem_type = random.choice(['identify_equation', 'verify_root'])
    
    if problem_type == 'identify_equation':
        return generate_identify_equation_problem()
    else:
        return generate_verify_root_problem()

def check(user_answer, correct_answer):
    """
    Checks the user's answer ('是' or '否') against the correct answer.
    """
    user_answer = user_answer.strip()
    is_correct = (user_answer == correct_answer)
    
    # Allow for common aliases to provide a better user experience
    aliases_yes = ["是", "Yes", "Y", "yes", "y", "True", "true", "T", "t", "O", "o", "○", "對"]
    aliases_no = ["否", "No", "N", "no", "n", "False", "false", "F", "f", "X", "x", "×", "錯"]

    if not is_correct:
        if correct_answer == "是" and user_answer in aliases_yes:
            is_correct = True
        elif correct_answer == "否" and user_answer in aliases_no:
            is_correct = True
            
    if is_correct:
        result_text = f"完全正確！答案是「{correct_answer}」。"
    else:
        result_text = f"答案不正確。正確答案應為：「{correct_answer}」。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}