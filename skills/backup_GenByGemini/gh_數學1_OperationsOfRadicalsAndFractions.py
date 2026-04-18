import random
from fractions import Fraction
import math

# --- Helper Functions ---

def simplify_radical(n):
    """
    Simplifies a radical expression sqrt(n).
    Returns a tuple (coefficient, radicand).
    e.g., simplify_radical(12) returns (2, 3) for 2*sqrt(3).
    """
    if n == 0:
        return 0, 1
    if n < 0:
        raise ValueError("Radical of a negative number is not supported in this context.")
    
    i = int(math.sqrt(n))
    while i > 1:
        if n % (i*i) == 0:
            return i, n // (i*i)
        i -= 1
    return 1, n

def format_radical(coeff, radicand):
    """
    Formats a radical into a LaTeX string without a leading sign.
    e.g., (2, 3) -> "2\\sqrt{3}"
    e.g., (1, 5) -> "\\sqrt{5}"
    e.g., (5, 1) -> "5"
    """
    if coeff == 0:
        return "0"
    
    if radicand == 1:
        return str(abs(coeff))
        
    if abs(coeff) == 1:
        return f"\\sqrt{{{radicand}}}"
    
    return f"{abs(coeff)}\\sqrt{{{radicand}}}"

# --- Problem Generation Functions ---

def generate_simplify_add_subtract():
    """
    Generates a problem for simplifying the sum or difference of radicals.
    e.g., sqrt(12) + sqrt(75)
    """
    radicand = random.choice([2, 3, 5, 6, 7])
    c1 = random.randint(2, 5)
    c2 = random.randint(2, 5)
    op_sym = random.choice(['+', '-'])

    if op_sym == '-' and c1 == c2:
        c2 += 1
    if op_sym == '-' and c1 < c2:
        c1, c2 = c2, c1

    n1 = c1 * c1 * radicand
    n2 = c2 * c2 * radicand
    
    question_text = f"化簡下列各式：$\\sqrt{{{n1}}} {op_sym} \\sqrt{{{n2}}}$"
    
    if op_sym == '+':
        ans_coeff = c1 + c2
    else:
        ans_coeff = c1 - c2
    
    correct_answer = format_radical(ans_coeff, radicand)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiplication_formula():
    """
    Generates problems using multiplication formulas.
    e.g., (sqrt(7)+sqrt(2))(sqrt(7)-sqrt(2)) or (sqrt(5)+sqrt(3))^2
    """
    sub_type = random.choice(['diff_squares', 'perfect_square'])
    options = [2, 3, 5, 6, 7, 10, 11]
    a, b = random.sample(options, 2)
    
    if sub_type == 'diff_squares':
        question_text = f"化簡下列各式：$(\\sqrt{{{a}}} + \\sqrt{{{b}}})(\\sqrt{{{a}}} - \\sqrt{{{b}}})$"
        correct_answer = str(a - b)
    else: # perfect_square
        op_sym = random.choice(['+', '-'])
        if a < b and op_sym == '-': a, b = b, a 
        
        question_text = f"化簡下列各式：$(\\sqrt{{{a}}} {op_sym} \\sqrt{{{b}}})^2$"
        
        term1 = a + b
        coeff_rad, radicand_rad = simplify_radical(a * b)
        
        full_coeff = 2 * coeff_rad
        
        rad_part = format_radical(full_coeff, radicand_rad)
        
        correct_answer = f"{term1}{op_sym}{rad_part}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rationalize_denominator():
    """
    Generates a problem for rationalizing the denominator.
    e.g., 2 / (sqrt(5) - sqrt(3))
    """
    options = [2, 3, 5, 6, 7, 10, 11, 13]
    a, b = random.sample(options, 2)
    if a < b: a, b = b, a

    diff = a - b
    k = random.randint(1, 3)
    numerator = k * diff
    op_sym = random.choice(['+', '-'])

    question_text = f"化簡下列各式：$\\frac{{{numerator}}}{{\\sqrt{{{a}}}{op_sym}\\sqrt{{{b}}}}}$"

    ans_op_sym = '-' if op_sym == '+' else '+'
    
    part_a = format_radical(k, a)
    part_b = format_radical(k, b)
    
    correct_answer = f"{part_a}{ans_op_sym}{part_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_double_radical():
    """
    Generates a problem for simplifying double radicals.
    e.g., sqrt(4 + 2*sqrt(3))
    """
    options = [1, 2, 3, 5, 6, 7, 10, 11]
    x, y = random.sample(options, 2)
    if x < y: x, y = y, x

    op_sym = random.choice(['+', '-'])
    A = x + y
    B = x * y
    
    style = random.choice(['standard', 'hidden_2', 'outside_factor'])
    
    if B < 4 or style == 'standard':
        question_text = f"化簡下列各式：$\\sqrt{{{A} {op_sym} 2\\sqrt{{{B}}}}}$"
    elif style == 'hidden_2':
        question_text = f"化簡下列各式：$\\sqrt{{{A} {op_sym} \\sqrt{{{4*B}}}}}$"
    else: # 'outside_factor'
        k, r = simplify_radical(B)
        if k == 1: # No factor to pull out, revert to standard
             question_text = f"化簡下列各式：$\\sqrt{{{A} {op_sym} 2\\sqrt{{{B}}}}}$"
        else:
             question_text = f"化簡下列各式：$\\sqrt{{{A} {op_sym} {2*k}\\sqrt{{{r}}}}}$"

    sqrt_x = format_radical(1, x)
    sqrt_y = format_radical(1, y)
    
    correct_answer = f"{sqrt_x}{op_sym}{sqrt_y}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_comparison():
    """
    Generates a problem for comparing the magnitude of radical sums.
    e.g., compare sqrt(2)+sqrt(11) , sqrt(3)+sqrt(10) , sqrt(6)+sqrt(7)
    """
    S = random.randint(10, 25)
    pairs = []
    # Generate pairs (i, S-i) where i < S-i
    for i in range(1, S // 2):
        pairs.append((i, S - i))
    
    # Ensure we have at least 3 pairs
    while len(pairs) < 3:
        S += 1
        pairs = []
        for i in range(1, S // 2):
            pairs.append((i, S - i))

    p1, p2, p3 = random.sample(pairs, 3)
    
    # Create the question text, shuffling the assignment of a, b, c
    labels = ['a', 'b', 'c']
    random.shuffle(labels)
    
    question_parts = []
    
    prod_map = {} # Maps label ('a', 'b', 'c') to product
    
    for label, pair in zip(labels, [p1, p2, p3]):
        val1, val2 = pair
        question_parts.append(f"${label} = \\sqrt{{{val1}}} + \\sqrt{{{val2}}}$")
        prod_map[label] = val1 * val2

    question_text = f"比較下列各數的大小：{', '.join(question_parts)} 。<br>（請由小到大排列，例如 c<a<b）"
    
    # Sort labels based on their product value
    sorted_labels = sorted(prod_map.keys(), key=prod_map.get)
    correct_answer = f"{sorted_labels[0]}<{sorted_labels[1]}<{sorted_labels[2]}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_am_gm_inequality():
    """
    Generates a word problem based on the AM-GM inequality.
    e.g., maximizing rectangle area for a fixed perimeter.
    """
    L = random.randint(5, 25) * 2
    side = L / 4
    max_area = side * side
    
    question_text = f"用一條長度為 ${L}$ 公尺的繩子圍成一矩形，求所圍矩形的最大面積為多少平方公尺？"
    
    if max_area == int(max_area):
        correct_answer = str(int(max_area))
    else:
        correct_answer = str(max_area)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_integer_decimal_part():
    """
    Generates a problem involving integer and decimal parts of a radical number.
    e.g., for sqrt(3+2sqrt(2)), find a, b and compute 1/b - 1/(a+b)
    """
    m_candidates = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15]
    m = random.choice(m_candidates)
    k = int(math.sqrt(m))

    A = m + k*k
    B = k*k*m

    double_radical_expr = f"\\sqrt{{{A} + 2\\sqrt{{{B}}}}}"
    question_text = f"已知 ${double_radical_expr}$ 的整數部分為 $a$，小數部分為 $b$，求 $\\frac{{1}}{{b}} - \\frac{{1}}{{a+b}}$ 的值。"

    ans_num = 2 * k
    ans_den = m - k*k
    ans = Fraction(ans_num, ans_den)

    if ans.denominator == 1:
        correct_answer = str(ans.numerator)
    else:
        correct_answer = f"\\frac{{{ans.numerator}}}{{{ans.denominator}}}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    Generates a problem for the 'Operations of Radicals and Fractions' skill.
    """
    problem_types = [
        generate_simplify_add_subtract,
        generate_multiplication_formula,
        generate_rationalize_denominator,
        generate_double_radical,
        generate_comparison,
        generate_am_gm_inequality,
        generate_integer_decimal_part
    ]
    
    # Level 1: Basic simplification, multiplication, rationalization
    # Level 2: Double radicals, comparison
    # Level 3: AM-GM, integer/decimal part problems
    if level == 1:
        generator = random.choice(problem_types[0:3])
    elif level == 2:
        generator = random.choice(problem_types[3:5])
    else:
        generator = random.choice(problem_types[5:])
        
    return generator()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles numerical and symbolic answers.
    """
    # Normalize by removing spaces and making LaTeX commands consistent
    user_answer = user_answer.strip().replace(" ", "").replace("\\sqrt", "\\sqrt")
    correct_answer = correct_answer.strip().replace(" ", "")

    is_correct = (user_answer == correct_answer)

    # Very basic check for swapped terms in addition
    # e.g., "1+\\sqrt{2}" vs "\\sqrt{2}+1"
    if not is_correct and '+' in correct_answer and '+' in user_answer:
        # Avoid splitting on '+' if it's a sign inside a term.
        # This check is simple and only works for simple sums.
        if correct_answer.count('+') == 1 and user_answer.count('+') == 1:
            correct_parts = sorted(correct_answer.split('+'))
            user_parts = sorted(user_answer.split('+'))
            if correct_parts == user_parts:
                is_correct = True
    
    # Fallback for numerical answers
    if not is_correct:
        try:
            # Avoid using eval for security. Try float conversion.
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                 is_correct = True
        except (ValueError, TypeError):
             pass
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}