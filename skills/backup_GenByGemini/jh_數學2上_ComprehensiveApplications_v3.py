import random
import math

# Helper function to format a binomial (ax + b) into a string.
def _format_binomial(a, b, var='x'):
    """Formats a binomial (ax+b) into a string like (2x - 3) or (x + 1)."""
    if a == 0 and b == 0:
        return "(0)"
    if a == 0:
        return f"({b})"
    
    if a == 1:
        a_str = var
    elif a == -1:
        a_str = f"-{var}"
    else:
        a_str = f"{a}{var}"
    
    if b == 0:
        return f"({a_str})"
    elif b > 0:
        return f"({a_str} + {b})"
    else: # b < 0
        return f"({a_str} - {-b})"

# Helper function to format a quadratic polynomial ax^2+bx+c.
def _format_quadratic(a, b, c, var='x'):
    """Formats a quadratic polynomial ax^2+bx+c into a LaTeX string."""
    parts = []
    if a == 1:
        parts.append(f"{var}^2")
    elif a == -1:
        parts.append(f"-{var}^2")
    elif a != 0:
        parts.append(f"{a}{var}^2")

    if b != 0:
        b_val = abs(b)
        b_sign = "+" if b > 0 else "-"
        b_term = f"{var}" if b_val == 1 else f"{b_val}{var}"
        if not parts:
            parts.append(f"{b_sign if b_sign == '-' else ''}{b_term}")
        else:
            parts.append(f"{b_sign} {b_term}")

    if c != 0:
        c_val = abs(c)
        c_sign = "+" if c > 0 else "-"
        if not parts:
            parts.append(f"{c_sign if c_sign == '-' else ''}{c_val}")
        else:
            parts.append(f"{c_sign} {c_val}")

    if not parts:
        return "0"
    return ' '.join(parts)


# --- Problem Generation Functions ---

def _generate_neg_lead_cross_mult():
    """Type 1: Negative Leading Coefficient + Cross-Multiplication.
       e.g., -x^2 + 2x + 63 = -(x+7)(x-9)
    """
    p, r = 1, random.choice([1, 2, 3])
    q = random.randint(1, 9) * random.choice([-1, 1])
    s = random.randint(1, 9) * random.choice([-1, 1])
    
    while p * s + q * r == 0 or (p==r and abs(q)==abs(s)): # Avoid zero middle term and perfect squares
        s = random.randint(1, 9) * random.choice([-1, 1])

    a, b, c = p * r, p * s + q * r, q * s
    
    poly_str = _format_quadratic(-a, -b, -c)
    
    f1 = _format_binomial(p, q)
    f2 = _format_binomial(r, s)
    
    ans1 = f"-{f1}{f2}"
    ans2 = f"-{f2}{f1}"
    correct_answer = f"{ans1}|{ans2}"

    question_text = f"因式分解 ${poly_str}$。"
    return {
        "question_text": question_text,
        "answer": ans1,
        "correct_answer": correct_answer
    }

def _generate_common_factor_perfect_square():
    """Type 2: Common Numeric Factor + Perfect Square.
       e.g., 8y^2 + 40y + 50 = 2(2y+5)^2
    """
    k = random.choice([2, 3, 5])
    a = random.randint(1, 3)
    b = random.randint(1, 5) * random.choice([-1, 1])
    var = random.choice(['x', 'y'])
    
    c2, c1, c0 = k * a * a, k * 2 * a * b, k * b * b
    poly_str = _format_quadratic(c2, c1, c0, var)
    
    factor = _format_binomial(a, b, var)
    correct_answer = f"{k}{factor}^2"
    
    question_text = f"因式分解 ${poly_str}$。"
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_common_factor_cross_mult():
    """Type 3: Common Numeric Factor + Cross-Multiplication.
       e.g., 24x^2 + 30x - 9 = 3(2x+3)(4x-1)
    """
    k = random.choice([2, 3, 5, 7])
    p, r = 1, random.choice([2, 3, 4])
    q = random.randint(1, 7) * random.choice([-1, 1])
    s = random.randint(1, 7) * random.choice([-1, 1])

    while p * s + q * r == 0:
        s = random.randint(1, 7) * random.choice([-1, 1])
    
    a, b, c = p * r, p * s + q * r, q * s
    c2, c1, c0 = k * a, k * b, k * c
    
    poly_str = _format_quadratic(c2, c1, c0)
    
    f1 = _format_binomial(p, q)
    f2 = _format_binomial(r, s)
    
    ans1 = f"{k}{f1}{f2}"
    ans2 = f"{k}{f2}{f1}"
    correct_answer = f"{ans1}|{ans2}"

    question_text = f"因式分解 ${poly_str}$。"
    return {
        "question_text": question_text,
        "answer": ans1,
        "correct_answer": correct_answer
    }

def _generate_common_var_factor_mcq():
    """Type 4: Common Variable Factor + Cross-Multiplication (Multiple Choice).
       e.g., 22x^7 - 83x^6 + 21x^5 = x^5(2x-7)(11x-3)
    """
    var = 'x'
    n = random.randint(3, 5)
    
    p = random.choice([1, 2])
    r = random.choice([3, 5, 7])
    q = random.randint(1, 7) * random.choice([-1, 1])
    s = random.randint(1, 7) * random.choice([-1, 1])
    while p*s + q*r == 0:
        s = random.randint(1, 7) * random.choice([-1, 1])
        
    a, b, c = p * r, p * s + q * r, q * s

    terms = [f"{a}{var}^{{{n+2}}}"]
    if b > 0: terms.append(f"+ {b}{var}^{{{n+1}}}")
    elif b < 0: terms.append(f"- {-b}{var}^{{{n+1}}}")
    if c > 0: terms.append(f"+ {c}{var}^{{{n}}}")
    elif c < 0: terms.append(f"- {-c}{var}^{{{n}}}")
    poly_str = ' '.join(terms)

    f1 = _format_binomial(p, q, var)
    f2 = _format_binomial(r, s, var)
    
    # Correct option
    correct_power = random.randint(1, n)
    correct_poly = random.choice([f1, f2])
    if correct_power == 1:
        correct_option_str = f"${var}{correct_poly}$"
    else:
        correct_option_str = f"${var}^{correct_power}{correct_poly}$"

    # Distractors
    options = {correct_option_str}
    while len(options) < 4:
        distractor_type = random.randint(1, 3)
        if distractor_type == 1: # Wrong sign
            options.add(f"${var}^{n}{_format_binomial(p, -q, var)}$")
        elif distractor_type == 2: # Wrong power
            options.add(f"${var}^{{{n+1}}}{f2}$")
        else: # Wrong combination
            options.add(f"${var}{_format_binomial(r, q, var)}$")

    options = list(options)
    random.shuffle(options)
    
    correct_label = 'ABCD'[options.index(correct_option_str)]
    
    options_str = "\n".join([f"({label}) {opt}" for label, opt in zip('ABCD', options)])
    
    question_text = f"下列何者是 ${poly_str}$ 的因式？\n{options_str}"

    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def _generate_diff_of_squares():
    """Type 5: Difference of Squares with Binomials.
       e.g., (4x+9)^2 - (3x-2)^2 = 7(x+1)(x+11)
    """
    var = 'x'
    a = random.randint(2, 6)
    c = random.randint(1, 5)
    if a == c: c += 1
    
    b = random.randint(-9, 9)
    d = random.randint(-9, 9)
    while a == -c and b == -d: # Avoids A+B=0
        d = random.randint(-9, 9)

    term1 = _format_binomial(a, b, var)
    term2 = _format_binomial(c, d, var)
    poly_str = f"{term1}^2 - {term2}^2"
    
    sum_a, sum_b = a + c, b + d
    diff_a, diff_b = a - c, b - d

    g1 = math.gcd(sum_a, sum_b) if sum_a != 0 or sum_b != 0 else 1
    g2 = math.gcd(diff_a, diff_b) if diff_a != 0 or diff_b != 0 else 1
    
    common_factor = g1 * g2

    f1_a, f1_b = sum_a // g1, sum_b // g1
    f2_a, f2_b = diff_a // g2, diff_b // g2
    
    factor1 = _format_binomial(f1_a, f1_b, var)
    factor2 = _format_binomial(f2_a, f2_b, var)

    cf_str = str(common_factor) if common_factor != 1 else ""

    ans1 = f"{cf_str}{factor1}{factor2}"
    ans2 = f"{cf_str}{factor2}{factor1}"
    
    correct_answer = f"{ans1}|{ans2}" if factor1 != factor2 else ans1

    question_text = f"因式分解 ${poly_str}$。"
    return {
        "question_text": question_text,
        "answer": ans1,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    生成「綜合應用因式分解」相關題目。
    題型包含：
    1. 提出負號，再十字交乘
    2. 提出公因數，再利用完全平方公式
    3. 提出公因數，再十字交乘
    4. 提出公變數，再因式分解（選擇題）
    5. 利用平方差公式分解二項式
    """
    problem_generators = [
        _generate_neg_lead_cross_mult,
        _generate_common_factor_perfect_square,
        _generate_common_factor_cross_mult,
        _generate_common_var_factor_mcq,
        _generate_diff_of_squares
    ]
    
    return random.choice(problem_generators)()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_cleaned = user_answer.strip().replace(' ', '').replace('**', '^')
    
    # For multiple choice questions (A, B, C, D)
    if correct_answer in ['A', 'B', 'C', 'D']:
        is_correct = (user_answer_cleaned.upper() == correct_answer)
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # For factoring questions, which may have multiple correct forms (swapped factors)
    # The correct_answer string contains all valid forms separated by '|'
    valid_answers = [ans.strip().replace(' ', '').replace('**', '^') for ans in correct_answer.split('|')]
    
    is_correct = user_answer_cleaned in valid_answers
    
    # Display the first valid answer as the canonical one
    display_answer = correct_answer.split('|')[0]
    
    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}