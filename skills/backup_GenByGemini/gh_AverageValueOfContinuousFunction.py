import random
from fractions import Fraction

def eval_poly(coeffs, x):
    """
    Evaluates a polynomial at a given x.
    coeffs are [c_n, c_{n-1}, ..., c_0] for c_n*x^n + ... + c_0.
    """
    result = Fraction(0)
    for i, coeff in enumerate(reversed(coeffs)):
        result += Fraction(coeff) * (Fraction(x)**i)
    return result

def get_antiderivative_coeffs(coeffs):
    """
    Calculates the coefficients of the antiderivative of a polynomial.
    If coeffs is [c_n, ..., c_0] for c_n*x^n + ... + c_0,
    Antiderivative will have coefficients [c_n/(n+1), ..., c_0/1, 0].
    """
    antider_coeffs = []
    for i, coeff in enumerate(coeffs):
        degree = len(coeffs) - 1 - i
        antider_coeffs.append(Fraction(coeff, degree + 1))
    antider_coeffs.append(Fraction(0)) # Constant of integration (ignored for definite integrals)
    return antider_coeffs

def definite_integral(coeffs, a, b):
    """
    Calculates the definite integral of a polynomial from a to b.
    """
    antider_coeffs = get_antiderivative_coeffs(coeffs)
    
    F_b = eval_poly(antider_coeffs, b)
    F_a = eval_poly(antider_coeffs, a)
    
    return F_b - F_a

def _format_poly_str_linear(coeffs, var='x'):
    """
    Formats a linear polynomial (c1*x + c0) into a LaTeX-friendly string.
    """
    c1, c0 = coeffs
    parts = []
    
    if c1 != 0:
        if c1 == 1:
            parts.append(var)
        elif c1 == -1:
            parts.append(f"-{var}")
        else:
            parts.append(f"{c1}{var}")
            
    if c0 != 0:
        if c0 > 0:
            if parts:
                parts.append(f"+{c0}")
            else:
                parts.append(str(c0))
        else: # c0 < 0
            parts.append(f"{c0}")
            
    if not parts:
        return "0"
    return "".join(parts)

def _format_poly_str_quadratic(coeffs, var='x'):
    """
    Formats a quadratic polynomial (c2*x^2 + c1*x + c0) into a LaTeX-friendly string.
    """
    c2, c1, c0 = coeffs
    parts = []
    
    # c2 term
    if c2 != 0:
        if c2 == 1:
            parts.append(f"{var}^{{2}}")
        elif c2 == -1:
            parts.append(f"-{var}^{{2}}")
        else:
            parts.append(f"{c2}{var}^{{2}}")
            
    # c1 term
    if c1 != 0:
        if c1 > 0:
            if parts:
                if c1 == 1: parts.append(f"+{var}")
                else: parts.append(f"+{c1}{var}")
            else:
                if c1 == 1: parts.append(var)
                else: parts.append(f"{c1}{var}")
        else: # c1 < 0
            if c1 == -1: parts.append(f"-{var}")
            else: parts.append(f"{c1}{var}")
            
    # c0 term
    if c0 != 0:
        if c0 > 0:
            if parts:
                parts.append(f"+{c0}")
            else:
                parts.append(str(c0))
        else: # c0 < 0
            parts.append(f"{c0}")
            
    if not parts:
        return "0"
    return "".join(parts)

def generate_avg_value_poly_problem(level):
    if level == 1: # Linear function
        a = random.randint(-3, 3)
        b = random.randint(a + 1, a + 5) # Ensure b > a

        c1 = random.randint(-5, 5)
        c0 = random.randint(-5, 5)
        
        coeffs = [c1, c0]
        while all(c == 0 for c in coeffs): # Ensure not all coefficients are zero
            c1 = random.randint(-5, 5)
            c0 = random.randint(-5, 5)
            coeffs = [c1, c0]
            
        func_str = _format_poly_str_linear(coeffs, 'x')
        
        question_text = f"求函數 ${{f(x)}} = ${func_str}$ 在閉區間 $[{a}, {b}]$ 上的平均值。"
        
    else: # level 2: Quadratic function
        a_val = random.randint(-2, 2)
        b_val = random.randint(a_val + 1, a_val + 4) # Ensure b_val > a_val

        c2 = random.randint(-3, 3)
        c1 = random.randint(-5, 5)
        c0 = random.randint(-5, 5)

        coeffs = [c2, c1, c0]
        while all(c == 0 for c in coeffs): # Ensure not all coefficients are zero
            c2 = random.randint(-3, 3)
            c1 = random.randint(-5, 5)
            c0 = random.randint(-5, 5)
            coeffs = [c2, c1, c0]
            
        func_str = _format_poly_str_quadratic(coeffs, 'x')

        question_text = f"求函數 ${{f(x)}} = ${func_str}$ 在閉區間 $[{a_val}, {b_val}]$ 上的平均值。"
        a, b = a_val, b_val

    integral_value = definite_integral(coeffs, a, b)
    interval_length = Fraction(b - a) # interval_length is guaranteed > 0
    
    correct_answer_frac = integral_value / interval_length
    
    correct_answer = str(correct_answer_frac)
    if '/' in correct_answer:
        num, den = map(int, correct_answer.split('/'))
        if den == 1:
            correct_answer = str(num)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_kinematics_displacement_problem(level):
    if level == 1: # Linear velocity function
        t1 = random.randint(0, 2)
        t2 = random.randint(t1 + 1, t1 + 4)

        c1 = random.randint(-4, 4)
        c0 = random.randint(-5, 5)

        coeffs = [c1, c0]
        while all(c == 0 for c in coeffs):
            c1 = random.randint(-4, 4)
            c0 = random.randint(-5, 5)
            coeffs = [c1, c0]
            
        func_str = _format_poly_str_linear(coeffs, 't')

        question_text = f"某物體的運動速度函數為 ${{v(t)}} = ${func_str}$ (m/s)，求此物體在時間區間 $[{t1}, {t2}]$ (秒) 內的位移。"
    else: # level 2: Quadratic velocity function
        t1 = random.randint(0, 1)
        t2 = random.randint(t1 + 2, t1 + 4)

        c2 = random.randint(-2, 2)
        c1 = random.randint(-4, 4)
        c0 = random.randint(-5, 5)

        coeffs = [c2, c1, c0]
        while all(c == 0 for c in coeffs):
            c2 = random.randint(-2, 2)
            c1 = random.randint(-4, 4)
            c0 = random.randint(-5, 5)
            coeffs = [c2, c1, c0]

        func_str = _format_poly_str_quadratic(coeffs, 't')

        question_text = f"某物體的運動速度函數為 ${{v(t)}} = ${func_str}$ (m/s)，求此物體在時間區間 $[{t1}, {t2}]$ (秒) 內的位移。"
        
    correct_answer_frac = definite_integral(coeffs, t1, t2)
    
    correct_answer = str(correct_answer_frac)
    if '/' in correct_answer:
        num, den = map(int, correct_answer.split('/'))
        if den == 1:
            correct_answer = str(num)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_kinematics_avg_velocity_problem(level):
    if level == 1: # Linear velocity function
        t1 = random.randint(0, 2)
        t2 = random.randint(t1 + 1, t1 + 4)

        c1 = random.randint(-4, 4)
        c0 = random.randint(-5, 5)
        
        coeffs = [c1, c0]
        while all(c == 0 for c in coeffs):
            c1 = random.randint(-4, 4)
            c0 = random.randint(-5, 5)
            coeffs = [c1, c0]

        func_str = _format_poly_str_linear(coeffs, 't')

        question_text = f"某物體的運動速度函數為 ${{v(t)}} = ${func_str}$ (m/s)，求此物體在時間區間 $[{t1}, {t2}]$ (秒) 內的平均速度。"
    else: # level 2: Quadratic velocity function
        t1 = random.randint(0, 1)
        t2 = random.randint(t1 + 2, t1 + 4)

        c2 = random.randint(-2, 2)
        c1 = random.randint(-4, 4)
        c0 = random.randint(-5, 5)
        
        coeffs = [c2, c1, c0]
        while all(c == 0 for c in coeffs):
            c2 = random.randint(-2, 2)
            c1 = random.randint(-4, 4)
            c0 = random.randint(-5, 5)
            coeffs = [c2, c1, c0]

        func_str = _format_poly_str_quadratic(coeffs, 't')

        question_text = f"某物體的運動速度函數為 ${{v(t)}} = ${func_str}$ (m/s)，求此物體在時間區間 $[{t1}, {t2}]$ (秒) 內的平均速度。"
        
    integral_value = definite_integral(coeffs, t1, t2)
    interval_length = Fraction(t2 - t1)
    
    correct_answer_frac = integral_value / interval_length
    
    correct_answer = str(correct_answer_frac)
    if '/' in correct_answer:
        num, den = map(int, correct_answer.split('/'))
        if den == 1:
            correct_answer = str(num)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    problem_type = random.choice([
        'avg_value_poly',
        'kinematics_displacement',
        'kinematics_avg_velocity'
    ])

    if problem_type == 'avg_value_poly':
        return generate_avg_value_poly_problem(level)
    elif problem_type == 'kinematics_displacement':
        return generate_kinematics_displacement_problem(level)
    else: # 'kinematics_avg_velocity'
        return generate_kinematics_avg_velocity_problem(level)

def check(user_answer, correct_answer):
    try:
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        is_correct = (user_frac == correct_frac)
    except ValueError:
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}