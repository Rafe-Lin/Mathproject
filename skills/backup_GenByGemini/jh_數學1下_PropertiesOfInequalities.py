import random
from fractions import Fraction
import re

def _format_x_term(coeff):
    """Helper to format a term like `ax` into a string."""
    if coeff == 1:
        return "x"
    if coeff == -1:
        return "-x"
    return f"{{coeff}}x"

def _format_const_term(val, is_leading=False):
    """Helper to format a constant term into a string."""
    if val == 0 and not is_leading:
        return ""
    if is_leading:
        return str(val)
    if val > 0:
        return f"+{{val}}"
    return str(val)

def _format_fraction_val(frac):
    """Formats a Fraction object into a string (integer if possible)."""
    if frac.denominator == 1:
        return str(frac.numerator)
    else:
        # Ensure the negative sign is on the numerator for consistency
        if frac < 0:
            return f"-{{abs(frac.numerator)}}/{{abs(frac.denominator)}}"
        return f"{{frac.numerator}}/{{frac.denominator}}"

def generate(level=1):
    """
    生成「一元一次不等式」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 等量公理/移項 (level 1)
    2. 乘除負數變號 (level 2)
    3. 綜合運算 (含分數) (level 3)
    """
    if level == 1:
        problem_type = 'simple_add_sub'
    elif level == 2:
        problem_type = 'neg_mul_div'
    elif level == 3:
        problem_type = 'complex'
    else:
        problem_type = random.choice(['simple_add_sub', 'neg_mul_div', 'complex'])
    
    if problem_type == 'simple_add_sub':
        return generate_simple_add_sub_problem()
    elif problem_type == 'neg_mul_div':
        return generate_neg_mul_div_problem()
    else:
        return generate_complex_problem()

def generate_simple_add_sub_problem():
    """題型：x - a < b"""
    a = random.randint(1, 15)
    b = random.randint(-10, 10)
    op = random.choice(['+', '-'])
    ineq_sym = random.choice(['<', '>', '<=', '>='])
    
    if op == '+':
        # x + a > b  =>  x > b - a
        val = b - a
        question_text = f"解一元一次不等式 $x + {a} {ineq_sym} {b}$。"
    else:
        # x - a > b  => x > b + a
        val = b + a
        question_text = f"解一元一次不等式 $x - {a} {ineq_sym} {b}$。"

    correct_answer = f"x {ineq_sym} {val}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_neg_mul_div_problem():
    """題型：-ax > b"""
    a = random.randint(2, 9)
    # Make b a non-zero multiple of a to ensure integer solution
    c = random.choice([i for i in range(-5, 6) if i != 0])
    b = a * c
    ineq_sym = random.choice(['<', '>', '<=', '>='])
    
    question_text = f"解一元一次不等式 $-{a}x {ineq_sym} {b}$。"
    
    # Flip the inequality sign
    flip_map = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
    flipped_ineq = flip_map[ineq_sym]
    
    # -ax > b  =>  x < b / (-a)
    val = b // (-a)
    correct_answer = f"x {flipped_ineq} {val}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_complex_problem():
    """題型：(ax+b)/c < (dx+e)/f"""
    c = random.randint(2, 5)
    f = random.randint(2, 5)
    while c == f:
        f = random.randint(2, 5)
        
    a, d = 0, 0
    # Ensure the final x-coefficient is not zero
    while a * f - c * d == 0:
        a = random.randint(-3, 3)
        d = random.randint(-3, 3)
        if a == 0: a = random.choice([-1, 1])
        if d == 0: d = random.choice([-1, 1])

    b = random.randint(-9, 9)
    e = random.randint(-9, 9)
    
    ineq_sym = random.choice(['<', '>', '<=', '>='])
    
    # Build LaTeX for the fractions
    term1_num = f"{{_format_x_term(a)}}{{_format_const_term(b)}}"
    term2_num = f"{{_format_x_term(d)}}{{_format_const_term(e)}}"
    frac1_latex = f"\\frac{{{term1_num}}}{{{c}}}"
    frac2_latex = f"\\frac{{{term2_num}}}{{{f}}}"

    question_text = f"解一元一次不等式 ${frac1_latex} {ineq_sym} {frac2_latex}$。"

    # Solve the inequality
    # f*(ax+b) < c*(dx+e)
    # afx + bf < cdx + ce
    # (af - cd)x < ce - bf
    coeff_x = a * f - c * d
    const = c * e - b * f
    
    final_ineq = ineq_sym
    if coeff_x < 0:
        flip_map = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
        final_ineq = flip_map[ineq_sym]

    val = Fraction(const, coeff_x)
    val_str = _format_fraction_val(val)
    
    correct_answer = f"x {final_ineq} {val_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查不等式答案是否正確。處理 `x<5` 和 `5>x` 等不同形式。
    """
    user_answer_norm = user_answer.replace(' ', '').lower()
    correct_answer_norm = correct_answer.replace(' ', '').lower()

    # Pattern to capture `var op val`, e.g., x < 5 or x >= -1/2
    pattern = re.compile(r"([a-zA-Z])\s*([<>=!]+)\s*(-?[\d\./]+)")
    # Pattern to capture `val op var`, e.g., 5 > x
    flipped_pattern = re.compile(r"(-?[\d\./]+)\s*([<>=!]+)\s*([a-zA-Z])")

    match_correct = pattern.match(correct_answer_norm)
    if not match_correct:
        # Fallback for unexpected correct_answer format (should not happen)
        is_correct = (user_answer_norm == correct_answer_norm)
    else:
        var_correct, op_correct, val_str_correct = match_correct.groups()
        val_correct = Fraction(val_str_correct)
        is_correct = False

        # Try to parse user answer in `x op val` format
        match_user = pattern.match(user_answer_norm)
        if match_user:
            var_user, op_user, val_str_user = match_user.groups()
            try:
                val_user = Fraction(val_str_user)
                if var_user == var_correct and op_user == op_correct and val_user == val_correct:
                    is_correct = True
            except (ValueError, ZeroDivisionError):
                pass  # Invalid number format

        # If not correct, try to parse `val op x` format
        if not is_correct:
            flipped_match_user = flipped_pattern.match(user_answer_norm)
            if flipped_match_user:
                val_str_user, op_user, var_user = flipped_match_user.groups()
                flip_map = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
                try:
                    val_user = Fraction(val_str_user)
                    # Check if user's flipped notation matches the correct answer
                    if (var_user == var_correct and op_user in flip_map and 
                        flip_map[op_user] == op_correct and val_user == val_correct):
                        is_correct = True
                except (ValueError, ZeroDivisionError):
                    pass
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}