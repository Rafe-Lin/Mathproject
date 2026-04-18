import random
from fractions import Fraction
import re

def format_answer_string(num_obj):
    """
    Formats a number (int, float, Fraction) into a display-friendly string.
    Handles integers, decimals, and mixed numbers.
    Example: Fraction(44, 3) -> '14 2/3'
    """
    if isinstance(num_obj, float) and num_obj.is_integer():
        num_obj = int(num_obj)
    if isinstance(num_obj, int):
        return str(num_obj)
    if isinstance(num_obj, float):
        # To handle potential floating point inaccuracies like 2.4000000000000004
        return f"{num_obj:.10g}".rstrip('0').rstrip('.')

    frac = Fraction(num_obj).limit_denominator()

    if frac.denominator == 1:
        return str(frac.numerator)

    if abs(frac.numerator) < frac.denominator:
        return f"{frac.numerator}/{frac.denominator}"

    sign = "-" if frac.numerator < 0 else ""
    frac = abs(frac)
    whole_part = frac.numerator // frac.denominator
    rem_num = frac.numerator % frac.denominator

    if rem_num == 0:
        return f"{sign}{whole_part}"
    else:
        return f"{sign}{whole_part} {rem_num}/{frac.denominator}"

def format_number_latex(num):
    """Formats a number for LaTeX display in the question."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        sign = "-" if num.numerator < 0 else ""
        return f"{sign}\\frac{{{abs(num.numerator)}}}{{{num.denominator}}}"
    return format_answer_string(num) # For floats and ints

def generate(level=1):
    """
    生成「代數式求值」相關題目。
    包含：
    1. 一元一次式 (整數係數)
    2. 一元一次式 (分數/小數係數)
    3. 應用問題
    """
    problem_type = random.choice(['simple_monomial', 'simple_binomial', 'fractional_binomial', 'word_problem'])

    if problem_type == 'simple_monomial':
        problem = generate_simple_monomial_problem()
    elif problem_type == 'simple_binomial':
        problem = generate_simple_binomial_problem()
    elif problem_type == 'fractional_binomial':
        problem = generate_fractional_binomial_problem()
    else:
        problem = generate_word_problem()
    
    return problem

def generate_simple_monomial_problem():
    # 題型: 當 x = a 時, 求 kx 的值 (k, a 為整數或小數)
    coeff = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])
    
    if random.random() < 0.5:
        # x is an integer
        x_val = random.randint(-10, 10)
    else:
        # x is a decimal
        x_val = random.choice([-2.5, -1.5, -0.6, -0.5, 0.5, 0.6, 1.5, 2.5])

    result = coeff * x_val
    
    # Format expression: e.g., -1x -> -x, 1x -> x
    if coeff == 1:
        expr_str = "x"
    elif coeff == -1:
        expr_str = "-x"
    else:
        expr_str = f"{coeff}x"
        
    question_text = f"當 $x = {format_number_latex(x_val)}$ 時，求代數式 ${expr_str}$ 的值。"
    correct_answer = format_answer_string(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_simple_binomial_problem():
    # 題型: 當 x = c 時, 求 ax + b 的值 (a, b, c 為整數)
    a = random.randint(2, 9) * random.choice([-1, 1])
    b = random.randint(1, 20) * random.choice([-1, 1])
    x_val = random.randint(-5, 5)
    
    result = a * x_val + b

    # Format expression string nicely
    b_str = f" + {b}" if b > 0 else f" - {abs(b)}"
    expr_str = f"{a}x{b_str}"

    question_text = f"當 $x = {x_val}$ 時，求代數式 ${expr_str}$ 的值。"
    correct_answer = str(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_fractional_binomial_problem():
    # 題型: 當 x = c 時, 求 a - kx 的值 (k 為分數)
    const = random.randint(5, 20)
    op_choice = random.choice(['+', '-'])

    coeff_den = random.randint(2, 6)
    coeff_num = random.randint(1, coeff_den - 1)
    coeff = Fraction(coeff_num, coeff_den)

    # Choose x_val to be a multiple of the denominator to simplify calculations
    x_val = random.choice([-3, -2, -1, 1, 2, 3]) * coeff_den

    if op_choice == '+':
        result = Fraction(const) + coeff * Fraction(x_val)
    else:
        result = Fraction(const) - coeff * Fraction(x_val)

    op_str = f" {op_choice} "
    coeff_latex = f"\\frac{{{coeff_num}}}{{{coeff_den}}}"
    expr_str = f"{const}{op_str}{coeff_latex}x"

    question_text = f"當 $x = {x_val}$ 時，求代數式 ${expr_str}$ 的值。"
    correct_answer = format_answer_string(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting"
    }

def generate_word_problem():
    # 題型: 應用問題
    # 情境：百貨公司週年慶，衣服售價依公式計算
    item = random.choice(['T-shirt', '外套', '褲子', '帽子'])
    x_val = random.randint(20, 50) * 10 # 原價 200, 300, 400, 500

    # 產生售價公式
    den = random.choice([2, 4, 5, 10])
    # numerator is chosen so the fraction is like 3/4 or 4/5 (discount)
    num = random.randint(1, den - 1)
    # constant is chosen to be a small adjustment like -1, -10, +1, +10
    const = random.randint(1, 5) * random.choice([-1, 1]) * random.choice([1, 10])

    coeff = Fraction(num, den)
    result = coeff * x_val + const

    const_op = "+" if const > 0 else "-"
    expr_latex = f"(\\frac{{{num}}}{{{den}}}x {const_op} {abs(const)})"

    question_text = f"百貨公司舉辦週年慶，原價為 $x$ 元的{item}都改以 ${expr_latex}$ 元出售。若一件{item}原價 {x_val} 元，則應付多少元？"
    correct_answer = f"{int(result)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def parse_to_fraction(s):
    """Robustly parses a string into a Fraction object."""
    s = str(s).strip()
    # Remove common units like '元'
    s = re.sub(r'[元度歲$]', '', s)
    
    if not s:
        return None

    # Case 1: Mixed number like "14 2/3" or "-1 2/3"
    mixed_match = re.match(r'^(-?\d+)\s+(\d+)\s*/\s*(\d+)$', s)
    if mixed_match:
        whole = int(mixed_match.group(1))
        num = int(mixed_match.group(2))
        den = int(mixed_match.group(3))
        if den == 0: return None
        if whole < 0:
            return Fraction(whole * den - num, den)
        else:
            return Fraction(whole * den + num, den)

    # Case 2: Simple fraction, decimal or integer
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，能處理整數、小數、分數與帶分數。
    """
    user_frac = parse_to_fraction(user_answer)
    correct_frac = parse_to_fraction(correct_answer)

    is_correct = False
    if user_frac is not None and correct_frac is not None:
        # Compare as fractions. Use a tolerance for float-based fractions.
        if abs(float(user_frac) - float(correct_frac)) < 1e-9:
            is_correct = True

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
