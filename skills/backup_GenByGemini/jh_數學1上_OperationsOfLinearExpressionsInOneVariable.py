import random
from fractions import Fraction
import math

# --- Helper Functions ---

def _lcm(a, b):
    """Calculates the least common multiple of two integers."""
    return abs(a * b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def _format_value(val, use_latex=True):
    """Formats an integer or Fraction into a string, potentially with LaTeX."""
    val = Fraction(val)
    if val.denominator == 1:
        return str(val.numerator)
    if use_latex:
        sign = "-" if val.numerator < 0 else ""
        num = abs(val.numerator)
        den = val.denominator
        return f"{sign}\\frac{{{num}}}{{{den}}}"
    else:
        # Non-LaTeX format for answer key if needed, though not used currently.
        return f"{val.numerator}/{val.denominator}"

def _format_term(val, var='x', is_first=False):
    """Formats a single term for display in a question expression."""
    if val == 0:
        return ""
    
    val = Fraction(val)
    sign_str = ""
    if is_first:
        if val < 0:
            sign_str = "-"
    else:
        sign_str = " + " if val > 0 else " - "
        
    val_abs = abs(val)
    val_str = _format_value(val_abs)

    if val_abs == 1 and var:
        return f"{sign_str}{var}"
    
    return f"{sign_str}{val_str}{var}"

def _build_answer_expression(coeff, const, var='x'):
    """Builds a canonical answer string like '5x+12' or '-x-7' or '\\frac{{1}}{{2}}x-3'."""
    coeff = Fraction(coeff)
    const = Fraction(const)
    
    if coeff == 0 and const == 0:
        return "0"

    parts = []
    # Variable term
    if coeff != 0:
        if coeff == 1:
            parts.append(var)
        elif coeff == -1:
            parts.append(f"-{var}")
        else:
            parts.append(f"{_format_value(coeff)}{var}")

    # Constant term
    if const != 0:
        sign = ""
        if coeff != 0: # Add a sign if it's not the first term
            sign = "+" if const > 0 else "" # Negative sign is part of _format_value
        
        parts.append(f"{sign}{_format_value(const)}")

    return "".join(parts)


# --- Problem Generators ---

def generate_mult_div_problem():
    """Generates a problem for multiplication or division of a monomial by a constant."""
    q_title = "化簡下列各式。"
    var = random.choice(['x', 'y', 'a'])
    
    if random.random() < 0.5:  # Multiplication: c1 * (c2*x)
        c1 = random.randint(2, 9) * random.choice([-1, 1])
        c2 = random.randint(2, 9) * random.choice([-1, 1])
        
        if random.random() < 0.5:
            expr = f"({c1}) \\cdot ({c2}{var})"
        else:
            expr = f"({c1}{var}) \\cdot ({c2})"
            
        ans_coeff = c1 * c2
        
    else:  # Division: (c1*x) / c2
        # Divisor can be integer or fraction
        if random.random() < 0.4: # Fractional divisor
            den_num = random.randint(1, 5) * random.choice([-1, 1])
            den_den = random.randint(2, 6)
            c2 = Fraction(den_num, den_den)
            c1 = random.randint(2, 10) * random.choice([-1, 1])
            
            c2_str = f"({_format_value(c2)})"
        else: # Integer divisor
            c2 = random.randint(2, 7) * random.choice([-1, 1])
            # Ensure the dividend's coefficient is a multiple for cleaner problems
            c1 = c2 * random.randint(1, 5) * random.choice([-1, 1])
            c2_str = f"({c2})"

        expr = f"({c1}{var}) \\div {c2_str}"
        ans_coeff = Fraction(c1) / Fraction(c2)

    question_text = f"{q_title}<br>${expr}$"
    correct_answer = _build_answer_expression(ans_coeff, 0, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_add_sub_problem():
    """Generates a problem for addition or subtraction of like terms."""
    q_title = "化簡下列各式。"
    var = random.choice(['x', 'y'])
    
    # Use fractions about 30% of the time
    if random.random() < 0.3:
        d1 = random.randint(2, 7)
        n1 = random.randint(1, d1-1) * random.choice([-1, 1])
        c1 = Fraction(n1, d1)
        
        d2 = random.randint(2, 7)
        n2 = random.randint(1, d2-1) * random.choice([-1, 1])
        c2 = Fraction(n2, d2)
    else:
        c1 = random.randint(-10, 10)
        c2 = random.randint(-10, 10)
        if c1 == 0 or c2 == 0: c1, c2 = random.randint(1,10), random.randint(1,10)

    op_choice = random.choice(['+', '-'])
    
    term1_str = f"{_format_value(c1)}{var}"
    # For subtraction of negative, show parentheses
    if op_choice == '-' and c2 < 0:
        term2_str = f"({_format_value(c2)}{var})"
    else:
        term2_str = f"{_format_value(c2)}{var}"
    
    question_text = f"{q_title}<br>${term1_str} {op_choice} {term2_str}$"
    
    if op_choice == '+':
        ans_coeff = Fraction(c1) + Fraction(c2)
    else:
        ans_coeff = Fraction(c1) - Fraction(c2)
        
    correct_answer = _build_answer_expression(ans_coeff, 0, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simplify_basic_problem():
    """Generates a problem like 3x + 5 + 2x + 7."""
    q_title = "化簡下列各式。"
    var = 'x'
    
    a = random.randint(-9, 9)
    b = random.randint(-15, 15)
    c = random.randint(-9, 9)
    d = random.randint(-15, 15)
    
    # Avoid trivial problems
    if a == -c: a += random.choice([-1, 1])
    if b == -d: b += random.choice([-1, 1])
    if a == 0: a = random.randint(1,5)
    
    term1 = _format_term(a, var, is_first=True)
    term2 = _format_term(b, "", is_first=False)
    term3 = _format_term(c, var, is_first=False)
    term4 = _format_term(d, "", is_first=False)
    
    # Shuffle terms for variety
    terms = [t for t in [term1, term2, term3, term4] if t]
    random.shuffle(terms)
    
    # Ensure first term doesn't start with " + "
    full_expr = "".join(terms).lstrip()
    if full_expr.startswith('+ '):
        full_expr = full_expr[2:]
        
    question_text = f"{q_title}<br>${full_expr}$"
    
    ans_coeff = a + c
    ans_const = b + d
    
    correct_answer = _build_answer_expression(ans_coeff, ans_const, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distributive_simple_problem():
    """Generates a problem using the distributive property, e.g., -3(4x-5)."""
    q_title = "化簡下列各式。"
    var = 'x'
    
    m = random.randint(2, 9) * random.choice([-1, 1])
    a = random.randint(1, 9) * random.choice([-1, 1])
    b = random.randint(1, 9) * random.choice([-1, 1])
    
    # Two main types: -(ax+b) and m(ax+b)
    if random.random() < 0.3: # -(ax+b)
        inside_expr = f"{_format_term(a, var, is_first=True)}{_format_term(b, '', is_first=False)}"
        expr = f"-({inside_expr})"
        ans_coeff = -a
        ans_const = -b
    else: # m(ax+b)
        inside_expr = f"{_format_term(a, var, is_first=True)}{_format_term(b, '', is_first=False)}"
        expr = f"{m}({inside_expr})"
        ans_coeff = m * a
        ans_const = m * b
        
    question_text = f"{q_title}<br>${expr}$"
    correct_answer = _build_answer_expression(ans_coeff, ans_const, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distributive_complex_problem():
    """Generates a problem combining distribution and like terms."""
    q_title = "化簡下列各式。"
    var = 'x'
    
    m1 = random.randint(2, 6) * random.choice([-1, 1])
    a1 = random.randint(1, 5) * random.choice([-1, 1])
    b1 = random.randint(1, 5) * random.choice([-1, 1])
    
    m2 = random.randint(2, 6) * random.choice([-1, 1])
    a2 = random.randint(1, 5) * random.choice([-1, 1])
    b2 = random.randint(1, 5) * random.choice([-1, 1])
    
    expr1_in = f"{_format_term(a1, var, is_first=True)}{_format_term(b1, '', is_first=False)}"
    expr1 = f"{m1}({expr1_in})"
    
    op_str = " + " if m2 > 0 else " - "
    m2_abs = abs(m2)
    m2_str = str(m2_abs) if m2_abs != 1 else ""
    
    expr2_in = f"{_format_term(a2, var, is_first=True)}{_format_term(b2, '', is_first=False)}"
    expr2 = f"{m2_str}({expr2_in})"
    
    question_text = f"{q_title}<br>${expr1}{op_str}{expr2}$"
    
    ans_coeff = (m1 * a1) + (m2 * a2)
    ans_const = (m1 * b1) + (m2 * b2)
    
    correct_answer = _build_answer_expression(ans_coeff, ans_const, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fractional_expr_problem():
    """Generates a problem involving adding/subtracting fractional expressions."""
    q_title = "化簡下列各式。"
    var = 'x'
    
    d1 = random.randint(2, 6)
    d2 = random.randint(2, 6)
    while d1 == d2:
        d2 = random.randint(2, 7)
    
    b1 = random.randint(1, 5) * random.choice([-1, 1])
    b2 = random.randint(1, 5) * random.choice([-1, 1])
    
    op = random.choice(['+', '-'])
    
    term1_num = f"{var}{_format_term(b1, '', is_first=False)}"
    term2_num = f"{var}{_format_term(b2, '', is_first=False)}"
    
    question_text = f"{q_title}<br>$\\frac{{{term1_num}}}{{{d1}}} {op} \\frac{{{term2_num}}}{{{d2}}}$"

    den_lcm = _lcm(d1, d2)
    m1 = den_lcm // d1
    m2 = den_lcm // d2
    
    op_sign = 1 if op == '+' else -1
    
    # Calculate new numerator coefficients: m1*(x+b1) op m2*(x+b2)
    final_coeff_x = m1 * 1 + op_sign * (m2 * 1)
    final_const = m1 * b1 + op_sign * (m2 * b2)
    
    # Simplify the whole fraction
    common_divisor = math.gcd(math.gcd(final_coeff_x, final_const), den_lcm)
    
    num_coeff = final_coeff_x // common_divisor
    num_const = final_const // common_divisor
    final_den = den_lcm // common_divisor
    
    num_expr = _build_answer_expression(num_coeff, num_const, var=var)
    
    if final_den == 1:
        correct_answer = num_expr
    else:
        correct_answer = f"\\frac{{{num_expr}}}{{{final_den}}}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """Generates a word problem that requires setting up and simplifying an expression."""
    var = 'x'
    items = [
        ('夏威夷披薩', '墨西哥披薩'), ('原子筆', '鉛筆'),
        ('成人票', '兒童票'), ('蘋果', '芭樂')
    ]
    contexts = [
        ('貴', '+', '元'), ('便宜', '-', '元'),
        ('多', '+', '元'), ('少', '-', '元')
    ]
    people = ['小妍', '小明', '志華', '文文']
    
    item1, item2 = random.choice(items)
    context, op, unit = random.choice(contexts)
    person = random.choice(people)
    
    diff = random.randint(10, 50)
    
    n1 = random.randint(2, 6)
    n2 = random.randint(2, 6)
    
    # Part 1: Ask for total cost
    question_text = (
        f"已知一個{item1} {var} {unit}，一個{item2}比一個{item1}{context} {diff} {unit}，"
        f"用含有 {var} 的代數式，回答下列問題。<br>"
        f"{person}買了 {n1} 個{item1}、{n2} 個{item2}共需多少{unit}？"
    )
    
    op_sign = 1 if op == '+' else -1
    
    # Total cost = n1*x + n2*(x + op_sign*diff)
    ans_coeff = n1 + n2
    ans_const = n2 * op_sign * diff
    
    correct_answer = _build_answer_expression(ans_coeff, ans_const, var=var)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「一元一次式的運算」相關題目 (標準 LaTeX 範本)。
    """
    problem_types = [
        'mult_div', 'add_sub', 'simplify_basic', 'distributive_simple',
        'distributive_complex', 'fractional_expr', 'word_problem'
    ]
    # Make some types more common than others
    weights = [10, 15, 15, 15, 15, 15, 15]
    problem_type = random.choices(problem_types, weights=weights, k=1)[0]
    
    if problem_type == 'mult_div':
        return generate_mult_div_problem()
    elif problem_type == 'add_sub':
        return generate_add_sub_problem()
    elif problem_type == 'simplify_basic':
        return generate_simplify_basic_problem()
    elif problem_type == 'distributive_simple':
        return generate_distributive_simple_problem()
    elif problem_type == 'distributive_complex':
        return generate_distributive_complex_problem()
    elif problem_type == 'fractional_expr':
        return generate_fractional_expr_problem()
    elif problem_type == 'word_problem':
        return generate_word_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    For algebraic expressions, this is a simplified check.
    It expects a canonical form (e.g., ax+b, no extra spaces).
    """
    # Normalize by removing spaces and making variable lowercase
    user_ans_norm = user_answer.strip().replace(" ", "").lower()
    correct_ans_norm = correct_answer.strip().replace(" ", "").lower()
    
    is_correct = (user_ans_norm == correct_ans_norm)
    
    # A simple check for commutative property in simple cases like '12+5x' vs '5x+12'
    if not is_correct and '+' in correct_ans_norm:
        parts = correct_ans_norm.split('+', 1)
        if len(parts) == 2:
            reversed_ans = f"{parts[1]}+{parts[0]}"
            if user_ans_norm == reversed_ans:
                is_correct = True
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}