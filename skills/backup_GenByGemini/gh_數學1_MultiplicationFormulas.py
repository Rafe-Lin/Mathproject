import random
import sympy

# --- Helper functions ---

def _sympy_to_strings(expr):
    """
    Converts a sympy expression to a tuple of (eval_string, latex_string).
    """
    # For checking: a parsable string in Python syntax
    eval_str = sympy.sstr(expr, order='lex')
    # For display: a LaTeX string
    latex_str = sympy.latex(expr)
    # The final Python code MUST have escaped backslashes in strings
    latex_str = latex_str.replace('\\', '\\\\')
    return eval_str, latex_str

def _pack_answer(eval_str, latex_str):
    """
    Packs the evaluatable string and LaTeX string into a single string for the check function.
    """
    return f"{eval_str}||{latex_str}"

# --- Problem Type Generators ---

def generate_expand_square_problem():
    """
    Generates problems involving square formulas.
    (a±b)^2, (a+b+c)^2, (a+b)(a-b)
    """
    sub_type = random.choice(['sum_of_squares', 'trinomial', 'grouping'])
    vars_pool = ['a', 'b', 'c', 'x', 'y', 'z', 'm', 'n']

    if sub_type == 'sum_of_squares':
        # e.g., (ax-by)^2 + (cx+dy)^2
        a, b, c, d = [random.randint(1, 4) for _ in range(4)]
        v1_s, v2_s = random.sample(vars_pool, 2)
        v1, v2 = sympy.symbols(f'{v1_s} {v2_s}')
        
        term1 = (a*v1 - b*v2)**2
        term2 = (c*v1 + d*v2)**2
        expr = term1 + term2
        
        # Ensure it doesn't simplify to 0 or something trivial
        if sympy.simplify(expr) == 0:
             return generate_expand_square_problem()

        question_text = f"利用乘法公式，展開下列各式：<br>$({sympy.latex(term1)}) + ({sympy.latex(term2)})$"
        
    elif sub_type == 'trinomial':
        # e.g., (ax-by+cz)^2
        a, b, c = [random.randint(1, 3) for _ in range(3)]
        b *= random.choice([-1, 1])
        c *= random.choice([-1, 1])
        v1_s, v2_s, v3_s = random.sample(vars_pool, 3)
        v1, v2, v3 = sympy.symbols(f'{v1_s} {v2_s} {v3_s}')
        
        expr = (a*v1 + b*v2 + c*v3)**2
        question_text = f"利用乘法公式，展開下列各式：<br>$({sympy.latex(expr)})$"

    else: # grouping (difference of squares)
        # e.g., ((ax+by)+c)((ax+by)-c)
        a, b, c = [random.randint(1, 3) for _ in range(3)]
        b *= random.choice([-1, 1])
        v1_s, v2_s = random.sample(vars_pool, 2)
        v1, v2 = sympy.symbols(f'{v1_s} {v2_s}')

        group = a*v1 + b*v2
        term1 = group + c
        term2 = group - c
        expr = term1 * term2
        
        # Manually format question for clarity
        group_latex = sympy.latex(group)
        question_text = f"利用乘法公式，展開下列各式：<br>$(({group_latex}) + {c})(({group_latex}) - {c})$"

    expanded_expr = sympy.expand(expr)
    eval_ans, latex_ans = _sympy_to_strings(expanded_expr)
    packed_answer = _pack_answer(eval_ans, latex_ans)

    return {
        "question_text": question_text,
        "answer": latex_ans,
        "correct_answer": packed_answer
    }

def generate_expand_cube_problem():
    """
    Generates problems involving cube of sum/difference. (a±b)^3
    """
    a = random.randint(1, 4)
    b = random.randint(1, 3)
    vars_pool = ['a', 'b', 'x', 'y', 'm', 'n']
    v1_s, v2_s = random.sample(vars_pool, 2)
    v1, v2 = sympy.symbols(f'{v1_s} {v2_s}')
    
    sign = random.choice([1, -1])
    
    if sign == 1:
        expr = (a*v1 + b*v2)**3
    else:
        expr = (a*v1 - b*v2)**3
        
    expanded_expr = sympy.expand(expr)
    eval_ans, latex_ans = _sympy_to_strings(expanded_expr)
    packed_answer = _pack_answer(eval_ans, latex_ans)

    question_text = f"利用乘法公式，展開下列各式：<br>$({sympy.latex(expr)})$"
    
    return {
        "question_text": question_text,
        "answer": latex_ans,
        "correct_answer": packed_answer
    }

def generate_expand_sum_diff_cubes_problem():
    """
    Generates expansion problems that result in sum or difference of cubes.
    e.g., (a+b)(a^2-ab+b^2) = a^3+b^3
    """
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    vars_pool = ['a', 'b', 'x', 'y']
    v1_s, v2_s = random.sample(vars_pool, 2)
    v1, v2 = sympy.symbols(f'{v1_s} {v2_s}')
    
    sign = random.choice([1, -1])
    
    term_a = a*v1
    term_b = b*v2
    
    if sign == 1: # Sum of cubes
        factor1 = term_a + term_b
        factor2 = term_a**2 - term_a*term_b + term_b**2
    else: # Difference of cubes
        factor1 = term_a - term_b
        factor2 = term_a**2 + term_a*term_b + term_b**2
        
    expr = factor1 * factor2
    result_expr = sympy.expand(expr)

    eval_ans, latex_ans = _sympy_to_strings(result_expr)
    packed_answer = _pack_answer(eval_ans, latex_ans)

    question_text = f"利用乘法公式，展開下列各式：<br>$({sympy.latex(factor1)})({sympy.latex(factor2)})$"

    return {
        "question_text": question_text,
        "answer": latex_ans,
        "correct_answer": packed_answer
    }

def generate_factorization_problem():
    """
    Generates factorization problems for perfect cubes or sum/difference of cubes.
    """
    sub_type = random.choice(['sum_diff_cubes', 'perfect_cube'])
    vars_pool = ['x', 'y', 'a', 'b']
    
    if sub_type == 'sum_diff_cubes':
        # e.g., 27x^3 - 8
        a = random.randint(2, 5)
        b = random.randint(2, 5)
        var_s = random.choice(vars_pool)
        v = sympy.Symbol(var_s)
        
        sign = random.choice([1, -1])
        
        if sign == 1:
            expanded_expr = (a*v)**3 + b**3
        else:
            expanded_expr = (a*v)**3 - b**3
            
    else: # perfect_cube
        # e.g., x^3 + 6x^2 + 12x + 8 = (x+2)^3
        a = random.randint(1, 3)
        b = random.randint(2, 4)
        var_s = random.choice(vars_pool)
        v = sympy.Symbol(var_s)
        
        sign = random.choice([1, -1])
        
        if sign == 1:
            factored_expr = (a*v + b)**3
        else:
            factored_expr = (a*v - b)**3
        
        expanded_expr = sympy.expand(factored_expr)
    
    factored_expr = sympy.factor(expanded_expr)
    eval_ans, latex_ans = _sympy_to_strings(factored_expr)
    packed_answer = _pack_answer(eval_ans, latex_ans)

    question_text = f"利用乘法公式，因式分解下列各式：<br>${sympy.latex(expanded_expr)}$"

    return {
        "question_text": question_text,
        "answer": latex_ans,
        "correct_answer": packed_answer
    }

def generate_application_problem():
    """
    Generates application problems, like given x+1/x, find x^2+1/x^2.
    """
    k = random.randint(3, 7)
    sign = random.choice([1, -1])
    
    if sign == 1:
        given_expr_str = f"x + \\\\frac{{1}}{{x}} = {k}"
    else:
        given_expr_str = f"x - \\\\frac{{1}}{{x}} = {k}"
        
    ask_type = random.choice(['square', 'cube'])
    
    if ask_type == 'square':
        question_to_ask_str = "x^2 + \\\\frac{1}{x^2}"
        if sign == 1: # (x+1/x)^2 = x^2+2+1/x^2 => x^2+1/x^2 = k^2-2
            answer = k**2 - 2
        else: # (x-1/x)^2 = x^2-2+1/x^2 => x^2+1/x^2 = k^2+2
            answer = k**2 + 2
    else: # cube
        if sign == 1: # Given x+1/x, ask x^3+1/x^3
            question_to_ask_str = "x^3 + \\\\frac{1}{x^3}"
            # x^3+1/x^3 = (x+1/x)(x^2-1+1/x^2) = k * ((k^2-2)-1) = k(k^2-3)
            answer = k * (k**2 - 3)
        else: # Given x-1/x, ask x^3-1/x^3
            question_to_ask_str = "x^3 - \\\\frac{1}{x^3}"
            # x^3-1/x^3 = (x-1/x)(x^2+1+1/x^2) = k * ((k^2+2)+1) = k(k^2+3)
            answer = k * (k**2 + 3)

    question_text = f"已知 ${given_expr_str}$，求下列各式的值：<br>${question_to_ask_str}$"
    
    # For numeric answers, eval_str and latex_str are the same.
    eval_ans = str(answer)
    latex_ans = str(answer)
    packed_answer = _pack_answer(eval_ans, latex_ans)

    return {
        "question_text": question_text,
        "answer": latex_ans,
        "correct_answer": packed_answer
    }


def generate(level=1):
    """
    生成「乘法公式」相關題目。
    包含：
    1. 展開平方與立方公式
    2. 展開立方和、立方差
    3. 因式分解
    4. 應用問題
    """
    problem_type = random.choice([
        'expand_square', 
        'expand_cube', 
        'expand_sum_diff_cubes', 
        'factorization', 
        'application'
    ])
    
    if problem_type == 'expand_square':
        return generate_expand_square_problem()
    elif problem_type == 'expand_cube':
        return generate_expand_cube_problem()
    elif problem_type == 'expand_sum_diff_cubes':
        return generate_expand_sum_diff_cubes_problem()
    elif problem_type == 'factorization':
        return generate_factorization_problem()
    else: # application
        return generate_application_problem()


def check(user_answer, packed_correct_answer):
    """
    檢查答案是否正確。能處理數值與符號表示式。
    """
    try:
        parts = packed_correct_answer.split("||")
        correct_eval_str = parts[0]
        correct_display_str = parts[1]
    except IndexError:
        # Fallback for answers not using the packed format
        correct_eval_str = packed_correct_answer
        correct_display_str = packed_correct_answer

    is_correct = False
    
    # Try checking as a number first
    try:
        if abs(float(user_answer) - float(correct_eval_str)) < 1e-9:
            is_correct = True
    except (ValueError, TypeError):
        # If it's not a number, check as a symbolic expression
        try:
            # Prepare user answer: replace ^ with **, remove spaces
            user_expr_str = user_answer.replace('^', '**').strip()
            
            # Define allowed symbols for safety
            allowed_symbols = {s: sympy.Symbol(s) for s in "abcmnxyz"}

            user_sym = sympy.sympify(user_expr_str, locals=allowed_symbols)
            # The eval string from sympy already uses **
            correct_sym = sympy.sympify(correct_eval_str, locals=allowed_symbols)
            
            # Use expand to handle factored vs expanded forms, then check for equality
            if sympy.expand(user_sym) == sympy.expand(correct_sym):
                is_correct = True
            # Also check if the simplified difference is zero
            elif sympy.simplify(user_sym - correct_sym) == 0:
                is_correct = True

        except (SyntaxError, TypeError, sympy.SympifyError):
            # Handle cases where user input is not a valid expression
            is_correct = False

    result_text = f"完全正確！答案是 ${correct_display_str}$。" if is_correct else f"答案不正確。正確答案應為：${correct_display_str}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}